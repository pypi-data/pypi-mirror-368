"""
# File       : get_db.py
# Time       ：2024/10/7 05:24
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from svc_order_zxw.config import DATABASE_URL

#
Base = declarative_base()

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# 创建同步引擎，用于表结构的创建
sync_engine = create_engine(DATABASE_URL)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def get_db_sync():
    db = sync_engine.connect()
    try:
        yield db
    finally:
        db.close()


# 初始化数据库
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
