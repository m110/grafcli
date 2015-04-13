from abc import ABCMeta, abstractmethod
import importlib

from grafcli.config import config
from grafcli.storage import Storage


def try_import(module_name):
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        module = None

    return module

sqlite3 = try_import('sqlite3')
mysql = try_import('mysql.connector')
psycopg2 = try_import('psycopg2')


class SQLStorage(Storage, metaclass=ABCMeta):
    def __init__(self, host):
        self._host = host
        self._config = config[host]
        self._connection = None

    @abstractmethod
    def _setup(self):
        """Should initialize _connection attribute."""

    def _execute(self, query, **kwargs):
        cursor = self._connection.cursor()

        cursor.execute(query, kwargs)
        self._connection.commit()

        return cursor.fetchall()

    def list(self):
        query = """SELECT slug
                   FROM dashboard
                   ORDER BY id ASC"""

        result = self._execute(query)

        return [row[0] for row in result]

    def get(self, dashboard_id):
        query = """SELECT id, version, title, data
                   FROM dashboard
                   WHERE slug = %(slug)s"""

        result = self._execute(query, slug=dashboard_id)

        # TODO return a dashboard

    def save(self, dashboard_id, dashboard):
        if self.get(dashboard_id):
            # TODO UPDATE
            pass
        else:
            # TODO INSERT
            pass

    def remove(self, dashboard_id):
        query = """DELETE FROM dashboard
                   WHERE slug = %(slug)s"""

        self._execute(query, slug=dashboard_id)


class SQLiteStorage(SQLStorage):
    def _setup(self):
        self._connection = sqlite3.connect(self._config['path'])


class MySQLStorage(SQLStorage):
    def _setup(self):
        self._connection = mysql.connect(host=self._config['host'],
                                         port=int(self._config['port']),
                                         user=self._config['user'],
                                         password=self._config['password'],
                                         database=self._config['database'])


class PostgreSQLStorage(SQLStorage):
    def _setup(self):
        self._connection = psycopg2.connect(host=self._config['host'],
                                            port=int(self._config['port']),
                                            user=self._config['user'],
                                            password=self._config['password'],
                                            database=self._config['database'])
