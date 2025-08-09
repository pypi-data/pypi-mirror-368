import asyncpg
from .base_sink import BaseIngestSink
import shared.helpers.sql_definitions as sql_definitions
from shared.helpers.ensure_db_schema import async_ensure_schema
from shared.helpers.config_loader import load_config

class AsyncPostgresSink(BaseIngestSink):
    """
    Asynchronous PostgreSQL sink for application logs, metrics, and Robot Framework events.
    All dispatching is expected to be done by the ingest API.
    Each handler function corresponds to a single use case.
    """

    def __init__(self, database_url=None):
        super().__init__()
        config = load_config()
        self.database_url = database_url or config.get("database_url")
        self.logger.debug("Async sink writing to PostgreSQL: %s", self.database_url)
        self.pool = None

    # call from ingest main.py to initialize the database schema
    async def initialize_database(self):
        try:
            await async_ensure_schema(self.database_url)
            # Create connection pool AFTER schema is initialized
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,      # Minimum connections
                max_size=10,     # Maximum connections  
                command_timeout=60
            )
            self.logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            self.logger.warning("[POSTGRES_ASYNC] Failed to initialize DB: %s", e)
            raise
    
    async def _execute_query(self, query: str, values: list, operation: str):
        """Helper method to execute queries using connection pool."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(query, *values)
            self.logger.debug("[POSTGRES_ASYNC] %s completed successfully", operation)
        except Exception as e:
            self.logger.warning("[POSTGRES_ASYNC] Failed to %s: %s", operation.lower(), e)
            raise
    
    async def handle_app_log(self, data):
        """Insert app-level log data into 'app_logs' table."""
        self.logger.debug("[POSTGRES_ASYNC] Inserting app_log: %s", data)
        values = [self.make_sql_safe(data.get(col)) for col, _ in sql_definitions.app_log_columns]
        await self._execute_query(sql_definitions.INSERT_APP_LOG, values, "insert app log")
    
    async def handle_metric(self, data):
        """Insert metric data into 'metrics' table."""
        self.logger.debug("[POSTGRES_ASYNC] Inserting metric: %s", data)
        values = [self.make_sql_safe(data.get(col)) for col, _ in sql_definitions.metric_columns]
        await self._execute_query(sql_definitions.INSERT_METRIC, values, "insert metric")
    
    async def handle_rf_events(self, data):
        """Insert Robot Framework event into 'rf_events' table."""
        self.logger.debug("[POSTGRES_ASYNC] Inserting RF event: %s", data)
        values = [self.make_sql_safe(data.get(col)) for col, _ in sql_definitions.event_columns]
        await self._execute_query(sql_definitions.INSERT_EVENT, values, "insert RF event")
    
    async def handle_rf_log(self, data):
        """Insert Robot Framework log message into 'rf_log_messages' table."""
        self.logger.debug("[POSTGRES_ASYNC] Inserting RF log message: %s", data)
        values = [self.make_sql_safe(data.get(col)) for col, _ in sql_definitions.rf_log_columns]
        await self._execute_query(sql_definitions.INSERT_RF_LOG_MESSAGE, values, "insert RF log message")
    
    async def close(self):
        """Clean shutdown of connection pool."""
        if self.pool:
            await self.pool.close()
            self.logger.info("PostgreSQL connection pool closed")