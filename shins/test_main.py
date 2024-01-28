import pymysql
from contextlib import closing

# 数据库配置
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'oneapi',
    'password': '123456',
    'db': 'one-api',
    'charset': 'utf8mb4'
}

# 连接数据库
try:
    with closing(pymysql.connect(**db_config)) as connection:
        with connection.cursor() as cursor:
            # 获取所有表的名称
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            for (table_name,) in tables:
                # 获取每个表的结构
                cursor.execute(f"SHOW CREATE TABLE {table_name}")
                create_table_sql = cursor.fetchone()[1]
                
                # 将表结构写入文件
                with open(f"{table_name}_structure.sql", "w") as f:
                    f.write(create_table_sql)

    print("所有表结构已成功导出！")
except pymysql.MySQLError as e:
    print(f"数据库错误：{e}")
