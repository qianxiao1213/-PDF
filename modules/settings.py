from PySide6.QtCore import QSettings

class SettingsManager:
    def __init__(self):
        self.settings = QSettings("GBViewer", "NormViewer")
    
    def get(self, key, default=None):
        return self.settings.value(key, default)
    
    def set(self, key, value):
        self.settings.setValue(key, value)
    
    def get_recent_files(self):
        return self.get("recent_files", [])
    
    def add_recent_file(self, file_path):
        recent = self.get_recent_files()
        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)
        self.set("recent_files", recent[:10])  # 最多保存10个最近文件