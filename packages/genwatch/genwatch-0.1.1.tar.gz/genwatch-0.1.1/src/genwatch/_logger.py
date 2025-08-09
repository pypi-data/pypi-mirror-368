import json
import logging
from datetime import datetime

class Encoder(json.JSONEncoder):
    def default(self, object):
        try:
            return super().default(object)
        except TypeError as e:
            return repr(object)

class JSONFormatter(logging.Formatter):
    def formatTime(self, record, datefmt = None):
        now = datetime.fromtimestamp(record.created)
        return now.isoformat() if datefmt is None else now.strftime(datefmt)

    def format(self, record: logging.LogRecord):
        lineno = {} if (lineno := record.msg.get("lineno")) is None else {"lineno": lineno}
        msg = {"timestamp": self.formatTime(record,self.datefmt), "level": record.levelname,
                "filename":record.msg["filename"],"msg": record.msg["msg"]} | lineno
        return json.dumps(msg, cls = Encoder)
    

