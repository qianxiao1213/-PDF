import os
import sqlite3
from PySide6.QtCore import QObject, Signal

class NormDatabase(QObject):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 创建规范表
        c.execute('''CREATE TABLE IF NOT EXISTS norms
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      path TEXT NOT NULL UNIQUE,
                      category TEXT,
                      last_page INTEGER DEFAULT 1,
                      rotation INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # 创建分类表
        c.execute('''CREATE TABLE IF NOT EXISTS categories
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL UNIQUE)''')
        
        conn.commit()
        conn.close()
    
    def add_norm(self, name, path, category=None):
        """添加规范"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("INSERT INTO norms (name, path, category) VALUES (?, ?, ?)",
                     (name, path, category))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_norms(self, category=None):
        """获取规范列表"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if category:
            c.execute("SELECT id, name, path, last_page, rotation FROM norms WHERE category=?", (category,))
        else:
            c.execute("SELECT id, name, path, last_page, rotation FROM norms")
        
        norms = [dict(zip(['id', 'name', 'path', 'last_page', 'rotation'], row)) for row in c.fetchall()]
        conn.close()
        return norms
    
    def update_norm_progress(self, norm_id, page, rotation):
        """更新阅读进度和旋转状态"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE norms SET last_page=?, rotation=? WHERE id=?", (page, rotation, norm_id))
        conn.commit()
        conn.close()
    
    def add_category(self, name):
        """添加分类"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_categories(self):
        """获取所有分类"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM categories")
        categories = [row[0] for row in c.fetchall()]
        conn.close()
        return categories