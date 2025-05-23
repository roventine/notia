import sqlite3
from datetime import datetime, timedelta
import os

def create_database():
    """创建数据库和表"""
    db_path = "notia.db"
    
    # 如果数据库文件已存在，删除它以重新创建
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建邮件表
    cursor.execute('''
    CREATE TABLE emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id VARCHAR(255) UNIQUE NOT NULL,
        title VARCHAR(500) NOT NULL,
        sender VARCHAR(255) NOT NULL,
        received_time DATETIME NOT NULL,
        content TEXT,
        category VARCHAR(50) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建任务表
    cursor.execute('''
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id VARCHAR(255) NOT NULL,
        title VARCHAR(500) NOT NULL,
        sender VARCHAR(255) NOT NULL,
        received_time DATETIME NOT NULL,
        feedback_time DATETIME,
        content TEXT,
        feedback_content TEXT,
        status VARCHAR(50) DEFAULT '未开始',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建知识库表
    cursor.execute('''
    CREATE TABLE knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(500) NOT NULL,
        content TEXT NOT NULL,
        source VARCHAR(255),
        embedding BLOB,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建用户配置表
    cursor.execute('''
    CREATE TABLE user_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_key VARCHAR(100) UNIQUE NOT NULL,
        config_value TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX idx_emails_category ON emails(category)')
    cursor.execute('CREATE INDEX idx_emails_sender ON emails(sender)')
    cursor.execute('CREATE INDEX idx_emails_received_time ON emails(received_time)')
    cursor.execute('CREATE INDEX idx_tasks_status ON tasks(status)')
    cursor.execute('CREATE INDEX idx_tasks_feedback_time ON tasks(feedback_time)')
    
    conn.commit()
    conn.close()
    print("数据库创建成功！")

def insert_test_data():
    """插入测试数据"""
    conn = sqlite3.connect("notia.db")
    cursor = conn.cursor()
    
    # 插入测试邮件数据
    test_emails = [
        {
            'email_id': 'email_001',
            'title': '【重要】项目进度汇报 - 需要本周五前反馈',
            'sender': 'manager@company.com',
            'received_time': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'content': '请各位项目成员在本周五下午5点前提交项目进度汇报，包括已完成工作、遇到的问题和下周计划。',
            'category': '任务类'
        },
        {
            'email_id': 'email_002',
            'title': '技术分享会邀请 - AI在企业中的应用',
            'sender': 'hr@company.com',
            'received_time': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'content': '我们将在下周三举办技术分享会，主题是"AI在企业中的应用"，欢迎大家参加。',
            'category': '资讯类'
        },
        {
            'email_id': 'email_003',
            'title': '客户需求确认 - 紧急',
            'sender': 'client@customer.com',
            'received_time': (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
            'content': '关于我们讨论的新功能需求，请在明天上午10点前确认技术方案的可行性。',
            'category': '任务类'
        },
        {
            'email_id': 'email_004',
            'title': '每周技术资讯 - 第45期',
            'sender': 'newsletter@techblog.com',
            'received_time': (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S'),
            'content': '本期内容包括：最新的AI模型发布、云计算趋势分析、开源项目推荐等。',
            'category': '资讯类'
        },
        {
            'email_id': 'email_005',
            'title': '会议室预订确认',
            'sender': 'admin@company.com',
            'received_time': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'content': '您预订的会议室A101已确认，时间：明天下午2-4点，请准时参加。',
            'category': '任务类'
        }
    ]
    
    for email in test_emails:
        cursor.execute('''
        INSERT INTO emails (email_id, title, sender, received_time, content, category)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (email['email_id'], email['title'], email['sender'], 
              email['received_time'], email['content'], email['category']))
    
    # 插入测试任务数据
    test_tasks = [
        {
            'email_id': 'email_001',
            'title': '项目进度汇报',
            'sender': 'manager@company.com',
            'received_time': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'feedback_time': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d 17:00:00'),
            'content': '请各位项目成员在本周五下午5点前提交项目进度汇报，包括已完成工作、遇到的问题和下周计划。',
            'feedback_content': '需要提交：1. 已完成工作清单 2. 遇到的问题和解决方案 3. 下周工作计划',
            'status': '进行中'
        },
        {
            'email_id': 'email_003',
            'title': '客户需求确认',
            'sender': 'client@customer.com',
            'received_time': (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
            'feedback_time': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d 10:00:00'),
            'content': '关于我们讨论的新功能需求，请在明天上午10点前确认技术方案的可行性。',
            'feedback_content': '需要确认技术方案的可行性，包括技术难度、开发周期和资源需求',
            'status': '未开始'
        },
        {
            'email_id': 'email_005',
            'title': '会议室预订确认',
            'sender': 'admin@company.com',
            'received_time': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'feedback_time': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d 14:00:00'),
            'content': '您预订的会议室A101已确认，时间：明天下午2-4点，请准时参加。',
            'feedback_content': '参加会议室A101的会议',
            'status': '未开始'
        }
    ]
    
    for task in test_tasks:
        cursor.execute('''
        INSERT INTO tasks (email_id, title, sender, received_time, feedback_time, 
                          content, feedback_content, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task['email_id'], task['title'], task['sender'], task['received_time'],
              task['feedback_time'], task['content'], task['feedback_content'], task['status']))
    
    # 插入测试知识库数据
    test_knowledge = [
        {
            'title': 'Python FastAPI 开发指南',
            'content': 'FastAPI是一个现代、快速的Web框架，用于构建API。它基于标准Python类型提示，具有自动API文档生成、数据验证等特性。',
            'source': '技术文档'
        },
        {
            'title': 'React TypeScript 最佳实践',
            'content': 'React与TypeScript结合使用可以提供更好的类型安全和开发体验。建议使用函数组件、Hooks和严格的类型定义。',
            'source': '开发规范'
        },
        {
            'title': '邮件处理自动化方案',
            'content': '使用IMAP协议可以实现邮件的自动读取和处理。结合AI模型可以实现邮件分类、任务提取等功能。',
            'source': '项目文档'
        }
    ]
    
    for knowledge in test_knowledge:
        cursor.execute('''
        INSERT INTO knowledge_base (title, content, source)
        VALUES (?, ?, ?)
        ''', (knowledge['title'], knowledge['content'], knowledge['source']))
    
    # 插入用户配置数据
    test_configs = [
        ('email_server', 'imap.gmail.com'),
        ('email_port', '993'),
        ('model_path', r'C:\Users\zangq\Repo\model\OpenVINO\Qwen3-1.7B-int4-ov'),
        ('auto_process_interval', '300'),  # 5分钟
        ('max_emails_per_batch', '10')
    ]
    
    for config_key, config_value in test_configs:
        cursor.execute('''
        INSERT INTO user_config (config_key, config_value)
        VALUES (?, ?)
        ''', (config_key, config_value))
    
    conn.commit()
    conn.close()
    print("测试数据插入成功！")

def main():
    """主函数"""
    print("开始初始化数据库...")
    create_database()
    insert_test_data()
    print("数据库初始化完成！")
    
    # 验证数据
    conn = sqlite3.connect("notia.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM emails")
    email_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
    knowledge_count = cursor.fetchone()[0]
    
    print(f"数据验证：邮件 {email_count} 条，任务 {task_count} 条，知识库 {knowledge_count} 条")
    
    conn.close()

if __name__ == "__main__":
    main()