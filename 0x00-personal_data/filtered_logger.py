import logging
import csv
import sys
import os
import re
import mysql.connector
from typing import List

class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """
        Initialize the RedactingFormatter with fields to obfuscate.
        Args:
            fields (List[str]): List of fields to obfuscate.
        """
        super().__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record, filtering values in incoming log records using filter_datum.
        Values for fields in self.fields should be filtered.
        """
        message = super().format(record)
        return filter_datum(self.fields, self.REDACTION, message, self.SEPARATOR)


def filter_datum(fields: List[str], redaction: str, message: str, separator: str) -> str:
    """
    Returns the log message obfuscated.
    
    """
    return re.sub(r'(?<=^|\b|\{0})({1})=[^;]*'.format(separator, '|'.join(fields)), lambda match: match.group(0).split('=')[0] + '=' + redaction, message)


PII_FIELDS = ("name", "email", "phone", "ssn", "password")

def get_logger() -> logging.Logger:
    """
    Returns a logging.Logger object named "user_data" with a StreamHandler and RedactingFormatter.
    Only logs up to logging.INFO level and does not propagate messages to other loggers.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    formatter = RedactingFormatter(fields=PII_FIELDS)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def get_db():
    """
    Returns a connector to the database (mysql.connector.connection.MySQLConnection object).
    """
    username = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    password = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    database = os.getenv("PERSONAL_DATA_DB_NAME")

    try:
        connection = mysql.connector.connect(
            user=username,
            password=password,
            host=host,
            database=database
        )
        return connection
    except mysql.connector.Error as err:
        print("Error connecting to the database:", err)
        raise

def main():
    # Obtain database connection
    db = get_db()
    cursor = db.cursor()

    # Retrieve all rows in the users table
    cursor.execute("SELECT * FROM users;")
    rows = cursor.fetchall()

    # Display each row under a filtered format
    logger = get_logger()
    for row in rows:
        formatted_row = "; ".join([f"{field}={value}" for field, value in zip(PII_FIELDS, row)])
        logger.info(formatted_row)

    cursor.close()
    db.close()

if __name__ == "__main__":
    main()
