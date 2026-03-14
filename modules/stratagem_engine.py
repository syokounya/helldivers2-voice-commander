"""
战备执行引擎
整合语音识别、战备匹配和按键执行
"""
import time
from typing import Optional, Callable, List
from .aliyun_asr import AliyunASREngine
from .stratagem_manager import StratagemManager
from .stratagem_matcher import StratagemMatcher
from .key_executor import KeyExecutor


class StratagemEngine:
    """战备执行引擎（使用阿里云实时语音识别）"""
    
    def __init__(
        self,
        stratagem_manager: StratagemManager,
        log_callback: Optional[Callable[[str], None]] = None,
        key_log_callback: Optional[Callable[[str, List[str], List[str]], None]] = None,
    ):
        self.stratagem_manager = stratagem_manager
        self.matcher = StratagemMatcher(
            similarity_threshold=0.55,  # 进一步降低到 0.55
            aliases=stratagem_manager.aliases
        )
        self.key_executor = KeyExecutor()
        
        self._log_callback = log_callback
        self._key_log_callback = key_log_callback
        self._asr_engine: Optional[AliyunASREngine] = None
        self._running = False
        
        # 防止重复触发
        self._last_trigger_time = 0
        self._last_trigger_name = ""
        self._cooldown = 3.0  # 增加冷却时间到3秒
        
        # 防止重复识别
        self._last_recognized_text = ""
        self._last_recognized_time = 0
        self._recognition_cooldown = 1.5  # 识别去重时间
        
        # 上下文感知匹配（新增）
        self._recent_triggers = []  # 最近触发的战备列表
        self._context_window = 10.0  # 上下文窗口时间（秒）
        self._confusion_pairs = {
            # 容易混淆的战备对（说同样的词可能想要不同的战备）
            "加特林哨戒炮": ["轨道加特林", "重装加特林"],
            "轨道加特林": ["加特林哨戒炮", "重装加特林"],
            "重装加特林": ["加特林哨戒炮", "轨道加特林"],
            "机炮": ["轨道炮", "机枪哨戒炮"],
            "轨道炮": ["机炮"],
            "弹链榴弹发射器": ["榴弹发射器", "榴弹墙"],
            "榴弹发射器": ["弹链榴弹发射器", "榴弹墙"],
            "榴弹墙": ["弹链榴弹发射器", "榴弹发射器"],
            "飞鹰500kg炸弹": ["地狱火炸弹"],
            "地狱火炸弹": ["飞鹰500kg炸弹"],
            "通用机枪": ["重机枪", "盟友机枪"],
            "重机枪": ["通用机枪", "盟友机枪"],
            "盟友机枪": ["通用机枪", "重机枪"],
        }
    
    def _log(self, message: str) -> None:
        """输出日志"""
        if self._log_callback:
            self._log_callback(message)
        else:
            print(message)
    
    def _log_keys(self, name: str, seq: List[str], arrows: List[str]) -> None:
        """记录按键序列"""
        if self._key_log_callback:
            self._key_log_callback(name, seq, arrows)
    
    def set_dry_run(self, value: bool) -> None:
        """设置测试模式"""
        self.key_executor.set_dry_run(value)
    
    def set_credentials(self, app_key: str, access_key_id: str, access_key_secret: str,
                        enable_noise_suppression: bool = True,
                        enable_voice_detection: bool = True,
                        enable_local_processing: bool = True,
                        on_status_callback: Optional[Callable[[str, str, str], None]] = None):
        """设置阿里云凭证"""
        self._asr_engine = AliyunASREngine(
            app_key=app_key,
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            sample_rate=16000,
            on_result_callback=self._on_asr_result,
            on_status_callback=on_status_callback,
            enable_noise_suppression=enable_noise_suppression,
            enable_voice_detection=enable_voice_detection,
            enable_local_processing=enable_local_processing,
        )
    
    def _on_asr_result(self, text: str, is_final: bool):
        """阿里云识别结果回调"""
        # 只处理最终结果，忽略部分识别
        if not is_final:
            return
        
        # 过滤太短的识别结果
        if len(text) < 2:
            return
        
        # 去除标点符号和空格
        text = text.strip().replace("。", "").replace("，", "").replace("、", "")
        
        # 检查是否是重复的识别结果
        current_time = time.time()
        if (text == self._last_recognized_text and 
            current_time - self._last_recognized_time < self._recognition_cooldown):
            # 重复识别，忽略
            return
        
        # 更新识别记录
        self._last_recognized_text = text
        self._last_recognized_time = current_time
        
        self._log(f"识别文本：{text}")
        
        # 获取当前允许的战备列表
        candidates = [
            name for name in self.stratagem_manager.get_all_names()
            if self.stratagem_manager.is_allowed(name)
        ]
        
        # 清理过期的上下文记录
        current_time = time.time()
        self._recent_triggers = [
            (t, name) for t, name in self._recent_triggers
            if current_time - t < self._context_window
        ]
        
        # 检查是否是重复指令（可能想切换到混淆的战备）
        confusion_target = None
        if self._recent_triggers:
            # 检查最近2秒内是否有相同或相似的识别文本
            recent_same_text = []
            for t, name in self._recent_triggers:
                if current_time - t < 2.0:
                    # 计算识别文本与上次识别文本的相似度
                    text_similarity = self.matcher.calculate_similarity(text, self._last_recognized_text)
                    if text_similarity >= 0.7:  # 70%相似就认为是重复
                        recent_same_text.append((t, name))
            
            if len(recent_same_text) >= 1:  # 如果有相似的识别文本
                last_time, last_name = recent_same_text[-1]
                self._log(f"🔍 检测到相似识别文本：'{text}' ≈ '{self._last_recognized_text}'，上次触发：{last_name}")
                
                # 检查是否是混淆对
                if last_name in self._confusion_pairs:
                    confusion_candidates = self._confusion_pairs[last_name]
                    self._log(f"📋 混淆候选：{confusion_candidates}")
                    
                    # 找到下一个可用的混淆战备
                    for conf_name in confusion_candidates:
                        if conf_name in candidates:
                            # 简单匹配检查
                            match_score = self.matcher.calculate_similarity(text, conf_name)
                            self._log(f"  - {conf_name}: 相似度 {match_score:.2f}")
                            if match_score >= 0.3:  # 降低到30%
                                confusion_target = conf_name
                                self._log(f"🔄 切换到混淆战备：{confusion_target}")
                                break
                else:
                    # 即使不在预定义混淆对中，也尝试智能切换
                    # 找到与上次触发战备相似的其他战备
                    similar_stratagems = []
                    for cand in candidates:
                        if cand != last_name:
                            sim = self.matcher.calculate_similarity(last_name, cand)
                            if sim >= 0.6:  # 60%相似的战备
                                similar_stratagems.append((cand, sim))
                    
                    if similar_stratagems:
                        similar_stratagems.sort(key=lambda x: x[1], reverse=True)
                        self._log(f"🔍 发现相似战备：{[s[0] for s in similar_stratagems[:3]]}")
                        
                        # 尝试匹配到相似战备
                        for sim_name, sim_score in similar_stratagems:
                            match_score = self.matcher.calculate_similarity(text, sim_name)
                            if match_score >= 0.3:
                                confusion_target = sim_name
                                self._log(f"🔄 智能切换到相似战备：{confusion_target}")
                                break
        
        # 如果检测到混淆切换，直接使用
        if confusion_target:
            chosen = confusion_target
        else:
            # 构建上下文权重
            context_boost = {}
            for t, name in self._recent_triggers:
                # 最近使用的战备，降低匹配阈值（提高权重）
                age = current_time - t
                boost = max(0, 1.0 - age / self._context_window)  # 0-1之间
                context_boost[name] = boost
            
            # 匹配战备名（带上下文权重）
            chosen = self.matcher.match(text, candidates, context_boost)
        
        if not chosen:
            self._log(f"未找到匹配：'{text}' 不在允许列表中")
            return
        
        # 记录匹配结果（帮助调试）
        if text != chosen:
            self._log(f"模糊匹配：'{text}' → '{chosen}'")
        
        # 检查冷却时间，防止重复触发
        if (current_time - self._last_trigger_time < self._cooldown and 
            chosen == self._last_trigger_name):
            self._log(f"⏱️ 冷却中，忽略：{chosen}")
            return
        
        self._log(f"✅ 触发战备：{chosen}")
        self.execute_stratagem(chosen)
        
        # 更新触发记录
        self._last_trigger_time = current_time
        self._last_trigger_name = chosen
        
        # 添加到上下文记录
        self._recent_triggers.append((current_time, chosen))
    
    def start(self) -> None:
        """启动语音识别"""
        if self._running or not self._asr_engine:
            return
        self._running = True
        self._asr_engine.start()
    
    def stop(self) -> None:
        """停止语音识别"""
        if not self._running or not self._asr_engine:
            return
        self._running = False
        self._asr_engine.stop()
    
    def execute_stratagem(self, name: str) -> None:
        """执行战备"""
        # 获取按键序列
        seq = self.stratagem_manager.get_sequence(name)
        if not seq:
            return
        
        # 执行按键
        arrows = self.key_executor.execute(seq)
        
        # 记录日志
        self._log_keys(name, seq, arrows)
        
        if self.key_executor.dry_run:
            self._log(f"[测试模式] 仅显示 {name} 的按键序列，不发送到游戏。")
