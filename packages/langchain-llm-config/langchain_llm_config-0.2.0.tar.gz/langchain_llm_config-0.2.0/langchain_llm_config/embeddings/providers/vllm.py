import asyncio
import os
import time
from pathlib import Path
from typing import Any, Dict, List

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from ..base import BaseEmbeddingProvider


class VLLMEmbeddingProvider(BaseEmbeddingProvider):
    """VLLM嵌入提供者（使用OpenAI兼容接口）"""

    def __init__(self, config: Dict[str, Any], **kwargs: Any) -> None:
        """
        初始化VLLM嵌入提供者

        Args:
            config: 配置字典，包含如下键:
                - model_name: 模型名称
                - api_base: API基础URL
                - api_key: API密钥（可选）
                - timeout: 超时时间（可选）
            **kwargs: 额外参数
        """
        # Calculate tiktoken cache directory
        tiktoken_cache_dir = str(
            Path(__file__).parent.parent.parent / ".tiktoken_cache"
        )

        # Set tiktoken cache directory environment variable
        os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir

        embedding_params = {
            "model": config["model_name"],
            "api_key": config.get("api_key"),
            "base_url": config.get(
                "api_base", "http://localhost:8000/v1"
            ),  # Make api_base optional
            "timeout": config.get("timeout", 30),
            "tiktoken_enabled": True,
        }

        # 记录初始化信息（隐藏敏感信息）
        safe_params = embedding_params.copy()
        if "api_key" in safe_params:
            safe_params["api_key"] = "******" if safe_params["api_key"] else None

        # 添加其他kwargs
        embedding_params.update(kwargs)

        self._embeddings = OpenAIEmbeddings(**embedding_params)
        self._max_retries = 3
        self._retry_delay = 1.0  # 初始重试延迟（秒）

    @property
    def embedding_model(self) -> Embeddings:
        """获取嵌入模型"""
        return self._embeddings  # type: ignore[no-any-return]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        嵌入文本列表（同步版本）

        Args:
            texts: 要嵌入的文本列表

        Returns:
            嵌入向量列表
        """
        if not texts:
            return []

        retry_count = 0
        last_error = None

        while retry_count < self._max_retries:
            try:
                result = self._embeddings.embed_documents(texts)
                return result  # type: ignore[no-any-return]
            except Exception as e:
                retry_count += 1
                last_error = e

                if retry_count < self._max_retries:
                    # 指数退避重试
                    wait_time = self._retry_delay * (2 ** (retry_count - 1))
                    time.sleep(wait_time)

        # 所有重试都失败，报告错误
        raise Exception(f"VLLM嵌入文本失败: {str(last_error)}")

    async def embed_texts_async(self, texts: List[str]) -> List[List[float]]:
        """
        嵌入文本列表（异步版本）

        Args:
            texts: 要嵌入的文本列表

        Returns:
            嵌入向量列表
        """
        if not texts:
            return []

        retry_count = 0
        last_error = None

        while retry_count < self._max_retries:
            try:
                result = await self._embeddings.aembed_documents(texts)
                return result  # type: ignore[no-any-return]
            except Exception as e:
                retry_count += 1
                last_error = e

                if retry_count < self._max_retries:
                    # 指数退避重试
                    wait_time = self._retry_delay * (2 ** (retry_count - 1))
                    await asyncio.sleep(wait_time)

        # 所有重试都失败，报告错误
        raise Exception(f"VLLM嵌入文本失败: {str(last_error)}")
