"""
Lightweight encapsulation of pymysql.
对pymysql的轻量级封装
"""
import pymysql
import logging
import traceback
import time


class Connect(object):
    def __init__(self,
                 host,
                 database,
                 user=None,
                 password=None,
                 port=0,
                 max_idle_time=7 * 3600,
                 connect_timeout=10,
                 charset="utf8mb4",
                 sql_mode="TRADITIONAL"
                 ):
        self.host = host
        self.database = database
        self.max_idle_time = float(max_idle_time)
        args = dict(
            use_unicode=True,
            charset=charset,
            database=database,
            connect_timeout=connect_timeout, sql_mode=sql_mode
        )
        if user is not None:
            args["user"] = user
        if password is not None:
            args["password"] = password

        if "/" in host:
            args["unix_socket"] = host
        else:
            self.socket = None
            pair = host.split(":")  # 127.0.0.1:3306
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = 3306

        if port:
            args["port"] = port

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            # 连接数据库
            self.connect()
        except Exception as e:
            # 将异常信息添加到日志消息中
            logging.error(f"Connect connect to MySQL on {self.host}", exc_info=True)

    def close(self):
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def connect(self):
        self.close()
        self._db = pymysql.connect(**self._db_args)
        # MySQLdb.connect方法建立数据库连接之后，会自动发送set autocommit=0，
        # 开启一个事务，如果用户不主动提交，这个事务不会被提交。
        self._db.autocommit(True)

    def _ensure_connected(self):
        """
        mysql默认8小时断开连接，所以需要检查连接是否断开，如果断开则重新连接
        """
        if (self._db is None or
                (time.time() - self._last_use_time > self.max_idle_time)):
            self.connect()
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def __del__(self):
        self.close()

    # ================== 以下是对数据库的基础操作 ================== #
    def query(self, query, *args, **kwargs):
        cursor = self._cursor()
        try:
            cursor.execute(query, kwargs or args)
            return cursor.fetchall()
        finally:
            cursor.close()

    def get(self, query, *args, **kwargs):
        cursor = self._cursor()
        try:
            cursor.execute(query, kwargs or args)
            return cursor.fetchone()
        finally:
            cursor.close()

    def execute(self, query, *args, **kwargs):
        cursor = self._cursor()
        try:
            cursor.execute(query, kwargs or args)
            return cursor.rowcount
        finally:
            cursor.close()

    insert = execute

    # ================== 以下是对数据库的高级操作 ================== #
    def table_has(self, table, field, value):
        if isinstance(value, str):
            value = value.encode('utf-8')

        sql = f"SELECT {field} FROM {table} WHERE {field}={value}"
        return self.get(sql)

    def table_insert(self, table_name, **kwargs):
        fields = kwargs.keys()
        values = map(lambda v: v.encode('utf-8') if isinstance(v, str) else v, kwargs.values())
        fields_str = ','.join(fields)
        val_str = ','.join(['%s'] * len(values))
        sql = "INSERT INTO %s (%s) VALUES(%s)" % (table_name, fields_str, val_str)
        try:
            last_id = self.insert(sql, *values)
            return last_id
        except Exception as e:
            if e.args[0] == 1062:
                # 主键或者唯一键重复
                pass
            else:
                # 查看异常传播轨迹
                traceback.print_exc()
                logging.error(f"table_insert error sql: {sql}")
                for i in range(len(fields)):
                    vs = str(values[i])
                    if len(vs) > 300:
                        print(fields[i], ' : ', len(vs), type(values[i]))
                    else:
                        print(fields[i], ' : ', vs, type(values[i]))
                # 将异常抛出到上一级
                raise e

    def table_update(self, table_name, updates, field_where, value_where):
        upsets, values = [], []
        for k, v in updates.items():
            s = '%s=%%s' % k
            upsets.append(s)
            values.append(v)
        upsets_str = ','.join(upsets)
        sql = "UPDATE %s SET %s WHERE %s=%s" % (table_name, upsets_str, field_where, value_where)
        self.execute(sql, *values)


if __name__ == '__main__':
    c = Connect(host='localhost',
                database='brain',
                user='root',
                password='123456',
                port=3306, )
    c.table_update('pose', {'assessStatus': 123141, "after_url": 123, "csv_url": 1234456}, 'id', 50)
    # db = pymysql.connect(
    #     **{'use_unicode': True, 'charset': 'utf8mb4', 'database': 'brain',
    #        'connect_timeout': 10, 'sql_mode': 'TRADITIONAL', 'user': 'root', 'password': '123456', 'host': 'localhost',
    #        'port': 3306})


    # def get_db():
    #     db = pymysql.connect(host="localhost", user="root", password="123456", database="brain", charset="utf8mb4")
    #     return db
    # db = get_db()
    # cursor = db.cursor()
    # # sql = "update pose set after_url='" + "123" + "'where id = " + str(50)
    # sql1 = "update pose set csv_url='" + "123" + "'where id = " + str(50)
    # sql = 'UPDATE pose SET assessStatus=%s WHERE id=50'
    # a = [1231242]
    # # 修改状态 assessstatus
    # cursor.execute(sql, *a)
    # try:
    #     db.commit()
    # except:
    #     db.rollback()
