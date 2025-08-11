import ydb
from ydb import OptionalType, ScanQuery, ListType

from spiderYdb.fields import Field


class Query:
    def __init__(self, table, args, kwargs):
        self.args = args
        self.table = table
        self.q = table.select_fields
        self.database = table._database_
        self.view = table.view
        self.join_many = []
    def select(self):
        objects = self[:]
        return [self.table.from_dict(item) for item in objects]

    def count(self):
        self.q = 'count(*) AS c'
        objects = self[:]
        return objects[0]['c']

    def bulk(self, item_list):
        column_types = ydb.BulkUpsertColumns()
        # column_list = []
        for key in item_list[0]:
            if key in self.table.attrs_dict:
                # print(self.table.attrs_dict[key].ydb_type)
                column_types.add_column(key, OptionalType(self.table.attrs_dict[key].ydb_type))
                # column_types.add_column(key, self.table.attrs_dict[key].ydb_type)
        return self.database.bulk(self.table.table_name, column_types, item_list)

    def delete(self):
        declare = []
        where = []
        params = {}
        i = 0
        for _ in self.args:
            t, field, value = _
            name, param, title = f"{field.name}", f"param{i}", field.title
            if t in ['in']:
                declare.append(f"DECLARE ${param} AS List<{title}>;")
            else:
                declare.append(f"DECLARE ${param} AS {title};")
            params[f'${param}'] = value
            where.append(f'{name} {t} ${param}')
            i += 1
        sql = f'DELETE from {self.table.table_name}'
        if self.view:
            sql += f' view {self.view} '
            self.view = ''
            self.table.view = ''
        if declare:
            sql = '\n'.join(declare) + '\n' + sql
        if where:
            sql = sql + '\nWHERE ' + ' AND '.join(where)
        # print(sql)
        return self.database.query(sql, params)

    def get(self):
        objects = self[:2]
        if not objects:
            return None
        if len(objects) > 1:
            raise (Exception, 'Multiple objects were found. Use select(...) to retrieve them')
        return self.table.from_dict(objects[0])

    def _fetch(self, limit=None, offset=None, lazy=False):
        return QueryResult(self, limit, offset, lazy=lazy)

    def get_join(self):
        sql_join = []
        sql_fields = []
        if self.table.join_:
            self.table.join_ = [self.table.join_] if not isinstance(self.table.join_, list) else self.table.join_
            joins = {}
            for join in self.table.join_:
                # print(join.class_name)
                t1 = self.database.get_table(join.class_name)
                if not t1:
                    continue
                # print(t1)
                for i in vars(t1):
                    param = getattr(t1, i)
                    if not isinstance(param, Field):
                        continue
                    sql_fields.append(f"{t1.table_name}.{i}")

                    if param.foreign_key:
                        for ii in param.foreign_key:
                            if ii.split('.')[0] == self.table.table_name:
                                if not t1.table_name in self.join_many:
                                    self.join_many.append(t1.table_name)

                                joins[f'LEFT JOIN {t1.table_name} ON '] = joins.get(f'LEFT JOIN {t1.table_name} ON ', [])
                                joins[f'LEFT JOIN {t1.table_name} ON '].append(f'{t1.table_name}.{i} = {ii}')
                                # sql_join.append(f'JOIN {t1.table_name} ON {t1.table_name}.{i} = {ii}')



                for i in vars(self.table):
                    param = getattr(self.table, i)
                    if not isinstance(param, Field):
                        continue
                    if param.foreign_key:
                        for ii in param.foreign_key:
                            if ii.split('.')[0] == t1.table_name:
                                joins[f'LEFT JOIN {t1.table_name} ON '] = joins.get(f'LEFT JOIN {t1.table_name} ON ', [])
                                joins[f'LEFT JOIN {t1.table_name} ON '].append(f'{self.table.table_name}.{i} = {ii}')
                                # sql_join.append(f'LEFT JOIN {t1.table_name} ON {self.table.table_name}.{i} = {ii}')
            sql_join.append('\n'.join([i + ' AND '.join(joins[i]) for i in joins]))
            sql_join.append('\nLEFT JOIN productdescriptionitems ON productdescription.shop_id = productdescriptionitems.shop_id AND productdescription.title = productdescriptionitems.title')


        return sql_fields, sql_join

    def _actual_fetch(self, limit, offset):
        parameters_types = {}
        self.join_many = []
        declare = []
        where = []
        params = {}
        sql_fields, sql_join = self.get_join()
        i = 0
        for _ in self.args:
            t, field, value = _
            # name, title = f"{field.name}", field.title
            name, param, title = f"{field.name}", f"param{i}", field.title
            # print(name, param, title)
            if t in ['in']:
                declare.append(f"DECLARE ${param} AS List<{title}>;")
                parameters_types[f"$param{i}"] = ListType(field.ydb_type)
                if isinstance(value, list) or isinstance(value, set):
                    value = tuple(value)
            elif t == 'is NULL':
                pass
                # print('is NULL')
            else:
                declare.append(f"DECLARE ${param} AS {title};")
                parameters_types[f"$param{i}"] = field.ydb_type
            if t == 'is NULL':
                where.append(f'{field.table.table_name}.{name} {t}')
            else:
                params[f'${param}'] = value
                where.append(f'{field.table.table_name}.{name} {t} ${param}')
            i += 1
        q = self.q
        if q == '*':
            # sql_fields.append(f'{self.table.table_name}.*')
            sql_fields.extend([f'{self.table.table_name}.{i}' for i in vars(self.table) if isinstance(getattr(self.table, i), Field)])
            q = ', '.join(sql_fields)
        if self.table.join_:
            sql = f'''SELECT {q} from 
(SELECT *
FROM {self.table.table_name}
{'WHERE ' + ' AND '.join(where) if where else ''}
LIMIT {self.table.limit}) {self.table.table_name}'''
        else:
            sql = f'SELECT {q} from {self.table.table_name}'
        if self.view:
            sql += f' view {self.view} '
            self.view = ''
            self.table.view = ''
        if declare:
            sql = '\n'.join(declare) + '\n' + sql
        if sql_join:
            sql += '\n' + '\n'.join(sql_join)
        if where and not self.table.join_:
            sql = sql + '\nWHERE ' + ' AND '.join(where)
        # print(sql)
        if self.table.order:
            sql += f' ORDER BY {self.table.order}'
            self.table.order = ''

        if not self.table.join_:
            sql += f' LIMIT {self.table.limit}'
        self.table.limit = 1000
        self.table.select_fields = '*'
        if self.table.is_scan:
            result = []

            items = self.database.scan_query(sql, params, parameters_types=parameters_types)

            for item in items:
                # print(dir(item.result_set.rows))
                for i in item.result_set.rows:
                    result.append(i)
            self.table.is_scan = False
        else:
            result = self.database.query(sql, params)
        if self.join_many:
            pkeys = [f'{self.table.table_name}.{i}' for i in vars(self.table) if isinstance(getattr(self.table, i), Field) and getattr(self.table, i).pk]

            new_result = {}
            for i in result:
                # print(i['products.id'])
                pk = ''.join([i.get(ii) if i.get(ii) else i.get(ii.split('.')[-1]) for ii in pkeys])
                if pk not in new_result:
                    new_result[pk] = {}
                    for param in i:
                        param1 = param.split('.')
                        if len(param1) <= 1 or param1[0] == self.table.table_name:
                            new_result[pk][param] = i[param]
                for join in self.join_many:
                    lst = new_result[pk].get(join, [])
                    subitem = {param: i[param] for param in i if param.startswith(f"{join}.")}
                    if any([subitem[q] for q in subitem]):
                        # lst.append(subitem)
                        lst.append({param: i[param] for param in i})
                    new_result[pk][join] = lst
            result = [new_result[i] for i in new_result]
            self.join_many = []
            self.table.join_ = None
        return result

    def __iter__(self):
        return iter(self._fetch(lazy=True))

    def __getitem__(self, key):
        if not isinstance(key, slice):
            raise (TypeError, 'If you want apply index to a query, convert it to list first')

        step = key.step
        if step is not None and step != 1:
            raise(TypeError, "Parameter 'step' of slice object is not allowed here")
        start = key.start
        if start is None:
            start = 0
        elif start < 0:
            raise (TypeError, "Parameter 'start' of slice object cannot be negative")
        stop = key.stop
        if stop is None:
            if not start:
                return self._fetch()
            else:
                return self._fetch(limit=None, offset=start)
        if start >= stop:
            return self._fetch(limit=0)
        return self._fetch(limit=stop-start, offset=start)

    @classmethod
    def save_item(cls, item, copy=False):
        if not item.need_update and not copy:
            return False
        declare = []
        params = {}
        added = []
        for field in item.params:
            field = item.params[field]
            if field.need_update or copy:
                field.changed = False
                added.append(field.name)
                params[f'${field.name}'] = field.to_save
                # print(field.title)
                if field.pk and field.optional:
                    declare.append(f"DECLARE ${field.name} AS {field.title};")
                else:
                    declare.append(f"DECLARE ${field.name} AS Optional<{field.title}>;")

        sql = f'''UPSERT INTO {item.table_name}
        ({', '.join([f'`{field}`' for field in added])})
        VALUES ({', '.join([f'${field}' for field in added])})'''
        if declare:
            sql = '\n'.join(declare) + '\n' + sql
        item._database_.query(sql, params)
        return True


class QueryResult:
    def __init__(self, query, limit, offset, lazy):
        self._query = query
        self._limit = limit
        self._offset = offset
        self._items = None if lazy else self._query._actual_fetch(limit, offset)

    def __len__(self):
        if self._items is None:
            self._items = self._query._actual_fetch(self._limit, self._offset)
        return len(self._items)

    def __getitem__(self, item):
        return self._items[item]