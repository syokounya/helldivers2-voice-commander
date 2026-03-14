"""
阿里云实时语音识别引擎
"""
import json
import threading
import time
import uuid
from typing import Callable, Optional
import numpy as np
import sounddevice as sd
import websocket
import requests
from .audio_processor import AudioProcessor, SimpleVAD


class AliyunASREngine:
    """阿里云实时语音识别引擎"""
    
    def __init__(
        self,
        app_key: str,
        access_key_id: str,
        access_key_secret: str,
        sample_rate: int = 16000,
        on_result_callback: Optional[Callable[[str, bool], None]] = None,
        enable_noise_suppression: bool = True,
        enable_voice_detection: bool = True,
        enable_local_processing: bool = True,
    ):
        self.app_key = app_key
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.sample_rate = sample_rate
        self.on_result_callback = on_result_callback
        self.enable_noise_suppression = enable_noise_suppression
        self.enable_voice_detection = enable_voice_detection
        self.enable_local_processing = enable_local_processing
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._ws: Optional[websocket.WebSocketApp] = None
        self._audio_stream = None
        self._token = None
        
        # 本地音频处理器
        if enable_local_processing:
            self.audio_processor = AudioProcessor(
                sample_rate=sample_rate,
                enable_noise_gate=True,
                noise_gate_threshold=0.008,  # 进一步降低阈值，更灵敏
                enable_echo_cancellation=True,
                echo_delay_samples=3200,  # 匹配音频块大小
                volume_boost=3.0,  # 3倍音量放大
            )
            # 不再使用 VAD，让阿里云端的 enable_voice_detection 来处理
            self.vad = None
        else:
            self.audio_processor = None
            self.vad = None
    
    def _get_token(self) -> str:
        """获取阿里云 Token"""
        import hmac
        import hashlib
        import base64
        from datetime import datetime
        from urllib.parse import quote
        
        # 构建请求参数
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        nonce = str(uuid.uuid4())
        
        params = {
            'AccessKeyId': self.access_key_id,
            'Action': 'CreateToken',
            'Format': 'JSON',
            'RegionId': 'cn-shanghai',
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': nonce,
            'SignatureVersion': '1.0',
            'Timestamp': timestamp,
            'Version': '2019-02-28'
        }
        
        # 构建签名字符串
        sorted_params = sorted(params.items())
        query_string = '&'.join([f'{quote(k, safe="")}={quote(str(v), safe="")}' for k, v in sorted_params])
        string_to_sign = f'GET&%2F&{quote(query_string, safe="")}'
        
        # 计算签名
        signature = base64.b64encode(
            hmac.new(
                (self.access_key_secret + '&').encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode('utf-8')
        
        params['Signature'] = signature
        
        # 发送请求
        url = "https://nls-meta.cn-shanghai.aliyuncs.com/"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"Token 请求状态码: {response.status_code}")
            print(f"Token 响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                token = result.get("Token", {}).get("Id")
                if token:
                    print(f"成功获取 Token: {token[:20]}...")
                    return token
                else:
                    print(f"响应中没有 Token: {result}")
            else:
                print(f"获取 Token 失败，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
            return None
        except Exception as e:
            print(f"获取 Token 出错：{e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_ws_url(self) -> str:
        """构建 WebSocket URL"""
        if not self._token:
            self._token = self._get_token()
            if not self._token:
                raise Exception("无法获取阿里云 Token，请检查 AccessKeyId 和 AccessKeySecret")
        
        # 使用 Token 方式连接
        url = (
            f"wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1"
            f"?appkey={self.app_key}"
            f"&token={self._token}"
        )
        return url
    
    def _on_ws_open(self, ws):
        """WebSocket 连接建立"""
        print(f"WebSocket 连接已建立，准备发送开始识别指令...")
        print(f"使用的 APP KEY: {self.app_key[:10]}...")
        
        # 生成符合阿里云要求的 ID（去掉连字符）
        message_id = str(uuid.uuid4()).replace('-', '')
        task_id = str(uuid.uuid4()).replace('-', '')
        
        # 发送开始识别指令
        start_msg = {
            "header": {
                "message_id": message_id,
                "task_id": task_id,
                "namespace": "SpeechTranscriber",
                "name": "StartTranscription",
                "appkey": self.app_key,
            },
            "payload": {
                "format": "pcm",
                "sample_rate": self.sample_rate,
                "enable_intermediate_result": True,
                "enable_punctuation_prediction": True,
                "enable_inverse_text_normalization": True,
                # 降噪和回音消除
                "enable_noise_suppression": self.enable_noise_suppression,
                # 语音检测（过滤非语音段）
                "enable_voice_detection": self.enable_voice_detection,
                "max_sentence_silence": 800,  # 句尾静音检测（毫秒）
            }
        }
        print(f"发送开始识别指令: {json.dumps(start_msg, ensure_ascii=False)}")
        ws.send(json.dumps(start_msg))
        
        # 启动音频发送线程
        threading.Thread(target=self._send_audio, args=(ws,), daemon=True).start()
    
    def _on_ws_message(self, ws, message):
        """接收识别结果"""
        try:
            result = json.loads(message)
            print(f"收到 WebSocket 消息: {message}")
            
            header = result.get("header", {})
            name = header.get("name", "")
            status = header.get("status")
            
            # 检查错误
            if status and status != 20000000:
                status_text = header.get("status_text", "")
                print(f"识别错误 - 状态码: {status}, 错误信息: {status_text}")
                if status == 40000002:
                    print("错误：APP KEY 不正确！请检查智能语音交互控制台中的项目 AppKey")
                return
            
            if name == "TranscriptionResultChanged":
                # 中间结果
                payload = result.get("payload", {})
                text = payload.get("result", "")
                if text and self.on_result_callback:
                    self.on_result_callback(text, False)
            
            elif name == "SentenceEnd":
                # 最终结果
                payload = result.get("payload", {})
                text = payload.get("result", "")
                if text and self.on_result_callback:
                    self.on_result_callback(text, True)
        
        except Exception as e:
            print(f"解析识别结果出错：{e}")
    
    def _on_ws_error(self, ws, error):
        """WebSocket 错误"""
        error_str = str(error)
        print(f"WebSocket 错误：{error_str}")
        
        # 解析错误码
        if 'opcode=8' in error_str:
            # WebSocket 关闭帧
            if '40000002' in error_str or b'40000002' in str(error).encode():
                print("=" * 60)
                print("错误：APP KEY 不正确！")
                print("请检查：")
                print("1. 在阿里云控制台 → 智能语音交互 → 项目管理")
                print("2. 查看或创建项目")
                print("3. 复制正确的 AppKey（不是 AccessKey）")
                print("4. 在程序的'设置'Tab 中重新填写并保存")
                print("=" * 60)
    
    def _on_ws_close(self, ws, close_status_code, close_msg):
        """WebSocket 关闭"""
        print(f"WebSocket 连接已关闭 - 状态码: {close_status_code}, 消息: {close_msg}")
    
    def _send_audio(self, ws):
        """持续发送音频数据"""
        try:
            self._audio_stream = sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=3200,  # 200ms @ 16kHz
                dtype="int16",
                channels=1,
            )
            self._audio_stream.start()
            
            while self._running and ws.sock and ws.sock.connected:
                data, _ = self._audio_stream.read(3200)
                audio_array = np.frombuffer(data, dtype=np.int16)
                
                # 本地音频预处理
                if self.enable_local_processing and self.audio_processor:
                    # 直接处理音频，不使用 VAD（避免截断开头）
                    audio_to_send = self.audio_processor.process(audio_array)
                else:
                    # 即使不启用完整预处理，也进行响度放大
                    audio_float = audio_array.astype(np.float32) / 32768.0
                    # 简单的响度放大（3倍）
                    audio_float = audio_float * 3.0
                    # 限制在 [-1, 1] 范围内，避免削波
                    audio_float = np.clip(audio_float, -1.0, 1.0)
                    audio_to_send = (audio_float * 32768.0).astype(np.int16)
                
                audio_bytes = audio_to_send.tobytes()
                ws.send(audio_bytes, opcode=websocket.ABNF.OPCODE_BINARY)
                time.sleep(0.01)
        
        except Exception as e:
            print(f"音频发送出错：{e}")
        finally:
            if self._audio_stream:
                self._audio_stream.stop()
                self._audio_stream.close()
    
    def start(self):
        """启动识别"""
        if self._running:
            return
        
        self._running = True
        
        def run_ws():
            url = self._build_ws_url()
            self._ws = websocket.WebSocketApp(
                url,
                on_open=self._on_ws_open,
                on_message=self._on_ws_message,
                on_error=self._on_ws_error,
                on_close=self._on_ws_close,
            )
            self._ws.run_forever()
        
        self._thread = threading.Thread(target=run_ws, daemon=True)
        self._thread.start()
    
    def stop(self):
        """停止识别"""
        self._running = False
        
        if self._ws:
            # 发送停止指令
            try:
                # 生成符合阿里云要求的 ID（去掉连字符）
                message_id = str(uuid.uuid4()).replace('-', '')
                task_id = str(uuid.uuid4()).replace('-', '')
                
                stop_msg = {
                    "header": {
                        "message_id": message_id,
                        "task_id": task_id,
                        "namespace": "SpeechTranscriber",
                        "name": "StopTranscription",
                        "appkey": self.app_key,
                    }
                }
                self._ws.send(json.dumps(stop_msg))
            except Exception:
                pass
            
            self._ws.close()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
