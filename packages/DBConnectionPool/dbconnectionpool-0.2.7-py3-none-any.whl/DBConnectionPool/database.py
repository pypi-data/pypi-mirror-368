import pymysql
import dbutils.pooled_db
import pymysql.cursors
import pymysql.connections
from . import interfaces


class ConnectionPool(interfaces.ConnectionPoolInterface):
    def __init__(self, password: str, user: str = 'root', host: str = 'localhost', port: int = 3306, database: str | None = None) -> None:
        """
        a class for managing the connection pool.

        <code>host: string: </code> the database host address.<br>
        <code>user: string: </code> the databse username.<br>
        <code>password: string: </code> the database password.<br>
        <code>database: string: </code> the default database of the connection.<br>
        <code>port: integer: </code> the port of the databse host.
        """
        self.pool = dbutils.pooled_db.PooledDB(
            creator=pymysql,
            maxconnections=10,
            mincached=2,
            maxcached=5,
            blocking=True,
            maxusage=None,
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            cursorclass=pymysql.cursors.DictCursor
        )


    def _connect(self) -> (pymysql.connections.Connection):
        """
        get a connection from the connection pool.
        """
        return self.pool.connection()


    def _disconnect(self, conn: pymysql.connections.Connection):
        """
        close the given connection.

        <code>conn: Connection: </code> the connection to be closed.

        <code>return: None. </code>
        """
        if conn:
            conn.close()


    def runsql(self, sql: str, placeholders: tuple | None = None) -> int:
        """
        runs sql in the database.

        <code>sql: string:</code> the sql to be runned.
        <code>placeholders: tuple | None:</code> placeholders to variables to protect from sql injection attacks.

        <code>return: integer: </code> the rowcount.
        """
        r = 0
        conn = self._connect()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, placeholders)
            conn.commit()
            r = cursor.rowcount
        self._disconnect(conn)
        return r


    def select(self, sql: str) -> interfaces.ReturnedSqlType:
        """
        select data from the database.

        <code>sql: string: </code> the sql to be runned.

        <code>return: _ReturnedSql: </code> an instance of the _ReturnedSql class containing the rowcount, the data itself, and a disconnect function.
        """
        conn = self._connect()
        with conn.cursor(pymysql.cursors.DictCursor) as crsor:
            crsor.execute(sql)
            columns = [desc[0] for desc in crsor.description] if crsor.description else []
            result = interfaces.ReturnedSqlType(crsor.fetchall(), crsor.rowcount, lambda: self._disconnect(conn), columns)
            return result
