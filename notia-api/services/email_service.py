import imaplib
import email
from email.header import decode_header
import json
from datetime import datetime
from typing import List, Dict, Optional
from .model_service import ModelService
from database.models import Email, EmailCategory, get_db
from sqlalchemy.orm import Session

class EmailService:
    def __init__(self, imap_server: str, email_addr: str, password: str):
        self.imap_server = imap_server
        self.email_addr = email_addr
        self.password = password
        self.model_service = ModelService()
        
    def connect(self):
        """连接到IMAP服务器"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_addr, self.password)
            self.mail.select('inbox')
            return True
        except Exception as e:
            print(f"邮件连接失败: {e}")
            return False
    
    def decode_mime_words(self, s):
        """解码邮件头部信息"""
        decoded_fragments = decode_header(s)
        fragments = []
        for fragment, encoding in decoded_fragments:
            if isinstance(fragment, bytes):
                if encoding:
                    fragment = fragment.decode(encoding)
                else:
                    fragment = fragment.decode('utf-8', errors='ignore')
            fragments.append(fragment)
        return ''.join(fragments)
    
    def extract_email_content(self, msg) -> Dict:
        """提取邮件内容"""
        # 获取邮件基本信息
        subject = self.decode_mime_words(msg.get('Subject', ''))
        sender = self.decode_mime_words(msg.get('From', ''))
        date_str = msg.get('Date', '')
        
        # 解析邮件正文
        content = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        content = payload.decode('utf-8', errors='ignore')
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                content = payload.decode('utf-8', errors='ignore')
        
        return {
            "title": subject,
            "sender": sender,
            "time": date_str,
            "content": content
        }
    
    def classify_email(self, email_data: Dict) -> Dict:
        """使用模型对邮件进行分类"""
        prompt = f"""
        请对以下邮件进行分类，分类结果只能是：资讯类、任务类、无法分类

        邮件标题：{email_data['title']}
        发件人：{email_data['sender']}
        邮件内容：{email_data['content'][:500]}...

        请直接返回分类结果：
        """
        
        try:
            classification = self.model_service.generate_response(prompt)
            
            # 解析分类结果
            if "任务类" in classification:
                category = EmailCategory.TASK
            elif "资讯类" in classification:
                category = EmailCategory.NEWS
            else:
                category = EmailCategory.UNCLASSIFIED
                
            return {
                "category": category.value,
                "classification_detail": classification
            }
        except Exception as e:
            print(f"邮件分类失败: {e}")
            return {
                "category": EmailCategory.UNCLASSIFIED.value,
                "classification_detail": "分类失败"
            }
    
    def process_new_emails(self) -> List[Dict]:
        """处理新邮件"""
        if not hasattr(self, 'mail'):
            if not self.connect():
                return []
        
        try:
            # 搜索未读邮件
            status, messages = self.mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            processed_emails = []
            
            for email_id in email_ids[-10:]:  # 只处理最新的10封邮件
                status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # 提取邮件内容
                        email_content = self.extract_email_content(msg)
                        
                        # 分类邮件
                        classification = self.classify_email(email_content)
                        
                        # 构建结果
                        result = {
                            "email_id": email_id.decode(),
                            "title": email_content["title"],
                            "sender": email_content["sender"],
                            "time": email_content["time"],
                            "content": email_content["content"],
                            "category": classification["category"]
                        }
                        
                        processed_emails.append(result)
                        
                        # 保存到数据库
                        self.save_email_to_db(result)
            
            return processed_emails
            
        except Exception as e:
            print(f"处理邮件失败: {e}")
            return []
    
    def save_email_to_db(self, email_data: Dict):
        """保存邮件到数据库"""
        db = next(get_db())
        try:
            # 检查邮件是否已存在
            existing_email = db.query(Email).filter(Email.email_id == email_data["email_id"]).first()
            if existing_email:
                return
            
            # 创建新邮件记录
            email_record = Email(
                email_id=email_data["email_id"],
                title=email_data["title"],
                sender=email_data["sender"],
                content=email_data["content"],
                category=EmailCategory(email_data["category"])
            )
            
            db.add(email_record)
            db.commit()
            
        except Exception as e:
            print(f"保存邮件失败: {e}")
            db.rollback()
        finally:
            db.close()