"""
统一输入适配器模块
处理来自不同数据源的输入，将其标准化为内部处理格式
"""

import json
import os
from typing import Dict, Any, Union, Optional
from enum import Enum
from datetime import datetime
import hashlib

class InputType(Enum):
    """输入类型枚举"""
    TEXT = "text"
    AUDIO = "audio"
    FILE = "file"
    WEB = "web"
    IMAGE = "image"
    VIDEO = "video"

class ContentCategory(Enum):
    """内容分类枚举"""
    DIALOGUE = "dialogue"
    DOCUMENT = "document"
    TASK = "task"
    KNOWLEDGE = "knowledge"
    DECISION = "decision"
    QUERY = "query"

class InputAdapter:
    """统一输入适配器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化输入适配器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.processors = {
            InputType.TEXT: self._process_text,
            InputType.AUDIO: self._process_audio,
            InputType.FILE: self._process_file,
            InputType.WEB: self._process_web,
            InputType.IMAGE: self._process_image,
            InputType.VIDEO: self._process_video
        }

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "max_text_length": 100000,
            "supported_file_types": [".txt", ".md", ".pdf", ".docx", ".json"],
            "audio_formats": [".mp3", ".wav", ".m4a"],
            "image_formats": [".jpg", ".png", ".gif", ".webp"],
            "video_formats": [".mp4", ".avi", ".mov"]
        }

    def process_input(self,
                     data: Any,
                     input_type: Union[InputType, str],
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理输入数据，将其转换为标准格式

        Args:
            data: 输入数据
            input_type: 输入类型
            metadata: 元数据

        Returns:
            标准化的数据格式
        """
        if isinstance(input_type, str):
            input_type = InputType(input_type)

        # 生成唯一ID
        input_id = self._generate_id(data, input_type)

        # 基础元数据
        result = {
            "id": input_id,
            "timestamp": datetime.now().isoformat(),
            "input_type": input_type.value,
            "metadata": metadata or {},
            "raw_data": data
        }

        # 调用对应的处理器
        processor = self.processors.get(input_type)
        if processor:
            processed = processor(data, metadata)
            result.update(processed)

        # 自动分类
        result["category"] = self._classify_content(result)

        # 添加标签
        result["tags"] = self._extract_tags(result)

        return result

    def _generate_id(self, data: Any, input_type: InputType) -> str:
        """生成唯一ID"""
        content = f"{input_type.value}_{str(data)[:100]}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()

    def _process_text(self, data: str, metadata: Optional[Dict]) -> Dict[str, Any]:
        """处理文本输入"""
        return {
            "content": data[:self.config["max_text_length"]],
            "length": len(data),
            "language": self._detect_language(data),
            "format": "plain_text"
        }

    def _process_audio(self, data: Any, metadata: Optional[Dict]) -> Dict[str, Any]:
        """处理音频输入"""
        # 这里应该集成语音转文字服务
        return {
            "content": "Audio content placeholder",
            "duration": metadata.get("duration", 0) if metadata else 0,
            "format": metadata.get("format", "unknown") if metadata else "unknown",
            "transcription": None  # 待实现
        }

    def _process_file(self, data: str, metadata: Optional[Dict]) -> Dict[str, Any]:
        """处理文件输入"""
        if not os.path.exists(data):
            return {"error": "File not found", "content": ""}

        file_ext = os.path.splitext(data)[1].lower()
        if file_ext not in self.config["supported_file_types"]:
            return {"error": "Unsupported file type", "content": ""}

        try:
            with open(data, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "content": content,
                "file_path": data,
                "file_type": file_ext,
                "file_size": os.path.getsize(data)
            }
        except Exception as e:
            return {"error": str(e), "content": ""}

    def _process_web(self, data: str, metadata: Optional[Dict]) -> Dict[str, Any]:
        """处理网页输入"""
        # 这里应该集成网页爬虫或API
        return {
            "url": data,
            "content": "Web content placeholder",
            "domain": self._extract_domain(data),
            "fetched_at": datetime.now().isoformat()
        }

    def _process_image(self, data: Any, metadata: Optional[Dict]) -> Dict[str, Any]:
        """处理图像输入"""
        return {
            "content": "Image analysis placeholder",
            "format": metadata.get("format", "unknown") if metadata else "unknown",
            "dimensions": metadata.get("dimensions") if metadata else None,
            "ocr_text": None  # 待实现OCR
        }

    def _process_video(self, data: Any, metadata: Optional[Dict]) -> Dict[str, Any]:
        """处理视频输入"""
        return {
            "content": "Video analysis placeholder",
            "duration": metadata.get("duration", 0) if metadata else 0,
            "format": metadata.get("format", "unknown") if metadata else "unknown",
            "frames_extracted": 0  # 待实现关键帧提取
        }

    def _classify_content(self, data: Dict[str, Any]) -> str:
        """内容分类"""
        content = data.get("content", "")

        # 简单的基于关键词的分类
        if any(word in content.lower() for word in ["任务", "todo", "计划", "deadline"]):
            return ContentCategory.TASK.value
        elif any(word in content.lower() for word in ["决策", "选择", "方案", "建议"]):
            return ContentCategory.DECISION.value
        elif any(word in content.lower() for word in ["学习", "知识", "概念", "理论"]):
            return ContentCategory.KNOWLEDGE.value
        elif any(word in content.lower() for word in ["文档", "报告", "总结"]):
            return ContentCategory.DOCUMENT.value
        elif any(word in content.lower() for word in ["问", "什么", "如何", "为什么"]):
            return ContentCategory.QUERY.value
        else:
            return ContentCategory.DIALOGUE.value

    def _extract_tags(self, data: Dict[str, Any]) -> list:
        """提取标签"""
        tags = []

        # 基于类型的标签
        tags.append(data["input_type"])

        # 基于分类的标签
        tags.append(data["category"])

        # 基于内容的标签（待实现更智能的标签提取）
        content = data.get("content", "")
        if "AI" in content:
            tags.append("artificial_intelligence")
        if "代码" in content or "编程" in content:
            tags.append("programming")

        return list(set(tags))

    def _detect_language(self, text: str) -> str:
        """检测语言"""
        # 简单的中英文检测
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if chinese_chars > len(text) * 0.3:
            return "zh"
        return "en"

    def _extract_domain(self, url: str) -> str:
        """提取域名"""
        from urllib.parse import urlparse
        try:
            return urlparse(url).netloc
        except:
            return "unknown"


# 使用示例
if __name__ == "__main__":
    adapter = InputAdapter()

    # 处理文本输入
    text_result = adapter.process_input(
        "这是一个测试任务，需要在明天完成AI工作台的架构设计。",
        InputType.TEXT
    )
    print("Text processing result:", json.dumps(text_result, ensure_ascii=False, indent=2))

    # 处理文件输入
    file_result = adapter.process_input(
        "/path/to/document.md",
        InputType.FILE,
        {"source": "local_filesystem"}
    )
    print("\nFile processing result:", json.dumps(file_result, ensure_ascii=False, indent=2))