import pymysql
from abc import ABC, abstractmethod
from typing import Any, Callable, TypeAlias


disconnect_t: TypeAlias = Callable[[], None]
_Column: TypeAlias = str
_Row: TypeAlias = dict[_Column, Any]


class Table:
    """
    a class for managing the table data.
    """


    def __init__(self, data: tuple[_Row, ...], columns: list[str]) -> None:
        """
        store the data.

        <code>data: list[_Row]:</code> the data of the table.<br>
        <code>columns: list of strings:</code> the columns of the table.

        <code>return: None. </code>
        """

        self._data = data
        self.length = len(data)
        self.columns = columns

    
    def get(self, row: int, column: _Column | None = None) -> dict[_Column, Any] | Any | None:
        """
        get the data of the given column.

        <code>column: string:</code> the column to get.

        <code>return: list: </code> the data of the column.
        """
        return self._data[row][column] if column in self._data[row] else None if column else self._data[row] if row < len(self._data) else None


class ReturnedSqlType:
    """
    a class for managing the returned data from the databse.
    """


    def __init__(self, sqlres: list[_Row], rowcount: int, close: disconnect_t, columns: list[str]) -> None:
        """
        store the data.
        
        <code>sqlres: list of dictionarys:</code> the data itself.<br>
        sqlres is build like this:
        [row1, row2, ...]
        each row is:
        {column1: value, column2: value, ...}<br>
        <code>rowcount: integer:</code> the rowcount.<br>
        <code>close: callable:</code> a disconnect function.<br>
        <code>columns: list of strings:</code> the columns of the table.<br>
        
        <code>return: None. </code>
        """
        self.sqlres = Table(sqlres, columns)
        self.rowcount = rowcount
        self.close = close


    def __enter__(self):
        return self


    def __exit__(self, *exc) -> None:
        self.close()


class ConnectionPoolInterface(ABC):
    """
    an interface for the ConnectionPool class.
    """
    @abstractmethod
    def _connect(self):
        pass


    @abstractmethod
    def _disconnect(self: pymysql.connections.Connection):
        pass

    
    @abstractmethod
    def runsql(self, sql: str):
        pass


    @abstractmethod
    def select(self, sql: str) -> ReturnedSqlType:
        pass
