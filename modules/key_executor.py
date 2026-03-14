"""
按键执行模块
负责模拟按键输入
"""
import time
from typing import List, Dict
import pydirectinput


class KeyExecutor:
    """按键执行器"""
    
    # WASD → 方向键映射
    KEY_MAP: Dict[str, str] = {
        "W": "up",
        "A": "left",
        "S": "down",
        "D": "right",
    }
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        pydirectinput.PAUSE = 0
    
    def set_dry_run(self, value: bool) -> None:
        """设置是否为测试模式（不发送真实按键）"""
        self.dry_run = value
    
    def execute(self, wasd_sequence: List[str]) -> List[str]:
        """
        执行战备按键序列
        
        Args:
            wasd_sequence: WASD 序列，如 ["W", "S", "D", "A"]
            
        Returns:
            实际发送的方向键序列，如 ["up", "down", "right", "left"]
        """
        # 转换为方向键
        arrows: List[str] = []
        for key in wasd_sequence:
            arrow = self.KEY_MAP.get(key.upper())
            if arrow:
                arrows.append(arrow)
        
        # 测试模式：只返回序列，不发送按键
        if self.dry_run:
            return arrows
        
        # 先轻触 Ctrl 呼出战备菜单
        pydirectinput.keyDown("ctrl")
        time.sleep(0.03)
        pydirectinput.keyUp("ctrl")
        time.sleep(0.05)
        
        # 依次按下方向键
        for arrow in arrows:
            pydirectinput.keyDown(arrow)
            time.sleep(0.03)
            pydirectinput.keyUp(arrow)
            time.sleep(0.05)
        
        return arrows
