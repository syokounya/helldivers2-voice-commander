"""
GUI 战备指令编辑器 Tab
"""
import customtkinter as ctk
from typing import Callable, Optional, Dict, List
import json
from pynput import keyboard as pynput_keyboard


# 模块级分类字典 —— 由 StratagemManager 在运行时填充，不硬编码任何战备名
STRATAGEM_CATEGORIES: Dict[str, List[str]] = {}
GLOBAL_CATEGORY: str = "任务类"


class StratagemEditorTab:
    def __init__(self, parent, stratagem_names, json_path="stratagems.json",
                 on_save_callback=None, stratagem_manager=None):
        self.parent = parent
        self.stratagem_names = stratagem_names
        self.json_path = json_path
        self.on_save_callback = on_save_callback
        self.stratagem_manager = stratagem_manager
        self.data: Dict = {}
        self.current_item_name: Optional[str] = None
        self.edit_mode: str = "战备"
        self.is_recording = False
        self.recorded_keys: List[str] = []
        self.listener = None
        self.tab_war_btn = None
        self.tab_alias_btn = None
        self.category_menu = None
        self.target_cat_menu = None
        self.target_cat_frame = None
        self.item_menu = None
        self.item_name_entry = None
        self.alias_target_menu = None
        self.alias_target_frame = None
        self.keys_frame = None
        self.keys_display = None
        self.record_btn = None
        self.status_label = None
        self._load_data()
        # 用 StratagemManager 的分类数据初始化模块级字典（零硬编码）
        self._sync_categories_from_manager()
        self._build()

    def _sync_categories_from_manager(self):
        """从 StratagemManager 同步分类数据到模块级 STRATAGEM_CATEGORIES"""
        global STRATAGEM_CATEGORIES, GLOBAL_CATEGORY
        if self.stratagem_manager and hasattr(self.stratagem_manager, 'categories') \
                and self.stratagem_manager.categories:
            STRATAGEM_CATEGORIES.clear()
            STRATAGEM_CATEGORIES.update(self.stratagem_manager.categories)
            GLOBAL_CATEGORY = self.stratagem_manager.global_category

    def _load_data(self):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception:
            self.data = {"stratagems": {}, "aliases": {}}

    def _save_data(self):
        try:
            # 把当前分类数据也写回 JSON
            self.data['categories'] = {k: list(v) for k, v in STRATAGEM_CATEGORIES.items()}
            self.data['global_category'] = GLOBAL_CATEGORY
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            if self.on_save_callback:
                self.on_save_callback(self.json_path)
            self._set_status("保存成功", "#4CAF50")
        except Exception as e:
            self._set_status(f"保存失败: {e}", "#F44336")

    def _get_category_for(self, name: str) -> str:
        for cat, members in STRATAGEM_CATEGORIES.items():
            if name in members:
                return cat
        return "未分类"

    def _get_items_in_category(self, category: str) -> List[str]:
        stratagems = self.data.get("stratagems", {})
        if category == "未分类":
            known = set(n for names in STRATAGEM_CATEGORIES.values() for n in names)
            return [n for n in stratagems if n not in known]
        return [n for n in STRATAGEM_CATEGORIES.get(category, []) if n in stratagems]

    def _all_category_names(self) -> List[str]:
        cats = list(STRATAGEM_CATEGORIES.keys())
        stratagems = self.data.get("stratagems", {})
        known = set(n for names in STRATAGEM_CATEGORIES.values() for n in names)
        if any(n not in known for n in stratagems):
            if "未分类" not in cats:
                cats.append("未分类")
        return cats

    def _build(self):
        outer = ctk.CTkFrame(self.parent, fg_color="#000000")
        outer.pack(fill="both", expand=True)
        header = ctk.CTkFrame(outer, fg_color="#111111", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="战备指令编辑器",
                     font=("Microsoft YaHei", 20, "bold"),
                     text_color="#FFD700").pack(side="left", padx=20)
        bf = ctk.CTkFrame(header, fg_color="#111111")
        bf.pack(side="right", padx=20)
        self.tab_war_btn = ctk.CTkButton(bf, text="编辑战备",
            command=lambda: self._switch_mode("战备"),
            width=90, height=30, fg_color="#FFD700", text_color="#000000",
            hover_color="#FFDD55", font=("Microsoft YaHei", 11))
        self.tab_war_btn.pack(side="left", padx=(0, 5))
        self.tab_alias_btn = ctk.CTkButton(bf, text="编辑别名",
            command=lambda: self._switch_mode("别名"),
            width=90, height=30, fg_color="#333333", text_color="#AAAAAA",
            hover_color="#444444", font=("Microsoft YaHei", 11))
        self.tab_alias_btn.pack(side="left")
        body = ctk.CTkFrame(outer, fg_color="#0a0a0a")
        body.pack(fill="both", expand=True, padx=20, pady=20)
        sel = ctk.CTkFrame(body, fg_color="#1a1a1a", corner_radius=8)
        sel.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(sel, text="分类:", text_color="#AAAAAA",
                     font=("Microsoft YaHei", 11)).grid(row=0, column=0, padx=(15, 5), pady=12)
        all_cats = self._all_category_names()
        self.category_menu = ctk.CTkOptionMenu(sel, values=all_cats,
            command=self._on_category_selected, width=140,
            fg_color="#2a2a2a", button_color="#FFD700", button_hover_color="#FFDD55",
            text_color="#FFFFFF", dropdown_fg_color="#2a2a2a",
            dropdown_text_color="#FFFFFF", font=("Microsoft YaHei", 11))
        self.category_menu.grid(row=0, column=1, padx=(0, 20), pady=12)
        ctk.CTkLabel(sel, text="战备:", text_color="#AAAAAA",
                     font=("Microsoft YaHei", 11)).grid(row=0, column=2, padx=(0, 5), pady=12)
        self.item_menu = ctk.CTkOptionMenu(sel, values=["── 新增战备 ──"],
            command=self._on_item_selected, width=200,
            fg_color="#2a2a2a", button_color="#FFD700", button_hover_color="#FFDD55",
            text_color="#FFFFFF", dropdown_fg_color="#2a2a2a",
            dropdown_text_color="#FFFFFF", font=("Microsoft YaHei", 11))
        self.item_menu.grid(row=0, column=3, padx=(0, 15), pady=12)
        form = ctk.CTkFrame(body, fg_color="#1a1a1a", corner_radius=8)
        form.pack(fill="both", expand=True, pady=(0, 15))
        ctk.CTkLabel(form, text="名称:", text_color="#AAAAAA",
                     font=("Microsoft YaHei", 11)).pack(anchor="w", padx=15, pady=(15, 3))
        self.item_name_entry = ctk.CTkEntry(form, placeholder_text="输入战备名称",
            fg_color="#2a2a2a", text_color="#FFFFFF", border_color="#444444",
            placeholder_text_color="#666666", font=("Microsoft YaHei", 12), height=36)
        self.item_name_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.target_cat_frame = ctk.CTkFrame(form, fg_color="#1a1a1a")
        ctk.CTkLabel(self.target_cat_frame, text="添加到分类:",
                     text_color="#AAAAAA", font=("Microsoft YaHei", 11)).pack(side="left", padx=(0, 10))
        self.target_cat_menu = ctk.CTkOptionMenu(self.target_cat_frame,
            values=list(STRATAGEM_CATEGORIES.keys()), width=160,
            fg_color="#2a2a2a", button_color="#FFD700", button_hover_color="#FFDD55",
            text_color="#FFFFFF", dropdown_fg_color="#2a2a2a",
            dropdown_text_color="#FFFFFF", font=("Microsoft YaHei", 11))
        self.target_cat_menu.pack(side="left")
        self.alias_target_frame = ctk.CTkFrame(form, fg_color="#1a1a1a")
        ctk.CTkLabel(self.alias_target_frame, text="指向战备:",
                     text_color="#AAAAAA", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=(0, 3))
        all_war = sorted(self.data.get("stratagems", {}).keys())
        self.alias_target_menu = ctk.CTkOptionMenu(self.alias_target_frame,
            values=all_war if all_war else ["无"], width=250,
            fg_color="#2a2a2a", button_color="#FFD700", button_hover_color="#FFDD55",
            text_color="#FFFFFF", dropdown_fg_color="#2a2a2a",
            dropdown_text_color="#FFFFFF", font=("Microsoft YaHei", 11))
        self.alias_target_menu.pack(anchor="w")
        self.keys_frame = ctk.CTkFrame(form, fg_color="#1a1a1a")
        self.keys_frame.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkLabel(self.keys_frame, text="指令序列:", text_color="#AAAAAA",
                     font=("Microsoft YaHei", 11)).pack(anchor="w", pady=(0, 5))
        self.keys_display = ctk.CTkLabel(self.keys_frame,
            text="请点击\"开始录制\"后按下按键", text_color="#888888",
            font=("Microsoft YaHei", 13), fg_color="#2a2a2a",
            corner_radius=6, padx=12, pady=14, anchor="w")
        self.keys_display.pack(fill="x", pady=(0, 10))
        rec_row = ctk.CTkFrame(self.keys_frame, fg_color="#1a1a1a")
        rec_row.pack(fill="x")
        self.record_btn = ctk.CTkButton(rec_row, text="⏺  开始录制",
            command=self._on_record_toggle, width=120, height=32,
            fg_color="#4CAF50", hover_color="#66BB6A",
            text_color="#FFFFFF", font=("Microsoft YaHei", 11))
        self.record_btn.pack(side="left", padx=(0, 10))
        ctk.CTkButton(rec_row, text="清除", command=self._on_clear_keys,
            width=70, height=32, fg_color="#555555", hover_color="#666666",
            text_color="#FFFFFF", font=("Microsoft YaHei", 11)).pack(side="left")
        btn_row = ctk.CTkFrame(body, fg_color="#0a0a0a")
        btn_row.pack(fill="x")
        ctk.CTkButton(btn_row, text="保存", command=self._on_save,
            width=100, height=36, fg_color="#FFD700", hover_color="#FFDD55",
            text_color="#000000", font=("Microsoft YaHei", 12, "bold")).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="删除", command=self._on_delete,
            width=100, height=36, fg_color="#C62828", hover_color="#EF5350",
            text_color="#FFFFFF", font=("Microsoft YaHei", 12)).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="新增", command=self._on_new,
            width=100, height=36, fg_color="#1565C0", hover_color="#1E88E5",
            text_color="#FFFFFF", font=("Microsoft YaHei", 12)).pack(side="left", padx=(0, 20))
        self.status_label = ctk.CTkLabel(btn_row, text="",
            text_color="#4CAF50", font=("Microsoft YaHei", 11))
        self.status_label.pack(side="left")
        self._on_category_selected(all_cats[0])

    # ─── 模式切换 ───

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
            all_cats = self._all_category_names()
            self.category_menu.configure(values=all_cats)
            self._on_category_selected(all_cats[0])
        else:
            self.tab_war_btn.configure(fg_color="#333333", text_color="#AAAAAA")
            self.tab_alias_btn.configure(fg_color="#FFD700", text_color="#000000")
            self.category_menu.configure(state="disabled")
            self.keys_frame.pack_forget()
            self.target_cat_frame.pack_forget()
            self.alias_target_frame.pack(fill="x", padx=15, pady=(0, 15))
            aliases = list(self.data.get("aliases", {}).keys())
            self.item_menu.configure(values=["── 新增别名 ──"] + aliases)
            self.item_menu.set("── 新增别名 ──")

    # ─── 选择事件 ───

    def _on_category_selected(self, category: str):
        items = self._get_items_in_category(category)
        self.item_menu.configure(values=["── 新增战备 ──"] + items)
        self.item_menu.set("── 新增战备 ──")
        self._clear_form()

    def _on_item_selected(self, item_name: str):
        if item_name.startswith("──"):
            self._clear_form()
            return
        self.current_item_name = item_name
        self.item_name_entry.delete(0, "end")
        self.item_name_entry.insert(0, item_name)
        self.target_cat_frame.pack_forget()
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

    # ─── 键盘录制 ───

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
                k = {"UP": "W", "DOWN": "S", "LEFT": "A", "RIGHT": "D"}.get(k, k)
                self.recorded_keys.append(k)
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
            self.keys_display.configure(text="  →  ".join(self.recorded_keys), text_color="#FFD700")
        else:
            self.keys_display.configure(text="请点击\"开始录制\"后按下按键", text_color="#888888")

    def _on_clear_keys(self):
        self._stop_recording()
        self.recorded_keys = []
        self._update_keys_display()

    # ─── 增删改 ───

    def _on_new(self):
        self._stop_recording()
        self._clear_form()
        if self.edit_mode == "战备":
            self.target_cat_menu.configure(values=list(STRATAGEM_CATEGORIES.keys()))
            self.target_cat_menu.set(self.category_menu.get()
                                     if self.category_menu.get() != "未分类"
                                     else list(STRATAGEM_CATEGORIES.keys())[0])
            self.target_cat_frame.pack(fill="x", padx=15, pady=(0, 15),
                                       before=self.keys_frame)
        self._set_status("请输入名称并录制指令", "#2196F3")

    def _on_save(self):
        name = self.item_name_entry.get().strip()
        if not name:
            self._set_status("名称不能为空", "#F44336")
            return
        if self.edit_mode == "战备":
            if not self.recorded_keys:
                self._set_status("指令序列不能为空", "#F44336")
                return
            is_new = not self.current_item_name
            old_name = self.current_item_name
            # 重命名：在分类字典中替换名称
            if old_name and old_name != name:
                old_cat = self._get_category_for(old_name)
                if old_cat != "未分类" and old_name in STRATAGEM_CATEGORIES.get(old_cat, []):
                    idx = STRATAGEM_CATEGORIES[old_cat].index(old_name)
                    STRATAGEM_CATEGORIES[old_cat][idx] = name
                self.data["stratagems"].pop(old_name, None)
            # 新增：加入用户选择的目标分类
            if is_new:
                tgt = (self.target_cat_menu.get()
                       if self.target_cat_frame.winfo_ismapped()
                       else self.category_menu.get())
                if tgt and tgt != "未分类":
                    if name not in STRATAGEM_CATEGORIES.get(tgt, []):
                        STRATAGEM_CATEGORIES.setdefault(tgt, []).append(name)
            self.data.setdefault("stratagems", {})[name] = self.recorded_keys
            self._save_data()
            self.current_item_name = name
            all_cats = self._all_category_names()
            self.category_menu.configure(values=all_cats)
            target_cat = self._get_category_for(name)
            self.category_menu.set(target_cat)
            items = self._get_items_in_category(target_cat)
            self.item_menu.configure(values=["── 新增战备 ──"] + items)
            if name in items:
                self.item_menu.set(name)
            self.target_cat_frame.pack_forget()
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
            aliases = list(self.data.get("aliases", {}).keys())
            self.item_menu.configure(values=["── 新增别名 ──"] + aliases)
            self.item_menu.set(name)

    def _on_delete(self):
        if not self.current_item_name:
            self._set_status("请先选择要删除的条目", "#F44336")
            return
        if self.edit_mode == "战备":
            old_cat = self._get_category_for(self.current_item_name)
            if old_cat != "未分类" and self.current_item_name in STRATAGEM_CATEGORIES.get(old_cat, []):
                STRATAGEM_CATEGORIES[old_cat].remove(self.current_item_name)
            self.data.get("stratagems", {}).pop(self.current_item_name, None)
            self._save_data()
            all_cats = self._all_category_names()
            self.category_menu.configure(values=all_cats)
            self._on_category_selected(self.category_menu.get())
        else:
            self.data.get("aliases", {}).pop(self.current_item_name, None)
            self._save_data()
            aliases = list(self.data.get("aliases", {}).keys())
            self.item_menu.configure(values=["── 新增别名 ──"] + aliases)
        self._clear_form()

    # ─── 辅助 ───

    def _clear_form(self):
        self.current_item_name = None
        if self.item_name_entry:
            self.item_name_entry.delete(0, "end")
        self.recorded_keys = []
        if self.keys_display:
            self._update_keys_display()
        if self.target_cat_frame:
            self.target_cat_frame.pack_forget()

    def _set_status(self, msg: str, color: str = "#AAAAAA"):
        if self.status_label:
            self.status_label.configure(text=msg, text_color=color)
