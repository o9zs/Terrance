from collections import namedtuple

from typing import Self
from sqlite3 import Connection, Row
from sqlite3 import Cursor as Sqlite3Cursor

def namedtuple_factory(cursor: Sqlite3Cursor, record: tuple):
    cls = namedtuple("Record", [column[0] for column in cursor.description])

    return cls._make(record)

class Cursor:
	def __init__(self, connection: Connection):
		self.connection = connection
		self.connection.row_factory = namedtuple_factory
		self.cursor = self.connection.cursor()
	
	def execute(self, command: str, *values: list) -> Self:
		self.cursor.execute(command, tuple(values))
		return self

	def get_field(self, command: str, *values: list):
		record = self.cursor.execute(command, tuple(values)).fetchone()

		return record[0]

	def get_column(self, command: str, *values: list) -> list:
		records = self.cursor.execute(command, tuple(values)).fetchall()

		return [record[0] for record in records]

	def get_record(self, command: str, *values: list) -> list:
		record = self.cursor.execute(command, tuple(values)).fetchone()
		
		return record
	
	def get_records(self, command: str, *values: list) -> list[tuple]:
		records = self.cursor.execute(command, tuple(values)).fetchall()

		return records
	
	def commit(self) -> Connection:
		self.connection.commit()

		return self.connection
	
	def close(self) -> Connection:
		self.connection.close()

		return self.connection