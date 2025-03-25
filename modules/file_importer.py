import os
import shutil
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QFileDialog, QListWidget,
                              QMessageBox)
from PySide6.QtCore import Qt, Signal

class FileImporter(QWidget):
    file_imported = Signal()
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 拖放区域
        self.drop_label = QLabel("拖放PDF文件到这里或点击下方按钮选择文件")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("QLabel { border: 2px dashed #aaa; padding: 20px; }")
        self.drop_label.setAcceptDrops(True)
        self.drop_label.dragEnterEvent = self.dragEnterEvent
        self.drop_label.dropEvent = self.dropEvent
        layout.addWidget(self.drop_label)
        
        # 选择文件按钮
        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("选择文件")
        self.select_btn.clicked.connect(self.select_files)
        btn_layout.addWidget(self.select_btn)
        
        self.select_dir_btn = QPushButton("选择文件夹")
        self.select_dir_btn.clicked.connect(self.select_directory)
        btn_layout.addWidget(self.select_dir_btn)
        layout.addLayout(btn_layout)
        
        # 文件列表
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)
        
        # 分类选择
        self.category_label = QLabel("分类:")
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("输入分类名称，如'土建'、'机械'等")
        layout.addWidget(self.category_label)
        layout.addWidget(self.category_input)
        
        # 导入按钮
        self.import_btn = QPushButton("导入选中文件")
        self.import_btn.clicked.connect(self.import_files)
        layout.addWidget(self.import_btn)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls() 
                if url.toLocalFile().lower().endswith('.pdf')]
        self.add_files_to_list(files)
    
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择PDF文件", "", "PDF文件 (*.pdf)")
        self.add_files_to_list(files)
    
    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择包含PDF的文件夹")
        if dir_path:
            files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) 
                    if f.lower().endswith('.pdf')]
            self.add_files_to_list(files)
    
    def add_files_to_list(self, files):
        for file in files:
            self.file_list.addItem(file)
    
    def import_files(self):
        category = self.category_input.text().strip() or None
        dest_dir = "user_files"
        
        for i in range(self.file_list.count()):
            src_path = self.file_list.item(i).text()
            if not os.path.exists(src_path):
                continue
            
            # 移动文件到用户目录
            filename = os.path.basename(src_path)
            dest_path = os.path.join(dest_dir, filename)
            
            try:
                if not os.path.exists(dest_path):
                    shutil.copy2(src_path, dest_path)
                
                # 添加到数据库
                self.db.add_norm(filename, dest_path, category)
            
            except Exception as e:
                QMessageBox.warning(self, "导入错误", f"导入文件失败: {str(e)}")
                continue
        
        self.file_list.clear()
        self.file_imported.emit()
        QMessageBox.information(self, "完成", "文件导入完成")