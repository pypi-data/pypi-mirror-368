import logging
import os
import re
from typing import Any, Dict, List, Optional, Union

from fastmcp import FastMCP

from .bps_api_client import BPSAPIInterface

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化FastMCP服务器
mcp = FastMCP("BPS Data Server")

# 从环境变量获取APP_ID，不提供默认值
APP_ID = os.environ.get("BPS_APP_ID")


# 动态数据查询请求
from pydantic import BaseModel

class DataQueryRequest(BaseModel):
    var: int
    ths: List[int]


# 初始化BPS接口的函数
def init_bps_interface():
    """初始化BPS接口"""
    # 检查是否设置了APP_ID，如果没有设置则抛出错误
    if not APP_ID:
        raise ValueError(
            "BPS_APP_ID环境变量未设置。请设置BPS_APP_ID环境变量以使用此MCP服务器。"
        )

    # 初始化BPS接口
    return BPSAPIInterface(APP_ID)


# 初始化BPS接口
bps_interface = None


@mcp.tool
def search_subjects(domain: str = "0000", page: int = 1, lang: str = "ind") -> dict:
    """搜索主题数据

    注意：此接口不支持keyword参数，请使用其他参数进行过滤。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    global bps_interface
    # 初始化BPS接口（如果尚未初始化）
    if bps_interface is None:
        bps_interface = init_bps_interface()

    try:
        logger.info(f"正在搜索主题数据，领域ID: {domain}，页码: {page}，语言: {lang}")
        response = bps_interface.search_subjects(domain=domain, page=page, lang=lang)
        logger.info(f"成功获取主题数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取主题数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取主题数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取主题数据时出错: {str(e)}",
        }


@mcp.tool
def search_news(
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
    keyword: Optional[str] = None,
) -> dict:
    """搜索新闻数据

    支持使用关键词进行搜索，关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"
        keyword: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索新闻数据，领域ID: {domain}，页码: {page}，语言: {lang}，关键词: {keyword}"
        )
        response = bps_interface.search_news(
            domain=domain, page=page, lang=lang, keyword=keyword
        )
        logger.info(f"成功获取新闻数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取新闻数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取新闻数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取新闻数据时出错: {str(e)}",
        }


