"""
指标管理器 - 管理指标定义和分组
"""

import json
from typing import Any

import aiofiles

from ..config import Config
from .base import Manager


class IndicatorManager(Manager):
    """指标管理器类"""

    def __init__(self):
        super().__init__()
        self.groups: dict[str, dict[str, Any]] = {}
        self.games: dict[str, dict[str, Any]] = {}

    async def load_indicators(self):
        """加载所有指标定义"""
        indicators_dir = Config.INDICATORS_DIR

        if not indicators_dir.exists():
            self.logger.warning(f"指标目录不存在: {indicators_dir}")
            return

        try:
            indicator_files = list(indicators_dir.glob("*.json"))
            self.logger.info(f"发现{len(indicator_files)}个指标文件")

            for file_path in indicator_files:
                indicator_name = file_path.stem  # 文件名不含扩展名
                try:
                    async with aiofiles.open(file_path, encoding="utf-8") as f:
                        content = await f.read()
                        indicator_data = json.loads(content)
                        self.data[indicator_name] = indicator_data

                except Exception as e:
                    self.logger.error(f"加载指标文件失败 {file_path}: {e}")

            self.logger.info(f"成功加载{len(self.data)}个指标定义")

        except Exception as e:
            self.logger.error(f"加载指标目录失败: {e}")
            raise

    async def load_groups(self):
        """加载所有指标分组"""
        groups_dir = Config.GROUPS_DIR

        if not groups_dir.exists():
            self.logger.warning(f"指标分组目录不存在: {groups_dir}")
            return

        try:
            group_files = list(groups_dir.glob("*.json"))
            self.logger.info(f"发现{len(group_files)}个分组文件")

            for file_path in group_files:
                group_name = file_path.stem
                try:
                    async with aiofiles.open(file_path, encoding="utf-8") as f:
                        content = await f.read()
                        group_data = json.loads(content)
                        self.groups[group_name] = group_data

                except Exception as e:
                    self.logger.error(f"加载分组文件失败 {file_path}: {e}")

            self.logger.info(f"成功加载{len(self.groups)}个指标分组")

        except Exception as e:
            self.logger.error(f"加载分组目录失败: {e}")
            raise

    async def load_games(self):
        """加载游戏指标配置"""
        games_dir = Config.GAMES_DIR

        if not games_dir.exists():
            self.logger.warning(f"游戏指标目录不存在: {games_dir}")
            return

        try:
            game_files = list(games_dir.glob("*.json"))
            self.logger.info(f"发现{len(game_files)}个游戏指标文件")

            for file_path in game_files:
                app_id = file_path.stem  # 文件名就是app_id
                try:
                    async with aiofiles.open(file_path, encoding="utf-8") as f:
                        content = await f.read()
                        game_data = json.loads(content)
                        self.games[app_id] = game_data

                except Exception as e:
                    self.logger.error(f"加载游戏指标文件失败 {file_path}: {e}")

            self.logger.info(f"成功加载{len(self.games)}个游戏指标配置")

        except Exception as e:
            self.logger.error(f"加载游戏指标目录失败: {e}")
            raise

    async def load_data(self) -> None:
        """实现基类的抽象方法加载数据"""
        await self.load_indicators()
        await self.load_groups()
        await self.load_games()
        self.loaded = True
        self.logger.info("指标管理器数据加载完成")

    async def initialize(self):
        """初始化管理器"""
        if self.is_loaded():
            return
        await self.load_data()
        self.logger.info("指标管理器初始化完成")

    def get_indicator(self, name: str) -> dict[str, Any] | None:
        """获取指标定义"""
        return self.get_data(name)

    def get_all_indicators(self) -> dict[str, dict[str, Any]]:
        """获取所有指标定义"""
        return self.get_all_data()

    def get_indicator_names(self) -> list[str]:
        """获取所有指标名称"""
        return list(self.data.keys())

    def search_indicators(self, keyword: str) -> list[str]:
        """搜索指标（按名称或描述）"""
        results = []
        keyword_lower = keyword.lower()

        for name, data in self.data.items():
            if (
                keyword_lower in name.lower()
                or keyword_lower in data.get("description", "").lower()
            ):
                results.append(name)

        return results

    def get_group(self, group_id: str) -> dict[str, Any] | None:
        """获取指标分组"""
        return self.groups.get(group_id)

    def get_all_groups(self) -> dict[str, dict[str, Any]]:
        """获取所有指标分组"""
        return self.groups.copy()

    def get_group_names(self) -> list[str]:
        """获取所有分组名称"""
        return list(self.groups.keys())

    def get_indicators_by_group(self, group_id: str) -> list[str]:
        """根据分组获取指标列表"""
        group = self.groups.get(group_id)
        if group:
            return group.get("indicators", [])
        return []

    def recommend_indicators_by_scenario(self, scenario: str) -> list[str]:
        """基于业务场景推荐指标"""
        group_id = Config.SCENARIO_MAPPING.get(scenario)
        if group_id:
            return self.get_indicators_by_group(group_id)
        return []

    def validate_indicators(self, indicators: list[str]) -> list[str]:
        """验证指标名称，返回无效的指标列表"""
        invalid_indicators = []
        for indicator in indicators:
            if indicator not in self.data:
                invalid_indicators.append(indicator)
        return invalid_indicators

    def get_indicator_stats(self) -> dict[str, Any]:
        """获取指标统计信息"""
        return {
            "total_indicators": self.get_data_count(),
            "total_groups": len(self.groups),
            "groups_info": [
                {
                    "group_id": group_id,
                    "name": group_data.get("name", ""),
                    "indicator_count": len(group_data.get("indicators", [])),
                }
                for group_id, group_data in self.groups.items()
            ],
        }

    def get_game_available_indicators_for_ad(self, app_id: str) -> list[str]:
        """获取指定游戏的广告数据查询可用指标列表"""
        game_data = self.games.get(app_id)
        if game_data:
            api_config = game_data.get("apis", {}).get("GetAdCountList", {})
            return api_config.get("available_indicators", [])
        return []

    def get_game_available_indicators_for_material(self, app_id: str) -> list[str]:
        """获取指定游戏的素材数据查询可用指标列表"""
        game_data = self.games.get(app_id)
        if game_data:
            api_config = game_data.get("apis", {}).get("GetMaterialCountList", {})
            return api_config.get("available_indicators", [])
        return []

    def get_all_games(self) -> dict[str, dict[str, Any]]:
        """获取所有游戏配置"""
        return self.games.copy()

    def get_game_info(self, app_id: str) -> dict[str, Any] | None:
        """获取指定游戏的信息"""
        return self.games.get(app_id)

    def validate_indicators_for_ad_query(
        self, indicators: list[str], app_id: str
    ) -> tuple[list[str], list[str]]:
        """验证广告数据查询的指标列表，返回(有效指标, 无效指标)"""
        available_indicators = self.get_game_available_indicators_for_ad(app_id)

        if not available_indicators:
            # 如果没有找到游戏指标配置，使用原有的全局指标验证
            invalid_indicators = self.validate_indicators(indicators)
            valid_indicators = [
                ind for ind in indicators if ind not in invalid_indicators
            ]
            return valid_indicators, invalid_indicators

        valid_indicators = []
        invalid_indicators = []

        for indicator in indicators:
            if indicator in available_indicators:
                valid_indicators.append(indicator)
            else:
                invalid_indicators.append(indicator)

        return valid_indicators, invalid_indicators

    def validate_indicators_for_material_query(
        self, indicators: list[str], app_id: str
    ) -> tuple[list[str], list[str]]:
        """验证素材数据查询的指标列表，返回(有效指标, 无效指标)"""
        available_indicators = self.get_game_available_indicators_for_material(app_id)

        if not available_indicators:
            # 如果没有找到游戏指标配置，使用原有的全局指标验证
            invalid_indicators = self.validate_indicators(indicators)
            valid_indicators = [
                ind for ind in indicators if ind not in invalid_indicators
            ]
            return valid_indicators, invalid_indicators

        valid_indicators = []
        invalid_indicators = []

        for indicator in indicators:
            if indicator in available_indicators:
                valid_indicators.append(indicator)
            else:
                invalid_indicators.append(indicator)

        return valid_indicators, invalid_indicators

    def recommend_indicators(
        self, scenario: str, app_id: str, query_type: str = "ad_query"
    ) -> list[str]:
        """基于游戏和业务场景推荐指标

        Args:
            scenario: 业务场景
            app_id: 游戏ID
            query_type: 查询类型，"ad_query" 或 "material_query"

        Returns:
            推荐的指标列表
        """
        # 先获取场景推荐的指标
        scenario_indicators = self.recommend_indicators_by_scenario(scenario)

        # 根据查询类型获取游戏可用指标
        if query_type == "ad_query":
            available_indicators = self.get_game_available_indicators_for_ad(app_id)
        else:  # material_query
            available_indicators = self.get_game_available_indicators_for_material(
                app_id
            )

        if not available_indicators:
            # 如果没有游戏特定配置，返回场景指标
            return scenario_indicators

        # 返回场景指标与游戏可用指标的交集
        return [ind for ind in scenario_indicators if ind in available_indicators]

    def recommend_indicators_for_ad_query_by_game_scenario(
        self, scenario: str, app_id: str
    ) -> list[str]:
        """基于游戏和业务场景推荐广告查询指标（兼容性包装）"""
        return self.recommend_indicators(scenario, app_id, "ad_query")

    def recommend_indicators_for_material_query_by_game_scenario(
        self, scenario: str, app_id: str
    ) -> list[str]:
        """基于游戏和业务场景推荐素材查询指标（兼容性包装）"""
        return self.recommend_indicators(scenario, app_id, "material_query")

    async def reload(self):
        """重新加载指标和分组数据"""
        self.clear_data()
        self.groups.clear()
        self.games.clear()

        await self.initialize()
        self.logger.info("指标管理器数据已重新加载")
