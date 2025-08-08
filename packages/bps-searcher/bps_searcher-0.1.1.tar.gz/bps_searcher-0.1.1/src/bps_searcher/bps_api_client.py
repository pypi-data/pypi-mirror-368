import json
import os
import pickle
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import requests


class ModelType(Enum):
    SUBJECT = "subject"
    SUBCAT = "subcat"
    DATA = "data"
    TRUTH = "truth"
    TURVAR = "turvar"
    TH = "th"
    UNIT = "unit"
    VAR = "var"
    VERVAR = "vervar"
    STATICTABLE = "statictable"
    SUBCATCSA = "subcatcsa"
    PRESSRELEASE = "pressrelease"
    PUBLICATION = "publication"
    INDICATORS = "indicators"
    INFOGRAPHIC = "infographic"
    GLOSARIUM = "glosarium"
    SDGS = "sdgs"
    SDDS = "sdds"
    NEWS = "news"


@dataclass
class SearchResult:
    page: int
    pages: int
    per_page: int
    count: int
    total: int


@dataclass
class APIResponse:
    status: str
    data_availability: str
    data: List[Any]
    pagination: Optional[SearchResult] = None


@dataclass
class PaginationResult:
    """分页结果"""

    data: List[Any]
    pagination: SearchResult
    has_next: bool
    has_previous: bool

    def get_next_page(self) -> Optional[int]:
        """获取下一页页码"""
        if self.has_next:
            return self.pagination.page + 1
        return None

    def get_previous_page(self) -> Optional[int]:
        """获取上一页页码"""
        if self.has_previous:
            return self.pagination.page - 1
        return None


# 定义各model的数据结构
@dataclass
class SubjectData:
    sub_id: int
    title: str
    subcat_id: int
    subcat: str
    ntabel: Optional[str]


@dataclass
class NewsData:
    news_id: int
    newscat_id: str
    newscat_name: str
    title: str
    news: str
    rl_date: str
    picture: str


@dataclass
class PublicationData:
    pub_id: str
    title: str
    abstract: str
    id_subject_csa: Optional[List[int]]
    subject_csa: Optional[List[str]]
    issn: str
    sch_date: Optional[str]
    rl_date: str
    updt_date: Optional[str]
    cover: str
    pdf: str
    size: str


@dataclass
class ThData:
    th_id: int
    th: str


@dataclass
class VervarData:
    kode_ver_id: int
    vervar: str
    item_ver_id: int
    group_ver_id: int
    name_group_ver_id: str


@dataclass
class VarData:
    var_id: int
    title: str
    sub_id: int
    sub_name: str
    subcsa_id: int
    subcsa_name: str
    def_: str
    notes: str
    vertical: int
    unit: str
    graph_id: int
    graph_name: str


@dataclass
class UnitData:
    unit_id: int
    unit: str