@mcp.tool
def search_publications(
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
    keyword: Optional[str] = None,
) -> dict:
    """搜索出版物数据

    支持使用关键词进行搜索，关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"
        keyword: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索出版物数据，领域ID: {domain}，页码: {page}，语言: {lang}，关键词: {keyword}"
        )
        response = bps_interface.search_publications(
            domain=domain, page=page, lang=lang, keyword=keyword
        )
        logger.info(f"成功获取出版物数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取出版物数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取出版物数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取出版物数据时出错: {str(e)}",
        }


@mcp.tool
def search_variables(
    keywords: List[str],
    domain: str = "0000",
    page: int = 1,
    subject: Optional[int] = None,
    year: Optional[int] = None,
    area: Optional[bool] = None,
    vervar: Optional[int] = None,
    lang: str = "ind",
) -> dict:
    """搜索变量数据

    重要：这是获取动态数据的关键第一步。在查询动态数据时，首先需要使用此工具通过关键词查找变量ID(var_id)。

    支持使用多种参数进行过滤搜索，关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    使用场景：
    1. 简单关键字搜索：直接使用keyword参数搜索相关变量
    2. 复杂查询的第一步：为获取动态数据而查找变量ID

    示例：
    1. 查找"镍矿"相关的变量：search_variables(keyword="nikel", lang="ind")
    2. 查找特定主题下的变量：search_variables(subject=104)

    获取到变量ID后，下一步应使用search_periods工具查找对应的时期数据。

    Args:
        keywords: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致
        支持多关键词查询，返回结果会根据关键字-对应结果返回
        domain: 领域ID，默认为"0000"表示全国数据。格式为4位数字，不足前面补0。
        page: 页码，默认为1
        subject: 主题ID，用于按主题过滤变量，可选参数
        year: 年份，用于按年份过滤变量，可选参数
        area: 显示领域内现有变量的参数，1表示显示现有变量，0表示不显示，可选参数
        vervar: 垂直变量ID，用于按垂直变量过滤，可选参数
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"

    Returns:
        包含搜索结果的字典，格式为：
        {
            "keyword": {
                "status": "OK" 或 "error",
                "data": 搜索结果列表,
                "message": 描述信息
            }
        }

        data中的每个变量对象包含以下字段：
        - var_id: 变量ID，用于后续查询
        - title: 变量标题
        - unit: 数据单位
    """
    try:
        result = {}
        for keyword in keywords:
            logger.info(
                f"正在搜索变量数据，领域ID: {domain}，页码: {page}，语言: {lang}，关键词: {keyword}"
            )
            response = bps_interface.search_variables(
                domain=domain,
                page=page,
                subject=subject,
                year=year,
                area=area,
                vervar=vervar,
                lang=lang,
                keyword=keyword,
            )
            logger.info(f"成功获取变量数据，共{len(response.data)}条记录")
            result[keyword] = {
                "status": response.status,
                "data": response.data,
                "message": f"成功获取变量数据，共{len(response.data)}条记录",
            }
        return result
    except Exception as e:
        logger.error(f"获取变量数据时出错: {str(e)}")
        return {
            "status": "error",
            "message": f"获取变量数据时出错: {str(e)}",
        }


@mcp.tool
def search_periods(
    vars: List[int], domain: str = "0000", page: int = 1, lang: str = "ind"
) -> dict:
    """搜索时期数据

    重要：这是获取动态数据的关键第二步。在获取变量ID后，使用此工具查找对应的时期数据ID(th_id)。

    注意：此接口不支持keyword参数，请使用其他参数进行过滤。

    使用场景：
    1. 复杂查询的第二步：为获取动态数据而查找时期ID

    示例：
    查找变量ID为2444的时期数据：search_periods(vars=[2444])

    获取到时期ID后，下一步应使用search_data工具获取实际的动态数据。

    Args:
        vars: 变量ID，用于按变量过滤时期数据。这是获取动态数据时的必填参数。
          支持多变量同时查询，返回结果根据变量ID-对应结果返回
        domain: 领域ID，默认为"0000"表示全国数据。格式为4位数字，不足前面补0。
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"

    Returns:
        包含搜索结果的字典，格式为：
        {
            var_id: {
                "status": "OK" 或 "error",
                "data": 搜索结果列表,
                "message": 描述信息
            }
        }

        data中的每个时期对象包含以下字段：
        - th_id: 时期ID，用于后续查询
        - th: 时期名称（如年份）
    """
    try:
        result = {}
        for var_id in vars:
            logger.info(
                f"正在搜索时期数据，领域ID: {domain}，页码: {page}，变量ID: {var_id}，语言: {lang}"
            )
            response = bps_interface.search_periods(
                domain=domain, page=page, var=var_id, lang=lang
            )
            logger.info(f"成功获取时期数据，共{len(response.data)}条记录")
            result[var_id] = {
                "status": response.status,
                "data": response.data,
                "message": f"成功获取时期数据，共{len(response.data)}条记录",
            }
        return result
    except Exception as e:
        logger.error(f"获取时期数据时出错: {str(e)}")
        return {
            "status": "error",
            "message": f"获取时期数据时出错: {str(e)}",
        }


@mcp.tool
def search_vervar(
    vars: List[int], domain: str = "0000", page: int = 1, lang: str = "ind"
) -> dict:
    """搜索垂直变量数据

    支持使用变量ID和关键词进行过滤搜索，关键词中的空格请使用"+"号代替。

    Args:
        vars: 变量ID，用于按变量过滤垂直变量数据
          支持多变量同时查询，返回结果根据变量ID-对应结果返回
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"

    Returns:
        包含搜索结果的字典，格式为：
        {
          var_id: {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
          }
        }
    """
    try:
        result = {}
        for var_id in vars:
            logger.info(
                f"正在搜索垂直变量数据，领域ID: {domain}，页码: {page}，变量ID: {var_id}，语言: {lang}"
            )
            response = bps_interface.search_vervar(
                domain=domain, page=page, var=var_id, lang=lang
            )
            logger.info(f"成功获取垂直变量数据，共{len(response.data)}条记录")
            result[var_id] = {
                "status": response.status,
                "data": response.data,
                "message": f"成功获取垂直变量数据，共{len(response.data)}条记录",
            }
        return result
    except Exception as e:
        logger.error(f"获取垂直变量数据时出错: {str(e)}")
        return {
            "status": "error",
            "message": f"获取垂直变量数据时出错: {str(e)}",
        }


@mcp.tool
def search_units(domain: str = "0000", page: int = 1, lang: str = "ind") -> dict:
    """搜索单位数据

    注意：此接口不支持keyword参数，请使用其他参数进行过滤。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(f"正在搜索单位数据，领域ID: {domain}，页码: {page}，语言: {lang}")
        response = bps_interface.search_units(domain=domain, page=page, lang=lang)
        logger.info(f"成功获取单位数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取单位数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取单位数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取单位数据时出错: {str(e)}",
        }


