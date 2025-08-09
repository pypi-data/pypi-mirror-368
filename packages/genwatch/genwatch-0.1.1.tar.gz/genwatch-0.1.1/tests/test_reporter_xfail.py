import pytest
import logging

from genwatch import GeneratorReporter as Reporter


@pytest.mark.xfail(strict=True, reason="Outer only logs immediate delegate; does not recurse into nested leaf")
def test_outer_logs_nested_leaf_name(caplog):
    caplog.set_level(logging.INFO)

    def leaf():
        yield "L1"
        yield "L2"

    def mid():
        yield from leaf()

    @Reporter
    def outer():
        yield from mid()

    it = outer()
    # consume to completion
    try:
        while True:
            next(it)
    except StopIteration:
        pass

    # This is intentionally impossible with current design:
    assert any("Entered subgenerator: leaf" in rec.message for rec in caplog.records)


@pytest.mark.xfail(strict=True, reason="Iterators have no locals; current design does not log locals for iterators")
def test_iterator_locals_are_logged(caplog):
    caplog.set_level(logging.INFO)

    @Reporter
    def outer_iter():
        yield from range(2)
        yield "done"

    it = outer_iter()
    try:
        while True:
            next(it)
    except StopIteration:
        pass

    # Current implementation explicitly logs that iterators have no locals
    assert any("Locals of" in rec.message for rec in caplog.records)

@pytest.mark.xfail(strict=True, reason="Proxy yields outside try; second throw bubbles out")
def test_throw_send_throw_wrapped():
    
    def gen():
        for _ in range(3):
            try:
                val = yield _
            except RuntimeError:
                val = yield "RECOVERED"
        


    RawGen = gen
    WrappedGen = Reporter(RawGen)
    g = RawGen()
    next(g)                              # prime
    assert g.throw(RuntimeError("x")) == "RECOVERED"
    assert g.send(None) == 1
    # This triggers the issue: should recover but currently raises RuntimeError
    assert g.throw(RuntimeError("x")) == "RECOVERED"

    g = WrappedGen()
    assert g.throw(RuntimeError("x")) == "RECOVERED"
    assert g.send(None) == 1
    # This triggers the issue: should recover but currently raises RuntimeError
    assert g.throw(RuntimeError("x")) == "RECOVERED"