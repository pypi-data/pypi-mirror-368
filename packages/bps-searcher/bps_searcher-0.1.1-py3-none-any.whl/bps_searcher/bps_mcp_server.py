import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from .bps_api_client import BPSAPIInterface

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化FastMCP服务器
mcp = FastMCP("BPS Data Server")

# 从环境变量获取APP_ID，不提供默认值
APP_ID = os.environ.get("BPS_APP_ID")


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
def search_subjects(domain: str = "0000", page: int = 1) -> dict:
    """搜索主题数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    global bps_interface
    # 初始化BPS接口（如果尚未初始化）
    if bps_interface is None:
        bps_interface = init_bps_interface()

    try:
        logger.info(f"正在搜索主题数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_subjects(domain, page)
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
def search_news(domain: str = "0000", page: int = 1) -> dict:
    """搜索新闻数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索新闻数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_news(domain, page)
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
def search_publications(domain: str = "0000", page: int = 1) -> dict:
    """搜索出版物数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索出版物数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_publications(domain, page)
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
def search_variables(domain: str = "0000", page: int = 1) -> dict:
    """搜索变量数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索变量数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_variables(domain, page)
        logger.info(f"成功获取变量数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取变量数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取变量数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取变量数据时出错: {str(e)}",
        }


@mcp.tool
def search_periods(domain: str = "0000", page: int = 1) -> dict:
    """搜索时期数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索时期数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_periods(domain, page)
        logger.info(f"成功获取时期数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取时期数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取时期数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取时期数据时出错: {str(e)}",
        }


@mcp.tool
def search_regions(domain: str = "0000", page: int = 1) -> dict:
    """搜索地区数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索地区数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_regions(domain, page)
        logger.info(f"成功获取地区数据，共{len(response.data)}条记录")
        return {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取地区数据，共{len(response.data)}条记录",
        }
    except Exception as e:
        logger.error(f"获取地区数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取地区数据时出错: {str(e)}",
        }


@mcp.tool
def search_units(domain: str = "0000", page: int = 1) -> dict:
    """搜索单位数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索单位数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_units(domain, page)
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
def search_subcat(domain: str = "0000", page: int = 1) -> dict:
    """搜索子主题数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索子主题数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_subcat(domain, page)
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
    domain: str = "0000",
    page: int = 1,
    var: int = None,
    th: int = None,
    turvar: int = None,
    vervar: int = None,
    turth: int = None,
) -> dict:
    """搜索动态数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1
        var: 变量ID（必填）
        th: 周期数据ID（必填）
        turvar: 派生变量ID（可选）
        vervar: 垂直变量ID（可选）
        turth: 派生周期数据ID（可选）

    Returns:
        包含搜索结果的字典
    """
    # 检查必填参数
    if var is None or th is None:
        return {
            "status": "error",
            "data": [],
            "message": "var和th参数为必填项",
        }

    try:
        logger.info(
            f"正在搜索动态数据，领域ID: {domain}，页码: {page}，变量ID: {var}，周期ID: {th}"
        )
        response = bps_interface.search_data(
            domain=domain,
            page=page,
            var=var,
            th=th,
            turvar=turvar,
            vervar=vervar,
            turth=turth,
        )
        logger.info(f"成功获取动态数据，共{len(response.data)}条记录")

        # 返回结果
        result = {
            "status": response.status,
            "data": response.data,
            "message": f"成功获取动态数据，共{len(response.data)}条记录",
        }

        return result
    except Exception as e:
        logger.error(f"获取动态数据时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"获取动态数据时出错: {str(e)}",
        }


@mcp.tool
def search_truth(domain: str = "0000", page: int = 1) -> dict:
    """搜索衍生周期数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索衍生周期数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_truth(domain, page)
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
def search_turvar(domain: str = "0000", page: int = 1) -> dict:
    """搜索派生变量数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索派生变量数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_turvar(domain, page)
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
def search_statictable(domain: str = "0000", page: int = 1) -> dict:
    """搜索静态表格数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索静态表格数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_statictable(domain, page)
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
def search_subcatcsa(domain: str = "0000", page: int = 1) -> dict:
    """搜索统计活动分类数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索统计活动分类数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_subcatcsa(domain, page)
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
def search_pressrelease(domain: str = "0000", page: int = 1) -> dict:
    """搜索新闻稿数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索新闻稿数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_pressrelease(domain, page)
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
def search_indicators(domain: str = "0000", page: int = 1) -> dict:
    """搜索指标数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索指标数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_indicators(domain, page)
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
def search_infographic(domain: str = "0000", page: int = 1) -> dict:
    """搜索信息图标数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索信息图标数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_infographic(domain, page)
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
def search_glosarium(domain: str = "0000", page: int = 1) -> dict:
    """搜索词汇表数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索词汇表数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_glosarium(domain, page)
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
def search_sdgs(domain: str = "0000", page: int = 1) -> dict:
    """搜索可持续发展数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索可持续发展数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_sdgs(domain, page)
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
def search_sdds(domain: str = "0000", page: int = 1) -> dict:
    """搜索特殊数据发布标准数据

    Args:
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"正在搜索特殊数据发布标准数据，领域ID: {domain}，页码: {page}")
        response = bps_interface.search_sdds(domain, page)
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


