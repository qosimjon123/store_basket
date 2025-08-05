import asyncio
import json
from rstream import Consumer, ConsumerOffsetSpecification, OffsetType, OffsetNotFound
import threading
import pprint
from . import get_sync_handler
from channels.db import aclose_old_connections

class ConsumerPool:
    def __init__(self):
        self.consumers = []
        self.sync_handler = get_sync_handler()()
        self.message_counter = 0
        self.CLOSE_CONNECTION_INTERVAL = 100  # Закрывать соединения каждые 100 сообщений

    def add_consumer(self, config):
        consumer = Consumer(host="rabbit-container", port=5552, username="user", password="password")
        self.consumers.append((consumer, config))


    async def start(self):
        tasks = []
        for consumer, config in self.consumers:
            task = asyncio.create_task(self.run_consumer(consumer, config))
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def run_consumer(self, consumer, config):
        stream_name = config["name"]
        subscriber_name = config["subscriber"]
        
        try:
            # Создать стрим с правильными параметрами
            stream_arguments = {
                "x-queue-leader-locator": "least-leaders",
                "x-queue-type": "stream",
                "x-max-length-bytes": 1000000000,
                "x-stream-max-segment-size-bytes": 100000000
            }
            await consumer.create_stream(stream_name, arguments=stream_arguments, exists_ok=True)
        except Exception as e:
            print(f"Stream {stream_name} already exists or error: {e}")
            # Продолжаем работу даже если поток уже существует
        

        # Запросить последний сохранённый оффсет
        try:
            stored_offset = await consumer.query_offset(stream=stream_name, subscriber_name=subscriber_name)
            start_offset = stored_offset + 1  # Начать с следующего сообщения
            offset_spec = ConsumerOffsetSpecification(OffsetType.OFFSET, start_offset)
            print(f"Starting from offset: {start_offset}")
        except OffsetNotFound:
            offset_spec = ConsumerOffsetSpecification(OffsetType.FIRST)  # Начать с начала, если оффсет не найден
            print(f"Starting from beginning of stream")
        
        # Определить обработчик сообщений
        async def on_message(msg, message_context):
            try:
                self.message_counter += 1
                if self.message_counter % self.CLOSE_CONNECTION_INTERVAL == 0:
                    self.message_counter = 0
                    await aclose_old_connections()
                # Найти первую и последнюю фигурную скобку
                json_start = msg.find(b'{')
                json_end = msg.rfind(b'}')
                if json_start == -1 or json_end == -1:
                    print("JSON braces not found in messagek")
                    return 
                json_bytes = msg[json_start:json_end+1]
                json_msg = json.loads(json_bytes)
                print(f"Received JSON message: {json_msg} from stream {stream_name}")

                success = await self.sync_handler.sync_data(json_msg)
 
                # Сохранить offset только после успешной обработки
                if success and message_context.offset:
                    try:
                        print(f"Storing offset: {message_context.offset} for stream {stream_name}")
                        print(f"Synced data from stream {stream_name}")

                        await consumer.store_offset(
                            stream=stream_name,
                            offset=message_context.offset,
                            subscriber_name=subscriber_name
                        )
                    except Exception as e:
                        print(f"Error storing offset: {e}")
                        print(f"Failed to sync data from stream {stream_name}")


            except Exception as e:
                print(f"Error processing message: {e}, raw message: {msg}")
                # Offset НЕ сохраняется при ошибке обработки
        
        try:

            # Запустить потребителя
            await consumer.start()
            await consumer.subscribe(
                stream=stream_name,
                subscriber_name=subscriber_name,
                callback=on_message,
                offset_specification=offset_spec
            )
            print(f"Successfully subscribed to stream: {stream_name}")
            await consumer.run()
        except Exception as e:
            print(f"Error in consumer {stream_name}: {e}")

# Функция для запуска пула потребителей
def start_consumer_pool():	
    streams_config = [
        {"name": "main_stream", "subscriber": "warehouse_main_sub1"},
        {"name": "inventory_stream", "subscriber": "warehouse_inventory_sub2"},

        # Добавьте больше конфигураций до MAX_WORKERS
    ]
    pool = ConsumerPool()
    for config in streams_config:
        pool.add_consumer(config)
    
    # Запуск в фоновом потоке
    thread = threading.Thread(target=lambda: asyncio.run(pool.start()), daemon=True)
    thread.start()

