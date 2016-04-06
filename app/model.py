import pymysql.cursors
import app_config


def update(temp_datetime):
    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 user=app_config.db_un,
                                 password=app_config.db_pwd,
                                 db='umls',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = """multiline SQL here with %s"""
            cursor.execute(sql, ('variables'))

    finally:
        connection.commit()
        connection.close()
