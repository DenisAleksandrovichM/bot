from aiogram.utils.markdown import hbold, hunderline, hlink


def order_message(value):
    return f'У Вас новый заказ! \n' \
           f'Номер заказа: {hbold(value["orderId"])} \n' \
           f'Дата заказа: {hunderline(value["date"])} \n' \
           f'Артикул: {hlink(str(value["nmId"]), value["url"])} \n' \
           f'Размер: {value["techSize"]} \n' \
           f'Брэнд: {value["brand"]} \n' \
           f'Категория: {value["category"]}/{value["subject"]} \n' \
           f'{value["warehouseName"]} -> {value["oblast"]} \n' \
           f'Скидка: {value["discountPercent"]}% \n' \
           f'Итоговая цена: {value["totalPrice"]} руб. \n\n' \
           f'Сегодня таких {value["countOrderToday"]} на сумму {value["sumPriceToday"]} руб. \n' \
           f'Вчера таких {value["countOrderYesterday"]} на сумму {value["sumPriceYesterday"]} руб.'


def sale_message(value):
    return f'У Вас новая продажа! \n' \
           f'Номер продажи: {hbold(value["orderId"])} \n' \
           f'Дата продажи: {hunderline(value["date"])} \n' \
           f'Артикул: {hlink(str(value["nmId"]), value["url"])} \n' \
           f'Размер: {value["techSize"]} \n' \
           f'Брэнд: {value["brand"]} \n' \
           f'Категория: {value["category"]}/{value["subject"]} \n' \
           f'{value["warehouseName"]} -> {value["oblast"]} \n' \
           f'Скидка: {value["discountPercent"]}% \n' \
           f'Итоговая цена: {value["totalPrice"]} руб. \n\n' \
           f'Сегодня таких {value["countOrderToday"]} на сумму {value["sumPriceToday"]} руб. \n' \
           f'Вчера таких {value["countOrderYesterday"]} на сумму {value["sumPriceYesterday"]} руб.'


def return_message(value):
    return f'У Вас возврат! \n' \
           f'Номер возврата: {hbold(value["orderId"])} \n' \
           f'Дата возврата: {hunderline(value["date"])} \n' \
           f'Артикул: {hlink(str(value["nmId"]), value["url"])} \n' \
           f'Размер: {value["techSize"]} \n' \
           f'Брэнд: {value["brand"]} \n' \
           f'Категория: {value["category"]}/{value["subject"]} \n' \
           f'{value["warehouseName"]} -> {value["oblast"]} \n' \
           f'Сумма возврата: -{value["totalPrice"]} руб. \n\n' \
           f'Сегодня таких {value["countOrderToday"]} на сумму {value["sumPriceToday"]} руб. \n' \
           f'Вчера таких {value["countOrderYesterday"]} на сумму {value["sumPriceYesterday"]} руб.'


def get_message_function(mode):
    messages_func = {
        'O': order_message,
        'S': sale_message,
        'R': return_message
    }

    return messages_func.get(mode)
