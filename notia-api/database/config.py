import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库配置
DATABASE_URL = "sqlite:///./notia.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # 设置为True可以看到SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 依赖注入函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 数据库初始化函数
def init_database():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)