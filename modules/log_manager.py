"""
日志管理模块
负责日志的显示和文件保存
"""
import time
from pathlib import Path
from queue import Queue, Empty
from typing import Optional


class LogManager:
    """日志管理器"""
    
    def __init__(self, log_file: str = "run.log", max_lines: int = 1000):
        self.log_file = Path(log_file)
        self.max_lines = max_lines
        self.log_queue: Queue[str] = Queue()
    
    def log(self, message: str) -> None:
        """记录日志"""
        timestamp = time.strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"
        
        # 放入队列供 GUI 显示
        self.log_queue.put(line)
        
        # 写入文件
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with self.log_file.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass
    
    def get_pending_logs(self) -> list[str]:
        """获取待显示的日志"""
        logs = []
        try:
            while True:
                logs.append(self.log_queue.get_nowait())
        except Empty:
            pass
        return logs
