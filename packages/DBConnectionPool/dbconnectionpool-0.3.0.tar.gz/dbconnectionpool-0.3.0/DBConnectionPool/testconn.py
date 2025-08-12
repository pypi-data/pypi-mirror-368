from .database import ConnectionPool
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('password', help="The password for the mysql server.")
    parser.add_argument('-i', '--host', default='localhost', type=str, help="The host (ip) of the mysql server.")
    parser.add_argument('-p', '--port', default='3306', type=int, help="The port of the mysql server.")
    parser.add_argument('-u', '--user', default='root', type=str, help="The user for the mysql server.")
    args = parser.parse_args()
    host = args.host
    port = args.port
    user = args.user
    password = args.password
    try:
        connection = ConnectionPool(password, user, host, port)
        print('Connection successful!')
    except:
        print('Server not found!')
