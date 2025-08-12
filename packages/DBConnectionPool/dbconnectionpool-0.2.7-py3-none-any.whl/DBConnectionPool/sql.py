from .database import ConnectionPool
import argparse
import pymysql


def runsql(conn: ConnectionPool):
    sql = None
    while not sql == 'exit':
        if sql:
            try:
                if 'select' in sql:
                    with conn.select(sql) as r:
                        head = ''
                        for i in range(len(r.sqlres.columns)):
                            column = r.sqlres.columns[i]
                            head += column + ' | ' if not i == len(r.sqlres.columns) - 1 else ''
                            print(column, end=' | ' if not i == len(r.sqlres.columns) - 1 else '')
                        print()
                        for _ in range(len(head) + 5):
                            print('-', end='')
                        print()
                        for ro in range(r.sqlres.length):
                            row = r.sqlres.get(row=ro)
                            for i in range(len(r.sqlres.columns)):
                                column = r.sqlres.columns[i]
                                print(row[column], end=' | ' if not i == len(r.sqlres.columns) - 1 else '')
                            print()
                        print(f'{r.rowcount} row(s) returned')
                else:
                    r = conn.runsql(sql)
                    if sql[:4] == 'use ' and len(sql[4:].split(' ')) == 1:
                        r = conn.runsql(sql)
                    print(f'{r} row(s) changed')
            except Exception as e:
                print(f'Error: {e}')
        sql = input('>>>')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('password', help="The password for the mysql server.")
    parser.add_argument('-i', '--host', default='localhost', type=str, help="The host (ip) of the mysql server.")
    parser.add_argument('-p', '--port', default='3306', type=int, help="The port of the mysql server.")
    parser.add_argument('-u', '--user', default='root', type=str, help="The user for the mysql server.")
    parser.add_argument('-d', '--database', default=None, help="The databse to connect to.")
    args = parser.parse_args()
    host = args.host
    port = args.port
    user = args.user
    password = args.password
    db = args.database
    try:
        connection = ConnectionPool(password, user, host, port, db)
        print('Connection successful!')
        runsql(connection)
    except pymysql.err.OperationalError:
        print('Server not found!')
