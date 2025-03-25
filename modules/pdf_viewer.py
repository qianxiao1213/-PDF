import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QSpinBox, QPushButton, QToolBar, QMessageBox)
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QKeySequence, QAction, QWheelEvent, QTransform
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView

class DraggablePdfView(QPdfView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_start_pos = None
        self._rotation = 0
        self._transform = QTransform()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self._drag_start_pos is not None:
            delta = event.pos() - self._drag_start_pos
            navigator = self.pageNavigator()
            current_pos = navigator.currentLocation()
            navigator.jump(current_pos - delta / self.zoomFactor(), self.zoomFactor())
            self._drag_start_pos = event.pos()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None
        super().mouseReleaseEvent(event)
    
    def setPageRotation(self, rotation):
        """设置页面旋转角度"""
        self._rotation = rotation % 360
        self._updateTransform()
    
    def _updateTransform(self):
        """更新变换矩阵"""
        self._transform = QTransform()
        if self._rotation == 90:
            self._transform.translate(self.height(), 0)
            self._transform.rotate(90)
        elif self._rotation == 180:
            self._transform.translate(self.width(), self.height())
            self._transform.rotate(180)
        elif self._rotation == 270:
            self._transform.translate(0, self.width())
            self._transform.rotate(270)
        self.viewport().update()
    
    def paintEvent(self, event):
        """重绘事件"""
        painter = self.viewport().painter()
        if painter is None:
            return
        
        painter.save()
        painter.setTransform(self._transform)
        super().paintEvent(event)
        painter.restore()

class PdfViewer(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_norm = None
        self.setup_ui()
        self.setup_shortcuts()
        self.refresh_norms()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 分类筛选
        self.filter_layout = QHBoxLayout()
        self.filter_label = QLabel("分类筛选:")
        self.filter_layout.addWidget(self.filter_label)
        layout.addLayout(self.filter_layout)
        
        # 搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索规范...")
        self.search_box.textChanged.connect(self.search_norms)
        layout.addWidget(self.search_box)
        
        # 规范列表
        self.norm_list = QListWidget()
        self.norm_list.itemClicked.connect(self.load_norm)
        layout.addWidget(self.norm_list)
        
        # PDF查看器
        self.pdf_view = DraggablePdfView()
        self.pdf_doc = QPdfDocument()
        self.pdf_view.setDocument(self.pdf_doc)
        
        # 工具栏
        self.toolbar = QToolBar()
        layout.addWidget(self.toolbar)
        
        # 页码导航
        self.page_label = QLabel("页码:")
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.valueChanged.connect(self.go_to_page)
        self.total_pages_label = QLabel("/ 0")
        
        self.toolbar.addWidget(self.page_label)
        self.toolbar.addWidget(self.page_spin)
        self.toolbar.addWidget(self.total_pages_label)
        
        # 缩放控制
        self.zoom_in_btn = QPushButton("放大")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn = QPushButton("缩小")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.toolbar.addWidget(self.zoom_in_btn)
        self.toolbar.addWidget(self.zoom_out_btn)
        
        # 旋转按钮
        self.rotate_btn = QPushButton("旋转90°")
        self.rotate_btn.clicked.connect(self.rotate_page)
        self.toolbar.addWidget(self.rotate_btn)
        
        # OCR按钮
        self.ocr_btn = QPushButton("OCR识别")
        self.ocr_btn.clicked.connect(self.run_ocr)
        self.toolbar.addWidget(self.ocr_btn)
        
        layout.addWidget(self.pdf_view)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # 上下翻页
        self.prev_page_action = QAction(self)
        self.prev_page_action.setShortcut(QKeySequence("W"))
        self.prev_page_action.triggered.connect(self.prev_page)
        self.addAction(self.prev_page_action)
        
        self.next_page_action = QAction(self)
        self.next_page_action.setShortcut(QKeySequence("S"))
        self.next_page_action.triggered.connect(self.next_page)
        self.addAction(self.next_page_action)
        
        # 放大缩小
        self.zoom_in_action = QAction(self)
        self.zoom_in_action.setShortcut(QKeySequence("Ctrl++"))
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.addAction(self.zoom_in_action)
        
        self.zoom_out_action = QAction(self)
        self.zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.addAction(self.zoom_out_action)
        
        # 旋转
        self.rotate_action = QAction(self)
        self.rotate_action.setShortcut(QKeySequence("R"))
        self.rotate_action.triggered.connect(self.rotate_page)
        self.addAction(self.rotate_action)
    
    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮事件处理"""
        if event.modifiers() & Qt.ControlModifier:
            # Ctrl+滚轮缩放
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
    
    def refresh_norms(self, category=None):
        """刷新规范列表"""
        self.norm_list.clear()
        norms = self.db.get_norms(category)
        for norm in norms:
            self.norm_list.addItem(norm['name'])
    
    def search_norms(self):
        """搜索规范"""
        keyword = self.search_box.text().lower()
        norms = self.db.get_norms()
        self.norm_list.clear()
        for norm in norms:
            if keyword in norm['name'].lower():
                self.norm_list.addItem(norm['name'])
    
    def load_norm(self, item):
        """加载选中的规范"""
        norm_name = item.text()
        norms = self.db.get_norms()
        norm = next((n for n in norms if n['name'] == norm_name), None)
        
        if norm and os.path.exists(norm['path']):
            self.current_norm = norm
            
            # 加载PDF文档
            self.pdf_doc.close()
            if self.pdf_doc.load(norm['path']):
                # 更新页面导航
                page_count = self.pdf_doc.pageCount()
                self.page_spin.setMaximum(page_count)
                self.total_pages_label.setText(f"/ {page_count}")
                
                # 恢复阅读进度和旋转
                self.page_spin.setValue(norm['last_page'])
                self.pdf_view.setPageRotation(norm['rotation'])
                
                # 跳转到保存的页面
                self.go_to_page(norm['last_page'])
            else:
                QMessageBox.warning(self, "错误", "无法加载PDF文档")
    
    def go_to_page(self, page):
        """跳转到指定页面"""
        if 1 <= page <= self.pdf_doc.pageCount():
            self.pdf_view.pageNavigator().jump(page - 1, QPointF(0, 0))
            if self.current_norm:
                self.db.update_norm_progress(
                    self.current_norm['id'], 
                    page, 
                    self.pdf_view._rotation
                )
    
    def prev_page(self):
        """上一页"""
        current = self.page_spin.value()
        if current > 1:
            self.page_spin.setValue(current - 1)
    
    def next_page(self):
        """下一页"""
        current = self.page_spin.value()
        if current < self.pdf_doc.pageCount():
            self.page_spin.setValue(current + 1)
    
    def zoom_in(self):
        """放大视图"""
        current_zoom = self.pdf_view.zoomFactor()
        self.pdf_view.setZoomFactor(current_zoom * 1.2)
    
    def zoom_out(self):
        """缩小视图"""
        current_zoom = self.pdf_view.zoomFactor()
        self.pdf_view.setZoomFactor(current_zoom / 1.2)
    
    def rotate_page(self):
        """旋转页面"""
        if not self.current_norm:
            return
        
        current_rotation = self.pdf_view._rotation
        new_rotation = (current_rotation + 90) % 360
        self.pdf_view.setPageRotation(new_rotation)
        
        # 更新数据库中的旋转状态
        self.db.update_norm_progress(
            self.current_norm['id'],
            self.page_spin.value(),
            new_rotation
        )
    
    def run_ocr(self):
        """执行OCR识别"""
        QMessageBox.information(self, "OCR", "OCR功能需要额外安装依赖库如pytesseract")
        # 实际实现需要安装:
        # pip install pytesseract pillow
        # 并下载Tesseract OCR引擎