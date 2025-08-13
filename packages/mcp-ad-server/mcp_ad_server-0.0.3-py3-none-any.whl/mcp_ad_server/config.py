"""
配置文件 - MCP服务器配置
"""

import os
from pathlib import Path

# 加载.env文件
try:
    from dotenv import load_dotenv

    # 从项目根目录加载.env文件
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    # 如果没有安装python-dotenv，继续使用系统环境变量
    pass


class Config:
    """MCP服务器配置类"""

    # 基础配置
    SERVER_NAME = "ad"
    SERVER_VERSION = "0.0.3"

    # API客户端版本
    API_CLIENT_VERSION = "0.0.1"

    # API配置
    BI_API_BASE_URL = "https://bi.dartou.com/testapi"
    BI_API_VERSION = "0.2.07"
    DEFAULT_APPID = "59"

    # 认证配置 - 从环境变量读取
    BI_API_TOKEN = os.getenv("BI_API_TOKEN", "")

    # 获取项目根目录（src/mcp_ad_server/config.py -> 项目根目录）
    BASE_DIR = Path(__file__).parent.parent.parent

    # 数据目录配置 - 支持打包后的环境
    @classmethod
    def get_data_dir(cls):
        """获取数据目录，支持打包和开发环境"""
        # 首先尝试从环境变量获取
        data_dir_env = os.getenv("MCP_AD_DATA_DIR")
        if data_dir_env:
            return Path(data_dir_env)

        # 包内数据目录：优先使用包内的data目录
        package_data_dir = Path(__file__).parent / "data"
        if package_data_dir.exists():
            return package_data_dir

        # 开发环境：使用项目根目录的data目录
        dev_data_dir = cls.BASE_DIR / "data"
        if dev_data_dir.exists():
            return dev_data_dir

        # 打包环境：使用importlib.resources查找包内数据
        try:
            import importlib.resources as pkg_resources

            # 检查包内是否有data目录
            try:
                data_package = pkg_resources.files("mcp_ad_server") / "data"
                if data_package.is_dir():
                    return Path(str(data_package))
            except (AttributeError, FileNotFoundError):
                pass
        except ImportError:
            pass

        # 如果都不存在，返回包内路径（即使不存在）
        return package_data_dir

    # 限制配置
    MAX_TIME_RANGE_DAYS = 30
    QUERY_TIMEOUT_SECONDS = 30

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # 支持的游戏应用ID
    SUPPORTED_APPIDS = {"59": "正统三国", "61": "银河战舰", "48": "开心十三张", "78": "哈局成语大师"}

    # 支持的媒体渠道
    SUPPORTED_MEDIA = [
        "全选",  # 全选
        "gdt",  # 广点通
        "tt",  # 今日头条
        "bd",  # 百度
        "bdss",  # 百度搜索
        "bz",  # B站
        "zh",  # 知乎
        "uc",  # UC
        "dx",  # 抖小广告量
        "sphdr",  # 视频号达人
        "xt",  # 星图
        "gg",  # 谷歌
        "nature",  # 自然量
    ]

    # 支持的投手列表
    SUPPORTED_TOUSHOU = [
        "lll",  # 李霖林
        "dcx",  # 戴呈翔
        "yxr",  # 尹欣然
        "syf",  # 施逸风
        "gyy",  # 郭耀月
        "zp",  # 张鹏
        "zmn",  # 宗梦男
        "fx2.0",  # fx2.0 (仅素材查询)
    ]

    # 支持的广告状态
    SUPPORTED_AD_STATUS = [
        "ADGROUP_STATUS_FROZEN",  # 已冻结
        "ADGROUP_STATUS_SUSPEND",  # 暂停中
        "ADGROUP_STATUS_DELETED",  # 已删除
        "ADGROUP_STATUS_NOT_IN_DELIVERY_TIME",  # 广告未到投放时间
        "ADGROUP_STATUS_ACTIVE",  # 投放中
        "ADGROUP_STATUS_ACCOUNT_BALANCE_NOT_ENOUGH",  # 账户余额不足
        "ADGROUP_STATUS_DAILY_BUDGET_REACHED",  # 广告达到日预算上限
        "ADGROUP_STATUS_STOP",  # 投放结束
    ]

    # 支持的制作人列表 (素材查询)
    SUPPORTED_PRODUCERS = [
        "蔡睿韬",
        "王子鹏",
        "颜隆隆",
        "郑显洋",
        "李霖林",
        "张鹏",
        "谢雨",
        "占雪涵",
        "方晓聪",
        "刘伍攀",
        "张航",
        "刘锦",
        "翁国峻",
        "刘婷婷",
        "张泽祖",
        "AI",
        "戴呈翔",
        "其他",
    ]

    # 支持的创意人列表 (素材查询)
    SUPPORTED_CREATIVE_USERS = [
        "蔡睿韬",
        "陈朝晖",
        "王子鹏",
        "颜隆隆",
        "郑显洋",
        "李霖林",
        "张鹏",
        "谢雨",
        "周义骅",
        "占雪涵",
        "方晓聪",
        "陈朝辉",
        "刘伍攀",
        "张航",
        "郭耀月",
        "宗梦男",
        "刘锦",
        "翁国峻",
        "刘婷婷",
        "秦翎丰",
        "张泽祖",
        "戴呈翔",
        "AI",
        "其他",
    ]

    # 支持的素材类型
    SUPPORTED_MATERIAL_TYPES = ["图片", "视频"]

    # 支持的分组维度
    SUPPORTED_GROUP_KEYS = {
        "vp_campaign_id": "广告ID",
        "vp_adgroup_id": "项目ID",
        "vp_originality_id": "创意ID",
        "vp_advert_pitcher_id": "投手",
        "dt_vp_fx_cid": "self_cid",
        "vp_advert_channame": "媒体",
    }

    # 业务场景映射
    SCENARIO_MAPPING = {
        "投放启动": "1_投放启动决策指标组",
        "效果监控": "2_投放效果实时监控指标组",
        "短期评估": "3_短期价值评估指标组(首日-7日)",
        "深度分析": "4_深度价值与留存指标组",
        "数据对账": "5_平台数据对账指标组",
        "风险预警": "6_终止决策预警指标组",
        "财务核算": "7_财务核算指标组",
    }


# 在类外初始化数据目录
_config = Config()
DATA_DIR = _config.get_data_dir()
INDICATORS_DIR = DATA_DIR / "indicators"
GROUPS_DIR = DATA_DIR / "groups"
PROPMAP_DIR = DATA_DIR / "propmap"
GAMES_DIR = DATA_DIR / "games"

# 将路径添加到Config类
Config.DATA_DIR = DATA_DIR
Config.INDICATORS_DIR = INDICATORS_DIR
Config.GROUPS_DIR = GROUPS_DIR
Config.PROPMAP_DIR = PROPMAP_DIR
Config.GAMES_DIR = GAMES_DIR
