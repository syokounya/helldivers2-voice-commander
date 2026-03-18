"""
GUI 战备指令编辑器 Tab
"""
import customtkinter as ctk
from typing import Callable, Optional, Dict, List
import json
from pynput import keyboard as pynput_keyboard


# 战备分类定义（与主界面保持一致）
STRATAGEM_CATEGORIES = {
    "任务类": ["增援", "补给", "SOS求救信标", "飞鹰整备", "呼叫超级驱逐舰",
              "地层钻机", "虫巢破坏者钻机", "地震探测器", "超级地球旗帜",
              "勘探钻机", "超级硬盘", "SEAF火炮", "上传数据", "增援舱",
              "货物集装箱", "地狱火炸弹"],
    "背包类": ["补给背包", "喷气背包", "防弹盾", "实弹狗", "激光狗", "护盾背包",
              "定向护盾", "热狗", "地狱火背包", "电弧狗", "悬浮背包", "毒气狗", "传送背包"],
    "载具类": ["爱国者机甲", "解放者机甲", "快速侦察车", "堡垒主战坦克"],
    "地雷类": ["反步兵地雷", "燃烧地雷", "反坦克地雷", "毒气地雷"],
    "防御建筑": ["护盾发生器中继站", "重机枪支架", "榴弹墙", "反坦克炮"],
    "哨戒炮": ["机枪哨戒炮", "加特林哨戒炮", "砰砰炮", "迫击炮", "火箭哨戒炮",
              "特斯拉电塔", "电磁迫击炮", "激光哨戒炮", "喷火哨戒炮"],
    "轨道打击": ["轨道精准打击", "轨道加特林", "轨道毒气", "轨道120mm火力网",
               "轨道空爆", "轨道烟幕", "轨道静电", "轨道380mm火力网",
               "轨道游走火力网", "轨道激光", "轨道燃烧弹", "轨道炮"],
    "飞鹰打击": ["飞鹰机枪扫射", "飞鹰空袭", "飞鹰集束炸弹", "飞鹰烟幕",
               "飞鹰燃烧弹", "飞鹰火箭巢", "飞鹰500kg炸弹"],
    "支援武器": ["电弧发射器", "类星体", "空爆火箭发射器", "突击兵", "飞矛",
               "磁轨炮", "黄蜂发射器", "纪元", "大锤", "毒矛枪", "燃烧次抛",
               "灭菌器", "除叶工具", "电榴弹", "荡平者", "C4炸药包", "导弹发射井",
               "弹链榴弹发射器", "重装加特林", "唯一真旗", "通用机枪", "反坦克次抛",
               "盟友机枪", "激光大炮", "反器材步枪", "无后坐力炮", "榴弹发射器",
               "喷火器", "重机枪", "机炮"],
    "未分类": [],  # 动态计算
}

# 按键名称映射（规范化显示）
KEY_MAP = {
    "w": "W", "a": "A", "s": "S", "d": "D",
    "up": "W", "down": "S", "left": "A", "right": "D",
}


