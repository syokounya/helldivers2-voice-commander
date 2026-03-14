"""
战备匹配模块
负责从识别文本中匹配战备名称
"""
import difflib
from typing import Optional, List, Dict
from pypinyin import lazy_pinyin


class StratagemMatcher:
    """战备匹配器"""
    
    def __init__(self, similarity_threshold: float = 0.7, aliases: Optional[Dict[str, str]] = None):
        self.similarity_threshold = similarity_threshold
        self.aliases = aliases or {}
    
    def calculate_similarity(self, text: str, name: str) -> float:
        """
        计算两个字符串的相似度
        
        Args:
            text: 识别的文本
            name: 战备名称
            
        Returns:
            相似度分数 (0-1)
        """
        # 字面相似度
        char_score = difflib.SequenceMatcher(None, text, name).ratio()
        # 拼音相似度
        py_score = self._pinyin_similarity(text, name)
        # 取最大值
        return max(char_score, py_score)
    
    def _pinyin_similarity(self, a: str, b: str) -> float:
        """计算拼音相似度"""
        pa = " ".join(lazy_pinyin(a))
        pb = " ".join(lazy_pinyin(b))
        return difflib.SequenceMatcher(None, pa, pb).ratio()
    
    def match(self, text: str, candidates: List[str], context_boost: Optional[Dict[str, float]] = None) -> Optional[str]:
        """
        从候选列表中匹配最佳战备名
        
        Args:
            text: 识别的文本
            candidates: 候选战备名列表
            context_boost: 上下文权重字典 {战备名: 权重(0-1)}
            
        Returns:
            匹配到的战备名，如果没有匹配则返回 None
        """
        text = text.strip()
        if not text or not candidates:
            return None
        
        context_boost = context_boost or {}
        
        # 0) 最优先：别名精确匹配
        if text in self.aliases:
            alias_target = self.aliases[text]
            if alias_target in candidates:
                return alias_target
        
        # 1) 精确匹配
        if text in candidates:
            return text
        
        # 2) 前缀匹配（支持说前几个字）
        prefix_hits = []
        for name in candidates:
            if name.startswith(text):
                # 计算基础分数
                base_score = len(text) / len(name)
                # 应用上下文权重
                boost = context_boost.get(name, 0)
                final_score = base_score + boost * 0.3  # 上下文权重占30%
                prefix_hits.append((name, final_score))
        
        if prefix_hits:
            # 如果识别文本 ≥2 个字
            if len(text) >= 2:
                prefix_hits.sort(key=lambda x: x[1], reverse=True)
                # 应用上下文权重后，可能优先返回最近使用的
                return prefix_hits[0][0]
        
        # 3) 部分包含（识别文本在战备名中）
        # 例如："500" 在 "飞鹰500kg炸弹" 中，"飞鹰500" 在 "飞鹰500kg炸弹" 中
        partial_hits = []
        for name in candidates:
            if text in name:
                # 计算匹配度
                base_score = len(text) / len(name)
                # 应用上下文权重
                boost = context_boost.get(name, 0)
                final_score = base_score + boost * 0.3
                partial_hits.append((name, final_score))
        
        if partial_hits:
            # 返回得分最高的（考虑上下文权重）
            partial_hits.sort(key=lambda x: x[1], reverse=True)
            return partial_hits[0][0]
        
        # 4) 反向包含 + 拼音验证（战备名在识别文本中）
        # 例如："机炮" 在 "击炮炮" 中
        substr_hits = []
        for name in candidates:
            if name in text:
                # 计算匹配度
                match_ratio = len(name) / len(text)
                # 同时检查拼音相似度，避免误匹配
                py_sim = self._pinyin_similarity(name, text)
                # 综合评分
                score = match_ratio * 0.6 + py_sim * 0.4
                substr_hits.append((name, score, match_ratio))
        
        if substr_hits:
            # 按综合得分排序
            substr_hits.sort(key=lambda x: x[1], reverse=True)
            best_match, score, ratio = substr_hits[0]
            # 要求：长度匹配 ≥40% 且 综合得分 ≥0.5
            if ratio >= 0.4 and score >= 0.5:
                return best_match
        
        # 5) 数字优先匹配
        # 提取识别文本中的数字
        text_digits = ''.join(c for c in text if c.isdigit())
        if text_digits:
            for name in candidates:
                name_digits = ''.join(c for c in name if c.isdigit())
                # 数字完全匹配
                if text_digits == name_digits:
                    return name
        
        # 6) 关键词匹配（支持说中间的关键词）
        if len(text) >= 2:
            keyword_hits = []
            for name in candidates:
                # 检查识别文本的每个字符是否按顺序出现在战备名中
                text_idx = 0
                for char in name:
                    if text_idx < len(text) and char == text[text_idx]:
                        text_idx += 1
                
                # 如果所有字符都匹配上了
                if text_idx == len(text):
                    # 计算基础匹配度
                    base_score = len(text) / len(name)
                    # 应用上下文权重
                    boost = context_boost.get(name, 0)
                    final_score = base_score + boost * 0.3
                    keyword_hits.append((name, final_score))
            
            if keyword_hits:
                # 返回得分最高的
                keyword_hits.sort(key=lambda x: x[1], reverse=True)
                if keyword_hits[0][1] >= 0.3:  # 至少30%匹配
                    return keyword_hits[0][0]
        
        # 7) 拼音相似度（应用上下文权重）
        best_name = None
        best_score = 0.0
        
        for name in candidates:
            py_score = self._pinyin_similarity(text, name)
            # 应用上下文权重
            boost = context_boost.get(name, 0)
            final_score = py_score + boost * 0.2  # 上下文权重占20%
            
            if final_score > best_score:
                best_score = final_score
                best_name = name
        
        # 动态阈值：有上下文权重时降低阈值
        threshold = 0.55  # 基础阈值降低到0.55
        if best_name and best_name in context_boost:
            threshold = max(0.4, 0.55 - context_boost[best_name] * 0.3)  # 最低降到0.4
        
        if best_name and best_score >= threshold:
            return best_name
        
        return None