@mcp.tool
def search_subcat(domain: str = "0000", page: int = 1, lang: str = "ind") -> dict:
    """搜索子主题数据

    注意：此接口不支持keyword参数，请使用其他参数进行过滤。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(f"正在搜索子主题数据，领域ID: {domain}，页码: {page}，语言: {lang}")
        response = bps_interface.search_subcat(domain=domain, page=page, lang=lang)
        logger.info(f"成功获取子主题数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取子主题数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取子主题数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取子主题数据时出错: {str(e)}",
        }


@mcp.tool
def search_data(
    query: List[DataQueryRequest],
    domain: str = "0000",
    turvar: Optional[int] = None,
    vervar: Optional[int] = None,
    turth: Optional[int] = None,
    lang: str = "ind",
) -> dict:
    """搜索动态数据

    重要：这是获取动态数据的最终步骤。在获取变量ID和时期ID后，使用此工具获取实际的动态数据。

    注意：此接口不支持keyword参数，请使用var、th等参数进行过滤。
    var和th参数为必填项，用于指定要查询的变量和时间周期。
    注意：此接口不支持分页参数。

    Args:
        query: 动态数据查询变量列表,包括以下字段
            var: 变量ID（必填），可通过search_variables工具获取
            ths: 周期数据ID列表（必填），可通过search_periods工具获取
        domain: 领域ID，默认为"0000"表示全国数据
        turvar: 派生变量ID（可选），可通过search_turvar工具获取
        vervar: 垂直变量ID（可选），可通过search_vervar工具获取
        turth: 派生周期数据ID（可选），可通过search_truth工具获取
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"

    Returns:
        包含搜索结果的字典，格式为：
        {
          var_id:th: {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
          }
        }
    """
    result = {}
    try:
        for data_query in query:
            var = data_query.var
            ths = data_query.ths
            for th in ths:
                # 检查必填参数
                if var is None or th is None:
                    # 忽略空参数
                    continue
                logger.info(
                    f"正在搜索动态数据，领域ID: {domain}，变量ID: {var}，周期ID: {th}，语言: {lang}"
                )
                response = bps_interface.search_data(
                    domain=domain,
                    var=var,
                    th=th,
                    turvar=turvar,
                    vervar=vervar,
                    turth=turth,
                    lang=lang,
                )
                logger.info(f"成功获取动态数据，共{len(response.data)}条记录")

                # 初始化变量的字典
                if var not in result:
                    result[var] = {}

                # 返回结果，确保返回完整的数据结构
                result[var][th] = {
                    "status": response.status,
                    "data": response.data,
                    "message": f"成功获取动态数据，共{len(response.data)}条记录",
                }

                # 如果response.data是一个字典（完整的数据结构），直接返回
                if isinstance(response.data, dict):
                    # 确保必要的字段都在
                    required_fields = ["status", "data-availability", "datacontent"]
                    if all(field in response.data for field in required_fields):
                        # 返回完整的数据结构
                        result[var][th] = response.data
        return result
    except Exception as e:
        logger.error(f"获取动态数据时出错: {str(e)}")
        return {
            "status": "error",
            "message": f"获取动态数据时出错: {str(e)}",
        }


@mcp.tool
def search_truth(
    domain: str = "0000", page: int = 1, var: Optional[int] = None, lang: str = "ind"
) -> dict:
    """搜索衍生周期数据

    注意：此接口不支持keyword参数，请使用其他参数进行过滤。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        var: 变量ID，用于按变量过滤衍生周期数据，可选参数
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索衍生周期数据，领域ID: {domain}，页码: {page}，变量ID: {var}，语言: {lang}"
        )
        response = bps_interface.search_truth(
            domain=domain, page=page, var=var, lang=lang
        )
        logger.info(f"成功获取衍生周期数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取衍生周期数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取衍生周期数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取衍生周期数据时出错: {str(e)}",
        }


