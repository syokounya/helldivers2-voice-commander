"""
战备数据管理模块
负责加载和管理战备配置
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Set


class StratagemManager:
    """战备管理器"""
    
    # 可选的全局指令列表
    AVAILABLE_GLOBAL_COMMANDS = [
        "增援",
        "补给",
        "SOS求救信标",
        "飞鹰整备",
        "呼叫超级驱逐舰",
        "地层钻机",
        "虫巢破坏者钻机",
        "地震探测器",
        "超级地球旗帜",
        "勘探钻机",
        "超级硬盘",
        "SEAF火炮",
        "上传数据",
        "增援舱",
        "货物集装箱",
        "地狱火炸弹",
    ]
    
    def __init__(self, json_path: str = "stratagems.json"):
        self.json_path = Path(json_path)
        self.stratagems: Dict[str, List[str]] = {}
        self.aliases: Dict[str, str] = {}  # 别名映射
        self.global_commands: Set[str] = {"增援", "补给", "SOS求救信标"}  # 默认启用的全局指令
        self.active_slots: List[str] = ["飞鹰500kg炸弹", "轨道炮", "机炮", "重机枪"]
        
        # 飞鹰战备列表
        self.eagle_stratagems = [
            "飞鹰500kg炸弹",
            "飞鹰机枪扫射",
            "飞鹰空袭",
            "飞鹰集束炸弹",
            "飞鹰烟幕",
            "飞鹰燃烧弹",
            "飞鹰火箭巢",
        ]
        
        self.load_stratagems()
    
    def load_stratagems(self) -> None:
        """从 JSON 文件加载战备数据"""
        if not self.json_path.exists():
            raise FileNotFoundError(f"找不到 {self.json_path}")
        
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        self.stratagems = data.get("stratagems", {})
        self.aliases = data.get("aliases", {})
        self.categories: Dict[str, List[str]] = data.get("categories", {})
        self.global_category: str = data.get("global_category", "任务类")
        self.eagle_stratagems = data.get("eagle_stratagems", self.eagle_stratagems)

        # 旧版 JSON 没有 categories 字段时，按战备名自动归类（兼容旧数据）
        if not self.categories:
            self.categories = self._infer_categories_from_stratagems()
            self.global_category = "任务类"
            # 自动补全写回 JSON，升级旧文件
            data["categories"] = self.categories
            data["global_category"] = self.global_category
            data["eagle_stratagems"] = self.eagle_stratagems
            self.json_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        # 更新全局指令候选列表
        self.AVAILABLE_GLOBAL_COMMANDS = list(self.categories.get(self.global_category, []))
    
    def is_allowed(self, name: str) -> bool:
        """检查战备是否允许触发"""
        # 飞鹰整备特殊处理：只有选择了飞鹰战备才能使用
        if name == "飞鹰整备":
            return self.has_eagle_stratagem()
        
        return (name in self.global_commands) or (name in self.active_slots)
    
    def has_eagle_stratagem(self) -> bool:
        """检查是否选择了飞鹰战备"""
        for slot in self.active_slots:
            if slot in self.eagle_stratagems:
                return True
        return False
    
    def get_sequence(self, name: str) -> Optional[List[str]]:
        """获取战备的按键序列"""
        if not self.is_allowed(name):
            return None
        return self.stratagems.get(name)
    
    def get_all_names(self) -> List[str]:
        """获取所有战备名称"""
        return list(self.stratagems.keys())
    
    def update_slot(self, index: int, name: str) -> None:
        """更新槽位战备"""
        if 0 <= index < 4:
            if index < len(self.active_slots):
                self.active_slots[index] = name
            else:
                while len(self.active_slots) <= index:
                    self.active_slots.append(name)
                self.active_slots[index] = name
            
            # 检查飞鹰整备状态
            self._update_eagle_rearm_status()
    
    def toggle_global_command(self, name: str, enabled: bool) -> None:
        """切换全局指令的启用状态"""
        if enabled:
            self.global_commands.add(name)
        else:
            self.global_commands.discard(name)
    
    def is_global_command_enabled(self, name: str) -> bool:
        """检查全局指令是否启用"""
        return name in self.global_commands
    
    def _update_eagle_rearm_status(self) -> None:
        """更新飞鹰整备的启用状态"""
        has_eagle = self.has_eagle_stratagem()
        
        if has_eagle:
            # 自动启用飞鹰整备
            if "飞鹰整备" not in self.global_commands:
                self.global_commands.add("飞鹰整备")
                return "enabled"
        else:
            # 自动禁用飞鹰整备
            if "飞鹰整备" in self.global_commands:
                self.global_commands.discard("飞鹰整备")
                return "disabled"
        
        return None
    
    def get_eagle_rearm_status_message(self) -> Optional[str]:
        """获取飞鹰整备状态消息"""
        status = self._update_eagle_rearm_status()
        if status == "enabled":
            return "✈️ 检测到飞鹰战备，已自动启用【飞鹰整备】"
        elif status == "disabled":
            return "⚠️ 未选择飞鹰战备，已自动禁用【飞鹰整备】"

    def _infer_categories_from_stratagems(self) -> Dict[str, List[str]]:
        """旧版 JSON 无分类数据时，将所有战备放入未分类（兼容升级）"""
        return {"未分类": list(self.stratagems.keys())}
        return None
