"""
Vosk 离线语音识别引擎
"""
import json
import os
import threading
import queue
from typing import Callable, Optional
import numpy as np
import sounddevice as sd


class VoskASREngine:
    """Vosk 离线语音识别引擎"""
    
    def __init__(
        self,
        model_path: str = "./vosk",
        sample_rate: int = 16000,
        on_result_callback: Optional[Callable[[str, bool], None]] = None,
        on_status_callback: Optional[Callable[[str, str, str], None]] = None,
    ):
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.on_result_callback = on_result_callback
        self.on_status_callback = on_status_callback
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._audio_stream = None
        self._recognizer = None
        self._model = None
        
        # 状态管理
        self._status = "未连接"
        self._error_message = ""
        self._error_analysis = ""
        
        # 音频队列
        self._audio_queue = queue.Queue()
    
    def _update_status(self, status: str, error_msg: str = "", analysis: str = ""):
        """更新状态并通知回调"""
        self._status = status
        self._error_message = error_msg
        self._error_analysis = analysis
        if self.on_status_callback:
            self.on_status_callback(status, error_msg, analysis)
    
    def _check_model(self) -> bool:
        """检查模型是否存在"""
        if not os.path.exists(self.model_path):
            self._update_status("错误", 
                f"模型路径不存在: {self.model_path}",
                "解决方案：\n"
                "1. 下载 Vosk 中文模型（推荐 vosk-model-cn-0.22）\n"
                "2. 从 https://alphacephei.com/vosk/models 下载\n"
                "3. 解压到程序目录下的 ./vosk 文件夹\n"
                "4. 确保路径为 ./vosk/am, ./vosk/conf 等文件夹"
            )
            return False
        
        # 检查模型文件
        required_files = ["am", "conf", "graph"]
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(self.model_path, f))]
        
        if missing_files:
            self._update_status("错误",
                f"模型文件不完整，缺少: {', '.join(missing_files)}",
                "解决方案：\n"
                "1. 重新下载完整的 Vosk 模型\n"
                "2. 确保解压后的文件夹包含 am, conf, graph 等子文件夹\n"
                "3. 模型下载地址: https://alphacephei.com/vosk/models"
            )
            return False
        
        return True
    
    def _load_model(self) -> bool:
        """加载 Vosk 模型"""
        try:
            # 延迟导入，避免没有安装 vosk 时报错
            import vosk
            
            self._update_status("连接中", "", "正在加载 Vosk 离线模型...")
            
            if not self._check_model():
                return False
            
            # 加载模型
            self._model = vosk.Model(self.model_path)
            self._recognizer = vosk.KaldiRecognizer(self._model, self.sample_rate)
            self._recognizer.SetWords(True)
            
            self._update_status("已连接", "", "Vosk 离线识别已就绪")
            return True
            
        except ImportError:
            self._update_status("错误",
                "未安装 vosk 库",
                "解决方案：\n"
                "1. 打开命令行\n"
                "2. 运行: pip install vosk\n"
                "3. 重启程序"
            )
            return False
        except Exception as e:
            self._update_status("错误",
                f"加载模型失败: {str(e)}",
                "可能原因：\n"
                "1. 模型文件损坏\n"
                "2. 模型版本不兼容\n"
                "解决方案：重新下载模型并解压"
            )
            return False
    
    def _audio_callback(self, indata, frames, time, status):
        """音频输入回调"""
        if status:
            print(f"音频输入状态: {status}")
        
        # 将音频数据放入队列
        self._audio_queue.put(bytes(indata))
    
    def _recognition_loop(self):
        """识别循环"""
        try:
            while self._running:
                try:
                    # 从队列获取音频数据
                    data = self._audio_queue.get(timeout=0.1)
                    
                    if self._recognizer.AcceptWaveform(data):
                        # 完整句子识别完成
                        result = json.loads(self._recognizer.Result())
                        text = result.get("text", "").strip()
                        
                        if text and self.on_result_callback:
                            self.on_result_callback(text, True)
                    else:
                        # 部分识别结果
                        partial_result = json.loads(self._recognizer.PartialResult())
                        text = partial_result.get("partial", "").strip()
                        
                        if text and self.on_result_callback:
                            self.on_result_callback(text, False)
                
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"识别出错: {e}")
                    continue
        
        except Exception as e:
            self._update_status("错误", f"识别循环异常: {str(e)}", 
                "可能原因：音频处理出错\n解决方案：重启监听")
    
    def start(self):
        """启动识别"""
        if self._running:
            return
        
        # 加载模型
        if not self._load_model():
            return
        
        self._running = True
        
        try:
            # 启动音频流
            self._audio_stream = sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,  # 0.5秒 @ 16kHz
                dtype="int16",
                channels=1,
                callback=self._audio_callback,
            )
            self._audio_stream.start()
            
            # 启动识别线程
            self._thread = threading.Thread(target=self._recognition_loop, daemon=True)
            self._thread.start()
            
            self._update_status("已连接", "", "Vosk 离线识别运行中")
            
        except Exception as e:
            self._running = False
            self._update_status("错误", f"启动失败: {str(e)}",
                "可能原因：\n"
                "1. 麦克风设备不可用\n"
                "2. 音频设备被占用\n"
                "解决方案：检查麦克风设置，关闭其他使用麦克风的程序")
    
    def stop(self):
        """停止识别"""
        self._running = False
        
        if self._audio_stream:
            self._audio_stream.stop()
            self._audio_stream.close()
            self._audio_stream = None
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        
        # 清空队列
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break
        
        self._update_status("未连接", "", "")