@mcp.tool
def search_turvar(
    domain: str = "0000",
    page: int = 1,
    var: Optional[int] = None,
    group: Optional[int] = None,
    nopage: Optional[bool] = None,
    lang: str = "ind",
) -> dict:
    """搜索派生变量数据

    注意：此接口不支持keyword参数，请使用其他参数进行过滤。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        var: 变量ID，用于按变量过滤派生变量，可选参数
        group: 选定分组垂直变量以显示派生变量，可选参数
        nopage: 是否不分页，0表示分页，1表示不分页，可选参数
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索派生变量数据，领域ID: {domain}，页码: {page}，变量ID: {var}，语言: {lang}"
        )
        response = bps_interface.search_turvar(
            domain=domain, page=page, var=var, group=group, nopage=nopage, lang=lang
        )
        logger.info(f"成功获取派生变量数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取派生变量数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取派生变量数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取派生变量数据时出错: {str(e)}",
        }


@mcp.tool
def search_statictable(
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
    keyword: Optional[str] = None,
) -> dict:
    """搜索静态表格数据

    支持使用关键词进行搜索，关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"
        keyword: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索静态表格数据，领域ID: {domain}，页码: {page}，语言: {lang}，关键词: {keyword}"
        )
        response = bps_interface.search_statictable(
            domain=domain, page=page, lang=lang, keyword=keyword
        )
        logger.info(f"成功获取静态表格数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取静态表格数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取静态表格数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取静态表格数据时出错: {str(e)}",
        }


@mcp.tool
def search_subcatcsa(
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
    keyword: Optional[str] = None,
) -> dict:
    """搜索统计活动分类数据

    支持使用关键词进行搜索，关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"
        keyword: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索统计活动分类数据，领域ID: {domain}，页码: {page}，语言: {lang}，关键词: {keyword}"
        )
        response = bps_interface.search_subcatcsa(
            domain=domain, page=page, lang=lang, keyword=keyword
        )
        logger.info(f"成功获取统计活动分类数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取统计活动分类数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取统计活动分类数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取统计活动分类数据时出错: {str(e)}",
        }


@mcp.tool
def search_pressrelease(
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
    keyword: Optional[str] = None,
) -> dict:
    """搜索新闻稿数据

    支持使用关键词进行搜索，关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"
        keyword: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索新闻稿数据，领域ID: {domain}，页码: {page}，语言: {lang}，关键词: {keyword}"
        )
        response = bps_interface.search_pressrelease(
            domain=domain, page=page, lang=lang, keyword=keyword
        )
        logger.info(f"成功获取新闻稿数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取新闻稿数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取新闻稿数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取新闻稿数据时出错: {str(e)}",
        }


@mcp.tool
def search_indicators(
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
    keyword: Optional[str] = None,
) -> dict:
    """搜索指标数据

    支持使用关键词进行搜索，关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"
        keyword: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索指标数据，领域ID: {domain}，页码: {page}，语言: {lang}，关键词: {keyword}"
        )
        response = bps_interface.search_indicators(
            domain=domain, page=page, lang=lang, keyword=keyword
        )
        logger.info(f"成功获取指标数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取指标数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取指标数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取指标数据时出错: {str(e)}",
        }


@mcp.tool
def search_infographic(
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
    keyword: Optional[str] = None,
) -> dict:
    """搜索信息图标数据

    支持使用关键词进行搜索，关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"
        keyword: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索信息图标数据，领域ID: {domain}，页码: {page}，语言: {lang}，关键词: {keyword}"
        )
        response = bps_interface.search_infographic(
            domain=domain, page=page, lang=lang, keyword=keyword
        )
        logger.info(f"成功获取信息图标数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取信息图标数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取信息图标数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取信息图标数据时出错: {str(e)}",
        }


@mcp.tool
def search_glosarium(
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
    keyword: Optional[str] = None,
) -> dict:
    """搜索词汇表数据

    支持使用关键词进行搜索，关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"
        keyword: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索词汇表数据，领域ID: {domain}，页码: {page}，语言: {lang}，关键词: {keyword}"
        )
        response = bps_interface.search_glosarium(
            domain=domain, page=page, lang=lang, keyword=keyword
        )
        logger.info(f"成功获取词汇表数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取词汇表数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取词汇表数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取词汇表数据时出错: {str(e)}",
        }


@mcp.tool
def search_sdgs(
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
    keyword: Optional[str] = None,
) -> dict:
    """搜索可持续发展数据

    支持使用关键词进行搜索，关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"
        keyword: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索可持续发展数据，领域ID: {domain}，页码: {page}，语言: {lang}，关键词: {keyword}"
        )
        response = bps_interface.search_sdgs(
            domain=domain, page=page, lang=lang, keyword=keyword
        )
        logger.info(f"成功获取可持续发展数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取可持续发展数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取可持续发展数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取可持续发展数据时出错: {str(e)}",
        }


