import json
import os
import re
from abc import ABCMeta, abstractmethod

from climb.config import config

from grafcli.documents import Dashboard
from grafcli.exceptions import DocumentNotFound
from grafcli.storage import Storage
from grafcli.utils import try_import

sqlite3 = try_import('sqlite3')
mysql = try_import('mysql.connector')
psycopg2 = try_import('psycopg2')

SELECT_PATTERN = re.compile(r'^select', re.IGNORECASE)


class SQLStorage(Storage, metaclass=ABCMeta):
    NOW = "NOW()"

    def __init__(self, host):
        self._host = host
        self._config = config[host]
        self._connection = None
        self._setup()

    @abstractmethod
    def _setup(self):
        """Should initialize _connection attribute."""

    def _execute(self, query, **kwargs):
        cursor = self._connection.cursor()

        cursor.execute(query, kwargs)

        if SELECT_PATTERN.search(query):
            return cursor.fetchall()
        else:
            self._connection.commit()
            return None

    def list(self):
        query = """SELECT slug
                   FROM dashboard
                   ORDER BY id ASC"""

        result = self._execute(query)

        return [row[0] for row in result]

    def get(self, dashboard_id):
        query = """SELECT data
                   FROM dashboard
                   WHERE slug = %(slug)s"""

        result = self._execute(query, slug=dashboard_id)
        if not result:
            raise DocumentNotFound("There is no such dashboard: {}".format(dashboard_id))

        source = result[0][0]
        if isinstance(source, bytes):
            source = source.decode('utf-8')

        source = json.loads(source)

        return Dashboard(source, dashboard_id)

    def save(self, dashboard_id, dashboard):
        try:
            self.get(dashboard_id)
            query = """UPDATE dashboard
                       SET data = %(data)s, title = %(title)s, slug = %(new_slug)s
                       WHERE slug = %(slug)s"""
            self._execute(query,
                          data=json.dumps(dashboard.source),
                          title=dashboard.title,
                          new_slug=dashboard.slug,
                          slug=dashboard_id)
        except DocumentNotFound:
            query = """INSERT INTO dashboard (version, slug, title, data, org_id, created, updated)
                       VALUES (1, %(slug)s, %(title)s, %(data)s, 1, {now}, {now})""".format(now=self.NOW)
            self._execute(query, slug=dashboard_id, title=dashboard.title, data=json.dumps(dashboard.source))

    def remove(self, dashboard_id):
        query = """DELETE FROM dashboard
                   WHERE slug = %(slug)s"""

        self._execute(query, slug=dashboard_id)


class SQLiteStorage(SQLStorage):
    NOW = "DATETIME('now')"

    def _setup(self):
        path = os.path.expanduser(self._config['path'])
        self._connection = sqlite3.connect(path)

    def _execute(self, query, **kwargs):
        query = query.replace('%s', '?')
        query = re.sub(r'%\((\w+)\)s', r':\1', query)
        return super()._execute(query, **kwargs)


class MySQLStorage(SQLStorage):
    def _setup(self):
        self._connection = mysql.connect(host=self._config['host'],
                                         port=int(self._config['port']),
                                         user=self._config['user'],
                                         password=self._config['password'],
                                         database=self._config['database'])
        self._connection.autocommit = True


class PostgreSQLStorage(SQLStorage):
    def _setup(self):
        self._connection = psycopg2.connect(host=self._config['host'],
                                            port=int(self._config['port']),
                                            user=self._config['user'],
                                            password=self._config['password'],
                                            database=self._config['database'])
