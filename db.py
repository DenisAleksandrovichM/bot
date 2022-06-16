import sqlite3

connect = sqlite3.connect('users.db')
cursor = connect.cursor()


def insert(table: str, column_values: (dict, list)):
    if isinstance(column_values, dict):
        column_values_keys = column_values.keys()
        columns = ', '.join(column_values_keys)
        values = [tuple(column_values.values())]
    elif isinstance(column_values, list):
        column_values_keys = column_values[0].keys()
        columns = ', '.join(column_values_keys)
        values = [tuple(item.values()) for item in column_values]
    else:
        return

    data = fetchall(table, tuple(column_values_keys))
    if column_values in data:
        return
    placeholders = ', '.join('?' * len(column_values_keys))
    print(values)
    cursor.executemany(
        f'INSERT INTO {table} '
        f'({columns}) '
        f'VALUES ({placeholders})',
        values)
    connect.commit()


def fetchall_result(rows: list, columns):
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def fetchall(table, columns, condition='True'):
    columns_joined = ', '.join(columns)
    cursor.execute(
        f'SELECT {columns_joined} '
        f'FROM {table} '
        f'WHERE {condition}')
    rows = cursor.fetchall()
    return fetchall_result(rows, columns)


def totals_orders_by_day(table, user_id, today, yesterday, nomenclatures):
    text = (
        'SELECT '
        f'nmId as nmId, '
        f'sum(ifnull(totalPrice, 0)) as sumPrice, '
        f'count(ifnull(orderId, 0)) as countOrder, '
        f'CASE WHEN unixTime >= {today} THEN 1 ELSE 0 END as todaysOrder '
        f'FROM {table} '
        f'WHERE userId = {user_id} AND nmId IN ({", ".join(nomenclatures)}) AND unixTime >= {yesterday} '
        f'GROUP BY nmId, todaysOrder')
    print(text)
    cursor.execute(text)
    rows = cursor.fetchall()
    result = {}
    for row in rows:
        dict_row = result.get(row[0], {})
        postfix = 'Today' if row[3] else 'Yesterday'
        dict_row[f'sumPrice{postfix}'], dict_row[f'countOrder{postfix}'] = row[1], row[2]
        result[row[0]] = dict_row
        print(dict_row)
    return result


def get_cursor():
    return cursor


def check_db_exists():
    cursor.execute(
        ''' CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY, wb_key TEXT)''')
    for table_name in ('orders', 'sales', 'returns'):
        cursor.execute(
            f'''CREATE TABLE IF NOT EXISTS {table_name} (id TEXT PRIMARY KEY,orderId INTEGER, unixTime REAL, 
            url TEXT, nmId INTEGER, brand TEXT, techSize TEXT, category TEXT, date TEXT, discountPercent INTEGER, 
            oblast TEXT, subject TEXT, supplierArticle TEXT, totalPrice REAL, warehouseName TEXT, userId INTEGER, 
            gNumber INTEGER, FOREIGN KEY (orderId) REFERENCES user(id))'''
        )
    connect.commit()


def drop_table(table):
    cursor.execute(f'DROP TABLE IF EXISTS {table}')


def delete_from_table(table, unixTime):
    cursor.execute(f'DELETE FROM {table} WHERE unixTime >= {unixTime}')


check_db_exists()


if __name__ == '__main__':
    for table_nam in ('orders', 'sales', 'returns'):
        delete_from_table(table_nam, 1654376400)
    pass
