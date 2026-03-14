"""
GUI 设置 Tab
"""
import customtkinter as ctk
from typing import Callable, Optional, Dict


class SettingsTab:
    """设置 Tab"""
    
    def __init__(
        self,
        parent,
        on_save_config: Callable[[str, str, str], None],
        on_load_config: Callable[[], Optional[Dict[str, str]]],
        on_audio_settings_changed: Optional[Callable[[bool, bool, bool], None]] = None,
        on_asr_mode_changed: Optional[Callable[[str], None]] = None,
    ):
        self.parent = parent
        self.on_save_config = on_save_config
        self.on_load_config = on_load_config
        self.on_audio_settings_changed = on_audio_settings_changed
        self.on_asr_mode_changed = on_asr_mode_changed
        
        self.app_key_entry: ctk.CTkEntry = None
        self.access_key_id_entry: ctk.CTkEntry = None
        self.access_key_secret_entry: ctk.CTkEntry = None
        
        # ASR 模式选择
        self.asr_mode_var = ctk.StringVar(value="aliyun")  # aliyun 或 vosk
        
        # 音频处理选项
        self.noise_suppression_var = ctk.BooleanVar(value=True)
        self.voice_detection_var = ctk.BooleanVar(value=True)
        self.local_processing_var = ctk.BooleanVar(value=True)
        
        self._build()
        self._load_saved_config()
    
    def _build(self):
        """构建设置界面"""
        # 创建可滚动的容器
        scrollable_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="#000000",
            scrollbar_button_color="#FFD700",
            scrollbar_button_hover_color="#FFDD55",
        )
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 绑定鼠标滚轮事件（修复滚动问题）
        def _on_mousewheel(event):
            scrollable_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 创建居中的内容容器（限制最大宽度）
        content_frame = ctk.CTkFrame(scrollable_frame, fg_color="#000000")
        content_frame.pack(fill="x", expand=False, padx=20, pady=20)
        
        # 配置内容框架，使其居中且有最大宽度
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        container = content_frame
        
        # 配置列权重
        container.grid_columnconfigure(0, weight=0, minsize=150)  # 标签列
        container.grid_columnconfigure(1, weight=1)  # 输入框列（有最大宽度限制）
        
        # ========== 语音识别模式选择 ==========
        ctk.CTkLabel(
            container,
            text="语音识别模式",
            text_color="#FFD700",
            font=("Arial", 16, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        mode_frame = ctk.CTkFrame(container, fg_color="#1a1a1a", border_width=2, border_color="#FFD700")
        mode_frame.grid(row=1, column=0, columnspan=2, pady=15, sticky="ew", padx=50)
        
        mode_inner = ctk.CTkFrame(mode_frame, fg_color="#1a1a1a")
        mode_inner.pack(padx=20, pady=20, fill="both")
        
        ctk.CTkRadioButton(
            mode_inner,
            text="☁️ 阿里云在线识别（推荐）",
            variable=self.asr_mode_var,
            value="aliyun",
            command=self._on_asr_mode_changed,
            fg_color="#FFD700",
            hover_color="#FFDD55",
            text_color="#FFFFFF",
            font=("Arial", 14, "bold"),
            radiobutton_width=24,
            radiobutton_height=24,
        ).pack(anchor="w", pady=10)
        
        ctk.CTkLabel(
            mode_inner,
            text="    • 识别准确率高，支持云端降噪\n    • 需要网络连接和阿里云账号\n    • 适合大多数用户",
            text_color="#AAAAAA",
            font=("Arial", 12),
            justify="left",
        ).pack(anchor="w", padx=30)
        
        ctk.CTkRadioButton(
            mode_inner,
            text="💾 Vosk 离线识别",
            variable=self.asr_mode_var,
            value="vosk",
            command=self._on_asr_mode_changed,
            fg_color="#FFD700",
            hover_color="#FFDD55",
            text_color="#FFFFFF",
            font=("Arial", 14, "bold"),
            radiobutton_width=24,
            radiobutton_height=24,
        ).pack(anchor="w", pady=10, padx=0)
        
        ctk.CTkLabel(
            mode_inner,
            text="    • 完全离线，无需网络\n    • 需要下载语音模型（约 50MB）\n    • 识别准确率略低于在线模式",
            text_color="#AAAAAA",
            font=("Arial", 12),
            justify="left",
        ).pack(anchor="w", padx=30)
        
        # Vosk 模型下载提示
        vosk_info_frame = ctk.CTkFrame(mode_inner, fg_color="#2a2a2a", border_width=1, border_color="#666666")
        vosk_info_frame.pack(fill="x", pady=10, padx=30)
        
        ctk.CTkLabel(
            vosk_info_frame,
            text="📥 Vosk 模型下载说明：",
            text_color="#FFD700",
            font=("Arial", 12, "bold"),
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            vosk_info_frame,
            text="1. 访问：https://alphacephei.com/vosk/models\n"
                 "2. 下载：vosk-model-cn-0.22（中文模型，推荐）\n"
                 "3. 解压到程序目录下的 ./vosk 文件夹\n"
                 "4. 确保路径为：./vosk/am, ./vosk/conf 等",
            text_color="#CCCCCC",
            font=("Arial", 11),
            justify="left",
            anchor="w",
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        # 分隔线
        separator0 = ctk.CTkFrame(container, height=2, fg_color="#333333")
        separator0.grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")
        
        # ========== 阿里云配置（仅在线模式需要）==========
        self.aliyun_config_frame = ctk.CTkFrame(container, fg_color="#000000")
        self.aliyun_config_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        
        # 标题
        ctk.CTkLabel(
            self.aliyun_config_frame,
            text="阿里云实时语音识别配置",
            text_color="#FFD700",
            font=("Arial", 16, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # APP KEY
        label_frame = ctk.CTkFrame(self.aliyun_config_frame, fg_color="#000000")
        label_frame.grid(row=1, column=0, columnspan=2, pady=15)
        
        ctk.CTkLabel(
            label_frame,
            text="APP KEY：",
            text_color="#FFFFFF",
            font=("Arial", 14),
            width=200,
            anchor="e",
        ).pack(side="left")
        
        self.app_key_entry = ctk.CTkEntry(
            label_frame,
            width=450,
            height=40,
            fg_color="#222222",
            text_color="#FFFFFF",
            border_color="#FFD700",
            font=("Arial", 13),
        )
        self.app_key_entry.pack(side="left", padx=10)
        
        # Access Key ID
        label_frame2 = ctk.CTkFrame(self.aliyun_config_frame, fg_color="#000000")
        label_frame2.grid(row=2, column=0, columnspan=2, pady=15)
        
        ctk.CTkLabel(
            label_frame2,
            text="Access Key ID：",
            text_color="#FFFFFF",
            font=("Arial", 14),
            width=200,
            anchor="e",
        ).pack(side="left")
        
        self.access_key_id_entry = ctk.CTkEntry(
            label_frame2,
            width=450,
            height=40,
            fg_color="#222222",
            text_color="#FFFFFF",
            border_color="#FFD700",
            font=("Arial", 13),
        )
        self.access_key_id_entry.pack(side="left", padx=10)
        
        # Access Key Secret
        label_frame3 = ctk.CTkFrame(self.aliyun_config_frame, fg_color="#000000")
        label_frame3.grid(row=3, column=0, columnspan=2, pady=15)
        
        ctk.CTkLabel(
            label_frame3,
            text="Access Key Secret：",
            text_color="#FFFFFF",
            font=("Arial", 14),
            width=200,
            anchor="e",
        ).pack(side="left")
        
        self.access_key_secret_entry = ctk.CTkEntry(
            label_frame3,
            width=450,
            height=40,
            show="*",
            fg_color="#222222",
            text_color="#FFFFFF",
            border_color="#FFD700",
            font=("Arial", 13),
        )
        self.access_key_secret_entry.pack(side="left", padx=10)
        
        # 按钮
        button_frame = ctk.CTkFrame(self.aliyun_config_frame, fg_color="#000000")
        button_frame.grid(row=4, column=0, columnspan=2, pady=30)
        
        ctk.CTkButton(
            button_frame,
            text="保存配置",
            command=self._on_save_click,
            fg_color="#FFD700",
            hover_color="#FFDD55",
            text_color="#000000",
            width=150,
            height=45,
            font=("Arial", 14, "bold"),
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="加载已保存配置",
            command=self._load_saved_config,
            fg_color="#555555",
            hover_color="#666666",
            text_color="#FFFFFF",
            width=150,
            height=45,
            font=("Arial", 14, "bold"),
        ).pack(side="left", padx=10)
        
        # 提示
        ctk.CTkLabel(
            self.aliyun_config_frame,
            text="提示：配置将加密保存在本地，下次启动自动加载。",
            text_color="#888888",
            font=("Arial", 11),
        ).grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        # 分隔线
        separator = ctk.CTkFrame(container, height=2, fg_color="#333333")
        separator.grid(row=4, column=0, columnspan=2, pady=20, sticky="ew")
        
        # 音频处理设置
        ctk.CTkLabel(
            container,
            text="音频处理设置（降噪和回音消除）",
            text_color="#FFD700",
            font=("Arial", 18, "bold"),
        ).grid(row=5, column=0, columnspan=2, pady=(0, 20))
        
        # 阿里云端降噪
        noise_frame = ctk.CTkFrame(container, fg_color="#1a1a1a", border_width=1, border_color="#333333")
        noise_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew", padx=50)
        
        ctk.CTkCheckBox(
            noise_frame,
            text="启用阿里云端降噪",
            variable=self.noise_suppression_var,
            command=self._on_audio_settings_changed,
            fg_color="#FFD700",
            hover_color="#FFDD55",
            text_color="#FFFFFF",
            font=("Arial", 13),
            checkbox_width=24,
            checkbox_height=24,
        ).pack(side="left", padx=15, pady=15)
        
        ctk.CTkLabel(
            noise_frame,
            text="（推荐）使用阿里云服务器端降噪算法",
            text_color="#888888",
            font=("Arial", 12),
        ).pack(side="left", padx=5)
        
        # 语音检测
        voice_frame = ctk.CTkFrame(container, fg_color="#1a1a1a", border_width=1, border_color="#333333")
        voice_frame.grid(row=7, column=0, columnspan=2, pady=10, sticky="ew", padx=50)
        
        ctk.CTkCheckBox(
            voice_frame,
            text="启用语音检测",
            variable=self.voice_detection_var,
            command=self._on_audio_settings_changed,
            fg_color="#FFD700",
            hover_color="#FFDD55",
            text_color="#FFFFFF",
            font=("Arial", 13),
            checkbox_width=24,
            checkbox_height=24,
        ).pack(side="left", padx=15, pady=15)
        
        ctk.CTkLabel(
            voice_frame,
            text="（推荐）过滤非语音段，减少误识别",
            text_color="#888888",
            font=("Arial", 12),
        ).pack(side="left", padx=5)
        
        # 本地音频处理
        local_frame = ctk.CTkFrame(container, fg_color="#1a1a1a", border_width=1, border_color="#333333")
        local_frame.grid(row=8, column=0, columnspan=2, pady=10, sticky="ew", padx=50)
        
        ctk.CTkCheckBox(
            local_frame,
            text="启用本地音频预处理",
            variable=self.local_processing_var,
            command=self._on_audio_settings_changed,
            fg_color="#FFD700",
            hover_color="#FFDD55",
            text_color="#FFFFFF",
            font=("Arial", 13),
            checkbox_width=24,
            checkbox_height=24,
        ).pack(side="left", padx=15, pady=15)
        
        ctk.CTkLabel(
            local_frame,
            text="（推荐）本地降噪、回音消除、噪音门",
            text_color="#888888",
            font=("Arial", 12),
        ).pack(side="left", padx=5)
        
        # 说明
        info_frame = ctk.CTkFrame(container, fg_color="#1a1a1a", border_width=1, border_color="#FFD700")
        info_frame.grid(row=9, column=0, columnspan=2, pady=20, sticky="ew", padx=50)
        
        info_text = """
💡 音频处理说明：

• 阿里云端降噪：使用阿里云服务器的专业降噪算法，效果最好
• 语音检测：自动过滤非语音段（如静音、纯噪音），减少误触发
• 本地音频预处理：在发送到云端前进行本地处理
  - 噪音门：过滤低音量背景噪音
  - 回音消除：减少音响回音干扰
  - 音量归一化：自动调整音量到合适水平

🎯 推荐配置：全部启用（默认）
⚠️ 如果遇到识别延迟，可以关闭"本地音频预处理"
        """
        
        ctk.CTkLabel(
            info_frame,
            text=info_text.strip(),
            text_color="#CCCCCC",
            font=("Arial", 12),
            justify="left",
        ).pack(padx=20, pady=20, anchor="w")
        
        # 分隔线
        separator2 = ctk.CTkFrame(container, height=2, fg_color="#333333")
        separator2.grid(row=10, column=0, columnspan=2, pady=20, sticky="ew")
        
        # 隐私信息管理
        ctk.CTkLabel(
            container,
            text="隐私信息管理",
            text_color="#FFD700",
            font=("Arial", 18, "bold"),
        ).grid(row=11, column=0, columnspan=2, pady=(0, 20))
        
        privacy_frame = ctk.CTkFrame(container, fg_color="#1a1a1a", border_width=1, border_color="#FF6B6B")
        privacy_frame.grid(row=12, column=0, columnspan=2, pady=10, sticky="ew", padx=50)
        
        privacy_text = """
⚠️ 清除隐私信息

如果你想分享此软件给朋友，可以点击下方按钮清除已保存的阿里云密钥。
清除后需要重新配置才能使用。

包含的文件：
• modules/.key（加密密钥）
• modules/config.enc（加密的配置文件）
        """
        
        ctk.CTkLabel(
            privacy_frame,
            text=privacy_text.strip(),
            text_color="#CCCCCC",
            font=("Arial", 12),
            justify="left",
        ).pack(padx=20, pady=20, anchor="w")
        
        # 清除按钮（居中）
        button_container = ctk.CTkFrame(privacy_frame, fg_color="#1a1a1a")
        button_container.pack(pady=(0, 20))
        
        ctk.CTkButton(
            button_container,
            text="🗑️ 清除隐私信息",
            command=self._clear_privacy_data,
            fg_color="#FF6B6B",
            hover_color="#FF5252",
            text_color="#FFFFFF",
            width=200,
            height=45,
            font=("Arial", 14, "bold"),
        ).pack()
    
    def _on_asr_mode_changed(self):
        """ASR 模式改变回调"""
        mode = self.asr_mode_var.get()
        
        # 显示或隐藏阿里云配置
        if mode == "aliyun":
            self.aliyun_config_frame.grid()
        else:
            self.aliyun_config_frame.grid_remove()
        
        # 通知主程序（如果回调已设置）
        if self.on_asr_mode_changed:
            self.on_asr_mode_changed(mode)
    
    def _on_save_click(self):
        """保存按钮点击"""
        app_key = self.app_key_entry.get().strip()
        access_key_id = self.access_key_id_entry.get().strip()
        access_key_secret = self.access_key_secret_entry.get().strip()
        
        self.on_save_config(app_key, access_key_id, access_key_secret)
    
    def _load_saved_config(self):
        """加载已保存的配置"""
        config = self.on_load_config()
        if config:
            self.app_key_entry.delete(0, "end")
            self.app_key_entry.insert(0, config["app_key"])
            self.access_key_id_entry.delete(0, "end")
            self.access_key_id_entry.insert(0, config["access_key_id"])
            self.access_key_secret_entry.delete(0, "end")
            self.access_key_secret_entry.insert(0, config["access_key_secret"])
    
    def _on_audio_settings_changed(self):
        """音频设置改变回调"""
        if self.on_audio_settings_changed:
            self.on_audio_settings_changed(
                self.noise_suppression_var.get(),
                self.voice_detection_var.get(),
                self.local_processing_var.get(),
            )
    
    def get_audio_settings(self) -> Dict[str, bool]:
        """获取音频设置"""
        return {
            "noise_suppression": self.noise_suppression_var.get(),
            "voice_detection": self.voice_detection_var.get(),
            "local_processing": self.local_processing_var.get(),
        }
    
    def get_asr_mode(self) -> str:
        """获取 ASR 模式"""
        return self.asr_mode_var.get()
    
    def _clear_privacy_data(self):
        """清除隐私信息"""
        import sys
        import os
        from pathlib import Path
        import tkinter.messagebox as messagebox
        
        # 确认对话框
        result = messagebox.askyesno(
            "确认清除",
            "确定要清除所有隐私信息吗？\n\n"
            "这将删除：\n"
            "• 阿里云 API 密钥\n"
            "• 加密配置文件\n\n"
            "清除后需要重新配置才能使用。",
            icon="warning"
        )
        
        if not result:
            return
        
        # 获取正确的路径（与 ConfigManager 一致）
        if getattr(sys, 'frozen', False):
            # 打包后的 exe 运行时
            base_path = Path(sys.executable).parent / "modules"
        else:
            # 开发环境
            base_path = Path(__file__).parent.parent / "modules"
        
        # 删除文件
        files_to_delete = [
            base_path / ".key",
            base_path / "config.enc",
        ]
        
        deleted_files = []
        for file_path in files_to_delete:
            if file_path.exists():
                try:
                    file_path.unlink()
                    deleted_files.append(str(file_path))
                except Exception as e:
                    messagebox.showerror("错误", f"删除文件失败：{file_path}\n{e}")
                    return
        
        # 清空输入框
        self.app_key_entry.delete(0, "end")
        self.access_key_id_entry.delete(0, "end")
        self.access_key_secret_entry.delete(0, "end")
        
        # 成功提示
        if deleted_files:
            messagebox.showinfo(
                "清除成功",
                f"已清除以下文件：\n" + "\n".join(f"• {f}" for f in deleted_files) + "\n\n"
                "现在可以安全地分享此软件了！\n"
                "接收者需要在设置页面重新配置阿里云密钥。"
            )
        else:
            messagebox.showinfo("提示", "没有找到需要清除的隐私信息。")
