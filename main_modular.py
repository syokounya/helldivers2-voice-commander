"""
绝地潜兵 2 语音战备助手 - 主程序
模块化重构版本
"""
import customtkinter as ctk
from typing import List

from modules.config_manager import ConfigManager
from modules.stratagem_manager import StratagemManager
from modules.stratagem_engine import StratagemEngine
from modules.log_manager import LogManager
from gui.gui_main_tab import MainTab
from gui.gui_test_tab import TestTab
from gui.gui_settings_tab import SettingsTab
from gui.gui_stratagem_editor_tab import StratagemEditorTab


class StratagemApp(ctk.CTk):
    """主应用程序"""
    
    def __init__(self):
        super().__init__()
        
        self.title("绝地潜兵 2 语音战备助手")
        self.geometry("900x650")
        
        # 初始化各个管理器
        self.config_manager = ConfigManager()
        self.stratagem_manager = StratagemManager()
        self.log_manager = LogManager()
        self.engine = StratagemEngine(
            stratagem_manager=self.stratagem_manager,
            log_callback=self.log_manager.log,
            key_log_callback=self.on_keys_executed,
        )
        
        self.engine_running = False
        
        # 构建 UI
        self._build_ui()
        
        # 加载已保存的配置（必须在 UI 构建之后）
        self._load_saved_config()
        
        # 启动日志处理循环
        self.after(100, self._process_logs)
    
    def _load_saved_config(self):
        """加载已保存的阿里云配置"""
        config = self.config_manager.load_config()
        if config:
            audio_settings = self.settings_tab.get_audio_settings()
            self.engine.set_credentials(
                config["app_key"],
                config["access_key_id"],
                config["access_key_secret"],
                enable_noise_suppression=audio_settings["noise_suppression"],
                enable_voice_detection=audio_settings["voice_detection"],
                enable_local_processing=audio_settings["local_processing"],
                on_status_callback=self._on_service_status_changed,
            )
    
    def _build_ui(self):
        """构建用户界面"""
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#000000")
        
        # 创建 Tab 视图
        tabview = ctk.CTkTabview(self, fg_color="#111111", segmented_button_fg_color="#222222")
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建四个 Tab
        main_tab = tabview.add("主界面")
        test_tab = tabview.add("测试")
        editor_tab = tabview.add("指令编辑")
        settings_tab = tabview.add("设置")
        
        # 构建主界面 Tab
        self.main_tab = MainTab(
            parent=main_tab,
            stratagem_names=self.stratagem_manager.get_all_names(),
            active_slots=self.stratagem_manager.active_slots,
            available_global_commands=self.stratagem_manager.AVAILABLE_GLOBAL_COMMANDS,
            enabled_global_commands=self.stratagem_manager.global_commands,
            on_slot_changed=self._on_slot_changed,
            on_global_command_toggled=self._on_global_command_toggled,
            on_toggle_engine=self._toggle_engine,
            stratagem_manager=self.stratagem_manager,
        )
        
        # 构建测试 Tab
        self.test_tab = TestTab(
            parent=test_tab,
            stratagem_names=self.stratagem_manager.get_all_names(),
            on_test_execute=self._on_test_execute,
            on_dry_run_toggled=self._on_dry_run_toggled,
        )
        
        # 构建指令编辑 Tab
        self.editor_tab = StratagemEditorTab(
            parent=editor_tab,
            stratagem_names=self.stratagem_manager.get_all_names(),
            json_path="stratagems.json",
            on_save_callback=self._on_stratagem_json_saved,
            stratagem_manager=self.stratagem_manager,
        )
        
        # 构建设置 Tab
        self.settings_tab = SettingsTab(
            parent=settings_tab,
            on_save_config=self._save_config,
            on_load_config=self.config_manager.load_config,
            on_audio_settings_changed=self._on_audio_settings_changed,
            on_asr_mode_changed=self._on_asr_mode_changed,
        )
    
    def _process_logs(self):
        """处理日志队列"""
        logs = self.log_manager.get_pending_logs()
        for log in logs:
            self.main_tab.append_log(log)
            self.test_tab.append_log(log)
        
        self.after(100, self._process_logs)
    
    def _on_slot_changed(self, index: int, value: str):
        """槽位改变回调"""
        self.stratagem_manager.update_slot(index, value)
        self.log_manager.log(f"槽位 {index + 1} 已更新为：{value}")
        
        eagle_msg = self.stratagem_manager.get_eagle_rearm_status_message()
        if eagle_msg:
            self.log_manager.log(eagle_msg)
    
    def _on_global_command_toggled(self, name: str, enabled: bool):
        """全局指令切换回调"""
        self.stratagem_manager.toggle_global_command(name, enabled)
        status = "启用" if enabled else "禁用"
        self.log_manager.log(f"全局指令 {name} 已{status}")
    
    def _toggle_engine(self):
        """切换引擎状态"""
        if not self.engine_running:
            asr_mode = self.settings_tab.get_asr_mode()
            
            if asr_mode == "aliyun":
                if not self.config_manager.has_config():
                    self.log_manager.log("错误：请先在'设置'页面配置阿里云 API 密钥。")
                    return
            
            self.engine.start()
            self.engine.set_dry_run(self.test_tab.dry_run_var.get())
            self.engine_running = True
            self.main_tab.set_button_state(True)
            
            mode_name = "阿里云在线识别" if asr_mode == "aliyun" else "Vosk 离线识别"
            self.log_manager.log(f"已开始监听语音指令（{mode_name}）。")
        else:
            self.engine.stop()
            self.engine_running = False
            self.main_tab.set_button_state(False)
            self.log_manager.log("已停止监听语音指令。")
    
    def _on_test_execute(self, name: str):
        """测试执行回调"""
        if name not in self.stratagem_manager.get_all_names():
            self.log_manager.log(f"测试失败：未找到战备 {name}")
            return
        
        if not self.stratagem_manager.is_allowed(name):
            self.log_manager.log(f"测试提示：{name} 不在当前允许列表中。")
        
        self.log_manager.log(f"测试执行战备：{name}")
        self.engine.execute_stratagem(name)
    
    def _on_dry_run_toggled(self, value: bool):
        """测试模式切换回调"""
        self.engine.set_dry_run(value)
        if value:
            self.log_manager.log("已开启语音测试模式：只做可视化，不发送按键到游戏。")
        else:
            self.log_manager.log("已关闭语音测试模式：将发送按键到游戏。")
    
    def on_keys_executed(self, name: str, seq: List[str], arrows: List[str]):
        """按键执行回调"""
        self.after(0, self._update_keys_display, name, seq, arrows)
    
    def _update_keys_display(self, name: str, seq: List[str], arrows: List[str]):
        """更新按键显示"""
        arrow_part = " ".join(arrows)
        self.test_tab.update_keys_display(name, seq, arrows)
        self.log_manager.log(f"{name} 执行按键：{arrow_part}")
        self.test_tab.play_dpad_animation(arrows, self.after)
    
    def _save_config(self, app_key: str, access_key_id: str, access_key_secret: str):
        """保存配置回调"""
        if not app_key or not access_key_id or not access_key_secret:
            self.log_manager.log("错误：请填写完整的阿里云配置信息。")
            return
        
        self.config_manager.save_config(app_key, access_key_id, access_key_secret)
        audio_settings = self.settings_tab.get_audio_settings()
        self.engine.set_credentials(
            app_key, access_key_id, access_key_secret,
            enable_noise_suppression=audio_settings["noise_suppression"],
            enable_voice_detection=audio_settings["voice_detection"],
            enable_local_processing=audio_settings["local_processing"],
            on_status_callback=self._on_service_status_changed,
        )
        self.log_manager.log("阿里云配置已保存并应用。")
    
    def _on_audio_settings_changed(self, noise_suppression: bool, voice_detection: bool, local_processing: bool):
        """音频设置改变回调"""
        status_parts = []
        if noise_suppression:
            status_parts.append("云端降噪")
        if voice_detection:
            status_parts.append("语音检测")
        if local_processing:
            status_parts.append("本地预处理")
        
        status = "、".join(status_parts) if status_parts else "无"
        self.log_manager.log(f"音频处理设置已更新：{status}")
        
        if self.engine_running:
            self.log_manager.log("提示：请重新启动监听以应用新的音频设置。")
    
    def _on_service_status_changed(self, status: str, error_msg: str, analysis: str):
        """阿里云服务状态改变回调"""
        self.after(0, self._update_service_status_ui, status, error_msg, analysis)
    
    def _update_service_status_ui(self, status: str, error_msg: str, analysis: str):
        """更新服务状态 UI（在主线程中）"""
        self.main_tab.update_service_status(status, error_msg, analysis)
        
        if status == "错误":
            self.log_manager.log(f"❌ 服务错误：{error_msg}")
        elif status == "已连接":
            mode_name = "阿里云" if self.settings_tab.get_asr_mode() == "aliyun" else "Vosk"
            self.log_manager.log(f"✅ {mode_name} 服务已连接")
    
    def _on_asr_mode_changed(self, mode: str):
        """ASR 模式改变回调"""
        if mode == "aliyun":
            config = self.config_manager.load_config()
            if config:
                audio_settings = self.settings_tab.get_audio_settings()
                self.engine.set_credentials(
                    config["app_key"],
                    config["access_key_id"],
                    config["access_key_secret"],
                    enable_noise_suppression=audio_settings["noise_suppression"],
                    enable_voice_detection=audio_settings["voice_detection"],
                    enable_local_processing=audio_settings["local_processing"],
                    on_status_callback=self._on_service_status_changed,
                )
                self.log_manager.log("已切换到阿里云在线识别模式")
        else:
            self.engine.set_vosk_model(
                model_path="./vosk",
                on_status_callback=self._on_service_status_changed,
            )
            self.log_manager.log("已切换到 Vosk 离线识别模式")
    
    def _on_stratagem_json_saved(self, json_path: str = None):
        """战备JSON保存回调（热更新）"""
        # 重新加载战备数据（含 categories、eagle_stratagems）
        self.stratagem_manager.load_stratagems()

        # 同步 matcher 的 aliases
        self.engine.matcher.aliases = self.stratagem_manager.aliases

        # 重新同步编辑器的数据引用（load_stratagems 会创建新对象）
        self.editor_tab._load_data()

        # 刷新主界面全局指令勾选框
        new_global = self.stratagem_manager.AVAILABLE_GLOBAL_COMMANDS
        self.main_tab.refresh_global_commands(new_global)

        # 刷新主界面和测试界面的战备列表
        all_names = self.stratagem_manager.get_all_names()
        self.main_tab.refresh_stratagem_names(all_names)
        self.test_tab.refresh_stratagem_names(all_names)

        # 如果引擎正在运行，重启监听使新数据立即生效
        if self.engine_running:
            self.engine.stop()
            self.engine.start()
            self.log_manager.log("战备指令已更新并热重载，监听已自动重启。")
        else:
            self.log_manager.log("战备指令已更新，下次启动监听时生效。")

if __name__ == "__main__":
    app = StratagemApp()
    app.mainloop()
