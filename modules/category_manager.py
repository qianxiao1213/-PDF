from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QListWidget, 
                              QMessageBox, QInputDialog)
from PySide6.QtCore import Signal

class CategoryManager(QWidget):
    category_updated = Signal()
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_categories()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 添加分类
        add_layout = QHBoxLayout()
        self.new_category_input = QLineEdit()
        self.new_category_input.setPlaceholderText("输入新分类名称")
        add_layout.addWidget(self.new_category_input)
        
        self.add_btn = QPushButton("添加分类")
        self.add_btn.clicked.connect(self.add_category)
        add_layout.addWidget(self.add_btn)
        layout.addLayout(add_layout)
        
        # 分类列表
        self.category_list = QListWidget()
        self.category_list.itemClicked.connect(self.show_category_norms)
        layout.addWidget(self.category_list)
        
        # 分类操作按钮
        btn_layout = QHBoxLayout()
        self.rename_btn = QPushButton("重命名")
        self.rename_btn.clicked.connect(self.rename_category)
        btn_layout.addWidget(self.rename_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.delete_category)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)
        
        # 分类下的规范列表
        self.norms_label = QLabel("该分类下的规范:")
        layout.addWidget(self.norms_label)
        
        self.norms_list = QListWidget()
        layout.addWidget(self.norms_list)
    
    def load_categories(self):
        """加载所有分类"""
        self.category_list.clear()
        categories = self.db.get_categories()
        for category in categories:
            self.category_list.addItem(category)
    
    def add_category(self):
        """添加新分类"""
        name = self.new_category_input.text().strip()
        if not name:
            QMessageBox.warning(self, "错误", "分类名称不能为空")
            return
        
        if self.db.add_category(name):
            self.new_category_input.clear()
            self.load_categories()
            self.category_updated.emit()
        else:
            QMessageBox.warning(self, "错误", "分类已存在")
    
    def rename_category(self):
        """重命名分类"""
        current_item = self.category_list.currentItem()
        if not current_item:
            return
        
        old_name = current_item.text()
        new_name, ok = QInputDialog.getText(
            self, "重命名分类", "输入新名称:", text=old_name)
        
        if ok and new_name:
            # 这里需要扩展数据库方法来实现重命名
            QMessageBox.information(self, "提示", "重命名功能需要数据库支持")
    
    def delete_category(self):
        """删除分类"""
        current_item = self.category_list.currentItem()
        if not current_item:
            return
        
        name = current_item.text()
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除分类'{name}'吗?这不会删除规范文件本身。",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 这里需要扩展数据库方法来实现删除
            QMessageBox.information(self, "提示", "删除功能需要数据库支持")
    
    def show_category_norms(self, item):
        """显示分类下的规范"""
        category = item.text()
        norms = self.db.get_norms(category)
        
        self.norms_list.clear()
        for norm in norms:
            self.norms_list.addItem(norm['name'])