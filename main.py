import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QTabWidget, QStatusBar)
from PySide6.QtCore import Qt, QStandardPaths

# 导入自定义模块
from modules.database import NormDatabase
from modules.file_importer import FileImporter
from modules.pdf_viewer import PdfViewer
from modules.category_manager import CategoryManager
from modules.settings import SettingsManager

class NormViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("工程规范管理系统")
        self.resize(1400, 900)
        
        # 初始化目录结构
        self.init_directories()
        
        # 初始化模块
        self.db = NormDatabase(os.path.join('user_files', 'norms.db'))
        self.settings = SettingsManager()
        
        # 主界面布局
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)
        
        # 创建标签页
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # 添加各个功能模块
        self.setup_modules()
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def init_directories(self):
        """初始化必要的目录结构"""
        os.makedirs('resources', exist_ok=True)
        os.makedirs('user_files', exist_ok=True)
    
    def setup_modules(self):
        """设置各个功能模块"""
        # 文件导入模块
        self.importer = FileImporter(self.db)
        self.tabs.addTab(self.importer, "导入规范")
        
        # PDF查看模块
        self.viewer = PdfViewer(self.db)
        self.tabs.addTab(self.viewer, "查看规范")
        
        # 分类管理模块
        self.category_manager = CategoryManager(self.db)
        self.tabs.addTab(self.category_manager, "分类管理")
        
        # 连接模块信号
        self.importer.file_imported.connect(self.viewer.refresh_norms)
        self.category_manager.category_updated.connect(self.viewer.refresh_norms)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 打包后资源路径处理
    if getattr(sys, 'frozen', False):
        # 如果是打包后的程序
        os.chdir(sys._MEIPASS)
    
    viewer = NormViewer()
    viewer.show()
    sys.exit(app.exec())
