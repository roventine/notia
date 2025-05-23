import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

class DatabaseUtils:
    def __init__(self, db_path: str = "notia.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """执行查询并返回结果"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """执行更新操作并返回影响的行数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def get_emails_by_category(self, category: str) -> List[Dict]:
        """根据分类获取邮件"""
        query = """
        SELECT * FROM emails 
        WHERE category = ? 
        ORDER BY received_time DESC
        """
        return self.execute_query(query, (category,))
    
    def get_pending_tasks(self) -> List[Dict]:
        """获取待处理任务"""
        query = """
        SELECT * FROM tasks 
        WHERE status IN ('未开始', '进行中')
        ORDER BY feedback_time ASC
        """
        return self.execute_query(query)
    
    def get_overdue_tasks(self) -> List[Dict]:
        """获取过期任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
        SELECT * FROM tasks 
        WHERE feedback_time < ? AND status != '已完成'
        ORDER BY feedback_time ASC
        """
        return self.execute_query(query, (current_time,))
    
    def search_knowledge(self, keyword: str) -> List[Dict]:
        """搜索知识库"""
        query = """
        SELECT * FROM knowledge_base 
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY created_at DESC
        """
        search_term = f"%{keyword}%"
        return self.execute_query(query, (search_term, search_term))
    
    def get_email_statistics(self) -> Dict:
        """获取邮件统计信息"""
        stats = {}
        
        # 总邮件数
        result = self.execute_query("SELECT COUNT(*) as count FROM emails")
        stats['total_emails'] = result[0]['count']
        
        # 按分类统计
        result = self.execute_query("""
        SELECT category, COUNT(*) as count 
        FROM emails 
        GROUP BY category
        """)
        stats['by_category'] = {row['category']: row['count'] for row in result}
        
        # 任务统计
        result = self.execute_query("""
        SELECT status, COUNT(*) as count 
        FROM tasks 
        GROUP BY status
        """)
        stats['task_status'] = {row['status']: row['count'] for row in result}
        
        return stats

# 使用示例
if __name__ == "__main__":
    db_utils = DatabaseUtils()
    
    # 获取统计信息
    stats = db_utils.get_email_statistics()
    print("邮件统计:", stats)
    
    # 获取待处理任务
    pending_tasks = db_utils.get_pending_tasks()
    print(f"待处理任务数量: {len(pending_tasks)}")
    
    # 搜索知识库
    knowledge_results = db_utils.search_knowledge("FastAPI")
    print(f"知识库搜索结果: {len(knowledge_results)}")