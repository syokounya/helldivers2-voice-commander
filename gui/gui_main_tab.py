"""
GUI 主界面 Tab
"""
import customtkinter as ctk
from typing import List, Callable, Dict


class MainTab:
    """主界面 Tab —— 完全通过 stratagem_manager 联动，零硬编码"""

    def __init__(
        self,
        parent,
        stratagem_names: List[str],
        active_slots: List[str],
        available_global_commands: List[str],
        enabled_global_commands: set,
        on_slot_changed: Callable[[int, str], None],
        on_global_command_toggled: Callable[[str, bool], None],
        on_toggle_engine: Callable[[], None],
        stratagem_manager=None,
    ):
        self.parent = parent
        self.stratagem_names = sorted(stratagem_names)
        self.active_slots = list(active_slots)
        self.available_global_commands = list(available_global_commands)
        self.enabled_global_commands = enabled_global_commands
        self.on_slot_changed = on_slot_changed
        self.on_global_command_toggled = on_global_command_toggled
        self.on_toggle_engine = on_toggle_engine
        self._sm = stratagem_manager

        if self._sm and getattr(self._sm, 'categories', None):
            self._cats = self._sm.categories
            self._global_cat = self._sm.global_category
            self._eagle_rearm = self._sm.eagle_rearm_name
        else:
            self._cats = {}
            self._global_cat = ""
            self._eagle_rearm = ""

        self._slot_cats = [c for c in self._cats if c != self._global_cat]

        self.slot_vars: List[ctk.StringVar] = []
        self.slot_category_vars: List[ctk.StringVar] = []
        self.slot_frames: List[ctk.CTkFrame] = []
        self.slot_menus: List[ctk.CTkOptionMenu] = []
        self.slot_category_menus: List[ctk.CTkOptionMenu] = []
        self.global_command_vars: Dict[str, ctk.BooleanVar] = {}
        self.toggle_button: ctk.CTkButton = None
        self.log_text: ctk.CTkTextbox = None
        self.status_label: ctk.CTkLabel = None
        self.status_detail_text: ctk.CTkTextbox = None
        self.scroll_frame = None

        self._build()

    def _build(self):
        mc = ctk.CTkFrame(self.parent, fg_color="#000000")
        mc.pack(fill="both", expand=True)
        mc.grid_rowconfigure(0, weight=1)
        mc.grid_columnconfigure(0, weight=3)
        mc.grid_columnconfigure(1, weight=1)

        lf = ctk.CTkFrame(mc, fg_color="#111111")
        lf.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        lf.grid_rowconfigure(0, weight=1)
        lf.grid_columnconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(
            lf, fg_color="#111111",
            scrollbar_button_color="#FFD700",
            scrollbar_button_hover_color="#FFDD55",
        )
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self._bind_scroll(self.scroll_frame)

        self._build_global_commands(self.scroll_frame)
        sep = ctk.CTkFrame(self.scroll_frame, height=2, fg_color="#333333")
        sep.grid(row=100, column=0, sticky="ew", padx=10, pady=15)
        self._build_slot_config(self.scroll_frame)

        rf = ctk.CTkFrame(mc, fg_color="#111111")
        rf.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        rf.grid_rowconfigure(3, weight=1)
        rf.grid_columnconfigure(0, weight=1)

        self.toggle_button = ctk.CTkButton(
            rf, text="开始监听", command=self.on_toggle_engine,
            fg_color="#FFD700", hover_color="#FFDD55", text_color="#000000",
            height=50, font=("Arial", 14, "bold"),
        )
        self.toggle_button.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        sf2 = ctk.CTkFrame(rf, fg_color="#1a1a1a", corner_radius=8)
        sf2.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        sf2.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(sf2, text="阿里云服务状态：", text_color="#FFFFFF",
                     anchor="w", font=("Arial", 11, "bold")
                     ).grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.status_label = ctk.CTkLabel(sf2, text="● 未连接", text_color="#888888",
                                          anchor="w", font=("Arial", 11, "bold"))
        self.status_label.grid(row=0, column=1, sticky="w", padx=5, pady=8)
        self.status_detail_text = ctk.CTkTextbox(
            sf2, wrap="word", fg_color="#0a0a0a",
            text_color="#FF6B6B", font=("Consolas", 9), height=80)
        self.status_detail_text.grid(row=1, column=0, columnspan=2,
                                      sticky="ew", padx=10, pady=(0, 10))
        self.status_detail_text.configure(state="disabled")
        self.status_detail_text.grid_remove()

        ctk.CTkLabel(rf, text="语音识别日志：", text_color="#FFFFFF",
                     anchor="w", font=("Arial", 12, "bold")
                     ).grid(row=2, column=0, sticky="w", padx=10, pady=(10, 5))
        self.log_text = ctk.CTkTextbox(
            rf, wrap="word", fg_color="#000000",
            text_color="#FFFFFF", font=("Consolas", 10))
        self.log_text.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.log_text.configure(state="disabled")

    def _bind_scroll(self, frame):
        """为 CTkScrollableFrame 及其所有子控件绑定快速鼠标滚轮"""
        def _on_mousewheel(event):
            frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 30)), "units")

        def _bind_to_widget(widget):
            widget.bind("<MouseWheel>", _on_mousewheel, add="+")
            for child in widget.winfo_children():
                _bind_to_widget(child)

        frame.bind("<MouseWheel>", _on_mousewheel, add="+")
        frame._parent_canvas.bind("<MouseWheel>", _on_mousewheel, add="+")
        _bind_to_widget(frame)

        # 当新子控件被添加时也自动绑定
        frame.bind("<Configure>", lambda e: _bind_to_widget(frame), add="+")

    def _build_global_commands(self, parent):
        parent.grid_columnconfigure(0, weight=1, uniform="gc")
        parent.grid_columnconfigure(1, weight=1, uniform="gc")
        parent.grid_columnconfigure(2, weight=1, uniform="gc")
        ctk.CTkLabel(parent, text="任务全局指令", text_color="#FFD700",
                     anchor="w", font=("Arial", 18, "bold")
                     ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))
        if self._eagle_rearm:
            ctk.CTkLabel(
                parent,
                text=f"💡 提示：【{self._eagle_rearm}】会根据槽位中的飞鹰战备自动启用/禁用",
                text_color="#888888", anchor="w", font=("Arial", 12),
                wraplength=600, justify="left",
            ).grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 5))
        self._render_global_checkboxes(parent, start_row=2)

    def _render_global_checkboxes(self, parent, start_row: int = 1):
        row, col = start_row, 0
        for cmd in self.available_global_commands:
            if cmd == self._eagle_rearm:
                continue
            if cmd not in self.global_command_vars:
                self.global_command_vars[cmd] = ctk.BooleanVar(
                    value=(cmd in self.enabled_global_commands))
            var = self.global_command_vars[cmd]
            cb = ctk.CTkCheckBox(
                parent, text=cmd, variable=var,
                command=lambda c=cmd, v=var: self.on_global_command_toggled(c, v.get()),
                text_color="#FFFFFF", fg_color="#FFD700",
                border_color="#FFD700", hover_color="#FFDD55",
                font=("Arial", 13), checkbox_width=24, checkbox_height=24,
            )
            cb.grid(row=row, column=col, sticky="w", padx=15, pady=10)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _build_slot_config(self, parent):
        ctk.CTkLabel(parent, text="本局战备配置（4个槽位）",
                     text_color="#FFD700", anchor="w",
                     font=("Arial", 18, "bold")
                     ).grid(row=200, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 10))

        self.slot_frames = []
        self.slot_menus = []
        self.slot_category_menus = []
        self.slot_vars = []
        self.slot_category_vars = []

        slot_cats = self._slot_cats or list(self._cats.keys())
        default_cat = slot_cats[0] if slot_cats else ""

        for i in range(4):
            sf = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=8)
            sf.grid(row=201 + i, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
            sf.grid_columnconfigure(2, weight=1)
            self.slot_frames.append(sf)

            ctk.CTkLabel(sf, text=f"槽位 {i + 1}",
                         text_color="#FFD700", font=("Arial", 14, "bold"),
                         width=80).grid(row=0, column=0, padx=15, pady=12)

            cur_val = self.active_slots[i] if i < len(self.active_slots) else ""
            cur_cat = default_cat
            for cat, items in self._cats.items():
                if cur_val in items and cat != self._global_cat:
                    cur_cat = cat
                    break

            cat_var = ctk.StringVar(value=cur_cat)
            cat_menu = ctk.CTkOptionMenu(
                sf, variable=cat_var,
                values=slot_cats if slot_cats else [""],
                command=lambda val, idx=i: self._on_category_changed(idx, val),
                fg_color="#FFD700", button_color="#FFDD55",
                button_hover_color="#FFE680", text_color="#000000",
                dropdown_fg_color="#FFD700", dropdown_text_color="#000000",
                width=120,
            )
            cat_menu.grid(row=0, column=1, padx=10, pady=12)
            self.slot_category_menus.append(cat_menu)
            self.slot_category_vars.append(cat_var)

            items = ["无"] + self._cats.get(cur_cat, [])
            slot_var = ctk.StringVar(value=cur_val if cur_val else "无")
            slot_menu = ctk.CTkOptionMenu(
                sf, variable=slot_var, values=items,
                command=lambda val, idx=i: self._on_slot_menu_changed(idx, val),
                fg_color="#333333", button_color="#444444",
                button_hover_color="#555555", text_color="#FFFFFF",
                dropdown_fg_color="#333333", dropdown_text_color="#FFFFFF",
            )
            slot_menu.grid(row=0, column=2, padx=10, pady=12, sticky="ew")
            self.slot_vars.append(slot_var)
            self.slot_menus.append(slot_menu)

    # ─── 事件回调 ───

    def _on_category_changed(self, slot_index: int, category: str):
        items = ["无"] + self._cats.get(category, [])
        old_menu = self.slot_menus[slot_index]
        sf = self.slot_frames[slot_index]
        slot_var = self.slot_vars[slot_index]
        slot_var.set("无")
        old_menu.destroy()
        new_menu = ctk.CTkOptionMenu(
            sf, variable=slot_var, values=items,
            command=lambda val, idx=slot_index: self._on_slot_menu_changed(idx, val),
            fg_color="#333333", button_color="#444444",
            button_hover_color="#555555", text_color="#FFFFFF",
            dropdown_fg_color="#333333", dropdown_text_color="#FFFFFF",
        )
        new_menu.grid(row=0, column=2, padx=10, pady=12, sticky="ew")
        self.slot_menus[slot_index] = new_menu
        self._on_slot_menu_changed(slot_index, "无")

    def _on_slot_menu_changed(self, slot_index: int, value: str):
        self.on_slot_changed(slot_index, "" if value == "无" else value)

    # ─── 公开方法 ───

    def append_log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        try:
            line_count = int(self.log_text.index("end-1c").split(".")[0])
            if line_count > 1000:
                self.log_text.delete("1.0", f"{line_count - 999}.0")
        except Exception:
            pass
        self.log_text.configure(state="disabled")

    def set_button_state(self, is_running: bool) -> None:
        if is_running:
            self.toggle_button.configure(text="停止监听", fg_color="#a62f2f")
        else:
            self.toggle_button.configure(text="开始监听", fg_color="#FFD700")

    def update_service_status(self, status: str, error_msg: str = "", analysis: str = "") -> None:
        colors = {"未连接": "#888888", "连接中": "#FFA500", "已连接": "#00FF00", "错误": "#FF0000"}
        self.status_label.configure(text=f"● {status}", text_color=colors.get(status, "#888888"))
        if error_msg or analysis:
            detail = (f"错误信息：{error_msg}\n\n" if error_msg else "") + (analysis or "")
            self.status_detail_text.configure(state="normal")
            self.status_detail_text.delete("1.0", "end")
            self.status_detail_text.insert("1.0", detail)
            self.status_detail_text.configure(state="disabled")
            self.status_detail_text.grid()
        else:
            self.status_detail_text.grid_remove()

    def refresh_stratagem_names(self, names) -> None:
        if self._sm:
            self._cats = self._sm.categories
            self._global_cat = self._sm.global_category
            self._eagle_rearm = self._sm.eagle_rearm_name
        self._slot_cats = [c for c in self._cats if c != self._global_cat]
        slot_cats = self._slot_cats or list(self._cats.keys())
        for cat_var, slot_menu, cat_menu in zip(
            self.slot_category_vars, self.slot_menus, self.slot_category_menus
        ):
            cat_menu.configure(values=slot_cats if slot_cats else [""])
            cur_cat = cat_var.get()
            if cur_cat not in self._cats:
                cur_cat = slot_cats[0] if slot_cats else ""
                cat_var.set(cur_cat)
            slot_menu.configure(values=["无"] + self._cats.get(cur_cat, []))

    def refresh_global_commands(self, new_global_commands) -> None:
        self.available_global_commands = list(new_global_commands)
        if self._sm:
            self._eagle_rearm = self._sm.eagle_rearm_name
        for widget in self.scroll_frame.winfo_children():
            info = widget.grid_info()
            if info:
                try:
                    if 1 <= int(info.get("row", 0)) < 100:
                        widget.destroy()
                except (ValueError, TypeError):
                    pass
        self._render_global_checkboxes(self.scroll_frame, start_row=2)
