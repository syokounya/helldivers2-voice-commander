"""
GUI 测试 Tab
"""
import customtkinter as ctk
from typing import List, Callable, Dict


class TestTab:
    """测试 Tab"""
    
    def __init__(
        self,
        parent,
        stratagem_names: List[str],
        on_test_execute: Callable[[str], None],
        on_dry_run_toggled: Callable[[bool], None],
    ):
        self.parent = parent
        self.stratagem_names = sorted(stratagem_names)
        self.on_test_execute = on_test_execute
        self.on_dry_run_toggled = on_dry_run_toggled
        
        self.test_var: ctk.StringVar = None
        self.current_keys_var: ctk.StringVar = ctk.StringVar(value="（尚未执行）")
        self.dry_run_var: ctk.BooleanVar = ctk.BooleanVar(value=False)
        self.dpad_labels: Dict[str, ctk.CTkLabel] = {}
        self.dpad_normal_color = "#222222"
        self.dpad_active_color = "#FFD700"
        self.log_text: ctk.CTkTextbox = None  # 添加日志文本框
        
        self._build()
    
    def _build(self):
        """构建测试界面"""
        container = ctk.CTkFrame(self.parent, fg_color="#000000")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 战备选择和执行按钮
        ctk.CTkLabel(
            container,
            text="测试当前战备指令：",
            text_color="#FFFFFF",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        
        self.test_var = ctk.StringVar(value=self.stratagem_names[0] if self.stratagem_names else "")
        
        self.test_menu = ctk.CTkOptionMenu(
            container,
            variable=self.test_var,
            values=self.stratagem_names,
            fg_color="#FFD700",
            button_color="#FFC000",
            button_hover_color="#FFDD55",
            text_color="#000000",
        )
        test_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        test_button = ctk.CTkButton(
            container,
            text="模拟执行（发送按键）",
            command=self._on_test_click,
            fg_color="#FFD700",
            hover_color="#FFDD55",
            text_color="#000000",
        )
        test_button.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        # D-Pad 可视化
        dpad_frame = ctk.CTkFrame(container, fg_color="#000000")
        dpad_frame.grid(row=1, column=0, columnspan=3, pady=(25, 10))
        
        for r in range(3):
            dpad_frame.grid_rowconfigure(r, weight=1)
        for c in range(3):
            dpad_frame.grid_columnconfigure(c, weight=1)
        
        # 创建方向键标签
        up_label = ctk.CTkLabel(dpad_frame, text="↑", fg_color=self.dpad_normal_color, text_color="#FFFFFF", width=60, height=40)
        up_label.grid(row=0, column=1, padx=5, pady=5)
        
        left_label = ctk.CTkLabel(dpad_frame, text="←", fg_color=self.dpad_normal_color, text_color="#FFFFFF", width=60, height=40)
        left_label.grid(row=1, column=0, padx=5, pady=5)
        
        center_label = ctk.CTkLabel(dpad_frame, text="●", fg_color=self.dpad_normal_color, text_color="#FFFFFF", width=60, height=40)
        center_label.grid(row=1, column=1, padx=5, pady=5)
        
        right_label = ctk.CTkLabel(dpad_frame, text="→", fg_color=self.dpad_normal_color, text_color="#FFFFFF", width=60, height=40)
        right_label.grid(row=1, column=2, padx=5, pady=5)
        
        down_label = ctk.CTkLabel(dpad_frame, text="↓", fg_color=self.dpad_normal_color, text_color="#FFFFFF", width=60, height=40)
        down_label.grid(row=2, column=1, padx=5, pady=5)
        
        self.dpad_labels["up"] = up_label
        self.dpad_labels["left"] = left_label
        self.dpad_labels["right"] = right_label
        self.dpad_labels["down"] = down_label
        self.dpad_labels["center"] = center_label
        
        # 按键序列显示
        ctk.CTkLabel(
            container,
            text="本次按键序列：",
            anchor="w",
            text_color="#FFFFFF",
        ).grid(row=3, column=0, sticky="ne", pady=(15, 0))
        
        keys_label = ctk.CTkLabel(
            container,
            textvariable=self.current_keys_var,
            anchor="w",
            justify="left",
            text_color="#FFFFFF",
        )
        keys_label.grid(row=3, column=1, columnspan=2, sticky="nw", pady=(15, 0))
        
        # 测试模式开关
        dry_run_checkbox = ctk.CTkCheckBox(
            container,
            text="语音测试模式（仅可视化，不发送按键到游戏）",
            variable=self.dry_run_var,
            command=self._on_dry_run_change,
            text_color="#FFFFFF",
            fg_color="#FFD700",
            border_color="#FFD700",
            hover_color="#FFDD55",
        )
        dry_run_checkbox.grid(row=2, column=0, columnspan=3, pady=(10, 0), sticky="w")
        
        # 测试日志显示
        ctk.CTkLabel(
            container,
            text="测试日志：",
            anchor="w",
            text_color="#FFFFFF",
        ).grid(row=4, column=0, columnspan=3, sticky="w", pady=(20, 5))
        
        self.log_text = ctk.CTkTextbox(
            container,
            wrap="word",
            fg_color="#111111",
            text_color="#FFFFFF",
            height=150,
        )
        self.log_text.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        self.log_text.configure(state="disabled")
        
        # 配置行列权重，让日志区域可以扩展
        container.grid_rowconfigure(5, weight=1)
        container.grid_columnconfigure(1, weight=1)
    
    def _on_test_click(self):
        """测试按钮点击"""
        name = self.test_var.get().strip()
        if name:
            self.on_test_execute(name)
    
    def _on_dry_run_change(self):
        """测试模式切换"""
        self.on_dry_run_toggled(self.dry_run_var.get())
    
    def update_keys_display(self, name: str, wasd_seq: List[str], arrow_seq: List[str]):
        """更新按键显示"""
        wasd_part = " ".join(wasd_seq)
        arrow_part = " ".join(arrow_seq)
        text = f"{name}\nWASD 序列：{wasd_part}\n方向键序列：Ctrl + {arrow_part}"
        self.current_keys_var.set(text)
    
    def play_dpad_animation(self, arrows: List[str], after_callback):
        """播放 D-Pad 动画"""
        self._reset_dpad()
        delay_per_key = 120
        
        if not arrows:
            return
        
        for idx, arrow in enumerate(arrows):
            t_on = idx * delay_per_key
            t_off = t_on + delay_per_key // 2
            
            def make_on(a: str):
                def _on():
                    self._reset_dpad()
                    lbl = self.dpad_labels.get(a)
                    if lbl:
                        lbl.configure(fg_color=self.dpad_active_color)
                return _on
            
            def make_off():
                def _off():
                    self._reset_dpad()
                return _off
            
            after_callback(t_on, make_on(arrow))
            after_callback(t_off, make_off())
    
    def _reset_dpad(self):
        """重置 D-Pad 颜色"""
        for lbl in self.dpad_labels.values():
            lbl.configure(fg_color=self.dpad_normal_color)
    
    def append_log(self, message: str) -> None:
        """添加日志到测试 Tab"""
        if not self.log_text:
            return
        
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        
        # 控制行数
        try:
            line_count = int(self.log_text.index("end-1c").split(".")[0])
            if line_count > 100:
                self.log_text.delete("1.0", f"{line_count - 99}.0")
        except Exception:
            pass
        
        self.log_text.configure(state="disabled")

    def refresh_stratagem_names(self, names: List[str]) -> None:
        """热更新战备列表"""
        self.stratagem_names = sorted(names)
        if self.test_menu:
            self.test_menu.configure(values=self.stratagem_names)
            if self.test_var.get() not in self.stratagem_names and self.stratagem_names:
                self.test_var.set(self.stratagem_names[0])