@mcp.tool
def search_sdds(
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
    keyword: Optional[str] = None,
) -> dict:
    """搜索特殊数据发布标准数据

    支持使用关键词进行搜索，关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"
        keyword: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在搜索特殊数据发布标准数据，领域ID: {domain}，页码: {page}，语言: {lang}，关键词: {keyword}"
        )
        response = bps_interface.search_sdds(
            domain=domain, page=page, lang=lang, keyword=keyword
        )
        logger.info(f"成功获取特殊数据发布标准数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取特殊数据发布标准数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取特殊数据发布标准数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取特殊数据发布标准数据时出错: {str(e)}",
        }


def parse_natural_language_query(query: str) -> Dict[str, Any]:
    """解析自然语言查询，提取关键词、时间范围等信息

    Args:
        query: 自然语言查询字符串

    Returns:
        包含解析结果的字典
    """
    # 提取年份范围 (如: 2022-2025)
    year_range_pattern = r"(\d{4})\s*[-~到至]\s*(\d{4})"
    year_range_match = re.search(year_range_pattern, query)

    # 提取单独年份 (如: 2022年)
    single_year_pattern = r"(\d{4})年?"
    single_year_matches = re.findall(single_year_pattern, query)

    # 提取关键词 (去除常见的停用词)
    stop_words = ["查询", "关于", "相关的", "信息", "数据", "统计"]
    # 移除停用词和数字
    keywords = [
        word for word in query.split() if word not in stop_words and not word.isdigit()
    ]
    # 从正则表达式匹配中添加年份关键词
    if year_range_match:
        start_year, end_year = year_range_match.groups()
        keywords.extend([start_year, end_year])
    elif single_year_matches:
        keywords.extend(single_year_matches)

    # 清理关键词，移除标点符号
    cleaned_keywords = []
    for keyword in keywords:
        # 移除标点符号
        cleaned_keyword = re.sub(r"[^\w\s]", "", keyword)
        if cleaned_keyword:
            cleaned_keywords.append(cleaned_keyword)

    result = {
        "original_query": query,
        "keywords": cleaned_keywords,
        "year_range": year_range_match.groups() if year_range_match else None,
        "single_years": single_year_matches if not year_range_match else [],
        "models_to_search": [],  # 将根据关键词确定要搜索的模型
    }

    # 根据关键词确定要搜索的模型
    models_to_search = set()

    # 与公司相关的关键词
    company_keywords = ["pt vale", "vale", "镍矿", "矿业", "公司", "企业"]
    if any(keyword.lower() in query.lower() for keyword in company_keywords):
        models_to_search.update(["news", "pressrelease", "publication"])

    # 与数据统计相关的关键词
    data_keywords = ["数据", "统计", "指标", "数值"]
    if any(keyword.lower() in query.lower() for keyword in data_keywords):
        models_to_search.update(["data", "statictable", "indicators"])

    # 与时间相关的关键词
    time_keywords = ["年", "季度", "月", "时期", "周期"]
    if any(keyword.lower() in query.lower() for keyword in time_keywords):
        models_to_search.update(["th", "truth"])

    # 默认搜索新闻
    if not models_to_search:
        models_to_search.add("news")

    result["models_to_search"] = list(models_to_search)

    return result


def filter_results_by_keywords(
    data: List[Any], keywords: List[str], model: str
) -> List[Any]:
    """根据关键词过滤搜索结果

    Args:
        data: 搜索结果数据
        keywords: 关键词列表
        model: 数据模型类型

    Returns:
        过滤后的数据
    """
    if not keywords or not data:
        return data

    filtered_data = []
    keywords_lower = [kw.lower() for kw in keywords]

    for item in data:
        # 将数据项转换为字符串进行匹配
        item_str = str(item).lower()

        # 检查是否包含任何关键词
        if any(keyword in item_str for keyword in keywords_lower):
            filtered_data.append(item)
        # 对于字典类型的数据，检查特定字段
        elif isinstance(item, dict):
            # 检查标题、名称等字段
            fields_to_check = [
                "title",
                "name",
                "新闻",
                "标题",
                "内容",
                "abstract",
                "press",
            ]
            for field in fields_to_check:
                if field in item and item[field]:
                    field_value = str(item[field]).lower()
                    if any(keyword in field_value for keyword in keywords_lower):
                        filtered_data.append(item)
                        break

    return filtered_data


# @mcp.tool
def natural_language_search(
    query: str,
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
    keyword: Optional[str] = None,
) -> dict:
    """自然语言搜索功能，支持关键词查询和年份范围过滤

    该工具可以解析自然语言查询，自动提取关键词和年份范围，并在多个相关模型中查找信息。
    支持的年份范围格式：2022-2025 或 2022到2025 或 2022至2025。
    关键词中的空格请使用"+"号代替。
    注意：keyword参数的语言应与lang参数保持一致，当lang="ind"时使用印尼语关键词，当lang="eng"时使用英语关键词。

    Args:
        query: 自然语言查询字符串，例如"查询2022-2025年关于PT Vale, 镍矿相关的信息"
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"
        keyword: 关键词，用于过滤搜索结果，可选参数。keyword参数的语言应与lang参数保持一致

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "success" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息,
            "query_info": {
                "original_query": 原始查询,
                "keywords": 提取的关键词,
                "year_range": 提取的年份范围,
                "models_to_search": 搜索的模型列表
            }
        }
    """
    global bps_interface
    # 初始化BPS接口（如果尚未初始化）
    if bps_interface is None:
        bps_interface = init_bps_interface()

    try:
        logger.info(
            f"正在进行自然语言搜索，查询: {query}，领域ID: {domain}，页码: {page}，语言: {lang}"
        )

        # 解析自然语言查询
        parsed_query = parse_natural_language_query(query)
        keywords = parsed_query["keywords"]
        year_range = parsed_query["year_range"]
        models_to_search = parsed_query["models_to_search"]

        logger.info(
            f"解析查询结果: 关键词={keywords}, 年份范围={year_range}, 搜索模型={models_to_search}"
        )

        # 存储所有搜索结果
        all_results = []

        # 遍历需要搜索的模型
        for model in models_to_search:
            try:
                logger.info(f"正在搜索模型: {model}")
                # 根据model类型调用相应的搜索方法
                if model == "subject":
                    response = bps_interface.search_subjects(
                        domain=domain, page=page, lang=lang
                    )
                elif model == "news":
                    response = bps_interface.search_news(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )
                elif model == "publication":
                    response = bps_interface.search_publications(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )
                elif model == "var":
                    response = bps_interface.search_variables(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )
                elif model == "th":
                    response = bps_interface.search_periods(
                        domain=domain, page=page, lang=lang
                    )
                elif model == "vervar":
                    response = bps_interface.search_vervar(
                        domain=domain, page=page, lang=lang
                    )
                elif model == "unit":
                    response = bps_interface.search_units(
                        domain=domain, page=page, lang=lang
                    )
                elif model == "subcat":
                    response = bps_interface.search_subcat(
                        domain=domain, page=page, lang=lang
                    )
                elif model == "data":
                    # 注意：data模型需要var和th参数，这里只是示例
                    # 实际使用时需要提供这些参数
                    response = bps_interface.search_data(
                        domain=domain, var=70, th=120, lang=lang
                    )  # 示例参数
                elif model == "truth":
                    response = bps_interface.search_truth(
                        domain=domain, page=page, lang=lang
                    )
                elif model == "turvar":
                    response = bps_interface.search_turvar(
                        domain=domain, page=page, lang=lang
                    )
                elif model == "statictable":
                    response = bps_interface.search_statictable(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )
                elif model == "subcatcsa":
                    response = bps_interface.search_subcatcsa(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )
                elif model == "pressrelease":
                    response = bps_interface.search_pressrelease(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )
                elif model == "indicators":
                    response = bps_interface.search_indicators(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )
                elif model == "infographic":
                    response = bps_interface.search_infographic(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )
                elif model == "glosarium":
                    response = bps_interface.search_glosarium(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )
                elif model == "sdgs":
                    response = bps_interface.search_sdgs(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )
                elif model == "sdds":
                    response = bps_interface.search_sdds(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )
                else:
                    # 默认使用新闻搜索
                    response = bps_interface.search_news(
                        domain=domain, page=page, lang=lang, keyword=keyword
                    )

                # 过滤结果
                filtered_data = filter_results_by_keywords(
                    response.data, keywords, model
                )

                # 如果有年份范围，进一步过滤
                if year_range and filtered_data:
                    start_year, end_year = map(int, year_range)
                    filtered_data = bps_interface.filter_data_by_year_range(
                        filtered_data, start_year, end_year
                    )

                # 为每个结果添加模型信息
                for item in filtered_data:
                    if isinstance(item, dict):
                        item["_model"] = model

                all_results.extend(filtered_data)
                logger.info(
                    f"模型 {model} 搜索完成，找到 {len(filtered_data)} 条匹配记录"
                )

            except Exception as e:
                logger.error(f"搜索模型 {model} 时出错: {str(e)}")
                # 继续搜索其他模型，不中断整个过程

        logger.info(f"自然语言搜索完成，共找到 {len(all_results)} 条记录")
        return {
            "status": "success",
            "data": all_results,
            "message": f"自然语言搜索完成，共找到 {len(all_results)} 条记录",
            "query_info": parsed_query,
        }

    except Exception as e:
        logger.error(f"自然语言搜索时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"自然语言搜索时出错: {str(e)}",
        }


# @mcp.tool
def advanced_search(
    query: str,
    model: str = "news",
    domain: str = "0000",
    page: int = 1,
    lang: str = "ind",
) -> dict:
    """高级搜索功能，支持关键词查询和指定模型搜索

    该工具允许在指定的数据模型中进行关键词搜索。与自然语言搜索不同，此工具需要明确指定搜索模型。
    支持19种不同的数据模型，关键词中的空格请使用"+"号代替。

    Args:
        query: 搜索关键词，例如"镍矿"
        model: 搜索模型，可选值包括：
            "subject"(主题), "news"(新闻), "publication"(出版物), "var"(变量),
            "th"(周期), "vervar"(地区), "unit"(单位), "subcat"(子主题),
            "data"(动态数据), "truth"(衍生周期), "turvar"(派生变量),
            "statictable"(静态表格), "subcatcsa"(统计活动分类), "pressrelease"(新闻稿),
            "indicators"(指标), "infographic"(信息图表), "glosarium"(词汇表),
            "sdgs"(可持续发展), "sdds"(特殊数据发布标准)
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        lang: 语言，可选值为"ind"(印尼语)或"eng"(英语)，默认为"ind"

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "model": 搜索的模型名称,
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    try:
        logger.info(
            f"正在进行高级搜索，关键词: {query}，模型: {model}，领域ID: {domain}，页码: {page}，语言: {lang}"
        )
        # 根据model类型调用相应的搜索方法
        if model == "subject":
            response = bps_interface.search_subjects(
                domain=domain, page=page, lang=lang
            )
        elif model == "news":
            response = bps_interface.search_news(
                domain=domain, page=page, lang=lang, keyword=query
            )
        elif model == "publication":
            response = bps_interface.search_publications(
                domain=domain, page=page, lang=lang, keyword=query
            )
        elif model == "var":
            response = bps_interface.search_variables(
                domain=domain, page=page, lang=lang, keyword=query
            )
        elif model == "th":
            response = bps_interface.search_periods(domain=domain, page=page, lang=lang)
        elif model == "vervar":
            response = bps_interface.search_vervar(domain=domain, page=page, lang=lang)
        elif model == "unit":
            response = bps_interface.search_units(domain=domain, page=page, lang=lang)
        elif model == "subcat":
            response = bps_interface.search_subcat(domain=domain, page=page, lang=lang)
        elif model == "data":
            response = bps_interface.search_data(domain=domain, page=page, lang=lang)
        elif model == "truth":
            response = bps_interface.search_truth(domain=domain, page=page, lang=lang)
        elif model == "turvar":
            response = bps_interface.search_turvar(domain=domain, page=page, lang=lang)
        elif model == "statictable":
            response = bps_interface.search_statictable(
                domain=domain, page=page, lang=lang, keyword=query
            )
        elif model == "subcatcsa":
            response = bps_interface.search_subcatcsa(
                domain=domain, page=page, lang=lang, keyword=query
            )
        elif model == "pressrelease":
            response = bps_interface.search_pressrelease(
                domain=domain, page=page, lang=lang, keyword=query
            )
        elif model == "indicators":
            response = bps_interface.search_indicators(
                domain=domain, page=page, lang=lang, keyword=query
            )
        elif model == "infographic":
            response = bps_interface.search_infographic(
                domain=domain, page=page, lang=lang, keyword=query
            )
        elif model == "glosarium":
            response = bps_interface.search_glosarium(
                domain=domain, page=page, lang=lang, keyword=query
            )
        elif model == "sdgs":
            response = bps_interface.search_sdgs(
                domain=domain, page=page, lang=lang, keyword=query
            )
        elif model == "sdds":
            response = bps_interface.search_sdds(
                domain=domain, page=page, lang=lang, keyword=query
            )
        else:
            # 默认使用新闻搜索
            response = bps_interface.search_news(
                domain=domain, page=page, lang=lang, keyword=query
            )

        logger.info(f"成功获取{model}数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "model": model,
            "data": response.data,
            "message": f"成功获取{model}数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取{model}数据时出错: {str(e)}")
        return {
            "status": "error",
            "model": model,
            "data": [],
            "message": f"获取{model}数据时出错: {str(e)}",
        }


