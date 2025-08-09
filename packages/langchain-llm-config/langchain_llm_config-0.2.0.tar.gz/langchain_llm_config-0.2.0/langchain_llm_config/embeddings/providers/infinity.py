import asyncio
import time
from typing import Any, Dict, List

from langchain_core.embeddings import Embeddings

from ..base import BaseEmbeddingProvider

# isort:skip_file
from langchain_community.embeddings import (
    InfinityEmbeddings as LangchainInfinityEmbeddings,
)


class InfinityEmbeddingProvider(BaseEmbeddingProvider):
    """Infinity嵌入提供者"""

    def __init__(self, config: Dict[str, Any], **kwargs: Any) -> None:
        """
        初始化Infinity嵌入提供者

        Args:
            config: 配置字典，包含如下键:
                - api_base: API基础URL
                - model_name: 模型名称
                - timeout: 超时时间（可选）
            **kwargs: 额外参数
        """
        # 创建参数字典，避免传递不支持的参数
        embedding_params = {
            "model": config["model_name"],
            "infinity_api_url": config["api_base"],
        }

        self._embeddings = LangchainInfinityEmbeddings(**embedding_params)
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

        # 所有重试都失败，使用内置模型或返回错误
        raise Exception(f"嵌入文本失败: {str(last_error)}")

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
                result = self._embeddings.embed_documents(texts)
                return result  # type: ignore[no-any-return]
            except Exception as e:
                retry_count += 1
                last_error = e

                if retry_count < self._max_retries:
                    # 指数退避重试
                    wait_time = self._retry_delay * (2 ** (retry_count - 1))
                    await asyncio.sleep(wait_time)

        # 所有重试都失败，使用内置模型或返回错误
        raise Exception(f"嵌入文本失败: {str(last_error)}")
