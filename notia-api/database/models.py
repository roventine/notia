from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import enum
from datetime import datetime

Base = declarative_base()

class EmailCategory(enum.Enum):
    NEWS = "资讯类"
    TASK = "任务类"
    UNCLASSIFIED = "无法分类"

class TaskStatus(enum.Enum):
    NOT_STARTED = "未开始"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    sender = Column(String, index=True)
    received_time = Column(DateTime, default=datetime.utcnow)
    content = Column(Text)
    category = Column(Enum(EmailCategory))
    created_at = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, index=True)
    title = Column(String, index=True)
    sender = Column(String)
    received_time = Column(DateTime)
    feedback_time = Column(DateTime, nullable=True)
    content = Column(Text)
    feedback_content = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.NOT_STARTED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 数据库连接
DATABASE_URL = "sqlite:///./notia.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()