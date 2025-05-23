from database.db_utils import DatabaseUtils
from typing import List, Dict

class KnowledgeService:
    def __init__(self):
        self.db_utils = DatabaseUtils()
    
    def search(self, query: str) -> List[Dict]:
        """搜索知识库"""
        try:
            results = self.db_utils.search_knowledge(query)
            return results
        except Exception as e:
            print(f"知识库搜索失败: {e}")
            return []
    
    def add_knowledge(self, title: str, content: str, source: str = "用户添加") -> bool:
        """添加知识"""
        try:
            query = """
            INSERT INTO knowledge_base (title, content, source)
            VALUES (?, ?, ?)
            """
            self.db_utils.execute_update(query, (title, content, source))
            return True
        except Exception as e:
            print(f"添加知识失败: {e}")
            return False
    
    def get_all_knowledge(self) -> List[Dict]:
        """获取所有知识"""
        try:
            query = "SELECT * FROM knowledge_base ORDER BY created_at DESC"
            return self.db_utils.execute_query(query)
        except Exception as e:
            print(f"获取知识库失败: {e}")
            return []