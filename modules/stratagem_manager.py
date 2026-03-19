"""
战备数据管理模块
负责加载和管理战备配置
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Set


class StratagemManager:
    """战备管理器 —— 所有数据从 JSON 加载，零硬编码"""

    def __init__(self, json_path: str = "stratagems.json"):
        self.json_path = Path(json_path)
        self.stratagems: Dict[str, List[str]] = {}
        self.aliases: Dict[str, str] = {}
        self.categories: Dict[str, List[str]] = {}
        self.global_category: str = ""
        self.eagle_stratagems: List[str] = []
        self.eagle_rearm_name: str = ""
        self.global_commands: Set[str] = set()
        self.active_slots: List[str] = ["", "", "", ""]
        self.AVAILABLE_GLOBAL_COMMANDS: List[str] = []
        self.load_stratagems()

    def load_stratagems(self) -> None:
        """从 JSON 文件加载所有战备数据"""
        if not self.json_path.exists():
            raise FileNotFoundError(f"找不到 {self.json_path}")

        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        self.stratagems = data.get("stratagems", {})
        self.aliases = data.get("aliases", {})
        self.eagle_stratagems = data.get("eagle_stratagems", [])
        self.global_category = data.get("global_category", "")

        # 分类数据：旧版 JSON 无此字段时自动迁移
        self.categories = data.get("categories", {})
        if not self.categories:
            self.categories = {"未分类": list(self.stratagems.keys())}
            self.global_category = "未分类"
            data["categories"] = self.categories
            data["global_category"] = self.global_category
            data["eagle_stratagems"] = self.eagle_stratagems

        # defaults 字段：无此字段时写入空白默认值
        defaults = data.get("defaults", {})
        if not defaults:
            defaults = {
                "active_slots": ["", "", "", ""],
                "global_commands_enabled": [],
                "eagle_rearm_name": "",
            }
            data["defaults"] = defaults

        self.eagle_rearm_name = defaults.get("eagle_rearm_name", "")

        # 全局指令候选列表（来自 global_category 分类）
        self.AVAILABLE_GLOBAL_COMMANDS = list(
            self.categories.get(self.global_category, [])
        )

        # 默认启用的全局指令（来自 defaults，过滤掉 eagle_rearm_name）
        enabled = defaults.get("global_commands_enabled", [])
        self.global_commands = set(
            c for c in enabled if c in self.AVAILABLE_GLOBAL_COMMANDS
            and c != self.eagle_rearm_name
        )

        # 默认槽位（来自 defaults）
        raw_slots = defaults.get("active_slots", [])
        self.active_slots = (list(raw_slots) + ["", "", "", ""])[:4]

        # 如果有需要写回（迁移），持久化
        if "defaults" not in data or "categories" not in data or "eagle_stratagems" not in data:
            self.json_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        # 初始化飞鹰整备状态
        self._sync_eagle_rearm()

    def _sync_eagle_rearm(self) -> None:
        """根据当前槽位同步飞鹰整备启用状态"""
        if not self.eagle_rearm_name:
            return
        if self.has_eagle_stratagem():
            self.global_commands.add(self.eagle_rearm_name)
        else:
            self.global_commands.discard(self.eagle_rearm_name)

    def is_allowed(self, name: str) -> bool:
        """检查战备是否允许触发"""
        if name == self.eagle_rearm_name:
            return self.has_eagle_stratagem()
        return (name in self.global_commands) or (name in self.active_slots)

    def has_eagle_stratagem(self) -> bool:
        """检查槽位中是否有飞鹰战备"""
        return any(s in self.eagle_stratagems for s in self.active_slots)

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
        while len(self.active_slots) <= index:
            self.active_slots.append("")
        self.active_slots[index] = name
        self._sync_eagle_rearm()

    def toggle_global_command(self, name: str, enabled: bool) -> None:
        """切换全局指令的启用状态"""
        if enabled:
            self.global_commands.add(name)
        else:
            self.global_commands.discard(name)

    def is_global_command_enabled(self, name: str) -> bool:
        """检查全局指令是否启用"""
        return name in self.global_commands

    def _update_eagle_rearm_status(self) -> Optional[str]:
        """更新飞鹰整备状态并返回变化消息键"""
        if not self.eagle_rearm_name:
            return None
        had = self.eagle_rearm_name in self.global_commands
        self._sync_eagle_rearm()
        now = self.eagle_rearm_name in self.global_commands
        if not had and now:
            return "enabled"
        if had and not now:
            return "disabled"
        return None

    def get_eagle_rearm_status_message(self) -> Optional[str]:
        """获取飞鹰整备状态消息"""
        status = self._update_eagle_rearm_status()
        if not self.eagle_rearm_name:
            return None
        if status == "enabled":
            return f"✈️ 检测到飞鹰战备，已自动启用【{self.eagle_rearm_name}】"
        elif status == "disabled":
            return f"⚠️ 未选择飞鹰战备，已自动禁用【{self.eagle_rearm_name}】"
        return None

    def _infer_categories_from_stratagems(self) -> Dict[str, List[str]]:
        """旧版 JSON 无分类数据时，将所有战备放入未分类"""
        return {"未分类": list(self.stratagems.keys())}
