from logging import getLogger, StreamHandler, Formatter, Handler, NOTSET, getLevelName
from datetime import datetime as date_time
from sqlite3 import connect


class DatabaseHandler(Handler):
    def __init__(self, db_file):
        super().__init__()
        self.db_file = db_file
        self.db_file = connect(self.db_file)
        self.db_file.execute(
            "CREATE TABLE IF NOT EXISTS logs (date TEXT, "
            "time TEXT, lvl INTEGER, lvl_name TEXT, msg TEXT, "
            "logger TEXT, lineno INTEGER)"
        )

    def emit(self, record):
        """
        Conditionally emit the specified logging record.

        Emission depends on filters which may have been added to the handler.
        Wrap the actual emission of the record with acquisition/release of
        the I/O thread lock. Returns whether the filter passed the record for
        emission.
        """
        self.db_file.execute(
            'INSERT INTO logs VALUES (:1,:2,:3,:4, :5, :6, :7)', (
                date_time.now().strftime('%A, the %d of %B, %Y'),
                date_time.now().strftime('%I:%M %p'),
                record.levelno,
                record.levelname,
                record.msg,
                record.name,
                record.lineno
            )
        )
        self.db_file.commit()
        self.db_file.close()


logger = getLogger(__name__)
logger.setLevel(10)

logger_database_handler = DatabaseHandler("summarizer_log.db")

logger.addHandler(logger_database_handler)
logger_database_handler.setLevel(10)

logger.log(msg="Something happened", level=10)

print(
    connect("test.db")
    .execute('SELECT name FROM sqlite_master WHERE type = "table"')
    .fetchall()
)
