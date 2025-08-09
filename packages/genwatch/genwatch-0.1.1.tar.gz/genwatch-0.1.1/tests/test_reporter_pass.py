import logging
import inspect
import pytest


from genwatch import GeneratorReporter as Reporter



# ----------------------------
# Helpers for the test suite
# ----------------------------

def drive_all(gen):
    """Exhaust a generator and return a list of yielded values."""
    out = []
    try:
        while True:
            out.append(next(gen))
    except StopIteration:
        pass
    return out


# ----------------------------
# Core behaviors
# ----------------------------

def test_decorate_non_generator_raises_typeerror():
    def not_a_gen():
        return 42
    with pytest.raises(TypeError):
        Reporter(not_a_gen)  # __new__ guard should raise

def test_basic_yield_sequence_and_logging(caplog):
    caplog.set_level(logging.INFO)
    @Reporter
    def g():
        yield "A"
        yield "B"

    it = g()
    assert next(it) == "A"
    assert next(it) == "B"
    with pytest.raises(StopIteration):
        next(it)

    # Should have logged the function name at least once
    assert any("g" in rec.message for rec in caplog.records)

def test_send_is_forwarded_and_affects_result(caplog):
    caplog.set_level(logging.INFO)
    @Reporter
    def g2():
        x = 10
        sent = yield x
        yield x + (sent or 0)

    it = g2()
    assert next(it) == 10
    assert it.send(5) == 15
    with pytest.raises(StopIteration):
        next(it)
    # Sanity: some logging happened for g2
    assert any("g2" in rec.message for rec in caplog.records)

def test_throw_forwarding_recovery_is_yielded_back(caplog):
    caplog.set_level(logging.INFO)

    @Reporter
    def recovering():
        try:
            yield "start"
        except RuntimeError:
            # recovery value
            yield "RECOVERED"
        yield "end"

    it = recovering()
    assert next(it) == "start"
    # Throw at the outer: wrapper should forward into inner and forward the recovery yield back
    assert it.throw(RuntimeError("boom")) == "RECOVERED"
    assert next(it) == "end"
    with pytest.raises(StopIteration):
        next(it)

    # The proxy logs the recovery path
    assert any("recovered from exception `.throw`" in rec.message for rec in caplog.records)

def test_close_then_next_raises_stopiteration(caplog):
    caplog.set_level(logging.INFO)
    @Reporter
    def g3():
        yield 1
        yield 2

    it = g3()
    assert next(it) == 1
    it.close()  # triggers GeneratorExit inside the proxy and closes inner
    with pytest.raises(StopIteration):
        next(it)  # closed generators cannot be advanced

def test_delegation_to_plain_generator_logs_entry_and_exit(caplog):
    caplog.set_level(logging.INFO)

    def subgen():
        yield "sub-1"
        yield "sub-2"

    @Reporter
    def outer():
        yield from subgen()
        yield "outer"

    it = outer()
    assert next(it) == "sub-1"
    assert next(it) == "sub-2"
    assert next(it) == "outer"
    with pytest.raises(StopIteration):
        next(it)

    # Reporter should note the subgenerator entry and later exit
    assert any("Entered subgenerator" in rec.message for rec in caplog.records)
    assert any("Exited subgenrator" in rec.message for rec in caplog.records)

def test_delegation_to_iterator_range_logs_iterator_path(caplog):
    caplog.set_level(logging.INFO)

    @Reporter
    def outer_iter():
        yield from range(3)
        yield "done"

    it = outer_iter()
    assert list(it) == [0, 1, 2, "done"]

    # Should log that we yielded from an iterator (non-generator)
    assert any("Yielding from iterator:" in rec.message for rec in caplog.records)

def test_nested_outer_logs_only_immediate_delegate(caplog):
    caplog.set_level(logging.INFO)

    def leaf():
        yield "L1"
        yield "L2"

    def mid():
        rv = yield from leaf()
        assert rv is None
        yield "M-after"

    @Reporter
    def outer():
        rv = yield from mid()
        assert rv is None
        yield "O-after"

    it = outer()
    assert next(it) == "L1"
    assert next(it) == "L2"
    assert next(it) == "M-after"
    assert next(it) == "O-after"
    with pytest.raises(StopIteration):
        next(it)

    # We only expect the immediate delegate (mid) to be logged, not leaf
    assert any("Entered subgenerator: mid" in rec.message for rec in caplog.records)
    assert not any("Entered subgenerator: leaf" in rec.message for rec in caplog.records)

def test_proxy_unwrap_when_sub_is_decorated(caplog):
    caplog.set_level(logging.INFO)

    @Reporter
    def sub_wrapped():
        got = yield 7
        yield 7 + (got or 0)

    @Reporter
    def outer_wrapped():
        rv = yield from sub_wrapped()
        assert rv is None
        yield "done"

    it = outer_wrapped()
    assert next(it) == 7
    assert it.send(3) == 10
    assert next(it) == "done"
    with pytest.raises(StopIteration):
        next(it)

    # Ensure we saw sub_wrapped by name (not ProxyReporter.__iter__)
    assert any("Entered subgenerator: sub_wrapped" in rec.message for rec in caplog.records)

def test_throw_send_throw_raw():
    def make_loop_gen():
        def gen():
            for _ in range(3):
                try:
                    val = yield _
                except RuntimeError:
                    val = yield "RECOVERED"
        return gen


    RawGen = make_loop_gen()
    WrappedGen = Reporter(RawGen)
    g = RawGen()
    next(g)                              # prime: yields 0
    assert g.throw(RuntimeError("x")) == "RECOVERED"
    assert g.send(None) == 1             # back inside the for-loop
    # Second throw should *also* be caught and recover
    assert g.throw(RuntimeError("x")) == "RECOVERED"