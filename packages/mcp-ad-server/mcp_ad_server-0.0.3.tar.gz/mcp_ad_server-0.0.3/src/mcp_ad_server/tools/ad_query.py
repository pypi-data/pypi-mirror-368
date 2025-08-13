"""
广告查询工具

从main.py提取的query_ad_data工具实现。
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from ..models import ErrorCodes, ErrorMessages, ToolPayload, ToolResponse

logger = logging.getLogger(__name__)


class AdQueryTool:
    """广告查询工具类"""

    def __init__(self, api_client, indicator_manager, propmap_manager, config):
        self.api_client = api_client
        self.indicator_manager = indicator_manager
        self.propmap_manager = propmap_manager
        self.config = config

    def register(self, mcp):
        """注册工具到MCP服务器"""

        @mcp.tool()
        async def query_ad_data(
            start_date: str,
            end_date: str,
            indicators: list[str],
            app_id: str = self.config.DEFAULT_APPID,
            group_key: str = "",
            is_deep: bool = False,
            hours_24: bool = False,
            # 广告计划相关参数
            campaign_name: str | None = None,
            campaign_ids: list[str] | None = None,
            # 媒体和投手参数
            media: list[str] | None = None,
            media_buyers: list[str] | None = None,
            # 账户和状态参数
            cids: list[str] | None = None,
            ad_statuses: list[str] | None = None,
            # 创意和广告组参数
            creative_ids: list[str] | None = None,
            adgroup_ids: list[str] | None = None,
        ) -> dict[str, Any]:
            """
            查询广告投放数据

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
                is_deep: 是否获取下探UI数据，默认False
                hours_24: 是否返回24小时数据，默认False
                         ⚠️ 启用时：
                         - 支持单天查询：start_date=end_date，返回24行数据（每小时一行）
                         - 支持多天查询：start_date<end_date，自动分天查询并合并
                         - 日期字段将显示为"2024-01-01 01"格式表示具体小时

                # 广告计划相关参数
                campaign_name: 广告计划名称筛选，可选
                campaign_ids: 广告计划ID列表筛选，可选

                # 媒体和投手参数
                media: 媒体渠道筛选，可选值：全选、gdt(广点通)、tt(今日头条)、bd(百度)、bdss(百度搜索)、bz(B站)、zh(知乎)、uc(UC)、dx(抖小广告量)、sphdr(视频号达人)、xt(星图)、gg(谷歌)、nature(自然量)
                media_buyers: 投手筛选，可选值：lll(李霖林)、dcx(戴呈翔)、yxr(尹欣然)、syf(施逸风)、gyy(郭耀月)、zp(张鹏)、zmn(宗梦男)

                # 账户和状态参数
                cids: 广告账户CID列表筛选，可选
                ad_statuses: 广告状态筛选，可选值：ADGROUP_STATUS_FROZEN(已冻结)、ADGROUP_STATUS_SUSPEND(暂停中)、ADGROUP_STATUS_DELETED(已删除)、ADGROUP_STATUS_NOT_IN_DELIVERY_TIME(广告未到投放时间)、ADGROUP_STATUS_ACTIVE(投放中)、ADGROUP_STATUS_ACCOUNT_BALANCE_NOT_ENOUGH(账户余额不足)、ADGROUP_STATUS_DAILY_BUDGET_REACHED(广告达到日预算上限)、ADGROUP_STATUS_STOP(投放结束)

                # 创意和广告组参数
                creative_ids: 创意ID列表筛选，可选
                adgroup_ids: 广告组ID列表筛选，可选

            Returns:
                查询结果包含数据列表和元数据：
                - success: 查询是否成功
                - data.records: 强类型广告数据记录列表
                - data.rows: 已做中文映射的展示数据
                - data.total: 总条数
                - data.summary: 汇总数据（如果后端提供了总计行）
                - metadata: 查询元数据（查询时间、记录数等）

            Note:
                - 支持按多种维度分组统计
                - 无效指标会被忽略，不会影响查询执行
            """
            return await self._query_ad_data(
                start_date=start_date,
                end_date=end_date,
                indicators=indicators,
                app_id=app_id,
                group_key=group_key,
                is_deep=is_deep,
                hours_24=hours_24,
                campaign_name=campaign_name,
                campaign_ids=campaign_ids,
                media=media,
                media_buyers=media_buyers,
                cids=cids,
                ad_statuses=ad_statuses,
                creative_ids=creative_ids,
                adgroup_ids=adgroup_ids,
            )

    async def _query_ad_data(
        self,
        start_date: str,
        end_date: str,
        indicators: list[str],
        app_id: str,
        group_key: str = "",
        is_deep: bool = False,
        hours_24: bool = False,
        # 广告计划相关参数
        campaign_name: str | None = None,
        campaign_ids: list[str] | None = None,
        # 媒体和投手参数
        media: list[str] | None = None,
        media_buyers: list[str] | None = None,
        # 账户和状态参数
        cids: list[str] | None = None,
        ad_statuses: list[str] | None = None,
        # 创意和广告组参数
        creative_ids: list[str] | None = None,
        adgroup_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """实际的查询实现"""
        try:
            # 多天24小时查询处理
            if hours_24 and start_date != end_date:
                return await self._handle_multi_day_24h_query(
                    start_date,
                    end_date,
                    indicators,
                    app_id,
                    group_key,
                    is_deep,
                    campaign_name,
                    campaign_ids,
                    media,
                    media_buyers,
                    cids,
                    ad_statuses,
                    creative_ids,
                    adgroup_ids,
                )

            # 验证指标是否存在
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

            # 验证指标是否支持该API
            unsupported = self.propmap_manager.validate_names(
                indicators, "GetAdCountList"
            )
            if unsupported:
                logger.warning(f"以下指标在GetAdCountList API中不支持: {unsupported}")

            # 调用API查询数据
            result = await self.api_client.get_ad_count_list(
                app_id=app_id,
                start_date=start_date,
                end_date=end_date,
                indicators=indicators,
                group_key=group_key,
                is_deep=is_deep,
                hours_24=hours_24,
                campaign_name=campaign_name,
                campaign_ids=campaign_ids,
                media=media,
                media_buyers=media_buyers,
                cids=cids,
                ad_statuses=ad_statuses,
                creative_ids=creative_ids,
                adgroup_ids=adgroup_ids,
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
                result_dict, "GetAdCountList", group_key
            )

            # 处理汇总数据映射
            mapped_summary = None
            if result.data and result.data.summary:
                # 将summary也进行中文字段映射
                summary_dict = {"data": {"list": [result.data.summary]}}
                mapped_summary_result = self.propmap_manager.map_fields_to_display(
                    summary_dict, "GetAdCountList", group_key
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
                api_endpoint="/ad/GetAdCountList",
                date_range=f"{start_date} 24小时维度"
                if hours_24
                else f"{start_date} 至 {end_date}",
                indicators_count=len(columns),
            ).to_dict()

        except Exception as e:
            logger.error(f"查询广告数据失败: {e}")
            msg, suggestions = ErrorMessages.api_request_failed(str(e))
            return ToolResponse.error_response(
                code=ErrorCodes.API_REQUEST_FAILED,
                message=msg,
                details=str(e),
                suggestions=suggestions,
                api_endpoint="/ad/GetAdCountList",
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

    async def _handle_multi_day_24h_query(
        self,
        start_date: str,
        end_date: str,
        indicators: list[str],
        app_id: str,
        group_key: str,
        is_deep: bool,
        campaign_name: str,
        campaign_ids: list[str] | None,
        media: list[str] | None,
        media_buyers: list[str] | None,
        cids: list[str] | None,
        ad_statuses: list[str] | None,
        creative_ids: list[str] | None,
        adgroup_ids: list[str] | None,
    ) -> dict[str, Any]:
        """处理多天24小时查询：分天调用并合并结果"""
        try:
            # 生成日期范围
            date_range = self._generate_date_range(start_date, end_date)
            logger.info(f"执行多天24小时查询: {len(date_range)}天，从{start_date}到{end_date}")

            # 验证指标是否存在（只需验证一次）
            invalid_indicators = self.indicator_manager.validate_indicators(indicators)
            if invalid_indicators:
                msg, suggestions = ErrorMessages.invalid_parameter(
                    "indicators", str(invalid_indicators)
                )
                return ToolResponse.error_response(
                    code=ErrorCodes.INVALID_INDICATORS,
                    message=msg,
                    details=f"无效指标: {invalid_indicators}",
                    suggestions=suggestions,
                ).to_dict()

            # 定义单天查询函数
            async def query_single_day(date: str):
                """查询单天数据，返回(date, result)元组"""
                result = await self.api_client.get_ad_count_list(
                    start_date=date,
                    end_date=date,  # 确保同一天
                    indicators=indicators,
                    app_id=app_id,
                    group_key=group_key,
                    is_deep=is_deep,
                    hours_24=True,  # 强制24小时
                    campaign_name=campaign_name,
                    campaign_ids=campaign_ids or [],
                    media=media or [],
                    media_buyers=media_buyers or [],
                    cids=cids or [],
                    ad_statuses=ad_statuses or [],
                    creative_ids=creative_ids or [],
                    adgroup_ids=adgroup_ids or [],
                )
                return (date, result)

            # 使用TaskGroup并发查询所有天
            logger.info(f"开始并发查询{len(date_range)}天的24小时数据")
            daily_results = []
            failed_dates = []

            async with asyncio.TaskGroup() as tg:
                # 创建所有任务
                tasks = []
                for date in date_range:
                    task = tg.create_task(query_single_day(date))
                    tasks.append((date, task))

            # 收集结果
            for date, task in tasks:
                try:
                    result = task.result()
                    daily_results.append(result)
                except Exception as e:
                    logger.error(f"查询日期{date}时发生错误: {e}")
                    failed_dates.append(date)

            logger.info(f"并发查询完成，成功{len(daily_results)}天，失败{len(failed_dates)}天")

            if not daily_results:
                return ToolResponse.error_response(
                    code=ErrorCodes.API_REQUEST_FAILED,
                    message="所有日期查询均失败",
                    details=f"查询日期范围: {start_date} - {end_date}",
                    suggestions=["请检查日期范围是否正确", "请稍后重试"],
                ).to_dict()

            # 合并查询结果
            merged_result = await self._merge_multi_day_results(
                daily_results, start_date, end_date, indicators, group_key
            )
            logger.info(f"成功合并{len(daily_results)}天的24小时数据")

            return merged_result

        except Exception as e:
            logger.error(f"多天24小时查询失败: {e}")
            msg, suggestions = ErrorMessages.api_request_failed(str(e))
            return ToolResponse.error_response(
                code=ErrorCodes.API_REQUEST_FAILED,
                message=msg,
                details=str(e),
                suggestions=suggestions,
            ).to_dict()

    def _generate_date_range(self, start_date: str, end_date: str) -> list[str]:
        """生成日期范围列表"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        date_list = []
        current = start
        while current <= end:
            date_list.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

        return date_list

    async def _merge_multi_day_results(
        self,
        daily_results: list[tuple[str, Any]],
        start_date: str,
        end_date: str,
        indicators: list[str],
        group_key: str,
    ) -> dict[str, Any]:
        """合并多天查询结果"""
        if not daily_results:
            return ToolResponse.error_response(
                code=ErrorCodes.INTERNAL_ERROR,
                message="没有可合并的查询结果",
            ).to_dict()

        columns = []
        merged_rows = []
        total_records = 0
        summaries = []

        # 处理每一天的数据
        for date, api_result in daily_results:
            try:
                # 转换API结果为字典格式
                result_dict = {
                    "code": api_result.code,
                    "msg": api_result.msg,
                    "data": {
                        "list": api_result.data.items if api_result.data else [],
                    },
                }

                # 字段映射
                mapped_result = self.propmap_manager.map_fields_to_display(
                    result_dict, "GetAdCountList", group_key
                )

                # 提取列名和行数据
                mapped_rows_data = mapped_result.get("data", {}).get("list", [])
                if mapped_rows_data:
                    if not columns:
                        # 第一天：建立列名标准
                        columns = list(mapped_rows_data[0].keys())

                    # 转换为二维数组格式并合并
                    for row_dict in mapped_rows_data:
                        row_values = [row_dict.get(col) for col in columns]
                        merged_rows.append(row_values)

                # 累计记录数
                total_records += len(mapped_rows_data)

                # 收集summary数据
                if api_result.data and api_result.data.summary:
                    summary_dict = {"data": {"list": [api_result.data.summary]}}
                    mapped_summary_result = self.propmap_manager.map_fields_to_display(
                        summary_dict, "GetAdCountList", group_key
                    )
                    summary_data = mapped_summary_result.get("data", {}).get(
                        "list", [{}]
                    )[0]
                    if summary_data:
                        summaries.append(summary_data)

            except Exception as e:
                logger.warning(f"处理日期{date}的数据时发生错误: {e}")
                continue

        # 合并summary数据
        merged_summary = None
        if summaries:
            merged_summary = self._merge_summaries(summaries)

        # 构建最终响应
        payload = ToolPayload(
            columns=columns,
            rows=merged_rows,
            total=total_records,
            summary=merged_summary,
        )

        return ToolResponse.success_response(
            data=payload,
            record_count=total_records,
            api_endpoint="/ad/GetAdCountList",
            date_range=f"{start_date} 至 {end_date} 24小时维度",
            indicators_count=len(columns),
        ).to_dict()

    def _merge_summaries(self, summaries: list[dict]) -> dict[str, Any]:
        """合并多个summary数据"""
        if not summaries:
            return None

        merged = {}

        # 遍历第一个summary的所有字段
        for key in summaries[0].keys():
            if key in ["日期", "Date"]:
                # 日期字段特殊处理
                merged[key] = "合计"
                continue

            values = []
            for summary in summaries:
                value = summary.get(key)
                if value is not None:
                    # 尝试转换为数值并累加
                    try:
                        if isinstance(value, str):
                            # 处理百分比格式
                            if value.endswith("%"):
                                # 百分比字段跳过累加，使用第一个值
                                if key not in merged:
                                    merged[key] = value
                                break
                            else:
                                # 尝试转换为数值
                                numeric_value = float(value.replace(",", ""))
                                values.append(numeric_value)
                        elif isinstance(value, (int, float)):
                            values.append(float(value))
                    except (ValueError, TypeError):
                        # 非数值字段，使用第一个值
                        if key not in merged:
                            merged[key] = value
                        break

            # 数值字段：累加
            if values:
                total = sum(values)
                # 保持原格式（整数或小数）
                if all(isinstance(v, int) or v.is_integer() for v in values):
                    merged[key] = int(total)
                else:
                    merged[key] = round(total, 2)

        return merged
