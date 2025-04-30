import json
import logging
import pprint
import threading
import pika
from .models import SyncedDataFromProduct, Basket

RabbitUser = "user"
RabbitPassword = "password"
logging.basicConfig(level=logging.INFO)


def bulk_create_or_update(data):
    to_create = [SyncedDataFromProduct(
        store_id=item['store_id'],
        product_id=item['product_id'],
        sku=item['sku'],
        price=item['price'],
        discount=item['discount'],
        quantity=item['quantity'],
    ) for item in data]

    SyncedDataFromProduct.objects.bulk_create(
        to_create,
        update_conflicts=True,
        update_fields=['price', 'discount', 'quantity', 'sku']
    )


def inactiveTheBasket(basket_id):

    Basket.objects.filter(id=basket_id).update(is_active=False)


def callback_from_products(ch, method, properties, body):
    data = json.loads(body)
    logging.info("Received product data: %r" % data)
    try:
        bulk_create_or_update(data)
        logging.info('Product data successfully processed')
    except Exception as err:
        logging.error(f"Error processing product message: {err}")
    ch.basic_ack(delivery_tag=method.delivery_tag)



def callback_from_order(ch, method, properties, body):
    data = json.loads(body)
    logging.info("Received order data: %r" % data)
    try:
        pprint.pprint(data)
        
        inactiveTheBasket(data['basket_id'])
        logging.info('Order data successfully processed')
    except Exception as err:
        logging.error(f"Error processing order message: {err}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_from_rabbitmq(queue, callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='rabbit-container',
        credentials=pika.PlainCredentials(RabbitUser, RabbitPassword),
    ))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=callback)
    logging.info(f'Consuming from {queue}')
    channel.start_consuming()


def start_consumer():
    queues = {
        'PriceOrQuantityUpdated': callback_from_products,
        'BasketIsOrdered': callback_from_order
    }

    threads = [
        threading.Thread(target=consume_from_rabbitmq, args=(queue, callback), daemon=True)
        for queue, callback in queues.items()
    ]

    for thread in threads:
        thread.start()

    # Optionally, wait for threads to finish if you need to block the main thread
    # for thread in threads:
    #     thread.join()