# BPS API接口定义
class BPSAPIInterface:
    def __init__(self, app_id: str, cache_ttl: int = 300):
        """
        初始化BPS API客户端

        Args:
            app_id: BPS API的鉴权KEY
            cache_ttl: 缓存过期时间（秒），默认300秒（5分钟）
        """
        self.app_id = app_id
        self.base_url = "https://webapi.bps.go.id/v1/api"
        self.cache_ttl = cache_ttl
        self.cache = {}  # 缓存字典，存储API响应

    def _make_request(self, endpoint: str) -> str:
        """发起API请求"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def _make_request_with_params(self, endpoint: str, params: dict = None) -> str:
        """发起带参数的API请求"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text

    def _get_cache_key(self, model: str, domain: str, page: int) -> str:
        """生成缓存键"""
        return f"{model}:{domain}:{page}"

    def _get_from_cache(
        self, model: str, domain: str, page: int
    ) -> Optional[APIResponse]:
        """从缓存中获取数据"""
        cache_key = self._get_cache_key(model, domain, page)
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            # 检查缓存是否过期
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                # 缓存过期，删除缓存项
                del self.cache[cache_key]
        return None

    def _get_from_cache_with_key(self, cache_key: str) -> Optional[APIResponse]:
        """从缓存中获取数据（使用自定义缓存键）"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            # 检查缓存是否过期
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                # 缓存过期，删除缓存项
                del self.cache[cache_key]
        return None

    def _set_cache(self, model: str, domain: str, page: int, data: APIResponse):
        """将数据存入缓存"""
        cache_key = self._get_cache_key(model, domain, page)
        self.cache[cache_key] = (data, time.time())

    def _set_cache_with_key(self, cache_key: str, data: APIResponse):
        """将数据存入缓存（使用自定义缓存键）"""
        self.cache[cache_key] = (data, time.time())

    def search_with_pagination(
        self, search_func, domain: str = "0000", page: int = 1
    ) -> PaginationResult:
        """
        使用分页搜索功能

        Args:
            search_func: 搜索函数（如 self.search_news）
            domain: 领域ID
            page: 页码

        Returns:
            PaginationResult: 包含数据和分页信息的结果
        """
        response = search_func(domain=domain, page=page)

        if response.pagination is None:
            raise ValueError("API响应中没有分页信息")

        pagination = response.pagination
        has_next = pagination.page < pagination.pages
        has_previous = pagination.page > 1

        return PaginationResult(
            data=response.data,
            pagination=pagination,
            has_next=has_next,
            has_previous=has_previous,
        )

    def search_subjects(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索主题数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("subject", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/subject/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("subject", domain, page, result)

        return result

    def search_news(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索新闻数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("news", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/news/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("news", domain, page, result)

        return result

    def search_publications(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索出版物数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("publication", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = (
            f"list/model/publication/domain/{domain}/page/{page}/key/{self.app_id}/"
        )
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("publication", domain, page, result)

        return result

    def search_variables(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索变量数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("var", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/var/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("var", domain, page, result)

        return result

    def search_periods(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索时期数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("th", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/th/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("th", domain, page, result)

        return result

    def search_regions(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索地区数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("vervar", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/vervar/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("vervar", domain, page, result)

        return result

    def search_units(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索单位数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("unit", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/unit/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("unit", domain, page, result)

        return result

    def search_subcat(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索子主题数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("subcat", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/subcat/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("subcat", domain, page, result)

        return result

    def search_data(
        self,
        domain: str = "0000",
        page: int = 1,
        var: int = None,
        th: int = None,
        turvar: Optional[int] = None,
        vervar: Optional[int] = None,
        turth: Optional[int] = None,
    ) -> APIResponse:
        """搜索动态数据

        Args:
            domain: 领域ID
            page: 页码
            var: 变量ID（必填）
            th: 周期数据ID（必填）
            turvar: 派生变量ID（可选）
            vervar: 垂直变量ID（可选）
            turth: 派生周期数据ID（可选）
        """
        # 检查必填参数
        if var is None or th is None:
            raise ValueError("var和th参数为必填项")

        # 生成缓存键
        cache_key = f"data:{domain}:{page}:{var}:{th}:{turvar}:{vervar}:{turth}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建参数
        params = {
            "model": "data",
            "domain": domain,
            "var": var,
            "th": th,
            "page": page,
            "key": self.app_id,
        }

        # 添加可选参数
        if turvar is not None:
            params["turvar"] = turvar
        if vervar is not None:
            params["vervar"] = vervar
        if turth is not None:
            params["turth"] = turth

        # 发起API请求
        endpoint = "list"
        try:
            response_text = self._make_request_with_params(endpoint, params)
            result = parse_api_response(response_text)
        except Exception as e:
            # 如果返回null，返回空数据
            if "null" in str(e) or "NoneType" in str(e):
                result = APIResponse(
                    status="OK", data_availability="unavailable", data=[]
                )
            else:
                raise e

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_truth(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索衍生周期数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("truth", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/truth/domain/{domain}/page/{page}/key/{self.app_id}/"
        try:
            response_text = self._make_request(endpoint)
            result = parse_api_response(response_text)
        except Exception as e:
            # 如果模型不被识别，返回空数据
            if "not recognized" in str(e):
                result = APIResponse(
                    status="Error", data_availability="unavailable", data=[]
                )
            else:
                raise e

        # 将结果存入缓存
        self._set_cache("truth", domain, page, result)

        return result

    def search_turvar(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索派生变量数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("turvar", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/turvar/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("turvar", domain, page, result)

        return result

    def search_statictable(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索静态表格数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("statictable", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = (
            f"list/model/statictable/domain/{domain}/page/{page}/key/{self.app_id}/"
        )
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("statictable", domain, page, result)

        return result

    def search_subcatcsa(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索统计活动分类数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("subcatcsa", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = (
            f"list/model/subcatcsa/domain/{domain}/page/{page}/key/{self.app_id}/"
        )
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("subcatcsa", domain, page, result)

        return result

    def search_pressrelease(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索新闻稿数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("pressrelease", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = (
            f"list/model/pressrelease/domain/{domain}/page/{page}/key/{self.app_id}/"
        )
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("pressrelease", domain, page, result)

        return result

    def search_indicators(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索指标数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("indicators", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = (
            f"list/model/indicators/domain/{domain}/page/{page}/key/{self.app_id}/"
        )
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("indicators", domain, page, result)

        return result

    def search_infographic(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索信息图标数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("infographic", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = (
            f"list/model/infographic/domain/{domain}/page/{page}/key/{self.app_id}/"
        )
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("infographic", domain, page, result)

        return result

    def search_glosarium(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索词汇表数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("glosarium", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = (
            f"list/model/glosarium/domain/{domain}/page/{page}/key/{self.app_id}/"
        )
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("glosarium", domain, page, result)

        return result

    def search_sdgs(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索可持续发展数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("sdgs", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/sdgs/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("sdgs", domain, page, result)

        return result

    def search_sdds(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索特殊数据发布标准数据"""
        # 尝试从缓存中获取数据
        cached_result = self._get_from_cache("sdds", domain, page)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/sdds/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache("sdds", domain, page, result)

        return result

    def filter_data_by_year_range(
        self,
        data: List[Any],
        start_year: int,
        end_year: int,
        date_field: str = "rl_date",
    ) -> List[Any]:
        """根据年份范围过滤数据

        Args:
            data: 要过滤的数据列表
            start_year: 开始年份
            end_year: 结束年份
            date_field: 日期字段名，默认为"rl_date"

        Returns:
            过滤后的数据列表
        """
        filtered_data = []

        for item in data:
            if isinstance(item, dict) and date_field in item:
                date_str = item[date_field]
                # 从日期字符串中提取年份
                year_match = re.search(r"(\d{4})", str(date_str))
                if year_match:
                    year = int(year_match.group(1))
                    if start_year <= year <= end_year:
                        filtered_data.append(item)
            else:
                # 如果没有日期字段，保留所有数据
                filtered_data.append(item)

        return filtered_data


