"""
素材查询工具

从main.py提取的query_material_data工具实现。
"""

import logging
from typing import Any

from ..models import ErrorCodes, ErrorMessages, ToolPayload, ToolResponse

logger = logging.getLogger(__name__)


class MaterialQueryTool:
    """素材查询工具类"""

    def __init__(self, api_client, indicator_manager, propmap_manager, config):
        self.api_client = api_client
        self.indicator_manager = indicator_manager
        self.propmap_manager = propmap_manager
        self.config = config

    def register(self, mcp):
        """注册工具到MCP服务器"""

        @mcp.tool()
        async def query_material_data(
            start_date: str,
            end_date: str,
            indicators: list[str],
            app_id: str = self.config.DEFAULT_APPID,
            group_key: str = "",
            is_low_quality: int = -1,
            is_inefficient: int = -1,
            is_deep: bool = False,
            is_old_table: bool = False,
            # 媒体和投手参数
            media: list[str] | None = None,
            media_buyers: list[str] | None = None,
            # 制作和创意人员参数
            producers: list[str] | None = None,
            creative_users: list[str] | None = None,
            # 账户参数
            cids: list[str] | None = None,
            # 素材相关参数 (originality_xxx)
            originality_ids: list[str] | None = None,
            originality_names: list[str] | None = None,
            originality_types: list[str] | None = None,
            # 广告组和创意参数
            adgroup_ids: list[str] | None = None,
            creative_ids: list[str] | None = None,
            component_ids: list[str] | None = None,
        ) -> dict[str, Any]:
            """
            查询素材效果数据

            ⚠️  重要提示：不同游戏支持的指标不同，调用前请先使用 get_game_available_indicators 或
                validate_indicators_for_game 工具检查指定游戏的可用指标，避免查询失败。

            Args:
                # 基础参数
                start_date: 查询范围开始时间，格式YYYY-MM-DD
                end_date: 查询范围结束时间，格式YYYY-MM-DD
                indicators: 指标列表，本工具会自动添加"日期"指标。
                           ⚠️ 建议先调用 get_game_available_indicators 确认游戏支持的指标
                app_id: 游戏ID，默认59(正统三国)，可选值：59(正统三国)、61(银河战舰)、48(开心十三张)、78(哈局成语大师)
                group_key: 分组维度，默认空字符串（不分组），可选值：
                          vp_campaign_id(广告ID)、vp_adgroup_id(项目ID)、vp_originality_id(创意ID)、vp_advert_pitcher_id(投手)、dt_vp_fx_cid(self_cid)、vp_advert_channame(媒体)
                          ⚠️ 设置后返回数据中会包含groupKey字段，自动映射为对应的中文名称
                is_low_quality: AD优/低质素材筛选，默认-1(全选)，可选值：-1(全选)、1(低质)、2(优质)
                is_inefficient: 低效素材筛选，默认-1(全选)，可选值：-1(全选)、1(是)、2(否)
                is_deep: 是否获取下探UI数据，默认False
                is_old_table: 是否使用旧报表，默认False，当media包含gdt(广点通)时可选

                # 媒体和投手参数
                media: 媒体渠道筛选，可选值：全选、gdt(广点通)、tt(今日头条)、bd(百度)、bdss(百度搜索)、bz(B站)、zh(知乎)、uc(UC)、dx(抖小广告量)、sphdr(视频号达人)、xt(星图)、gg(谷歌)、nature(自然量)
                media_buyers: 投手筛选，可选值：lll(李霖林)、dcx(戴呈翔)、yxr(尹欣然)、syf(施逸风)、gyy(郭耀月)、zp(张鹏)、zmn(宗梦男)、fx2.0

                # 制作和创意人员参数
                producers: 制作人筛选，可选值：蔡睿韬、王子鹏、颜隆隆、郑显洋、李霖林、张鹏、谢雨、占雪涵、方晓聪、刘伍攀、张航、刘锦、翁国峻、刘婷婷、张泽祖、AI、戴呈翔、其他
                creative_users: 创意人筛选，可选值：蔡睿韬、陈朝晖、王子鹏、颜隆隆、郑显洋、李霖林、张鹏、谢雨、周义骅、占雪涵、方晓聪、陈朝辉、刘伍攀、张航、郭耀月、宗梦男、刘锦、翁国峻、刘婷婷、秦翎丰、张泽祖、戴呈翔、AI、其他

                # 账户参数
                cids: 广告账户CID列表筛选

                # 素材相关参数 (originality_xxx)
                originality_ids: 素材ID列表筛选
                originality_names: 素材名称列表筛选
                originality_types: 素材类型筛选，可选值：图片、视频

                # 广告组和创意参数
                adgroup_ids: 广告组ID列表筛选
                creative_ids: 创意ID列表筛选
                component_ids: 组件ID列表筛选

            Returns:
                查询结果包含数据列表和元数据：
                - success: 查询是否成功
                - data.records: 强类型素材数据记录列表
                - data.rows: 已做中文映射的展示数据
                - data.total: 总条数
                - data.summary: 汇总数据（如果后端提供了总计行）
                - metadata: 查询元数据（查询时间、记录数等）

            Note:
                - 支持按多种维度分组统计
                - 支持低效和低质素材筛选
                - 无效指标会被忽略，不会影响查询执行
            """
            return await self._query_material_data(
                start_date=start_date,
                end_date=end_date,
                indicators=indicators,
                app_id=app_id,
                group_key=group_key,
                is_low_quality=is_low_quality,
                is_inefficient=is_inefficient,
                is_deep=is_deep,
                is_old_table=is_old_table,
                media=media,
                media_buyers=media_buyers,
                producers=producers,
                creative_users=creative_users,
                cids=cids,
                originality_ids=originality_ids,
                originality_names=originality_names,
                originality_types=originality_types,
                adgroup_ids=adgroup_ids,
                creative_ids=creative_ids,
                component_ids=component_ids,
            )

    async def _query_material_data(
        self,
        start_date: str,
        end_date: str,
        indicators: list[str],
        app_id: str,
        group_key: str = "",
        is_low_quality: int = -1,
        is_inefficient: int = -1,
        is_deep: bool = False,
        is_old_table: bool = False,
        # 媒体和投手参数
        media: list[str] | None = None,
        media_buyers: list[str] | None = None,
        # 制作和创意人员参数
        producers: list[str] | None = None,
        creative_users: list[str] | None = None,
        # 账户参数
        cids: list[str] | None = None,
        # 素材相关参数 (originality_xxx)
        originality_ids: list[str] | None = None,
        originality_names: list[str] | None = None,
        originality_types: list[str] | None = None,
        # 广告组和创意参数
        adgroup_ids: list[str] | None = None,
        creative_ids: list[str] | None = None,
        component_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """实际的查询实现"""
        try:
            # 验证指标
            invalid_indicators = self.indicator_manager.validate_indicators(indicators)
            if invalid_indicators:
                msg, suggestions = ErrorMessages.invalid_parameter(
                    "indicators", str(invalid_indicators)
                )
                return ToolResponse.error_response(
                    code=ErrorCodes.INVALID_INDICATORS,
                    message=msg,
                    suggestions=suggestions,
                ).to_dict()

            # 调用API查询数据
            result = await self.api_client.get_material_count_list(
                app_id=app_id,
                start_date=start_date,
                end_date=end_date,
                indicators=indicators,
                group_key=group_key,
                is_low_quality=is_low_quality,
                is_inefficient=is_inefficient,
                is_deep=is_deep,
                is_old_table=is_old_table,
                media=media,
                media_buyers=media_buyers,
                producers=producers,
                creative_users=creative_users,
                cids=cids,
                originality_ids=originality_ids,
                originality_names=originality_names,
                originality_types=originality_types,
                adgroup_ids=adgroup_ids,
                creative_ids=creative_ids,
                component_ids=component_ids,
            )

            # 转换Pydantic响应为字典格式以供映射使用
            result_dict = {
                "code": result.code,
                "msg": result.msg,
                "data": {
                    "list": result.data.items if result.data else [],
                },
            }

            # 将字段名映射为显示名称
            mapped_result = self.propmap_manager.map_fields_to_display(
                result_dict, "GetMaterialCountList", group_key
            )

            # 处理汇总数据映射
            mapped_summary = None
            if result.data and result.data.summary:
                # 将summary也进行中文字段映射
                summary_dict = {"data": {"list": [result.data.summary]}}
                mapped_summary_result = self.propmap_manager.map_fields_to_display(
                    summary_dict, "GetMaterialCountList", group_key
                )
                mapped_summary = mapped_summary_result.get("data", {}).get(
                    "list", [{}]
                )[0]

            # 提取列名和行数据
            mapped_rows = mapped_result.get("data", {}).get("list", [])
            columns, rows = self._extract_columns_and_rows(mapped_rows)

            payload = ToolPayload(
                columns=columns,
                rows=rows,
                total=len(result.data.items) if result.data else 0,
                summary=mapped_summary,
            )

            return ToolResponse.success_response(
                data=payload,
                record_count=len(result.data.items) if result.data else 0,
                api_endpoint="/ad/GetMaterialCountList",
                date_range=f"{start_date} 至 {end_date}",
                indicators_count=len(columns),
            ).to_dict()

        except Exception as e:
            logger.error(f"查询素材数据失败: {e}")
            msg, suggestions = ErrorMessages.api_request_failed(str(e))
            return ToolResponse.error_response(
                code=ErrorCodes.API_REQUEST_FAILED,
                message=msg,
                details=str(e),
                suggestions=suggestions,
                api_endpoint="/ad/GetMaterialCountList",
                date_range=f"{start_date} 至 {end_date}",
                indicators_count=len(indicators),
            ).to_dict()

    def _extract_columns_and_rows(
        self, mapped_rows: list[dict]
    ) -> tuple[list[str], list[list[Any]]]:
        """从字典列表提取列名和行数据

        Args:
            mapped_rows: 已映射的字典格式数据行

        Returns:
            tuple: (columns, rows) - 列名列表和二维数组数据
        """
        if not mapped_rows:
            return [], []

        # 从第一行提取列名，保持字段顺序
        columns = list(mapped_rows[0].keys())

        # 转换为二维数组，按列名顺序提取值
        rows = []
        for row_dict in mapped_rows:
            row_values = [row_dict.get(col) for col in columns]
            rows.append(row_values)

        return columns, rows