@mcp.tool
def extract_hs_codes(keywords: List[str]) -> dict:
    """根据关键字获取对应的HS CODE
    
    该工具会从PDF文件中提取与给定关键字匹配的HS CODE信息。
    调用大模型将对应的关键词转换为英文和印尼语，以提高搜索准确性。
    甚至可以建议大模型根据用户给出的关键字扩展出其他相关项进行搜索。

    Args:
        keywords: 要搜索的关键字列表。
          使用英语和印尼语，可能不同的HS CODE使用了不同语言，例如镍可能在PDF存在 nickel 和 nikel 两种表示

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
        
        每个结果包含以下字段：
        - hs_code: HS CODE
        - year: 年份
        - description: 描述
    """
    global bps_interface
    try:
        logger.info(f"正在提取HS CODE，关键字: {keywords}")
        results = bps_interface.extract_hs_codes(keywords)
        logger.info(f"成功提取HS CODE，共{len(results)}条记录")
        return {
            "status": "OK",
            "data": results,
            "message": f"成功提取HS CODE，共{len(results)}条记录",
        }
    except Exception as e:
        logger.error(f"提取HS CODE时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"提取HS CODE时出错: {str(e)}",
        }


@mcp.tool
def search_foreign_trade_data(
    sumber: int,
    periode: int,
    kodehs: List[str],
    jenishs: int = 2,
    tahun: List[str] | None = None,
    lang: str = "ind"
) -> dict:
    """根据HS CODE查询对应的外贸数据
    
    外部接口通过';'分割多个HS CODE，而MCP暴露的接口接收参数使用数组接口，
    然后使用;分割符拼接后传给bps_api_client。
    
    Tahun 参数，外部接口只允许查询单年份。 而MCP暴露的接口数据年份入参允许传入数组，
    然后循环调用上述接口获取数据，减少大模型工具调用次数。

    Args:
        sumber: 数据类型 (1.出口 2.进口)
        periode: 数据时期 (1.月度 2.年度)
        kodehs: HS CODE列表
        jenishs: HS CODE类型，默认使用2
        tahun: 数据年份列表，默认为当前年份
        lang: 语言，默认为"ind"

    Returns:
        包含搜索结果的字典，格式为：
        {
            "status": "OK" 或 "error",
            "data": 搜索结果列表,
            "message": 描述信息
        }
    """
    global bps_interface
    
    # 如果tahun未提供，默认为当前年份
    if tahun is None:
        import datetime
        tahun = [str(datetime.datetime.now().year)]
    
    try:
        logger.info(f"正在查询外贸数据，数据类型: {sumber}，时期: {periode}，HS CODE: {kodehs}，年份: {tahun}")
        
        # 调用API客户端的批量查询方法
        results = bps_interface.search_foreign_trade_data_batch(
            sumber=sumber,
            periode=periode,
            kodehs_list=kodehs,
            jenishs=jenishs,
            tahun_list=tahun,
            lang=lang
        )
        
        # 统计总记录数
        total_records = 0
        for result in results.values():
            if result.status == "OK" and isinstance(result.data, list):
                total_records += len(result.data)
        
        logger.info(f"成功获取外贸数据，共{total_records}条记录")
        return {
            "status": "OK",
            "data": results,
            "message": f"成功获取外贸数据，共{total_records}条记录",
        }
    except Exception as e:
        logger.error(f"获取外贸数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取外贸数据时出错: {str(e)}",
        }


def main():
    # 在启动MCP服务器之前初始化BPS接口，确保环境变量已设置
    global bps_interface
    bps_interface = init_bps_interface()
    mcp.run()


if __name__ == "__main__":
    main()
