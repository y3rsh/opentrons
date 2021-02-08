import typing
import sqlite3

from dataclasses import dataclass
from datetime import datetime

from opentrons import APIVersion


@dataclass
class SimulationEntry:
    name: str
    author: str
    content_hash: str
    api_version: APIVersion
    robot_version: str
    ts: datetime
    id: int


class SimulationHistoryDB:
    """Simulation history database interface"""

    _connection: sqlite3.Connection

    def __init__(self, location: str) -> None:
        """Construct."""
        self._connection = self.create_connection(location)

    @staticmethod
    def create_connection(location: str) -> sqlite3.Connection:
        """Create and initialize db connection."""
        connection = sqlite3.connect(location)
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS simhistory (
                id INTEGER PRIMARY KEY,
                name TEXT,
                author TEXT,
                content_hash TEXT,
                api_version TEXT,
                robot_version TEXT,
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
        return connection

    def add(
            self,
            name: str,
            author: str,
            content_hash: str,
            api_version: str,
            robot_version: str
    ) -> None:
        """Insert an entry into the simulation history table."""
        with self._connection:
            self._connection.execute(
                f"""
                INSERT INTO simhistory (
                    name, author, content_hash, api_version, robot_version)
                VALUES (
                    '{name}', '{author}', '{content_hash}',
                    '{api_version}', '{robot_version}'
                    )
                """
            )

    def find(
            self,
            name: str,
            content_hash: str,
            api_version: str,
            robot_version: str) \
            -> typing.Generator[SimulationEntry, None, None]:
        """Query for entries in simulation history table."""
        for row in self._connection.execute(
                f"""
                SELECT id, name, author, content_hash, api_version, robot_version, ts
                FROM simhistory
                WHERE name='{name}' and content_hash='{content_hash}' and
                    api_version='{api_version}' and robot_version='{robot_version}'"""):
            yield self._row_to_entry(row)

    def all(self) -> typing.Generator[SimulationEntry, None, None]:
        """Get all the entries in the history table."""
        for row in self._connection.execute(
                """
                SELECT id, name, author, content_hash,
                    api_version, robot_version, ts
                FROM simhistory
                """):
            yield self._row_to_entry(row)

    @staticmethod
    def _row_to_entry(row) -> SimulationEntry:
        """Convert a row to a SimulationEntry object."""
        return SimulationEntry(
            id=row[0],
            name=row[1],
            author=row[2],
            content_hash=row[3],
            api_version=APIVersion.from_string(row[4]),
            robot_version=row[5],
            ts=row[6]
        )
