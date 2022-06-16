import requests

from datetime import datetime, timedelta
from db import fetchall, insert, totals_orders_by_day


def get_response(key: str, operation: str = 'orders'):
    date = __date_offset_in_days(1)
    date_form = f'{date.date()}T{max(date.hour, 0)}%3A{date.minute}%3A{date.second}.{date.microsecond}Z'
    url = f'https://suppliers-stats.wildberries.ru/api/v1/supplier/{operation}?dateFrom={date_form}&flag=0&key={key}'
    print(f'{url=}')
    return requests.get(url)


def check_order_update(user_data, isOrders: bool):
    response = get_response(user_data['wb_key'], 'orders' if isOrders else 'sales')
    print(f'{response=}')
    if response.status_code == 200:
        response_json = response.json()
        if isOrders:
            print(f'{response_json[0]=}')

            print(f'{list(filter(lambda order: not order["isCancel"], response_json))[0]=}')
            return __process_response(
                user_data['id'],
                'orders',
                [order for order in response_json if not not order['isCancel']]
                )
        else:
            fresh_sales, fresh_returns = [], []
            print(response_json)
            for item in response_json:
                print(f'{item["saleID"][0]=}')
                if item['saleID'][0] == 'S':
                    fresh_sales.append(item)
                elif item['saleID'][0] == 'R':
                    fresh_returns.append(item)
            return (__process_response(user_data['id'], 'sales', fresh_sales),
                    __process_response(user_data['id'], 'returns', fresh_returns))


def __date_offset_in_days(days: int):
    date = datetime.today() - timedelta(days=days)
    return date.combine(date.date(), date.min.time())


def __process_sum(s: (float, int)):
    if isinstance(s, int):
        return s
    return int(s) if s.is_integer() else round(s, 2)


def __process_response(user_id: int, file_name: str, response_list: list):
    fresh_orders = __get_fresh_orders(file_name, response_list, user_id)
    print(f'{fresh_orders=}')
    if len(fresh_orders):
        insert(file_name, fresh_orders)
        totals_orders = totals_orders_by_day(
            file_name,
            user_id,
            __date_offset_in_days(0).timestamp(),
            __date_offset_in_days(1).timestamp(),
            set(str(item['nmId']) for item in fresh_orders)
        )

        for order in fresh_orders:
            total_order = totals_orders.get(order['nmId'], {})
            order['sumPriceToday'] = __process_sum(total_order.get('sumPriceToday', 0))
            order['sumPriceYesterday'] = __process_sum(total_order.get('sumPriceYesterday', 0))
            order['countOrderToday'] = total_order.get('countOrderToday', 0)
            order['countOrderYesterday'] = total_order.get('countOrderYesterday', 0)

    return fresh_orders


def __get_fresh_orders(file_name: str, response_list: list, user_id: int):
    fresh_orders = []
    old_orders = fetchall(
        file_name,
        ('id', 'userId', 'gNumber', 'unixTime', 'orderId', 'url', 'nmId', 'brand', 'techSize', 'category',
         'date', 'discountPercent', 'oblast', 'subject', 'supplierArticle', 'totalPrice', 'warehouseName'
         )
    )
    old_orders_id = [item['id'] for item in old_orders]
    print(f'{type(old_orders_id[0])}')
    for order in response_list:
        if f'{order["gNumber"]}{order["odid"]}' not in old_orders_id:
            convert_order = __get_dict_order(
                order, file_name == 'orders', user_id)
            fresh_orders.append(convert_order)
    if len(fresh_orders):
        fresh_orders.sort(key=lambda item: item['unixTime'])

    print(f'{fresh_orders=}')
    return fresh_orders


def __get_dict_order(order: dict, is_order: bool, user_id: int):
    return {
        'userId': user_id,
        'id': f'{order["gNumber"]}{order["odid"]}',
        'unixTime': float(f"{datetime.fromisoformat(order['date']).timestamp()}"),
        'orderId': order['odid'],
        'url': f'https://www.wildberries.ru/catalog/{order["nmId"]}/detail.aspx',
        'nmId': order["nmId"],
        'brand': order['brand'],
        'techSize': order['techSize'],
        'category': order['category'],
        'date': f"{datetime.fromisoformat(order['date']).strftime('%d-%m-%Y %H:%M:%S')}",
        'discountPercent': order['discountPercent'],
        'oblast': order['oblast'] if is_order else order['regionName'],
        'subject': order['subject'],
        'supplierArticle': order['supplierArticle'],
        'totalPrice': __process_sum((order['totalPrice'] * (100 - order['discountPercent']) / 100 if is_order
                                     else order['priceWithDisc'])),
        'warehouseName': order['warehouseName']
    }
