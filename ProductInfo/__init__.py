def get_sync_handler():
    from .DebeziumSync.debezium_syncing import SyncDataFromDebezium
    return SyncDataFromDebezium