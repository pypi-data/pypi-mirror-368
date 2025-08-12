"""
配置资源
"""

import logging

logger = logging.getLogger(__name__)

from typing import Any

from ..models import ToolResponse


class ConfigResources:
    """配置资源处理类"""

    def __init__(self, config):
        self.config = config

    def register(self, mcp):
        """注册资源到MCP服务器"""

        @mcp.resource("mcp://config/media")
        async def get_media() -> dict[str, Any]:
            """获取支持的媒体渠道列表"""
            return await self._get_media()

        @mcp.resource("mcp://config/group_keys")
        async def get_group_keys() -> dict[str, Any]:
            """获取支持的分组维度"""
            return await self._get_group_keys()

    async def _get_media(self) -> dict[str, Any]:
        """获取媒体渠道列表"""
        media_descriptions = {
            "gdt": "广点通",
            "tt": "今日头条",
            "bd": "百度",
            "bdss": "百度搜索",
            "bz": "B站",
            "zh": "知乎",
            "uc": "UC",
            "dx": "抖小广告量",
            "sphdr": "视频号达人",
            "xt": "星图",
            "gg": "谷歌",
            "nature": "自然量",
        }

        supported_media = list(self.config.SUPPORTED_MEDIA)
        data = {
            "media": [
                {"id": m, "name": media_descriptions.get(m, m)} for m in supported_media
            ]
        }

        return ToolResponse.success_response(
            data=data,
            record_count=len(supported_media),
        ).to_dict()

    async def _get_group_keys(self) -> dict[str, Any]:
        """获取分组维度"""
        supported_group_keys = self.config.SUPPORTED_GROUP_KEYS
        items = [
            {"key": key, "name": desc} for key, desc in supported_group_keys.items()
        ]

        return ToolResponse.success_response(
            data={"group_keys": items},
            record_count=len(items),
        ).to_dict()
