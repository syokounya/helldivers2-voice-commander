"""
音频预处理模块
提供降噪、回音消除、音量归一化等功能
"""
import numpy as np
from collections import deque


class AudioProcessor:
    """音频预处理器"""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        enable_noise_gate: bool = True,
        noise_gate_threshold: float = 0.01,
        enable_echo_cancellation: bool = True,
        echo_delay_samples: int = 3200,  # 匹配音频块大小
        volume_boost: float = 3.0,  # 音量放大倍数
    ):
        self.sample_rate = sample_rate
        self.enable_noise_gate = enable_noise_gate
        self.noise_gate_threshold = noise_gate_threshold
        self.enable_echo_cancellation = enable_echo_cancellation
        self.echo_delay_samples = echo_delay_samples
        self.volume_boost = volume_boost
        
        # 回音消除缓冲区
        self.echo_buffer = deque(maxlen=echo_delay_samples)
        
        # 噪音门状态
        self.noise_gate_open = False
        self.noise_gate_smoothing = 0.85  # 降低平滑系数，响应更快
        
        # 音量归一化
        self.target_rms = 0.15  # 提高目标音量
        self.max_gain = 5.0  # 提高最大增益
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """
        处理音频数据
        
        Args:
            audio_data: 输入音频数据 (int16)
        
        Returns:
            处理后的音频数据 (int16)
        """
        # 转换为 float32 进行处理
        audio_float = audio_data.astype(np.float32) / 32768.0
        
        # 1. 简单的回音消除（减去延迟的信号）
        if self.enable_echo_cancellation:
            audio_float = self._cancel_echo(audio_float)
        
        # 2. 噪音门（过滤低音量噪音）
        if self.enable_noise_gate:
            audio_float = self._apply_noise_gate(audio_float)
        
        # 3. 音量归一化
        audio_float = self._normalize_volume(audio_float)
        
        # 4. 响度放大（最后一步，确保音量足够）
        audio_float = audio_float * self.volume_boost
        
        # 5. 限制在 [-1, 1] 范围内，避免削波
        audio_float = np.clip(audio_float, -1.0, 1.0)
        
        # 转换回 int16
        audio_int16 = (audio_float * 32768.0).astype(np.int16)
        return audio_int16
    
    def _cancel_echo(self, audio: np.ndarray) -> np.ndarray:
        """
        简单的回音消除
        通过减去延迟的信号来消除回音
        """
        # 如果缓冲区为空，初始化为零
        if len(self.echo_buffer) == 0:
            for _ in range(self.echo_delay_samples):
                self.echo_buffer.append(0.0)
        
        # 获取延迟的信号（取前 N 个样本，N = 当前音频长度）
        delayed_signal = np.array(list(self.echo_buffer)[:len(audio)])
        
        # 将当前音频添加到缓冲区
        for sample in audio:
            self.echo_buffer.append(sample)
        
        # 减去延迟信号的一部分（回音通常比原信号弱）
        echo_reduction_factor = 0.3
        result = audio - (delayed_signal * echo_reduction_factor)
        
        return result
    
    def _apply_noise_gate(self, audio: np.ndarray) -> np.ndarray:
        """
        应用噪音门
        当音量低于阈值时，将音频静音
        """
        # 计算 RMS（均方根）音量
        rms = np.sqrt(np.mean(audio ** 2))
        
        # 平滑的噪音门开关
        if rms > self.noise_gate_threshold:
            target_gate = 1.0
        else:
            target_gate = 0.0
        
        # 平滑过渡
        self.noise_gate_open = (
            self.noise_gate_smoothing * self.noise_gate_open +
            (1 - self.noise_gate_smoothing) * target_gate
        )
        
        # 应用门控
        return audio * self.noise_gate_open
    
    def _normalize_volume(self, audio: np.ndarray) -> np.ndarray:
        """
        音量归一化
        将音频音量调整到目标水平
        """
        # 计算当前 RMS
        rms = np.sqrt(np.mean(audio ** 2))
        
        if rms < 1e-6:  # 避免除以零
            return audio
        
        # 计算增益
        gain = self.target_rms / rms
        gain = min(gain, self.max_gain)  # 限制最大增益
        
        # 应用增益
        normalized = audio * gain
        
        # 限制在 [-1, 1] 范围内
        normalized = np.clip(normalized, -1.0, 1.0)
        
        return normalized


class SimpleVAD:
    """
    简单的语音活动检测（Voice Activity Detection）
    用于区分语音和非语音（噪音、静音）
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration_ms: int = 30,
        energy_threshold: float = 0.01,  # 进一步降低默认阈值
        zero_crossing_threshold: int = 20,  # 进一步降低过零率阈值
        pre_speech_buffer_frames: int = 3,  # 保留说话前的帧数
    ):
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.energy_threshold = energy_threshold
        self.zero_crossing_threshold = zero_crossing_threshold
        self.pre_speech_buffer_frames = pre_speech_buffer_frames
        
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        
        # 状态跟踪
        self.speech_frames = 0
        self.silence_frames = 0
        self.is_speaking = False
        
        # 预缓冲区（保留说话前的音频）
        self.pre_buffer = deque(maxlen=pre_speech_buffer_frames)
    
    def is_speech(self, audio_data: np.ndarray) -> tuple:
        """
        判断音频帧是否包含语音
        
        Args:
            audio_data: 音频数据 (int16)
        
        Returns:
            (is_speech, buffered_audio): 是否为语音，以及包含预缓冲的音频
        """
        # 转换为 float
        audio_float = audio_data.astype(np.float32) / 32768.0
        
        # 1. 能量检测
        energy = np.sqrt(np.mean(audio_float ** 2))
        
        # 2. 过零率检测（语音通常有较高的过零率）
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_float)))) / 2
        
        # 判断是否为语音
        is_speech_frame = (
            energy > self.energy_threshold and
            zero_crossings > self.zero_crossing_threshold
        )
        
        was_speaking = self.is_speaking
        
        # 状态平滑
        if is_speech_frame:
            self.speech_frames += 1
            self.silence_frames = 0
            if self.speech_frames > 1:  # 只需1帧就认为是语音，更快响应
                self.is_speaking = True
        else:
            self.silence_frames += 1
            self.speech_frames = 0
            if self.silence_frames > 20:  # 增加到20帧，避免过早停止
                self.is_speaking = False
        
        # 如果刚开始说话，返回预缓冲 + 当前帧
        if self.is_speaking and not was_speaking and len(self.pre_buffer) > 0:
            # 合并预缓冲和当前音频
            buffered_frames = list(self.pre_buffer) + [audio_data]
            buffered_audio = np.concatenate(buffered_frames)
            self.pre_buffer.clear()  # 清空预缓冲
            return True, buffered_audio
        
        # 如果正在说话，直接返回当前帧
        if self.is_speaking:
            return True, audio_data
        
        # 如果不是语音，添加到预缓冲区
        self.pre_buffer.append(audio_data.copy())
        return False, audio_data
    
    def reset(self):
        """重置状态"""
        self.speech_frames = 0
        self.silence_frames = 0
        self.is_speaking = False
        self.pre_buffer.clear()
