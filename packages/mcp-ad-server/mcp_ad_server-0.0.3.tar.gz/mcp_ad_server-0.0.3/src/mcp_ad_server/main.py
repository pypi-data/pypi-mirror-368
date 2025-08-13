#!/usr/bin/env python3
"""
广告投放数据平台 MCP 服务器
"""
import asyncio
import logging
import sys

from mcp.server.fastmcp import FastMCP

from .config import Config
from .managers import IndicatorManager, PropmapManager
from .resources import ConfigResources, IndicatorResources, MappingResources
from .services import BiApiClient
from .tools import AdQueryTool, GameIndicatorQueryTool, MaterialQueryTool

# 配置日志
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class AdMCPServer:
    """广告MCP服务器主类"""

    def __init__(self):
        # 初始化MCP服务器
        self.mcp = FastMCP(Config.SERVER_NAME)

        # 初始化服务层
        self.api_client = BiApiClient()
        self.indicator_manager = IndicatorManager()
        self.propmap_manager = PropmapManager()

        # 初始化MCP组件
        self._init_tools()
        self._init_resources()
        self._init_prompts()

        logger.info("MCP服务器组件初始化完成")

    def _init_tools(self):
        """初始化MCP工具"""
        # 广告查询工具
        self.ad_query_tool = AdQueryTool(
            self.api_client, self.indicator_manager, self.propmap_manager, Config
        )
        self.ad_query_tool.register(self.mcp)

        # 素材查询工具
        self.material_query_tool = MaterialQueryTool(
            self.api_client, self.indicator_manager, self.propmap_manager, Config
        )
        self.material_query_tool.register(self.mcp)

        # 游戏指标查询工具
        self.indicator_query_tool = GameIndicatorQueryTool(
            self.indicator_manager, Config
        )
        self.indicator_query_tool.register(self.mcp)

        logger.info("MCP工具注册完成")

    def _init_resources(self):
        """初始化MCP资源"""
        # 指标资源
        self.indicator_resources = IndicatorResources(self.indicator_manager, Config)
        self.indicator_resources.register(self.mcp)

        # 映射资源
        self.mapping_resources = MappingResources(self.propmap_manager)
        self.mapping_resources.register(self.mcp)

        # 配置资源
        self.config_resources = ConfigResources(Config)
        self.config_resources.register(self.mcp)

        logger.info("MCP资源注册完成")

    def _init_prompts(self):
        """初始化MCP提示（暂未实现）"""
        # 提示功能将在后续版本中实现
        logger.info("MCP提示功能暂未实现")

    async def initialize(self):
        """初始化服务器，加载静态数据"""
        try:
            logger.info("初始化MCP服务器...")

            # 加载指标数据（包括游戏配置）
            await self.indicator_manager.load_data()

            # 加载字段映射
            await self.propmap_manager.load_mappings()

            # 测试API连接
            connection_status = await self.api_client.test_connection()
            if connection_status:
                logger.info("API连接测试成功")
            else:
                logger.warning("API连接测试失败，请检查配置")

            logger.info("MCP服务器初始化完成")

        except Exception as e:
            logger.error(f"服务器初始化失败: {e}")
            raise

    def run(self):
        """启动MCP服务器"""
        logger.info(f"启动MCP服务器: {Config.SERVER_NAME} v{Config.SERVER_VERSION}")
        return self.mcp.run()


def main():
    """主函数"""
    try:
        # 创建服务器实例
        server = AdMCPServer()

        # 异步初始化
        async def init_and_run():
            await server.initialize()
            return server

        # 运行初始化
        server = asyncio.run(init_and_run())

        # 启动服务器
        server.run()

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务器...")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
