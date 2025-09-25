"""
预处理器模块
对输入数据进行标准化处理、内容识别和分类标记
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import nltk
from collections import Counter

class Preprocessor:
    """数据预处理器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化预处理器

        Args:
            config: 配置参数
        """
        self.config = config or self._default_config()
        self.pipeline = [
            self.normalize_format,
            self.clean_content,
            self.identify_entities,
            self.extract_keywords,
            self.analyze_sentiment,
            self.extract_structure
        ]

    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "remove_html": True,
            "normalize_whitespace": True,
            "extract_urls": True,
            "extract_emails": True,
            "max_keywords": 10,
            "min_keyword_length": 2
        }

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行预处理流水线

        Args:
            data: 输入适配器产生的标准化数据

        Returns:
            预处理后的数据
        """
        result = data.copy()

        # 执行预处理管道
        for processor in self.pipeline:
            result = processor(result)

        # 添加处理时间戳
        result["preprocessed_at"] = datetime.now().isoformat()

        return result

    def normalize_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式规范化"""
        content = data.get("content", "")

        if self.config["remove_html"]:
            content = self._remove_html_tags(content)

        if self.config["normalize_whitespace"]:
            content = self._normalize_whitespace(content)

        data["normalized_content"] = content
        return data

    def clean_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """内容清洗"""
        content = data.get("normalized_content", data.get("content", ""))

        # 提取URL
        if self.config["extract_urls"]:
            urls = self._extract_urls(content)
            data["urls"] = urls
            # 从内容中移除URL
            for url in urls:
                content = content.replace(url, " [URL] ")

        # 提取邮箱
        if self.config["extract_emails"]:
            emails = self._extract_emails(content)
            data["emails"] = emails
            # 从内容中移除邮箱
            for email in emails:
                content = content.replace(email, " [EMAIL] ")

        # 移除特殊字符
        content = self._remove_special_chars(content)

        data["cleaned_content"] = content
        return data

    def identify_entities(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """实体识别"""
        content = data.get("cleaned_content", "")

        entities = {
            "dates": self._extract_dates(content),
            "numbers": self._extract_numbers(content),
            "mentions": self._extract_mentions(content),
            "hashtags": self._extract_hashtags(content)
        }

        # 识别中文实体
        if data.get("language") == "zh":
            entities.update({
                "chinese_names": self._extract_chinese_names(content),
                "chinese_orgs": self._extract_chinese_orgs(content)
            })

        data["entities"] = entities
        return data

    def extract_keywords(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """关键词提取"""
        content = data.get("cleaned_content", "")

        # 基于词频的关键词提取
        keywords = self._extract_keywords_by_frequency(content)

        # 基于模式的关键词提取
        pattern_keywords = self._extract_pattern_keywords(content)

        # 合并并排序
        all_keywords = list(set(keywords + pattern_keywords))[:self.config["max_keywords"]]

        data["keywords"] = all_keywords
        return data

    def analyze_sentiment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """情感分析"""
        content = data.get("cleaned_content", "")

        # 简单的情感分析（基于关键词）
        sentiment_score = 0
        positive_words = ["好", "优秀", "成功", "完成", "提升", "改进", "good", "excellent", "success"]
        negative_words = ["问题", "错误", "失败", "延迟", "困难", "bad", "error", "fail", "problem"]

        for word in positive_words:
            sentiment_score += content.lower().count(word)

        for word in negative_words:
            sentiment_score -= content.lower().count(word)

        # 归一化到 -1 到 1
        if sentiment_score > 0:
            sentiment = "positive"
        elif sentiment_score < 0:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        data["sentiment"] = {
            "label": sentiment,
            "score": min(max(sentiment_score / 10, -1), 1)  # 简单归一化
        }

        return data

    def extract_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """结构提取"""
        content = data.get("content", "")

        structure = {
            "has_lists": bool(re.search(r'^\s*[-*•]\s+', content, re.MULTILINE)),
            "has_headers": bool(re.search(r'^#+\s+', content, re.MULTILINE)),
            "has_code_blocks": bool(re.search(r'```[\s\S]*?```', content)),
            "has_tables": bool(re.search(r'\|.*\|', content)),
            "paragraph_count": len(re.findall(r'\n\n+', content)) + 1,
            "sentence_count": len(re.findall(r'[.!?。！？]', content)),
            "word_count": len(content.split())
        }

        # 检测文档类型
        if structure["has_headers"] and structure["paragraph_count"] > 5:
            structure["document_type"] = "article"
        elif structure["has_lists"]:
            structure["document_type"] = "list"
        elif structure["has_code_blocks"]:
            structure["document_type"] = "technical"
        else:
            structure["document_type"] = "general"

        data["structure"] = structure
        return data

    # 辅助方法
    def _remove_html_tags(self, text: str) -> str:
        """移除HTML标签"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    def _normalize_whitespace(self, text: str) -> str:
        """规范化空白字符"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _extract_urls(self, text: str) -> List[str]:
        """提取URL"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)

    def _extract_emails(self, text: str) -> List[str]:
        """提取邮箱"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)

    def _remove_special_chars(self, text: str) -> str:
        """移除特殊字符"""
        # 保留中文、英文、数字和基本标点
        pattern = r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,!?;:，。！？；：\n]'
        return re.sub(pattern, ' ', text)

    def _extract_dates(self, text: str) -> List[str]:
        """提取日期"""
        date_patterns = [
            r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?',
            r'\d{1,2}[-/月]\d{1,2}[日]?',
            r'\d{4}年',
            r'今天|明天|昨天|前天|后天'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))
        return list(set(dates))

    def _extract_numbers(self, text: str) -> List[str]:
        """提取数字"""
        number_pattern = r'\b\d+(?:\.\d+)?(?:%|％)?\b'
        return re.findall(number_pattern, text)

    def _extract_mentions(self, text: str) -> List[str]:
        """提取@提及"""
        mention_pattern = r'@\w+'
        return re.findall(mention_pattern, text)

    def _extract_hashtags(self, text: str) -> List[str]:
        """提取话题标签"""
        hashtag_pattern = r'#\w+'
        return re.findall(hashtag_pattern, text)

    def _extract_chinese_names(self, text: str) -> List[str]:
        """提取中文人名（简单实现）"""
        # 这里应该使用NER模型，暂时用简单的规则
        name_pattern = r'[王李张刘陈杨黄赵吴周徐孙马朱胡林郭何高罗郑梁谢宋唐许韩冯邓曹彭曾萧田董潘袁于蒋蔡余杜叶程魏苏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤]\w{1,2}'
        names = re.findall(name_pattern, text)
        return list(set(names))[:10]  # 限制数量

    def _extract_chinese_orgs(self, text: str) -> List[str]:
        """提取中文机构名（简单实现）"""
        org_keywords = ["公司", "集团", "银行", "学校", "大学", "医院", "政府", "部门", "委员会"]
        orgs = []
        for keyword in org_keywords:
            pattern = r'\w{2,10}' + keyword
            orgs.extend(re.findall(pattern, text))
        return list(set(orgs))[:10]

    def _extract_keywords_by_frequency(self, text: str) -> List[str]:
        """基于词频提取关键词"""
        # 分词（简单实现）
        words = re.findall(r'\b\w+\b', text.lower())

        # 过滤停用词和短词
        stopwords = {"的", "是", "在", "和", "了", "与", "及", "等", "the", "is", "at", "on", "and", "a", "an"}
        words = [w for w in words if w not in stopwords and len(w) >= self.config["min_keyword_length"]]

        # 统计词频
        word_freq = Counter(words)

        # 返回高频词
        return [word for word, _ in word_freq.most_common(self.config["max_keywords"])]

    def _extract_pattern_keywords(self, text: str) -> List[str]:
        """基于模式提取关键词"""
        patterns = [
            r'(?:关于|针对|基于|通过)\s*(\w+)',
            r'(\w+)(?:系统|平台|框架|模块|功能)',
            r'(?:完成|实现|开发|设计|优化)\s*(\w+)'
        ]

        keywords = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            keywords.extend(matches)

        return list(set(keywords))


# 使用示例
if __name__ == "__main__":
    preprocessor = Preprocessor()

    # 测试数据
    test_data = {
        "content": """
        今天完成了AI工作台架构设计，主要包括以下几个模块：
        1. 输入适配器 - 处理不同类型的输入
        2. 预处理器 - 数据清洗和标准化
        3. 核心引擎 - 智能调度中心

        联系人：张三 @zhangsan
        邮箱：example@email.com
        网址：https://example.com

        #AI工作台 #架构设计
        """,
        "input_type": "text",
        "language": "zh"
    }

    result = preprocessor.process(test_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))