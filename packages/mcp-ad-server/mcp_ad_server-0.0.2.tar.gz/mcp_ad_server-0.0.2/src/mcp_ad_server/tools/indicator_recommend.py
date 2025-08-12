"""
指标推荐工具

从main.py提取的recommend_indicators工具实现。
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class IndicatorRecommendTool:
    """指标推荐工具类"""

    def __init__(self, indicator_manager, config):
        self.indicator_manager = indicator_manager
        self.config = config

    def register(self, mcp):
        """注册工具到MCP服务器"""

        @mcp.tool()
        async def recommend_indicators(
            business_scenario: str, current_indicators: list[str] | None = None
        ) -> dict[str, Any]:
            """
            基于业务场景智能推荐相关指标

            ⚠️  推荐升级：现在支持基于游戏的智能推荐！建议使用 recommend_indicators_by_game_scenario
                工具，它会根据具体游戏筛选可用指标，避免推荐不支持的指标。

            Args:
                business_scenario: 业务场景，如"投放启动"、"效果监控"、"短期评估"、"深度分析"、"数据对账"、"风险预警"、"财务核算"
                current_indicators: 当前已选指标，用于补充推荐

            Returns:
                推荐的指标列表和分组信息（注意：此工具返回全局指标，不考虑游戏兼容性）
            """
            return await self._recommend_indicators(
                business_scenario, current_indicators
            )

    async def _recommend_indicators(
        self, business_scenario: str, current_indicators: list[str] | None = None
    ) -> dict[str, Any]:
        """实际的推荐实现"""
        try:
            # 基于场景推荐
            scenario_indicators = (
                self.indicator_manager.recommend_indicators_by_scenario(
                    business_scenario
                )
            )

            # 基于当前指标推荐相关指标
            related_indicators = []
            if current_indicators:
                related_indicators = (
                    self.indicator_manager.recommend_related_indicators(
                        current_indicators
                    )
                )

            # 合并推荐结果，去重
            all_recommended = list(set(scenario_indicators + related_indicators))

            # 获取对应分组信息
            scenario_mapping = self.config.SCENARIO_MAPPING
            group_id = scenario_mapping.get(business_scenario)
            group_info = (
                self.indicator_manager.get_group(group_id) if group_id else None
            )

            return {
                "success": True,
                "business_scenario": business_scenario,
                "scenario_indicators": scenario_indicators,
                "related_indicators": related_indicators,
                "all_recommended": all_recommended,
                "group_info": group_info,
                "total_recommended": len(all_recommended),
            }

        except Exception as e:
            logger.error(f"指标推荐失败: {e}")
            return {"success": False, "error": str(e)}