class StratagemEditorTab:
    """战备指令编辑器 Tab"""

    def __init__(
        self,
        parent,
        stratagem_names: List[str],
        json_path: str = "stratagems.json",
        on_save_callback: Optional[Callable[[str], None]] = None,
    ):
        self.parent = parent
        self.stratagem_names = stratagem_names
        self.json_path = json_path
        self.on_save_callback = on_save_callback

        self.data: Dict = {}
        self.current_item_name: Optional[str] = None  # 当前编辑的战备名
        self.edit_mode: str = "战备"  # "战备" 或 "别名"

        # 键盘录制状态
        self.is_recording = False
        self.recorded_keys: List[str] = []
        self.listener: Optional[pynput_keyboard.Listener] = None

        # UI 组件
        self.tab_war_btn: Optional[ctk.CTkButton] = None
        self.tab_alias_btn: Optional[ctk.CTkButton] = None
        self.category_menu: Optional[ctk.CTkOptionMenu] = None
        self.item_menu: Optional[ctk.CTkOptionMenu] = None
        self.item_name_entry: Optional[ctk.CTkEntry] = None
        self.alias_target_menu: Optional[ctk.CTkOptionMenu] = None
        self.alias_target_frame: Optional[ctk.CTkFrame] = None
        self.keys_frame: Optional[ctk.CTkFrame] = None
        self.keys_display: Optional[ctk.CTkLabel] = None
        self.record_btn: Optional[ctk.CTkButton] = None
        self.status_label: Optional[ctk.CTkLabel] = None

        self._load_data()
        self._build()

    # ───────────────────────── 数据 ─────────────────────────

    def _load_data(self):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {"stratagems": {}, "aliases": {}}
        except Exception as e:
            print(f"[错误] 加载数据失败: {e}")
            self.data = {"stratagems": {}, "aliases": {}}

    def _save_data(self):
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            if self.on_save_callback:
                self.on_save_callback(self.json_path)
            self._set_status("保存成功", "#4CAF50")
        except Exception as e:
            self._set_status(f"保存失败: {e}", "#F44336")

    def _get_category_for(self, name: str) -> str:
        """根据战备名称查找分类"""
        for cat, members in STRATAGEM_CATEGORIES.items():
            if name in members:
                return cat
        return "未分类"

    def _get_items_in_category(self, category: str) -> List[str]:
        """获取某分类下所有已存在的战备"""
        stratagems = self.data.get("stratagems", {})
        if category == "未分类":
            known = set(n for names in STRATAGEM_CATEGORIES.values() for n in names)
            return [n for n in stratagems if n not in known]
        members = STRATAGEM_CATEGORIES.get(category, [])
        return [n for n in members if n in stratagems]

    # ───────────────────────── 构建 UI ─────────────────────────

    def _build(self):
        outer = ctk.CTkFrame(self.parent, fg_color="#000000")
        outer.pack(fill="both", expand=True)

        # ── 标题栏 ──
        header = ctk.CTkFrame(outer, fg_color="#111111", height=50)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="战备指令编辑器",
            font=("Microsoft YaHei", 20, "bold"),
            text_color="#FFD700"
        ).pack(side="left", padx=20)

        # 模式切换按钮
        btn_frame = ctk.CTkFrame(header, fg_color="#111111")
        btn_frame.pack(side="right", padx=20)

        self.tab_war_btn = ctk.CTkButton(
            btn_frame, text="编辑战备",
            command=lambda: self._switch_mode("战备"),
            width=90, height=30,
            fg_color="#FFD700", text_color="#000000",
            hover_color="#FFDD55", font=("Microsoft YaHei", 11)
        )
        self.tab_war_btn.pack(side="left", padx=(0, 5))

        self.tab_alias_btn = ctk.CTkButton(
            btn_frame, text="编辑别名",
            command=lambda: self._switch_mode("别名"),
            width=90, height=30,
            fg_color="#333333", text_color="#AAAAAA",
            hover_color="#444444", font=("Microsoft YaHei", 11)
        )
        self.tab_alias_btn.pack(side="left")

        # ── 主体 ──
        body = ctk.CTkFrame(outer, fg_color="#0a0a0a")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        # 选择行：分类 + 战备
        sel_frame = ctk.CTkFrame(body, fg_color="#1a1a1a", corner_radius=8)
        sel_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            sel_frame, text="分类:",
            text_color="#AAAAAA", font=("Microsoft YaHei", 11)
        ).grid(row=0, column=0, padx=(15, 5), pady=12, sticky="w")

        all_cats = list(STRATAGEM_CATEGORIES.keys())
        self.category_menu = ctk.CTkOptionMenu(
            sel_frame, values=all_cats,
            command=self._on_category_selected,
            width=140,
            fg_color="#2a2a2a", button_color="#FFD700",
            button_hover_color="#FFDD55", text_color="#FFFFFF",
            dropdown_fg_color="#2a2a2a", dropdown_text_color="#FFFFFF",
            font=("Microsoft YaHei", 11)
        )
        self.category_menu.grid(row=0, column=1, padx=(0, 20), pady=12)

        ctk.CTkLabel(
            sel_frame, text="战备:",
            text_color="#AAAAAA", font=("Microsoft YaHei", 11)
        ).grid(row=0, column=2, padx=(0, 5), pady=12, sticky="w")

        self.item_menu = ctk.CTkOptionMenu(
            sel_frame, values=["── 新增战备 ──"],
            command=self._on_item_selected,
            width=200,
            fg_color="#2a2a2a", button_color="#FFD700",
            button_hover_color="#FFDD55", text_color="#FFFFFF",
            dropdown_fg_color="#2a2a2a", dropdown_text_color="#FFFFFF",
            font=("Microsoft YaHei", 11)
        )
        self.item_menu.grid(row=0, column=3, padx=(0, 15), pady=12)

        # ── 编辑表单 ──
        form = ctk.CTkFrame(body, fg_color="#1a1a1a", corner_radius=8)
        form.pack(fill="both", expand=True, pady=(0, 15))

        # 名称
        ctk.CTkLabel(
            form, text="名称:",
            text_color="#AAAAAA", font=("Microsoft YaHei", 11)
        ).pack(anchor="w", padx=15, pady=(15, 3))

        self.item_name_entry = ctk.CTkEntry(
            form,
            placeholder_text="输入战备名称",
            fg_color="#2a2a2a", text_color="#FFFFFF",
            border_color="#444444", placeholder_text_color="#666666",
            font=("Microsoft YaHei", 12), height=36
        )
        self.item_name_entry.pack(fill="x", padx=15, pady=(0, 15))

        # 别名目标（仅别名模式显示）
        self.alias_target_frame = ctk.CTkFrame(form, fg_color="#1a1a1a")
        ctk.CTkLabel(
            self.alias_target_frame, text="指向战备:",
            text_color="#AAAAAA", font=("Microsoft YaHei", 11)
        ).pack(anchor="w", padx=0, pady=(0, 3))
        all_war_names = sorted(self.data.get("stratagems", {}).keys())
        self.alias_target_menu = ctk.CTkOptionMenu(
            self.alias_target_frame,
            values=all_war_names if all_war_names else ["无"],
            width=250,
            fg_color="#2a2a2a", button_color="#FFD700",
            button_hover_color="#FFDD55", text_color="#FFFFFF",
            dropdown_fg_color="#2a2a2a", dropdown_text_color="#FFFFFF",
            font=("Microsoft YaHei", 11)
        )
        self.alias_target_menu.pack(anchor="w", padx=0)

        # 指令录制区域（仅战备模式）
        self.keys_frame = ctk.CTkFrame(form, fg_color="#1a1a1a")
        self.keys_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(
            self.keys_frame, text="指令序列:",
            text_color="#AAAAAA", font=("Microsoft YaHei", 11)
        ).pack(anchor="w", pady=(0, 5))

        # 按键显示框
        self.keys_display = ctk.CTkLabel(
            self.keys_frame,
            text="请点击\"开始录制\"后按下按键",
            text_color="#888888",
            font=("Microsoft YaHei", 13),
            fg_color="#2a2a2a",
            corner_radius=6,
            padx=12, pady=14,
            anchor="w"
        )
        self.keys_display.pack(fill="x", pady=(0, 10))

        rec_row = ctk.CTkFrame(self.keys_frame, fg_color="#1a1a1a")
        rec_row.pack(fill="x")

        self.record_btn = ctk.CTkButton(
            rec_row, text="⏺  开始录制",
            command=self._on_record_toggle,
            width=120, height=32,
            fg_color="#4CAF50", hover_color="#66BB6A",
            text_color="#FFFFFF", font=("Microsoft YaHei", 11)
        )
        self.record_btn.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            rec_row, text="清除",
            command=self._on_clear_keys,
            width=70, height=32,
            fg_color="#555555", hover_color="#666666",
            text_color="#FFFFFF", font=("Microsoft YaHei", 11)
        ).pack(side="left")

        # ── 操作按钮 ──
        btn_row = ctk.CTkFrame(body, fg_color="#0a0a0a")
        btn_row.pack(fill="x")

        ctk.CTkButton(
            btn_row, text="保存",
            command=self._on_save,
            width=100, height=36,
            fg_color="#FFD700", hover_color="#FFDD55",
            text_color="#000000", font=("Microsoft YaHei", 12, "bold")
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row, text="删除",
            command=self._on_delete,
            width=100, height=36,
            fg_color="#C62828", hover_color="#EF5350",
            text_color="#FFFFFF", font=("Microsoft YaHei", 12)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row, text="新增",
            command=self._on_new,
            width=100, height=36,
            fg_color="#1565C0", hover_color="#1E88E5",
            text_color="#FFFFFF", font=("Microsoft YaHei", 12)
        ).pack(side="left", padx=(0, 20))

        self.status_label = ctk.CTkLabel(
            btn_row, text="",
            text_color="#4CAF50",
            font=("Microsoft YaHei", 11)
        )
        self.status_label.pack(side="left")

        # 初始化分类列表
        self._on_category_selected(all_cats[0])

    # ───────────────────────── 模式切换 ─────────────────────────

    def _switch_mode(self, mode: str):
        self.edit_mode = mode
        self._stop_recording()
        self._clear_form()

        if mode == "战备":
            self.tab_war_btn.configure(fg_color="#FFD700", text_color="#000000")
            self.tab_alias_btn.configure(fg_color="#333333", text_color="#AAAAAA")
            self.category_menu.configure(state="normal")
            self.keys_frame.pack(fill="x", padx=15, pady=(0, 15))
            self.alias_target_frame.pack_forget()
            # 重新填充分类
            all_cats = list(STRATAGEM_CATEGORIES.keys())
            self.category_menu.configure(values=all_cats)
            self._on_category_selected(all_cats[0])
        else:
            self.tab_war_btn.configure(fg_color="#333333", text_color="#AAAAAA")
            self.tab_alias_btn.configure(fg_color="#FFD700", text_color="#000000")
            self.category_menu.configure(state="disabled")
            self.keys_frame.pack_forget()
            self.alias_target_frame.pack(fill="x", padx=15, pady=(0, 15))
            # 填充别名列表
            aliases = list(self.data.get("aliases", {}).keys())
            self.item_menu.configure(values=["── 新增别名 ──"] + aliases)
            self.item_menu.set("── 新增别名 ──")

    # ───────────────────────── 选择事件 ─────────────────────────

    def _on_category_selected(self, category: str):
        """切换分类时刷新战备列表"""
        items = self._get_items_in_category(category)
        values = ["── 新增战备 ──"] + items
        self.item_menu.configure(values=values)
        self.item_menu.set("── 新增战备 ──")
        self._clear_form()

    def _on_item_selected(self, item_name: str):
        """选择条目时填充表单"""
        if item_name.startswith("──"):
            self._clear_form()
            return

        self.current_item_name = item_name
        self.item_name_entry.delete(0, "end")
        self.item_name_entry.insert(0, item_name)

        if self.edit_mode == "战备":
            keys = self.data.get("stratagems", {}).get(item_name, [])
            self.recorded_keys = list(keys)
            self._update_keys_display()
        else:
            target = self.data.get("aliases", {}).get(item_name, "")
            all_war = sorted(self.data.get("stratagems", {}).keys())
            self.alias_target_menu.configure(values=all_war if all_war else ["无"])
            if target in all_war:
                self.alias_target_menu.set(target)

    # ───────────────────────── 键盘录制 ─────────────────────────

    def _on_record_toggle(self):
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        self.is_recording = True
        self.recorded_keys = []
        self.record_btn.configure(text="⏹  停止录制", fg_color="#F44336", hover_color="#EF5350")
        self._update_keys_display()
        self._set_status("正在录制，请按下按键...", "#FF9800")

        def on_press(key):
            if not self.is_recording:
                return False
            try:
                if hasattr(key, 'char') and key.char:
                    k = key.char.upper()
                else:
                    k = key.name.upper()
                # 规范化方向键
                k = {"UP": "W", "DOWN": "S", "LEFT": "A", "RIGHT": "D"}.get(k, k)
                self.recorded_keys.append(k)
                # 在主线程更新 UI
                self.parent.after(0, self._update_keys_display)
            except Exception:
                pass

        self.listener = pynput_keyboard.Listener(on_press=on_press)
        self.listener.start()

    def _stop_recording(self):
        self.is_recording = False
        if self.listener:
            self.listener.stop()
            self.listener = None
        if self.record_btn:
            self.record_btn.configure(text="⏺  开始录制", fg_color="#4CAF50", hover_color="#66BB6A")
        if self.recorded_keys:
            self._set_status(f"已录制 {len(self.recorded_keys)} 个按键", "#4CAF50")
        else:
            self._set_status("", "#AAAAAA")

    def _update_keys_display(self):
        if self.recorded_keys:
            display = "  →  ".join(self.recorded_keys)
            self.keys_display.configure(text=display, text_color="#FFD700")
        else:
            self.keys_display.configure(
                text="请点击\"开始录制\"后按下按键",
                text_color="#888888"
            )

    def _on_clear_keys(self):
        self._stop_recording()
        self.recorded_keys = []
        self._update_keys_display()

    # ───────────────────────── 增删改 ─────────────────────────

    def _on_new(self):
        """清空表单，准备新增"""
        self._stop_recording()
        self._clear_form()
        self._set_status("请输入名称并录制指令", "#2196F3")

    def _on_save(self):
        """保存当前表单"""
        name = self.item_name_entry.get().strip()
        if not name:
            self._set_status("名称不能为空", "#F44336")
            return

        if self.edit_mode == "战备":
            if not self.recorded_keys:
                self._set_status("指令序列不能为空", "#F44336")
                return
            # 重命名处理
            if self.current_item_name and self.current_item_name != name:
                self.data["stratagems"].pop(self.current_item_name, None)
            self.data.setdefault("stratagems", {})[name] = self.recorded_keys
            self._save_data()
            self.current_item_name = name
            # 判断该战备属于哪个分类
            target_cat = self._get_category_for(name)
            # 如果不在任何已知分类，归入未分类
            if target_cat == "未分类":
                STRATAGEM_CATEGORIES["未分类"] = [
                    n for n in self.data.get("stratagems", {})
                    if self._get_category_for(n) == "未分类"
                ]
                all_cats = list(STRATAGEM_CATEGORIES.keys())
                self.category_menu.configure(values=all_cats)
            # 切换到对应分类并选中该战备
            self.category_menu.set(target_cat)
            self._on_category_selected(target_cat)
            # 找到后在列表中选中
            items = self._get_items_in_category(target_cat)
            values = ["── 新增战备 ──"] + items
            self.item_menu.configure(values=values)
            if name in items:
                self.item_menu.set(name)
        else:
            target = self.alias_target_menu.get()
            if not target or target == "无":
                self._set_status("请选择指向的战备", "#F44336")
                return
            if self.current_item_name and self.current_item_name != name:
                self.data["aliases"].pop(self.current_item_name, None)
            self.data.setdefault("aliases", {})[name] = target
            self._save_data()
            self.current_item_name = name
            # 刷新列表
            aliases = list(self.data.get("aliases", {}).keys())
            self.item_menu.configure(values=["── 新增别名 ──"] + aliases)
            self.item_menu.set(name)

    def _on_delete(self):
        """删除当前选中条目"""
        if not self.current_item_name:
            self._set_status("请先选择要删除的条目", "#F44336")
            return
        if self.edit_mode == "战备":
            self.data.get("stratagems", {}).pop(self.current_item_name, None)
            self._save_data()
            cat = self.category_menu.get()
            self._on_category_selected(cat)
        else:
            self.data.get("aliases", {}).pop(self.current_item_name, None)
            self._save_data()
            aliases = list(self.data.get("aliases", {}).keys())
            self.item_menu.configure(values=["── 新增别名 ──"] + aliases)
        self._clear_form()

    # ───────────────────────── 辅助 ─────────────────────────

    def _clear_form(self):
        self.current_item_name = None
        if self.item_name_entry:
            self.item_name_entry.delete(0, "end")
        self.recorded_keys = []
        if self.keys_display:
            self._update_keys_display()

    def _set_status(self, msg: str, color: str = "#AAAAAA"):
        if self.status_label:
            self.status_label.configure(text=msg, text_color=color)
 