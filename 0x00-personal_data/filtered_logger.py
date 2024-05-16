#!/usr/bin/env python3
"""Module that will obfusticate a given
string and help it out"""


from mysql.connector import connection
from typing import List, Sequence
import logging
import os
import re


PII_FIELDS = ('name', 'email', 'ssn', 'password', 'phone')


def filter_datum(fields: Sequence[str], redaction: str, message: str,
                 seperator: str) -> str:
    """Function to implement obfustication based"""
    if len(fields) > 0:
        pattern = r"(" + "|".join(fields) + r")" + r"(=.*?)" + seperator
        return re.sub(pattern, r"\1=" + redaction + seperator, message)
    return message


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
                """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: Sequence[str]) -> None:
        """The initialization method"""
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """The format method that will format respectilvely"""
        record_str = super(RedactingFormatter, self).format(record)
        return filter_datum(self.fields,
                            self.REDACTION,
                            record_str,
                            self.SEPARATOR)


def get_logger() -> logging.Logger:
    """Function that takes no argument and returns a Logger object"""
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.addHandler(handler)
    return logger


def get_db() -> connection.MySQLConnection:
    """Function that returns a mysql connector to a db"""
    user = os.getenv('PERSONAL_DATA_DB_USERNAME', "root")
    password = os.getenv('PERSONAL_DATA_DB_PASSWORD', "")
    host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    database = os.getenv('PERSONAL_DATA_DB_NAME')
    return connection.MySQLConnection(user=user,
                                      password=password,
                                      host=host,
                                      database=database)


def main() -> None:
    """Main Function that takes and return nothing
    Uses logger to log info from database"""
    logger = get_logger()
    col_names = ("name", "email", "phone", "ssn", "password", "ip",
                 "last_login", "user_agent")
    db_conn = get_db()
    curr = db_conn.cursor()
    curr.execute("SELECT * FROM users")
    row = curr.fetchone()
    while row is not None:
        msg_string = ""
        for i in range(len(col_names)):
            msg_string += f"{col_names[i]}={row[i]};"
        # print(msg_string)
        logger.info(msg_string)
        row = curr.fetchone()
    curr.close()
    db_conn.close()


if __name__ == "__main__":
    main()