@mcp.tool
def natural_language_search(query: str, domain: str = "0000", page: int = 1) -> dict:
    """自然语言搜索功能，支持关键词查询

    Args:
        query: 自然语言查询字符串
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    global bps_interface
    # 初始化BPS接口（如果尚未初始化）
    if bps_interface is None:
        bps_interface = init_bps_interface()

    try:
        logger.info(
            f"正在进行自然语言搜索，查询: {query}，领域ID: {domain}，页码: {page}"
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
                    response = bps_interface.search_subjects(domain, page)
                elif model == "news":
                    response = bps_interface.search_news(domain, page)
                elif model == "publication":
                    response = bps_interface.search_publications(domain, page)
                elif model == "var":
                    response = bps_interface.search_variables(domain, page)
                elif model == "th":
                    response = bps_interface.search_periods(domain, page)
                elif model == "vervar":
                    response = bps_interface.search_regions(domain, page)
                elif model == "unit":
                    response = bps_interface.search_units(domain, page)
                elif model == "subcat":
                    response = bps_interface.search_subcat(domain, page)
                elif model == "data":
                    # 注意：data模型需要var和th参数，这里只是示例
                    # 实际使用时需要提供这些参数
                    response = bps_interface.search_data(
                        domain, page, var=70, th=120
                    )  # 示例参数
                elif model == "truth":
                    response = bps_interface.search_truth(domain, page)
                elif model == "turvar":
                    response = bps_interface.search_turvar(domain, page)
                elif model == "statictable":
                    response = bps_interface.search_statictable(domain, page)
                elif model == "subcatcsa":
                    response = bps_interface.search_subcatcsa(domain, page)
                elif model == "pressrelease":
                    response = bps_interface.search_pressrelease(domain, page)
                elif model == "indicators":
                    response = bps_interface.search_indicators(domain, page)
                elif model == "infographic":
                    response = bps_interface.search_infographic(domain, page)
                elif model == "glosarium":
                    response = bps_interface.search_glosarium(domain, page)
                elif model == "sdgs":
                    response = bps_interface.search_sdgs(domain, page)
                elif model == "sdds":
                    response = bps_interface.search_sdds(domain, page)
                else:
                    # 默认使用新闻搜索
                    response = bps_interface.search_news(domain, page)

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


@mcp.tool
def advanced_search(
    query: str, model: str = "news", domain: str = "0000", page: int = 1
) -> dict:
    """高级搜索功能，支持关键词查询

    Args:
        query: 搜索关键词
        model: 搜索模型，可选值见ModelType
        domain: 领域ID，默认为"0000"表示全国数据
        page: 页码，默认为1

    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(
            f"正在进行高级搜索，关键词: {query}，模型: {model}，领域ID: {domain}，页码: {page}"
        )
        # 根据model类型调用相应的搜索方法
        if model == "subject":
            response = bps_interface.search_subjects(domain, page)
        elif model == "news":
            response = bps_interface.search_news(domain, page)
        elif model == "publication":
            response = bps_interface.search_publications(domain, page)
        elif model == "var":
            response = bps_interface.search_variables(domain, page)
        elif model == "th":
            response = bps_interface.search_periods(domain, page)
        elif model == "vervar":
            response = bps_interface.search_regions(domain, page)
        elif model == "unit":
            response = bps_interface.search_units(domain, page)
        elif model == "subcat":
            response = bps_interface.search_subcat(domain, page)
        elif model == "data":
            response = bps_interface.search_data(domain, page)
        elif model == "truth":
            response = bps_interface.search_truth(domain, page)
        elif model == "turvar":
            response = bps_interface.search_turvar(domain, page)
        elif model == "statictable":
            response = bps_interface.search_statictable(domain, page)
        elif model == "subcatcsa":
            response = bps_interface.search_subcatcsa(domain, page)
        elif model == "pressrelease":
            response = bps_interface.search_pressrelease(domain, page)
        elif model == "indicators":
            response = bps_interface.search_indicators(domain, page)
        elif model == "infographic":
            response = bps_interface.search_infographic(domain, page)
        elif model == "glosarium":
            response = bps_interface.search_glosarium(domain, page)
        elif model == "sdgs":
            response = bps_interface.search_sdgs(domain, page)
        elif model == "sdds":
            response = bps_interface.search_sdds(domain, page)
        else:
            # 默认使用新闻搜索
            response = bps_interface.search_news(domain, page)

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


def main():
    # 在启动MCP服务器之前初始化BPS接口，确保环境变量已设置
    global bps_interface
    bps_interface = init_bps_interface()
    mcp.run()


if __name__ == "__main__":
    main()
