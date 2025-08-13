"""
BI API客户端 - 处理与BI接口的通信
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import httpx
from pydantic import ValidationError

from ..config import Config
from ..models.api_models import (
    GetAdCountListRequest,
    GetAdCountListResponse,
    GetMaterialCountListRequest,
    GetMaterialCountListResponse,
)

logger = logging.getLogger(__name__)


class BiApiClient:
    """BI API客户端类"""

    # API客户端版本号
    CLIENT_VERSION = Config.API_CLIENT_VERSION

    def __init__(self, token: str | None = None):
        self.base_url = Config.BI_API_BASE_URL
        self.token = token or Config.BI_API_TOKEN
        self.api_version = Config.BI_API_VERSION  # API版本
        self.client_version = self.CLIENT_VERSION  # 客户端版本
        self.timeout = Config.QUERY_TIMEOUT_SECONDS

        logger.info(f"初始化BI API客户端 v{self.client_version} (API版本: {self.api_version})")

        if not self.token:
            logger.warning("BI API Token未设置，请设置环境变量 BI_API_TOKEN")

    @classmethod
    def get_version_info(cls) -> dict[str, str]:
        """获取客户端版本信息"""
        return {
            "client_version": cls.CLIENT_VERSION,
            "api_version": Config.BI_API_VERSION,
            "client_name": "mcp-ad-server",
            "description": "MCP广告数据服务API客户端",
        }

    @classmethod
    def is_compatible_with(cls, required_version: str) -> bool:
        """检查客户端版本兼容性"""
        current = cls._parse_version(cls.CLIENT_VERSION)
        required = cls._parse_version(required_version)

        # 简单的语义版本比较：major.minor.patch
        return current[0] == required[0] and current[1] >= required[1]

    @staticmethod
    def _parse_version(version_str: str) -> tuple[int, int, int]:
        """解析版本号字符串"""
        try:
            parts = version_str.split(".")
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            return (0, 0, 0)

    def get_client_info(self) -> dict[str, Any]:
        """获取完整的客户端信息（用于日志和调试）"""
        from datetime import datetime

        return {
            **self.get_version_info(),
            "base_url": self.base_url,
            "api_version": self.api_version,
            "timeout": self.timeout,
            "initialized_at": datetime.now().isoformat(),
            "has_token": bool(self.token),
        }

    def _get_headers(self) -> dict[str, str]:
        """获取请求头"""
        return {
            "X-Token": self.token,
            "X-Ver": self.api_version,
            "Content-Type": "application/json",
        }

    def _resolve_param_alias(
        self, current_value: Any, default_value: Any, kwargs: dict, *alias_keys: str
    ) -> Any:
        """
        解析参数别名，按优先级查找同义词

        Args:
            current_value: 当前参数值
            default_value: 默认值（用于判断是否使用别名）
            kwargs: 关键字参数字典
            *alias_keys: 按优先级排序的别名键列表

        Returns:
            解析后的参数值
        """
        # 如果参数不是默认值，说明是用户显式提供的，优先使用
        if current_value != default_value:
            return current_value

        # 如果是默认值，尝试从别名中获取
        for alias_key in alias_keys:
            if alias_key in kwargs:
                return kwargs.pop(alias_key)

        # 别名中也没有，返回原值
        return current_value

    def _ensure_date_indicator(self, indicators: list[str]) -> list[str]:
        """
        确保指标列表包含"日期"字段

        API要求必须包含"日期"指标，如果用户没有提供则自动添加
        """
        if not indicators:
            return ["日期"]

        # 创建指标副本避免修改原列表
        result_indicators = indicators.copy()

        # 如果没有"日期"指标，添加到列表开头
        if "日期" not in result_indicators:
            result_indicators.insert(0, "日期")
            logger.info("自动添加必需的'日期'指标到查询列表")

        return result_indicators

    async def get_ad_count_list(
        self,
        # 基础参数
        app_id: str = Config.DEFAULT_APPID,
        start_date: str = "",
        end_date: str = "",
        indicators: list[str] | None = None,
        group_key: str = "",
        is_deep: bool = False,
        hours_24: bool = False,
        # 广告计划相关参数
        campaign_name: str = "",
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
        **kwargs,
    ) -> GetAdCountListResponse:
        """
        查询广告数据统计

        Args:
            # 基础参数
            app_id: 游戏ID，默认59(正统三国)，可选值：59(正统三国)、78(哈局成语大师)、61(银河战舰)
            start_date: 查询范围开始时间，格式YYYY-MM-DD
            end_date: 查询范围结束时间，格式YYYY-MM-DD
            indicators: 指标列表，本客户端会自动添加"日期"指标
            group_key: 分组维度，默认空字符串（不分组），可选值：
                      vp_campaign_id(广告ID)、vp_adgroup_id(项目ID)、vp_originality_id(创意ID)、vp_advert_pitcher_id(投手)、dt_vp_fx_cid(self_cid)、vp_advert_channame(媒体)
            is_deep: 是否获取下探UI数据，默认False
            hours_24: 是否返回24小时数据，默认False
                      ⚠️ 启用时：
                      - start_date和end_date必须是同一天
                      - 日期字段将显示为01,02,03...24表示小时

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

            **kwargs: 其他查询参数（用于未来扩展）

        Returns:
            GetAdCountListResponse: 包含查询结果
                - code: 0表示成功，500表示错误
                - data.items: 广告数据列表（已过滤总计项，只包含实际业务数据）
                - data.summary: 总计数据（从原数据中提取，已移除日期字段）
                - data.prop_map: 中文指标名到API字段的映射
                - data.ui_cols: UI显示的字段列表
                - data.indicator_list: 指标列表
                - msg: 成功时为"查询成功"

        Raises:
            ValueError: 参数验证失败（时间格式、指标数量、游戏ID等）
            Exception: API请求失败或返回错误

        Note:
            - 支持按多种维度分组统计
            - 无效指标会被忽略，不会影响查询执行
            - 自动处理后端API返回的总计项：识别日期字段为"总计"或空的行，提取到summary并从数据列表中移除
        """
        # 参数同义词兼容处理（按参数类型分组）
        # 基础参数
        app_id = self._resolve_param_alias(
            app_id, Config.DEFAULT_APPID, kwargs, "appid"
        )
        start_date = self._resolve_param_alias(start_date, "", kwargs, "start_time")
        end_date = self._resolve_param_alias(end_date, "", kwargs, "end_time")
        indicators = self._resolve_param_alias(indicators, None, kwargs, "zhibiao_list")
        # 广告计划相关
        campaign_name = self._resolve_param_alias(
            campaign_name, "", kwargs, "ji_hua_name"
        )
        campaign_ids = self._resolve_param_alias(
            campaign_ids, None, kwargs, "ji_hua_id"
        )
        # 媒体和投手参数
        media = self._resolve_param_alias(media, None, kwargs, "media")
        media_buyers = self._resolve_param_alias(media_buyers, None, kwargs, "toushou")
        # 账户和状态
        cids = self._resolve_param_alias(cids, None, kwargs, "self_cid")
        ad_statuses = self._resolve_param_alias(ad_statuses, None, kwargs, "ad_status")
        # 创意和广告组
        creative_ids = self._resolve_param_alias(
            creative_ids, None, kwargs, "creative_id"
        )
        adgroup_ids = self._resolve_param_alias(
            adgroup_ids, None, kwargs, "vp_adgroup_id"
        )

        # 确保指标包含日期
        indicators = self._ensure_date_indicator(indicators)

        # 使用Pydantic模型进行参数验证和构建请求
        try:
            request_model = GetAdCountListRequest(
                # 基础参数
                appid=app_id or Config.DEFAULT_APPID,
                start_time=start_date,
                end_time=end_date,
                zhibiao_list=indicators,
                # 以下非必须参数
                group_key=group_key,
                is_deep=is_deep,
                hours_24=hours_24,
                # 广告计划相关参数
                ji_hua_name=campaign_name or "",
                ji_hua_id=campaign_ids or [],
                # 媒体和投手参数
                media=media or [],
                toushou=media_buyers or [],
                # 账户和状态参数
                self_cid=cids or [],
                ad_status=ad_statuses or [],
                # 创意和广告组参数
                creative_id=creative_ids or [],
                vp_adgroup_id=adgroup_ids or [],
                **kwargs,  # 允许额外参数
            )

            # 生成请求payload
            payload = request_model.model_dump(by_alias=True)
            # 添加固定参数
            payload["deep_bid_type"] = []
            payload["is_test"] = True

        except ValueError as e:
            raise ValueError(f"请求参数验证失败: {e}")

        # 验证24小时查询的单天限制
        if hours_24 and start_date != end_date:
            raise ValueError(
                f"24小时数据查询要求单天查询：start_date({start_date}) != end_date({end_date})"
            )

        # 发送请求
        url = f"{self.base_url}/ad/GetAdCountList"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url, json=payload, headers=self._get_headers()
                )
                response.raise_for_status()
                result = response.json()

                try:
                    # 使用Pydantic模型解析响应
                    api_response = GetAdCountListResponse(**result)

                    if not api_response.is_success:
                        raise Exception(f"API返回错误: {api_response.msg}")

                    record_count = (
                        len(api_response.data.items) if api_response.data else 0
                    )
                    logger.info(f"成功查询广告数据，返回{record_count}条记录")

                    # 24小时数据预处理
                    if hours_24 and api_response.data:
                        self._preprocess_hours24_data(api_response.data, start_date)
                    # 普通数据按日期倒序排列（最新日期在前）
                    elif api_response.data and api_response.data.items:
                        self._sort_data_by_date(api_response.data)

                    return api_response

                except ValidationError as e:
                    logger.error(f"响应数据格式验证失败: {e}")
                    # 如果验证失败，仍然可以返回一个基本的响应对象
                    return GetAdCountListResponse(
                        code=result.get("code", -1),
                        msg=f"数据格式验证失败: {str(e)}",
                        data=None,
                    )

        except httpx.TimeoutException:
            raise Exception(f"请求超时({self.timeout}秒)")
        except httpx.HTTPError as e:
            raise Exception(f"HTTP请求错误: {e}")
        except Exception as e:
            logger.error(f"查询广告数据失败: {e}")
            raise

    async def get_material_count_list(
        self,
        # 基础参数
        app_id: str = Config.DEFAULT_APPID,
        start_date: str = "",
        end_date: str = "",
        indicators: list[str] | None = None,
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
        # 素材相关参数（originality_xxx）
        originality_ids: list[str] | None = None,
        originality_names: list[str] | None = None,
        originality_types: list[str] | None = None,
        # 广告组和创意参数
        adgroup_ids: list[str] | None = None,
        creative_ids: list[str] | None = None,
        component_ids: list[str] | None = None,
        **kwargs,
    ) -> GetMaterialCountListResponse:
        """
        查询素材数据统计

        Args:
            # 基础参数
            app_id: 游戏ID，默认59(正统三国)，可选值：59(正统三国)、78(哈局成语大师)、61(银河战舰)
            start_date: 查询范围开始时间，格式YYYY-MM-DD
            end_date: 查询范围结束时间，格式YYYY-MM-DD
            indicators: 指标列表，本客户端会自动添加"日期"指标
            group_key: 分组维度，默认空字符串（不分组），可选值：
                      vp_campaign_id(广告ID)、vp_adgroup_id(项目ID)、vp_originality_id(创意ID)、vp_advert_pitcher_id(投手)、dt_vp_fx_cid(self_cid)、vp_advert_channame(媒体)
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
            cids: 广告账户CID列表筛选，可选

            # 素材相关参数 (originality_xxx)
            originality_ids: 素材ID列表筛选，可选
            originality_names: 素材名称列表筛选，可选
            originality_types: 素材类型筛选，可选值：图片、视频

            # 广告组和创意参数
            adgroup_ids: 广告组ID列表筛选，可选
            creative_ids: 创意ID列表筛选，可选
            component_ids: 组件ID列表筛选，可选
            **kwargs: 其他查询参数（用于未来扩展）

        Returns:
            GetMaterialCountListResponse: 包含查询结果
                - code: 0表示成功，500表示错误
                - data.items: 广告素材报表数据列表（已过滤总计项，只包含实际业务数据）
                - data.summary: 总计数据（从原数据中提取，已移除groupKey字段）
                - data.prop_map: 中文指标名到API字段的映射
                - data.ui_cols: UI显示的字段列表
                - data.indicator_list: 指标列表
                - data.group_key_alias: 分组别名
                - msg: 成功时为"查询成功"

        Raises:
            ValueError: 参数验证失败（时间格式、指标数量、游戏ID、制作人、创意人等）
            Exception: API请求失败或返回错误

        Note:
            - 支持按多种维度分组统计
            - 支持低效和低质素材筛选
            - 无效指标会被忽略，不会影响查询执行
            - 自动处理后端API返回的总计项：识别groupKey字段为"总计"的行，提取到summary并从数据列表中移除
        """
        # 参数同义词兼容处理（按参数类型分组）
        # 基础参数
        app_id = self._resolve_param_alias(
            app_id, Config.DEFAULT_APPID, kwargs, "appid"
        )
        start_date = self._resolve_param_alias(start_date, "", kwargs, "start_time")
        end_date = self._resolve_param_alias(end_date, "", kwargs, "end_time")
        indicators = self._resolve_param_alias(indicators, None, kwargs, "zhibiao_list")
        # 媒体和投手
        media = self._resolve_param_alias(media, None, kwargs, "media")
        media_buyers = self._resolve_param_alias(media_buyers, None, kwargs, "toushou")
        # 制作和创意人员
        producers = self._resolve_param_alias(producers, None, kwargs, "producer")
        creative_users = self._resolve_param_alias(
            creative_users, None, kwargs, "creative_user"
        )
        # 账户参数
        cids = self._resolve_param_alias(cids, None, kwargs, "self_cid")
        # 素材相关参数 (originality_xxx)
        originality_ids = self._resolve_param_alias(
            originality_ids, None, kwargs, "vp_originality_id"
        )
        originality_names = self._resolve_param_alias(
            originality_names, None, kwargs, "vp_originality_name"
        )
        originality_types = self._resolve_param_alias(
            originality_types, None, kwargs, "vp_originality_type"
        )
        # 广告组和创意
        adgroup_ids = self._resolve_param_alias(
            adgroup_ids, None, kwargs, "vp_adgroup_id"
        )
        creative_ids = self._resolve_param_alias(
            creative_ids, None, kwargs, "creative_id"
        )
        component_ids = self._resolve_param_alias(
            component_ids, None, kwargs, "component_id"
        )

        # 确保指标包含日期
        indicators = self._ensure_date_indicator(indicators)

        # 使用Pydantic模型进行参数验证和构建请求
        try:
            request_model = GetMaterialCountListRequest(
                # 基础参数
                appid=app_id or Config.DEFAULT_APPID,
                start_time=start_date,
                end_time=end_date,
                zhibiao_list=indicators,
                # 以下非必须参数
                group_key=group_key,
                is_inefficient_material=is_inefficient,
                is_ad_low_quality_material=is_low_quality,
                is_deep=is_deep,
                is_old_table=is_old_table,
                # 媒体和投手参数
                media=media or [],
                toushou=media_buyers or [],
                # 制作和创意人员参数
                producer=producers or [],
                creative_user=creative_users or [],
                # 账户参数
                self_cid=cids or [],
                # 素材相关参数 (originality_xxx)
                vp_originality_id=originality_ids or [],
                vp_originality_name=originality_names or [],
                vp_originality_type=originality_types or [],
                # 广告组和创意参数
                vp_adgroup_id=adgroup_ids or [],
                creative_id=creative_ids or [],
                component_id=component_ids or [],
                **kwargs,  # 允许额外参数
            )

            # 生成请求payload
            payload = request_model.model_dump(by_alias=True)
            # 添加固定参数
            payload["deep_bid_type"] = []

        except ValueError as e:
            raise ValueError(f"请求参数验证失败: {e}")

        # 发送请求
        url = f"{self.base_url}/ad/GetMaterialCountList"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url, json=payload, headers=self._get_headers()
                )
                response.raise_for_status()
                result = response.json()

                try:
                    # 使用Pydantic模型解析响应
                    api_response = GetMaterialCountListResponse(**result)

                    if not api_response.is_success:
                        raise Exception(f"API返回错误: {api_response.msg}")

                    record_count = (
                        len(api_response.data.items) if api_response.data else 0
                    )
                    logger.info(f"成功查询素材数据，返回{record_count}条记录")

                    # 素材数据按日期倒序排列（最新日期在前）
                    if api_response.data and api_response.data.items:
                        self._sort_data_by_date(api_response.data)

                    return api_response

                except ValidationError as e:
                    logger.error(f"响应数据格式验证失败: {e}")
                    # 如果验证失败，仍然可以返回一个基本的响应对象
                    return GetMaterialCountListResponse(
                        code=result.get("code", -1),
                        msg=f"数据格式验证失败: {str(e)}",
                        data=None,
                    )

        except httpx.TimeoutException:
            raise Exception(f"请求超时({self.timeout}秒)")
        except httpx.HTTPError as e:
            raise Exception(f"HTTP请求错误: {e}")
        except Exception as e:
            logger.error(f"查询素材数据失败: {e}")
            raise

    async def test_connection(self) -> bool:
        """测试API连接"""
        try:
            # 使用简单的查询测试连接
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            await self.get_ad_count_list(
                start_date=yesterday, end_date=yesterday, indicators=["日期", "消耗"]
            )
            return True
        except Exception as e:
            logger.error(f"API连接测试失败: {e}")
            return False

    def _preprocess_hours24_data(self, response_data, base_date: str):
        """预处理24小时数据：排序并格式化日期字段

        Args:
            response_data: API响应的data部分
            base_date: 基准日期 (YYYY-MM-DD)

        将Date字段从"01", "02", "03"转换为"2024-01-01 01", "2024-01-01 02"等格式
        并确保数据按小时正序排列（01-24）
        """
        if not response_data.items:
            return

        # 先按小时值排序，然后格式化
        def get_hour_value(item):
            # items是字典列表，使用字典访问方式
            date_field = item.get("Date") or item.get("日期")
            if date_field:
                try:
                    # 将小时值转换为整数用于排序
                    return int(str(date_field).strip())
                except (ValueError, AttributeError):
                    return 999  # 无效值放到最后
            return 999

        # 按小时值排序
        response_data.items.sort(key=get_hour_value)

        # 格式化日期字段
        for item in response_data.items:
            date_field = item.get("Date") or item.get("日期")
            if date_field:
                hour_str = str(date_field).zfill(2)  # 确保两位数格式
                # 格式化为 "YYYY-MM-DD HH"
                formatted_date = f"{base_date} {hour_str}"

                # 更新字典中的字段值
                if "Date" in item:
                    item["Date"] = formatted_date
                elif "日期" in item:
                    item["日期"] = formatted_date

        # 同时处理summary数据
        if hasattr(response_data, "summary") and response_data.summary:
            summary = response_data.summary
            if isinstance(summary, dict):
                if "Date" in summary:
                    summary["Date"] = "汇总"
                elif "日期" in summary:
                    summary["日期"] = "汇总"

    def _sort_data_by_date(self, response_data):
        """对普通日期数据按日期倒序排列（最新日期在前）

        Args:
            response_data: API响应的data部分
        """
        if not response_data.items:
            return

        def get_date_value(item):
            # 查找日期字段
            date_field = item.get("Date") or item.get("日期")
            if date_field:
                try:
                    # 返回日期字符串用于排序
                    return str(date_field)
                except (ValueError, AttributeError):
                    return "0000-00-00"  # 无效值放到最前面
            return "0000-00-00"

        # 按日期倒序排列（最新日期在前）
        response_data.items.sort(key=get_date_value, reverse=True)