# 工具函数
def parse_api_response(response_text: str) -> APIResponse:
    """解析API响应"""
    try:
        data = json.loads(response_text)
        # 检查响应是否包含预期的字段
        if "status" not in data:
            raise ValueError("响应中缺少status字段")
        if "data-availability" not in data:
            # 如果没有data-availability字段，使用默认值
            data_availability = (
                "available" if "data" in data and data["data"] else "unavailable"
            )
        else:
            data_availability = data["data-availability"]

        # 如果没有data字段，使用空列表
        api_data = data.get("data", [])

        # 提取分页信息
        pagination = None
        if (
            isinstance(api_data, list)
            and len(api_data) >= 1
            and isinstance(api_data[0], dict)
        ):
            try:
                pagination = format_search_result(api_data)
                # 只返回实际的数据部分（去掉分页信息）
                if len(api_data) > 1:
                    api_data = api_data[1]
                else:
                    api_data = []
            except ValueError:
                # 如果格式化搜索结果失败，保持原始数据
                pass

        return APIResponse(
            status=data["status"],
            data_availability=data_availability,
            data=api_data,
            pagination=pagination,
        )
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON response")


def format_search_result(data: List[Any]) -> SearchResult:
    """格式化搜索结果"""
    if not data or len(data) < 2:
        raise ValueError("Invalid data structure")

    meta = data[0]
    return SearchResult(
        page=meta["page"],
        pages=meta["pages"],
        per_page=meta["per_page"],
        count=meta["count"],
        total=meta["total"],
    )
