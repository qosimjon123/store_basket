import base64
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from .mapping import TABLE_MODEL_MAPPING, BASE64_FIELDS, TIME_FIELDS, FIELD_MAPPING, IGNORE_FIELDS
from channels.db import database_sync_to_async

class SyncDataFromDebezium:


    def _decode_base64_fields(self, table_name, data):
        if table_name in BASE64_FIELDS:
            for field in BASE64_FIELDS[table_name]:
                if field in data and data[field]:
                    try:
                        bytes_data = base64.b64decode(data[field])
                        int_value = int.from_bytes(bytes_data, byteorder='big')
                        data[field] = int_value / 100
                    except (ValueError, UnicodeDecodeError) as e:
                        print(f"Ошибка декодирования Base64 для поля {field}: {e}")
        return data


    def _convert_time_fields(self, table_name, data):
        if table_name in TIME_FIELDS:
            for field in TIME_FIELDS[table_name]:
                if field in data and data[field]:
                    try:
                        seconds = data[field] / 1_000_000
                        hours = int(seconds // 3600)
                        minutes = int((seconds % 3600) // 60)
                        seconds = int(seconds % 60)
                        data[field] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    except ValueError as e:
                        print(f"Ошибка преобразования времени для поля {field}: {e}")
        return data

    def _prepare_data(self, table_name, data):
        data = self._decode_base64_fields(table_name, data.copy())
        data = self._convert_time_fields(table_name, data)
        return data

    @database_sync_to_async
    def sync_data(self, message):
        table_name = message.get('source', {}).get('table')
        operation = message.get('op')
        model_class = TABLE_MODEL_MAPPING.get(table_name)
        
        if not model_class:
            print(f"Неизвестная таблица: {table_name}")
            return
        
        payload = create_payload(message)
        if not payload:
            print(f"Нет данных для операции {operation} в таблице {table_name}")
            return False
        
        payload = self._prepare_data(table_name, payload)
        
        try:
            if operation in ['c', 'r']:
                
                instance, created = model_class.objects.update_or_create(
                    id=payload.get('id'),
                    defaults=payload
                )
                print(f"{'Создана' if created else 'Обновлена'} запись в {table_name}: {payload}")
            
            elif operation == 'u':
                instance, created = model_class.objects.update_or_create(
                    id=payload.get('id'),
                    defaults=payload
                )
                if created:
                    print(f"Создана запись в {table_name}: {payload} по причине того, что не было найдено")
                else:
                    print(f"Обновлена запись в {table_name}: {payload}")
            
            elif operation == 'd':
                obj = model_class.objects.filter(id=payload.get('id')).first()
                if obj:
                    obj.delete()
                    print(f"Удалена запись в {obj.id}: {payload}")
                else:
                    print(f"Запись для удаления не найдена в {table_name}: {payload}")
            
            else:
                print(f"Неизвестная операция: {operation} для таблицы {table_name}")
                return False
            return True
        except Exception as e:
            print(f"Ошибка обработки данных для таблицы {table_name}: {e}")
            return False

def create_payload(message):
    table_name = message.get('source', {}).get('table')
    operation = message.get('op')
    data = message.get('after', {}) if operation in ['c', 'u', 'r'] else message.get('before', {})
    
    if not data:
        return None
    
    mapping = FIELD_MAPPING.get(table_name, {})
    payload = {}
    for key, value in data.items():
        if key in IGNORE_FIELDS:
            continue
        model_key = mapping.get(key, key)
        payload[model_key] = value
    
    return payload