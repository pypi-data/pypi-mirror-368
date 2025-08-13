"""
字段映射管理器 - 管理API字段的显示名称与字段名映射关系
"""

import json
from typing import Any

import aiofiles

from ..config import Config
from .base import Manager


class PropmapManager(Manager):
    """字段映射管理器类"""

    def __init__(self):
        super().__init__()
        self.reverse_mappings: dict[str, dict[str, str]] = {}

    async def load_mappings(self):
        """加载所有字段映射文件"""
        propmap_dir = Config.PROPMAP_DIR

        if not propmap_dir.exists():
            self.logger.warning(f"映射目录不存在: {propmap_dir}")
            return

        try:
            mapping_files = list(propmap_dir.glob("*.json"))
            self.logger.info(f"发现{len(mapping_files)}个映射文件")

            for file_path in mapping_files:
                api_name = file_path.stem  # 如 GetAdCountList, GetMaterialCountList

                try:
                    async with aiofiles.open(file_path, encoding="utf-8") as f:
                        content = await f.read()
                        mapping_data = json.loads(content)

                        # 提取propMap部分
                        prop_map = mapping_data.get("propMap", {})
                        self.data[api_name] = prop_map

                        # 创建反向映射（字段名 -> 显示名称）
                        reverse_map = {v: k for k, v in prop_map.items()}
                        self.reverse_mappings[api_name] = reverse_map

                        self.logger.info(f"加载映射文件 {api_name}: {len(prop_map)}个字段")

                except Exception as e:
                    self.logger.error(f"加载映射文件失败 {file_path}: {e}")

            self.logger.info(f"成功加载{len(self.data)}个API的字段映射")

        except Exception as e:
            self.logger.error(f"加载映射目录失败: {e}")
            raise

    async def load_data(self) -> None:
        """实现基类的抽象方法加载数据"""
        await self.load_mappings()
        self.loaded = True
        self.logger.info("字段映射管理器数据加载完成")

    async def initialize(self):
        """初始化管理器"""
        if self.is_loaded():
            return
        await self.load_data()
        self.logger.info("字段映射管理器初始化完成")

    def get_field_name(self, display_name: str, api_name: str) -> str | None:
        """获取显示名称对应的字段名"""
        api_mapping = self.data.get(api_name, {})
        return api_mapping.get(display_name)

    def get_display_name(self, field_name: str, api_name: str) -> str | None:
        """获取字段名对应的显示名称"""
        api_reverse_mapping = self.reverse_mappings.get(api_name, {})
        return api_reverse_mapping.get(field_name)

    def get_all_mappings(self, api_name: str) -> dict[str, str]:
        """获取指定API的所有字段映射（显示名称 -> 字段名）"""
        return self.data.get(api_name, {}).copy()

    def get_all_reverse_mappings(self, api_name: str) -> dict[str, str]:
        """获取指定API的所有反向字段映射（字段名 -> 显示名称）"""
        return self.reverse_mappings.get(api_name, {}).copy()

    def get_supported_apis(self) -> list[str]:
        """获取支持的API列表"""
        return list(self.data.keys())

    def get_display_names(self, api_name: str) -> list[str]:
        """获取指定API支持的所有显示名称"""
        return list(self.data.get(api_name, {}).keys())

    def get_field_names(self, api_name: str) -> list[str]:
        """获取指定API支持的所有字段名"""
        return list(self.data.get(api_name, {}).values())

    def map_to_fields(self, display_names: list[str], api_name: str) -> list[str]:
        """将显示名称列表映射为字段名列表"""
        api_mapping = self.data.get(api_name, {})
        field_names = []

        for display_name in display_names:
            field_name = api_mapping.get(display_name)
            if field_name:
                field_names.append(field_name)
            else:
                self.logger.warning(f"显示名称'{display_name}'在API '{api_name}'中没有对应的字段名")
                # 如果没有映射，保留原始名称
                field_names.append(display_name)

        return field_names

    def map_fields_to_display(
        self, result_data: dict[str, Any], api_name: str, group_key: str = ""
    ) -> dict[str, Any]:
        """将API返回结果的字段名映射为显示名称

        Args:
            result_data: API返回的结果数据
            api_name: API名称
            group_key: 分组维度参数，用于动态映射groupKey字段
        """
        if not result_data:
            return result_data

        api_reverse_mapping = self.reverse_mappings.get(api_name, {}).copy()

        # 动态映射groupKey字段
        if group_key:
            from ..config import Config

            group_display_name = Config.SUPPORTED_GROUP_KEYS.get(group_key, group_key)
            api_reverse_mapping["groupKey"] = group_display_name

        # 处理data.list中的数据
        data = result_data.get("data", {})
        data_list = data.get("list", [])

        mapped_list = []
        for item in data_list:
            mapped_item = {}
            for field_name, value in item.items():
                display_name = api_reverse_mapping.get(field_name, field_name)
                mapped_item[display_name] = value
            mapped_list.append(mapped_item)

        # 构建映射后的结果
        mapped_result = result_data.copy()
        if "data" in mapped_result:
            mapped_result["data"] = data.copy()
            mapped_result["data"]["list"] = mapped_list

        return mapped_result

    def validate_names(self, names: list[str], api_name: str) -> list[str]:
        """验证名称是否支持指定API，返回不支持的名称列表"""
        api_mapping = self.data.get(api_name, {})
        unsupported = []

        for name in names:
            if name not in api_mapping:
                unsupported.append(name)

        return unsupported

    def search_fields(
        self, keyword: str, api_name: str | None = None
    ) -> dict[str, list[str]]:
        """搜索包含关键词的字段"""
        results = {}
        keyword_lower = keyword.lower()

        apis_to_search = [api_name] if api_name else self.data.keys()

        for api in apis_to_search:
            api_mapping = self.data.get(api, {})
            matched_fields = []

            for display_name, field_name in api_mapping.items():
                if (
                    keyword_lower in display_name.lower()
                    or keyword_lower in field_name.lower()
                ):
                    matched_fields.append(display_name)

            if matched_fields:
                results[api] = matched_fields

        return results

    def get_mapping_stats(self) -> dict[str, Any]:
        """获取映射统计信息"""
        return {
            "total_apis": self.get_data_count(),
            "api_details": [
                {"api_name": api_name, "field_count": len(mappings)}
                for api_name, mappings in self.data.items()
            ],
            "total_fields": sum(len(mappings) for mappings in self.data.values()),
        }

    async def reload(self):
        """重新加载映射数据"""
        self.clear_data()
        self.reverse_mappings.clear()

        await self.initialize()
        self.logger.info("字段映射管理器数据已重新加载")
