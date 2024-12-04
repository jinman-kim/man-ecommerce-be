### based on asyncpg RAW Query
import asyncio
import asyncpg
from fastapi import FastAPI
import logging

logger = logging.getLogger('db')


DATABASE_URL = "postgresql://ecommerce_user:ecommerce_pass@localhost:5434/ecommerce_db"

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)
        logger.info('DB 커넥션 성공')
        

    async def disconnect(self):
        await self.pool.close()

database = Database()
