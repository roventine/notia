from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.models import create_tables, get_db, Email, Task, TaskStatus
from services.email_service import EmailService
from services.model_service import ModelService
from services.knowledge_service import KnowledgeService
from typing import List, Dict
import os
from datetime import datetime

# 创建FastAPI应用
app = FastAPI(title="Notia智能邮件助手", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
create_tables()

# 初始化服务
model_service = ModelService()
knowledge_service = KnowledgeService()

# 邮件服务配置（需要用户配置）
EMAIL_CONFIG = {
    "imap_server": "imap.yeah.net",  # 示例配置
    "email_addr": "",  # 需要用户配置
    "password": ""     # 需要用户配置
}

@app.get("/")
async def root():
    return {"message": "Notia智能邮件助手API"}

@app.get("/api/emails")
async def get_emails(db: Session = Depends(get_db)):
    """获取邮件列表"""
    emails = db.query(Email).order_by(Email.received_time.desc()).limit(50).all()
    return emails

@app.get("/api/tasks")
async def get_tasks(db: Session = Depends(get_db)):
    """获取任务列表"""
    tasks = db.query(Task).order_by(Task.received_time.desc()).all()
    return tasks

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int, status: str, db: Session = Depends(get_db)):
    """更新任务状态"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task.status = TaskStatus(status)
    task.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "任务状态更新成功"}

@app.post("/api/chat")
async def chat(message: dict):
    """聊天接口"""
    user_message = message.get("message", "")
    
    # 使用模型生成响应
    response = model_service.generate_response(user_message)
    
    return {"response": response}

@app.get("/api/search")
async def search_knowledge(query: str):
    """知识库搜索"""
    results = knowledge_service.search(query)
    return {"results": results}

@app.post("/api/process-emails")
async def process_emails():
    """手动处理邮件"""
    if not EMAIL_CONFIG["email_addr"] or not EMAIL_CONFIG["password"]:
        raise HTTPException(status_code=400, detail="邮件配置未完成")
    
    email_service = EmailService(
        EMAIL_CONFIG["imap_server"],
        EMAIL_CONFIG["email_addr"],
        EMAIL_CONFIG["password"]
    )
    
    processed_emails = email_service.process_new_emails()
    return {"processed_count": len(processed_emails), "emails": processed_emails}

@app.get("/api/statistics")
async def get_statistics():
    """获取统计信息"""
    from database.db_utils import DatabaseUtils
    db_utils = DatabaseUtils()
    stats = db_utils.get_email_statistics()
    return stats

@app.post("/api/knowledge")
async def add_knowledge(knowledge_data: dict):
    """添加知识"""
    title = knowledge_data.get("title", "")
    content = knowledge_data.get("content", "")
    source = knowledge_data.get("source", "用户添加")
    
    success = knowledge_service.add_knowledge(title, content, source)
    if success:
        return {"message": "知识添加成功"}
    else:
        raise HTTPException(status_code=500, detail="知识添加失败")

@app.get("/api/knowledge")
async def get_knowledge():
    """获取知识库"""
    knowledge_list = knowledge_service.get_all_knowledge()
    return knowledge_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)