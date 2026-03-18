"""
GUI 主界面 Tab
"""
import customtkinter as ctk
from typing import List, Callable, Dict


class MainTab:
    """主界面 Tab"""
    
    # 战备分类
    STRATAGEM_CATEGORIES = {
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
    }
    
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
    ):
        self.parent = parent
        self.stratagem_names = sorted(stratagem_names)
        self.active_slots = active_slots
        self.available_global_commands = available_global_commands
        self.enabled_global_commands = enabled_global_commands
        self.on_slot_changed = on_slot_changed
        self.on_global_command_toggled = on_global_command_toggled
        self.on_toggle_engine = on_toggle_engine
        
        self.slot_vars: List[ctk.StringVar] = []
        self.slot_category_vars: List[ctk.StringVar] = []
        self.slot_frames: List[ctk.CTkFrame] = []
        self.slot_menus: List[ctk.CTkOptionMenu] = []
        self.global_command_vars: Dict[str, ctk.BooleanVar] = {}
        self.toggle_button: ctk.CTkButton = None
        self.log_text: ctk.CTkTextbox = None
        self.status_label: ctk.CTkLabel = None
        self.status_detail_text: ctk.CTkTextbox = None
        
        self._build()
    
    def _build(self):
        """构建主界面"""
        # 主容器（支持窗口缩放）
        main_container = ctk.CTkFrame(self.parent, fg_color="#000000")
        main_container.pack(fill="both", expand=True)
        
        # 配置行列权重，使其可以缩放
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=3)
        main_container.grid_columnconfigure(1, weight=1)
        
        # 左侧：配置区域（带滚动）
        left_frame = ctk.CTkFrame(main_container, fg_color="#111111")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # 创建滚动框架
        scroll_frame = ctk.CTkScrollableFrame(
            left_frame,
            fg_color="#111111",
            scrollbar_button_color="#FFD700",
            scrollbar_button_hover_color="#FFDD55",
        )
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # 全局指令区域
        self._build_global_commands(scroll_frame)
        
        # 分隔线
        separator = ctk.CTkFrame(scroll_frame, height=2, fg_color="#333333")
        separator.grid(row=100, column=0, sticky="ew", padx=10, pady=15)
        
        # 槽位战备区域
        self._build_slot_config(scroll_frame)
        
        # 右侧：控制和日志区域
        right_frame = ctk.CTkFrame(main_container, fg_color="#111111")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_frame.grid_rowconfigure(3, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # 控制按钮
        self.toggle_button = ctk.CTkButton(
            right_frame,
            text="开始监听",
            command=self.on_toggle_engine,
            fg_color="#FFD700",
            hover_color="#FFDD55",
            text_color="#000000",
            height=50,
            font=("Arial", 14, "bold"),
        )
        self.toggle_button.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # 阿里云服务状态区域
        status_frame = ctk.CTkFrame(right_frame, fg_color="#1a1a1a", corner_radius=8)
        status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        status_frame.grid_columnconfigure(1, weight=1)
        
        status_title = ctk.CTkLabel(
            status_frame,
            text="阿里云服务状态：",
            text_color="#FFFFFF",
            anchor="w",
            font=("Arial", 11, "bold"),
        )
        status_title.grid(row=0, column=0, sticky="w", padx=10, pady=8)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="● 未连接",
            text_color="#888888",
            anchor="w",
            font=("Arial", 11, "bold"),
        )
        self.status_label.grid(row=0, column=1, sticky="w", padx=5, pady=8)
        
        # 状态详情（可折叠）
        self.status_detail_text = ctk.CTkTextbox(
            status_frame,
            wrap="word",
            fg_color="#0a0a0a",
            text_color="#FF6B6B",
            font=("Consolas", 9),
            height=80,
        )
        self.status_detail_text.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.status_detail_text.configure(state="disabled")
        self.status_detail_text.grid_remove()  # 默认隐藏
        
        # 日志区域
        log_label = ctk.CTkLabel(
            right_frame,
            text="语音识别日志：",
            text_color="#FFFFFF",
            anchor="w",
            font=("Arial", 12, "bold"),
        )
        log_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 5))
        
        self.log_text = ctk.CTkTextbox(
            right_frame,
            wrap="word",
            fg_color="#000000",
            text_color="#FFFFFF",
            font=("Consolas", 10),
        )
        self.log_text.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.log_text.configure(state="disabled")
        
        # 配置右侧框架的行权重
        right_frame.grid_rowconfigure(3, weight=1)
    
    def _build_global_commands(self, parent):
        """构建全局指令区域"""
        # 标题
        title = ctk.CTkLabel(
            parent,
            text="任务全局指令",
            text_color="#FFD700",
            anchor="w",
            font=("Arial", 16, "bold"),
        )
        title.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(0, 20))
        
        # 飞鹰整备提示
        eagle_hint = ctk.CTkLabel(
            parent,
            text="💡 提示：【飞鹰整备】会根据槽位中的飞鹰战备自动启用/禁用",
            text_color="#888888",
            anchor="w",
            font=("Arial", 11),
        )
        eagle_hint.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(25, 0))
        
        # 配置列权重，使3列均匀分布
        parent.grid_columnconfigure(0, weight=1, uniform="global_cmd")
        parent.grid_columnconfigure(1, weight=1, uniform="global_cmd")
        parent.grid_columnconfigure(2, weight=1, uniform="global_cmd")
        
        # 使用网格布局，3列显示（排除飞鹰整备）
        row = 1
        col = 0
        for i, cmd in enumerate(self.available_global_commands):
            # 跳过飞鹰整备，它会自动管理
            if cmd == "飞鹰整备":
                continue
            
            var = ctk.BooleanVar(value=(cmd in self.enabled_global_commands))
            checkbox = ctk.CTkCheckBox(
                parent,
                text=cmd,
                variable=var,
                command=lambda c=cmd, v=var: self.on_global_command_toggled(c, v.get()),
                text_color="#FFFFFF",
                fg_color="#FFD700",
                border_color="#FFD700",
                hover_color="#FFDD55",
                font=("Arial", 13),
                checkbox_width=24,
                checkbox_height=24,
            )
            checkbox.grid(row=row, column=col, sticky="w", padx=15, pady=10)
            self.global_command_vars[cmd] = var
            
            # 3列布局
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    def _build_slot_config(self, parent):
        """构建槽位配置区域"""
        # 标题
        title = ctk.CTkLabel(
            parent,
            text="本局战备配置（4个槽位）",
            text_color="#FFD700",
            anchor="w",
            font=("Arial", 16, "bold"),
        )
        title.grid(row=200, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 10))
        
        # 保存槽位框架和战备菜单的引用
        self.slot_frames = []
        self.slot_menus = []
        
        # 4个槽位
        for i in range(4):
            slot_frame = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=8)
            slot_frame.grid(row=201 + i, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
            slot_frame.grid_columnconfigure(1, weight=1)
            slot_frame.grid_columnconfigure(2, weight=2)
            self.slot_frames.append(slot_frame)
            
            # 槽位标签
            label = ctk.CTkLabel(
                slot_frame,
                text=f"槽位 {i + 1}",
                text_color="#FFD700",
                font=("Arial", 14, "bold"),
                width=80,
            )
            label.grid(row=0, column=0, padx=15, pady=12)
            
            # 确定默认值和分类
            default_value = self.active_slots[i] if i < len(self.active_slots) else ""
            default_category = "背包类"
            for cat, items in self.STRATAGEM_CATEGORIES.items():
                if default_value in items:
                    default_category = cat
                    break
            
            # 分类选择
            category_var = ctk.StringVar(value=default_category)
            category_menu = ctk.CTkOptionMenu(
                slot_frame,
                variable=category_var,
                values=list(self.STRATAGEM_CATEGORIES.keys()),
                command=lambda val, idx=i: self._on_category_changed(idx, val),
                fg_color="#FFD700",
                button_color="#FFDD55",
                button_hover_color="#FFE680",
                text_color="#000000",
                dropdown_fg_color="#FFD700",
                dropdown_text_color="#000000",
                width=120,
            )
            category_menu.grid(row=0, column=1, padx=10, pady=12)
            self.slot_category_vars.append(category_var)
            
            # 战备选择（添加"无"选项）
            category_items = ["无"] + self.STRATAGEM_CATEGORIES[default_category]
            slot_var = ctk.StringVar(value=default_value if default_value else "无")
            slot_menu = ctk.CTkOptionMenu(
                slot_frame,
                variable=slot_var,
                values=category_items,
                command=lambda val, idx=i: self._on_slot_menu_changed(idx, val),
                fg_color="#333333",
                button_color="#444444",
                button_hover_color="#555555",
                text_color="#FFFFFF",
                dropdown_fg_color="#333333",
                dropdown_text_color="#FFFFFF",
            )
            slot_menu.grid(row=0, column=2, padx=10, pady=12, sticky="ew")
            self.slot_vars.append(slot_var)
            self.slot_menus.append(slot_menu)
    
    def _on_category_changed(self, slot_index: int, category: str):
        """分类改变时更新战备列表"""
        items = ["无"] + self.STRATAGEM_CATEGORIES.get(category, [])
        if not items:
            return
        
        # 获取旧的战备菜单
        old_menu = self.slot_menus[slot_index]
        slot_frame = self.slot_frames[slot_index]
        
        # 更新变量
        stratagem_var = self.slot_vars[slot_index]
        stratagem_var.set("无")
        
        # 销毁旧菜单
        old_menu.destroy()
        
        # 创建新菜单
        new_menu = ctk.CTkOptionMenu(
            slot_frame,
            variable=stratagem_var,
            values=items,
            command=lambda value, idx=slot_index: self._on_slot_menu_changed(idx, value),
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555",
            text_color="#FFFFFF",
            dropdown_fg_color="#333333",
            dropdown_text_color="#FFFFFF",
        )
        new_menu.grid(row=0, column=2, padx=10, pady=12, sticky="ew")
        self.slot_menus[slot_index] = new_menu
        
        # 触发回调
        self._on_slot_menu_changed(slot_index, "无")
    
    def _on_slot_menu_changed(self, slot_index: int, value: str):
        """槽位菜单改变回调"""
        if value == "无":
            value = ""
        self.on_slot_changed(slot_index, value)
    
    def append_log(self, message: str) -> None:
        """添加日志"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        
        # 控制行数
        try:
            line_count = int(self.log_text.index("end-1c").split(".")[0])
            if line_count > 1000:
                self.log_text.delete("1.0", f"{line_count - 999}.0")
        except Exception:
            pass
        
        self.log_text.configure(state="disabled")
    
    def set_button_state(self, is_running: bool) -> None:
        """设置按钮状态"""
        if is_running:
            self.toggle_button.configure(text="停止监听", fg_color="#a62f2f")
        else:
            self.toggle_button.configure(text="开始监听", fg_color="#FFD700")
    
    def update_service_status(self, status: str, error_msg: str = "", analysis: str = "") -> None:
        """更新阿里云服务状态显示"""
        # 状态颜色映射
        status_colors = {
            "未连接": "#888888",
            "连接中": "#FFA500",
            "已连接": "#00FF00",
            "错误": "#FF0000",
        }
        
        color = status_colors.get(status, "#888888")
        self.status_label.configure(text=f"● {status}", text_color=color)
        
        # 显示或隐藏详情
        if error_msg or analysis:
            detail_text = ""
            if error_msg:
                detail_text += f"错误信息：{error_msg}\n\n"
            if analysis:
                detail_text += f"{analysis}"
            
            self.status_detail_text.configure(state="normal")
            self.status_detail_text.delete("1.0", "end")
            self.status_detail_text.insert("1.0", detail_text)
            self.status_detail_text.configure(state="disabled")
            self.status_detail_text.grid()  # 显示
        else:
            self.status_detail_text.grid_remove()  # 隐藏

    def refresh_stratagem_names(self, names: List[str]) -> None:
        """热更新战备名称列表，将不在已有分类中的战备加入未分类"""
        all_categorized = set(
            item
            for items in self.STRATAGEM_CATEGORIES.values()
            for item in items
        )
        uncategorized = [n for n in names if n not in all_categorized]
        if uncategorized:
            self.STRATAGEM_CATEGORIES["未分类"] = uncategorized
        elif "未分类" in self.STRATAGEM_CATEGORIES:
            del self.STRATAGEM_CATEGORIES["未分类"]
