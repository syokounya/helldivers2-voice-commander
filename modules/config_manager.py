"""
配置管理模块：负责阿里云 API 密钥的加密存储和读取
"""
import json
import base64
import sys
import os
from pathlib import Path
from typing import Optional, Dict
from cryptography.fernet import Fernet


class ConfigManager:
    """管理阿里云 API 配置的加密存储"""
    
    def __init__(self, config_file: str = "config.enc"):
        # 获取正确的基础路径（支持 PyInstaller 打包）
        if getattr(sys, 'frozen', False):
            # 打包后的 exe 运行时
            base_path = Path(sys.executable).parent / "modules"
        else:
            # 开发环境
            base_path = Path(__file__).parent
        
        # 确保 modules 目录存在
        base_path.mkdir(parents=True, exist_ok=True)
        
        self.config_path = base_path / config_file
        self.key_path = base_path / ".key"
        self._ensure_key()
    
    def _ensure_key(self):
        """确保加密密钥存在"""
        if not self.key_path.exists():
            key = Fernet.generate_key()
            self.key_path.write_bytes(key)
        
    def _get_cipher(self) -> Fernet:
        """获取加密器"""
        key = self.key_path.read_bytes()
        return Fernet(key)
    
    def save_config(self, app_key: str, access_key_id: str, access_key_secret: str) -> None:
        """保存配置（加密）"""
        config = {
            "app_key": app_key,
            "access_key_id": access_key_id,
            "access_key_secret": access_key_secret,
        }
        cipher = self._get_cipher()
        json_str = json.dumps(config)
        encrypted = cipher.encrypt(json_str.encode('utf-8'))
        self.config_path.write_bytes(encrypted)
    
    def load_config(self) -> Optional[Dict[str, str]]:
        """加载配置（解密）"""
        if not self.config_path.exists():
            return None
        
        try:
            cipher = self._get_cipher()
            encrypted = self.config_path.read_bytes()
            decrypted = cipher.decrypt(encrypted)
            config = json.loads(decrypted.decode('utf-8'))
            return config
        except Exception:
            return None
    
    def has_config(self) -> bool:
        """检查是否已有配置"""
        return self.config_path.exists()
