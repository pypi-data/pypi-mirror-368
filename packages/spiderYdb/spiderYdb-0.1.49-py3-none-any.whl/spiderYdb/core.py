import datetime
import os

import traceback
import ydb
from ydb import ScanQuery

from .config import ydb_configuration
from .entity import Entity
from .entityMeta import EntityMeta

class DiagnosticDB(object):
    ReadBytes = 0
    ReadRows = 0
    IntervalEnd = 0
    RequestUnits = 0
    QueryText = ''
    def __init__(self,*args, **kwargs):
        for key in kwargs:
            self.__setattr__(key, kwargs[key])
    def to_object(self):
        return {
            'ReadBytes': self.ReadBytes,
            'ReadRows': self.ReadRows,
            'RequestUnits': self.RequestUnits,
            'IntervalEnd': datetime.datetime.fromtimestamp(int(self.IntervalEnd / 100_0000)),
            'QueryText': self.QueryText,
            'QueryText': self.QueryText,
        }

class Database:
    def __init__(self, *args, echo=False, show_traceback=False, stat=False, credentials=None, title_program='orm', connetion_timeout=5,
                 fail_fast=True, **kwargs):
        self.title_program = title_program
        self.stat = stat
        self.credentials = credentials
        self.echo = echo
        self.show_traceback = show_traceback
        self.config = ydb_configuration
        self.connetion_timeout = connetion_timeout
        self.fail_fast = fail_fast
        self.driver = self.create_driver()
        self._database = self.config.database
        self.pool = ydb.SessionPool(self.driver)
        # self.query_pool = ydb.QuerySessionPool(self.driver)
        self.entities = {}
        self.schema = None
        self.Entity = type.__new__(EntityMeta, 'Entity', (Entity,), {})
        self.Entity._database_ = self
        self.__item_list = []
        self._path = ''

    def create_driver(self):
        # driver_config = ydb.DriverConfig.default_from_endpoint_and_database(
        #     self.config.endpoint,
        #     self.config.database
        # )
        if not self.credentials:
            if os.getenv("SA_KEY_FILE"):
                self.credentials = ydb.iam.ServiceAccountCredentials.from_file(os.getenv("SA_KEY_FILE"),)
            else:
                self.credentials = ydb.iam.MetadataUrlCredentials()
        driver = ydb.Driver(
            endpoint=os.getenv("YDB_ENDPOINT"),
            database=os.getenv("YDB_DATABASE"),
            credentials=self.credentials
        )
        i = 0
        connected = False
        # print(self.connetion_timeout)
        while i < 5:
            try:
                driver.wait(fail_fast=self.fail_fast, timeout=self.connetion_timeout)
                connected = True
                break
            except Exception:
                i += 1
        if not connected:
            raise Exception("Can't connect to YDB")
        return driver

    def add_item(self, item):
        self.__item_list.append(item)
        return True

    def get_table(self, table_name):
        tables = {cls.__name__: cls for cls in self.Entity.__subclasses__()}
        return tables.get(table_name, None)

    def most_cost(self):
        sql = '''SELECT
    ReadBytes,
    ReadRows,
    IntervalEnd,
    QueryText
FROM `.sys/top_queries_by_read_bytes_one_hour`
WHERE Rank = 1
ORDER BY IntervalEnd DESC '''
        result = self.pool.retry_operation_sync(self.create_query(sql))[0].rows
        # print(result)
        # result = [DiagnosticDB(**_) for _ in result]
        result = [DiagnosticDB(**_).to_object() for _ in result]

        def custom_key(o):
            return o['IntervalEnd']

        result.sort(key=custom_key, reverse=True)

        return result

    def most_count(self):
        sql = '''SELECT
            RequestUnits,
            ReadBytes,
            ReadRows,
            IntervalEnd,
            QueryText
        FROM `.sys/top_queries_by_request_units_one_hour`
        WHERE Rank = 1
        ORDER BY IntervalEnd DESC '''
        result = self.pool.retry_operation_sync(self.create_query(sql))[0].rows
        # print(result)
        # result = [DiagnosticDB(**_) for _ in result]
        result = [DiagnosticDB(**_).to_object() for _ in result]

        def custom_key(o):
            return o['IntervalEnd']

        result.sort(key=custom_key, reverse=True)

        return result

    def save_all(self):
        for item in self.__item_list:
            item.save()

    def create_query(self, query, params={}):
        query = f"""PRAGMA TablePathPrefix("{self._database}");
        {query}"""

        def execute_query(session):
            if self.show_traceback:
                traceback.print_stack()
            if self.echo:
                # print('traceback', )
                print(query)
                print(params)
            prepared_query = session.prepare(query)
            result = session.transaction().execute(
                prepared_query,
                parameters=params,
                commit_tx=True,
                settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2),
            )
            if self.stat:
                pass
                # print('stat', dir(session))
            return result
        return execute_query


    def query(self, sql, params={}):
        if self.title_program:
            sql = f'''-- {self.title_program}
{sql}'''
        q = self.pool.retry_operation_sync(self.create_query(sql, params))


        # if self.stat:
        #     print(dir(q[0]))
        if q:
            return q[0].rows


    def scan_query(self, sql, params={}, parameters_types=None):
        if self.title_program:
            sql = f'''-- {self.title_program}
{sql}'''
        if self.echo:
            print(sql)
            print(params)

        query = ScanQuery(sql, parameters_types=parameters_types)
        items = self.driver.table_client.scan_query(query, parameters=params)
        return items

    def bulk(self, table, column_types, item_list):
        return self.driver.table_client.bulk_upsert(f'{self._database}/{table}', item_list, column_types)

    def create_table(self, table, params, pk):
        session = self.driver.table_client.session().create()
        columns = ydb.TableDescription()
        for param in params:
            columns.with_column(ydb.Column(param[0], ydb.OptionalType(param[1])))
        columns.with_primary_keys(*pk)
        session.create_table(
            self._database + '/' + table,
            columns
        )

    def update_columns(self, table, params, pk):
        path = self._database + '/' + table
        session = self.driver.table_client.session().create()
        result = session.describe_table(path)
        columns = [column.name for column in result.columns]
        new_columns = []
        for param in params:
            if param[0] not in columns:
                new_columns.append(ydb.Column(param[0], ydb.OptionalType(param[1])))
        if new_columns:
            session.alter_table(path, add_columns=new_columns)
