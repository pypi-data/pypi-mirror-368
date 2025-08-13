import json
import os
import re
import time
from dataclasses import dataclass
from enum import Enum
from importlib import resources
from typing import Any, List, Optional

import fitz  # PyMuPDF
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

    def _make_request_with_params(
        self, endpoint: str, params: dict | None = None
    ) -> str:
        """发起带参数的API请求"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text

    def _make_foreign_trade_request(self, params: dict) -> str:
        """发起外贸数据API请求

        外贸数据API使用不同的端点: https://webapi.bps.go.id/v1/api/dataexim/
        """
        url = "https://webapi.bps.go.id/v1/api/dataexim/"
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

    def search_subjects(
        self, domain: str = "0000", page: int = 1, lang: str = "ind"
    ) -> APIResponse:
        """搜索主题数据

        注意：此接口不支持keyword参数，请使用其他参数进行过滤。
        """
        # 尝试从缓存中获取数据
        cache_key = f"subject:{domain}:{page}:{lang}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/subject/domain/{domain}/page/{page}/lang/{lang}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_news(
        self,
        domain: str = "0000",
        page: int = 1,
        lang: str = "ind",
        keyword: Optional[str] = None,
    ) -> APIResponse:
        """搜索新闻数据"""
        # 尝试从缓存中获取数据
        cache_key = f"news:{domain}:{page}:{lang}:{keyword}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/news/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了keyword，添加到endpoint中
        if keyword is not None:
            # 将空格替换为"+"号
            formatted_keyword = keyword.replace(" ", "+")
            endpoint += f"/keyword/{formatted_keyword}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_publications(
        self,
        domain: str = "0000",
        page: int = 1,
        lang: str = "ind",
        keyword: Optional[str] = None,
    ) -> APIResponse:
        """搜索出版物数据"""
        # 尝试从缓存中获取数据
        cache_key = f"publication:{domain}:{page}:{lang}:{keyword}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/publication/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了keyword，添加到endpoint中
        if keyword is not None:
            # 将空格替换为"+"号
            formatted_keyword = keyword.replace(" ", "+")
            endpoint += f"/keyword/{formatted_keyword}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_variables(
        self,
        domain: str = "0000",
        page: int = 1,
        subject: Optional[int] = None,
        year: Optional[int] = None,
        area: Optional[bool] = None,
        vervar: Optional[int] = None,
        lang: str = "ind",
        keyword: Optional[str] = None,
    ) -> APIResponse:
        """搜索变量数据

        Args:
            domain: 领域ID
            page: 页码
            subject: 主题ID（可选）
            year: 年份（可选）
            area: 显示领域内现有变量的参数（可选，1表示显示现有变量，0表示不显示）
            vervar: 垂直变量ID（可选）
            lang: 语言（可选，默认为"ind"）
            keyword: 关键字（可选）
        """
        # 尝试从缓存中获取数据
        cache_key = (
            f"var:{domain}:{page}:{subject}:{year}:{area}:{vervar}:{lang}:{keyword}"
        )
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/var/domain/{domain}/page/{page}/lang/{lang}"

        # 添加可选参数
        if subject is not None:
            endpoint += f"/subject/{subject}"
        if year is not None:
            endpoint += f"/year/{year}"
        if area is not None:
            endpoint += f"/area/{1 if area else 0}"
        if vervar is not None:
            endpoint += f"/vervar/{vervar}"
        if keyword is not None:
            # 将空格替换为"+"号
            formatted_keyword = keyword.replace(" ", "+")
            endpoint += f"/keyword/{formatted_keyword}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_periods(
        self,
        domain: str = "0000",
        page: int = 1,
        var: Optional[int] = None,
        lang: str = "ind",
    ) -> APIResponse:
        """搜索时期数据

        Args:
            domain: 领域ID
            page: 页码
            var: 变量ID（可选）
            lang: 语言（可选，默认为"ind"）

        注意：此接口不支持keyword参数，请使用其他参数进行过滤。
        """
        # 尝试从缓存中获取数据
        cache_key = f"th:{domain}:{page}:{var}:{lang}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/th/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了var，添加到endpoint中
        if var is not None:
            endpoint += f"/var/{var}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_vervar(
        self,
        domain: str = "0000",
        page: int = 1,
        var: Optional[int] = None,
        lang: str = "ind",
    ) -> APIResponse:
        """搜索垂直变量数据

        Args:
            domain: 领域ID
            page: 页码
            var: 变量ID（可选）
            lang: 语言（可选，默认为"ind"）
        """
        # 尝试从缓存中获取数据
        cache_key = f"vervar:{domain}:{page}:{var}:{lang}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/vervar/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了var，添加到endpoint中
        if var is not None:
            endpoint += f"/var/{var}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_units(
        self, domain: str = "0000", page: int = 1, lang: str = "ind"
    ) -> APIResponse:
        """搜索单位数据

        注意：此接口不支持keyword参数，请使用其他参数进行过滤。
        """
        # 尝试从缓存中获取数据
        cache_key = f"unit:{domain}:{page}:{lang}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/unit/domain/{domain}/page/{page}/lang/{lang}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_subcat(
        self, domain: str = "0000", page: int = 1, lang: str = "ind"
    ) -> APIResponse:
        """搜索子主题数据

        注意：此接口不支持keyword参数，请使用其他参数进行过滤。
        """
        # 尝试从缓存中获取数据
        cache_key = f"subcat:{domain}:{page}:{lang}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 缓存中没有数据，发起API请求
        endpoint = f"list/model/subcat/domain/{domain}/page/{page}/lang/{lang}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_data(
        self,
        domain: str = "0000",
        var: int | None = None,
        th: int | None = None,
        turvar: Optional[int] = None,
        vervar: Optional[int] = None,
        turth: Optional[int] = None,
        lang: str = "ind",
    ) -> APIResponse:
        """搜索动态数据

        Args:
            domain: 领域ID
            var: 变量ID（必填）
            th: 周期数据ID（必填）
            turvar: 派生变量ID（可选）
            vervar: 垂直变量ID（可选）
            turth: 派生周期数据ID（可选）
            lang: 语言（可选，默认为"ind"）

        注意：此接口不支持keyword参数，请使用var、th等参数进行过滤。
        注意：此接口不支持分页参数。
        """
        # 检查必填参数
        if var is None or th is None:
            raise ValueError("var和th参数为必填项")

        # 生成缓存键
        cache_key = f"data:{domain}:{var}:{th}:{turvar}:{vervar}:{turth}:{lang}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建参数
        params = {
            "model": "data",
            "domain": domain,
            "var": var,
            "th": th,
            "lang": lang,
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
            # data接口的响应格式与其他接口不同，需要特殊处理
            result = self._parse_data_response(response_text)
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

    def _parse_data_response(self, response_text: str) -> APIResponse:
        """解析data接口的响应

        data接口的响应格式与其他接口不同，不包含分页信息。
        """
        try:
            data = json.loads(response_text)
            # 检查响应是否包含预期的字段
            if "status" not in data:
                raise ValueError("响应中缺少status字段")
            if "data-availability" not in data:
                # 如果没有data-availability字段，使用默认值
                data_availability = (
                    "available"
                    if "datacontent" in data and data["datacontent"]
                    else "unavailable"
                )
            else:
                data_availability = data["data-availability"]

            # data接口不包含分页信息
            return APIResponse(
                status=data["status"],
                data_availability=data_availability,
                data=data,  # 返回完整的数据结构，而不是仅仅datacontent字段
            )
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response")

    def search_truth(
        self,
        domain: str = "0000",
        page: int = 1,
        var: Optional[int] = None,
        lang: str = "ind",
    ) -> APIResponse:
        """搜索衍生周期数据

        Args:
            domain: 领域ID
            page: 页码
            var: 变量ID（可选）
            lang: 语言（可选，默认为"ind"）
        """
        # 尝试从缓存中获取数据
        cache_key = f"truth:{domain}:{page}:{var}:{lang}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/truth/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了var，添加到endpoint中
        if var is not None:
            endpoint += f"/var/{var}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
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
        self._set_cache_with_key(cache_key, result)

        return result

    def search_turvar(
        self,
        domain: str = "0000",
        page: int = 1,
        var: Optional[int] = None,
        group: Optional[int] = None,
        nopage: Optional[bool] = None,
        lang: str = "ind",
    ) -> APIResponse:
        """搜索派生变量数据

        Args:
            domain: 领域ID
            page: 页码
            var: 变量ID（可选）
            group: 选定分组垂直变量以显示派生变量（可选）
            nopage: 是否不分页（可选，0表示分页，1表示不分页）
            lang: 语言（可选，默认为"ind"）
        """
        # 尝试从缓存中获取数据
        cache_key = f"turvar:{domain}:{page}:{var}:{group}:{nopage}:{lang}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/turvar/domain/{domain}/page/{page}/lang/{lang}"

        # 添加可选参数
        if var is not None:
            endpoint += f"/var/{var}"
        if group is not None:
            endpoint += f"/group/{group}"
        if nopage is not None:
            endpoint += f"/nopage/{1 if nopage else 0}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_statictable(
        self,
        domain: str = "0000",
        page: int = 1,
        lang: str = "ind",
        keyword: Optional[str] = None,
    ) -> APIResponse:
        """搜索静态表格数据"""
        # 尝试从缓存中获取数据
        cache_key = f"statictable:{domain}:{page}:{lang}:{keyword}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/statictable/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了keyword，添加到endpoint中
        if keyword is not None:
            # 将空格替换为"+"号
            formatted_keyword = keyword.replace(" ", "+")
            endpoint += f"/keyword/{formatted_keyword}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_subcatcsa(
        self,
        domain: str = "0000",
        page: int = 1,
        lang: str = "ind",
        keyword: Optional[str] = None,
    ) -> APIResponse:
        """搜索统计活动分类数据"""
        # 尝试从缓存中获取数据
        cache_key = f"subcatcsa:{domain}:{page}:{lang}:{keyword}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/subcatcsa/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了keyword，添加到endpoint中
        if keyword is not None:
            # 将空格替换为"+"号
            formatted_keyword = keyword.replace(" ", "+")
            endpoint += f"/keyword/{formatted_keyword}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_pressrelease(
        self,
        domain: str = "0000",
        page: int = 1,
        lang: str = "ind",
        keyword: Optional[str] = None,
    ) -> APIResponse:
        """搜索新闻稿数据"""
        # 尝试从缓存中获取数据
        cache_key = f"pressrelease:{domain}:{page}:{lang}:{keyword}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/pressrelease/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了keyword，添加到endpoint中
        if keyword is not None:
            # 将空格替换为"+"号
            formatted_keyword = keyword.replace(" ", "+")
            endpoint += f"/keyword/{formatted_keyword}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_indicators(
        self,
        domain: str = "0000",
        page: int = 1,
        lang: str = "ind",
        keyword: Optional[str] = None,
    ) -> APIResponse:
        """搜索指标数据"""
        # 尝试从缓存中获取数据
        cache_key = f"indicators:{domain}:{page}:{lang}:{keyword}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/indicators/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了keyword，添加到endpoint中
        if keyword is not None:
            # 将空格替换为"+"号
            formatted_keyword = keyword.replace(" ", "+")
            endpoint += f"/keyword/{formatted_keyword}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_infographic(
        self,
        domain: str = "0000",
        page: int = 1,
        lang: str = "ind",
        keyword: Optional[str] = None,
    ) -> APIResponse:
        """搜索信息图标数据"""
        # 尝试从缓存中获取数据
        cache_key = f"infographic:{domain}:{page}:{lang}:{keyword}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/infographic/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了keyword，添加到endpoint中
        if keyword is not None:
            # 将空格替换为"+"号
            formatted_keyword = keyword.replace(" ", "+")
            endpoint += f"/keyword/{formatted_keyword}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_glosarium(
        self,
        domain: str = "0000",
        page: int = 1,
        lang: str = "ind",
        keyword: Optional[str] = None,
    ) -> APIResponse:
        """搜索词汇表数据"""
        # 尝试从缓存中获取数据
        cache_key = f"glosarium:{domain}:{page}:{lang}:{keyword}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/glosarium/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了keyword，添加到endpoint中
        if keyword is not None:
            # 将空格替换为"+"号
            formatted_keyword = keyword.replace(" ", "+")
            endpoint += f"/keyword/{formatted_keyword}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_sdgs(
        self,
        domain: str = "0000",
        page: int = 1,
        lang: str = "ind",
        keyword: Optional[str] = None,
    ) -> APIResponse:
        """搜索可持续发展数据"""
        # 尝试从缓存中获取数据
        cache_key = f"sdgs:{domain}:{page}:{lang}:{keyword}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/sdgs/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了keyword，添加到endpoint中
        if keyword is not None:
            # 将空格替换为"+"号
            formatted_keyword = keyword.replace(" ", "+")
            endpoint += f"/keyword/{formatted_keyword}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_sdds(
        self,
        domain: str = "0000",
        page: int = 1,
        lang: str = "ind",
        keyword: Optional[str] = None,
    ) -> APIResponse:
        """搜索特殊数据发布标准数据"""
        # 尝试从缓存中获取数据
        cache_key = f"sdds:{domain}:{page}:{lang}:{keyword}"
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建基础endpoint
        endpoint = f"list/model/sdds/domain/{domain}/page/{page}/lang/{lang}"

        # 如果提供了keyword，添加到endpoint中
        if keyword is not None:
            # 将空格替换为"+"号
            formatted_keyword = keyword.replace(" ", "+")
            endpoint += f"/keyword/{formatted_keyword}"

        # 添加key到endpoint
        endpoint += f"/key/{self.app_id}/"

        # 缓存中没有数据，发起API请求
        response_text = self._make_request(endpoint)
        result = parse_api_response(response_text)

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

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

    def search_foreign_trade_data(
        self,
        sumber: int,
        periode: int,
        kodehs: str,
        jenishs: int,
        tahun: str,
        lang: str = "ind",
    ) -> APIResponse:
        """查询外贸数据

        Args:
            sumber: 数据类型 (1.出口 2.进口)
            periode: 数据时期 (1.月度 2.年度)
            kodehs: HS CODE，使用';'分割多个CODE
            jenishs: HS CODE类型 (使用2)
            tahun: 数据年份
            lang: 语言，默认为"ind"

        Returns:
            APIResponse: 包含外贸数据的响应对象
        """
        # 生成缓存键
        cache_key = (
            f"foreign_trade:{sumber}:{periode}:{kodehs}:{jenishs}:{tahun}:{lang}"
        )
        cached_result = self._get_from_cache_with_key(cache_key)
        if cached_result is not None:
            return cached_result

        # 构建参数
        params = {
            "sumber": sumber,
            "periode": periode,
            "kodehs": kodehs,
            "jenishs": jenishs,
            "tahun": tahun,
            "lang": lang,
            "key": self.app_id,
        }

        # 发起API请求
        try:
            response_text = self._make_foreign_trade_request(params)
            result = self._parse_foreign_trade_response(response_text)
        except Exception as e:
            # 如果出现错误，返回空数据
            result = APIResponse(
                status="error", data_availability="unavailable", data=[]
            )
            # 记录错误日志
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"获取外贸数据时出错: {str(e)}")

        # 将结果存入缓存
        self._set_cache_with_key(cache_key, result)

        return result

    def search_foreign_trade_data_batch(
        self,
        sumber: int,
        periode: int,
        kodehs_list: List[str],
        jenishs: int,
        tahun_list: List[str],
        lang: str = "ind",
    ) -> dict[str, APIResponse]:
        """批量查询外贸数据

        支持多个年份和多个HS CODE的组合查询

        Args:
            sumber: 数据类型 (1.出口 2.进口)
            periode: 数据时期 (1.月度 2.年度)
            kodehs_list: HS CODE列表
            jenishs: HS CODE类型 (使用2)
            tahun_list: 数据年份列表
            lang: 语言，默认为"ind"

        Returns:
            Dict[str, APIResponse]: 以"tahun:kodehs"为键，APIResponse为值的字典
        """
        results = {}

        # 为每个年份和HS CODE组合发起查询
        for tahun in tahun_list:
            for kodehs in kodehs_list:
                # 将多个HS CODE用';'连接
                kodehs_str = ";".join(kodehs_list)

                # 生成缓存键
                cache_key = f"foreign_trade:{sumber}:{periode}:{kodehs_str}:{jenishs}:{tahun}:{lang}"
                cached_result = self._get_from_cache_with_key(cache_key)

                if cached_result is not None:
                    results[f"{tahun}:{kodehs}"] = cached_result
                else:
                    # 构建参数
                    params = {
                        "sumber": sumber,
                        "periode": periode,
                        "kodehs": kodehs_str,
                        "jenishs": jenishs,
                        "tahun": tahun,
                        "lang": lang,
                        "key": self.app_id,
                    }

                    # 发起API请求
                    try:
                        response_text = self._make_foreign_trade_request(params)
                        result = self._parse_foreign_trade_response(response_text)
                    except Exception as e:
                        # 如果出现错误，返回空数据
                        result = APIResponse(
                            status="error", data_availability="unavailable", data=[]
                        )
                        # 记录错误日志
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.error(f"获取外贸数据时出错: {str(e)}")

                    # 将结果存入缓存
                    self._set_cache_with_key(cache_key, result)

                    # 为每个HS CODE单独存储结果
                    results[f"{tahun}:{kodehs}"] = result

        return results

    def _parse_foreign_trade_response(self, response_text: str) -> APIResponse:
        """解析外贸数据API的响应

        外贸数据API的响应格式与其他接口不同，需要特殊处理。
        """
        try:
            data = json.loads(response_text)
            # 检查响应是否包含预期的字段
            if "status" not in data:
                raise ValueError("响应中缺少status字段")

            # 外贸数据API使用"data"字段而不是"data-availability"
            data_availability = (
                "available" if "data" in data and data["data"] else "unavailable"
            )

            # 外贸数据API不包含分页信息
            return APIResponse(
                status=data["status"],
                data_availability=data_availability,
                data=data.get("data", []),
            )
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response")

    def extract_hs_codes(self, keywords: List[str]) -> List[dict[str, str]]:
        """
        从PDF文件中根据关键字搜索HS CODE信息

        Args:
            keywords (List[str]): 要搜索的关键字列表

        Returns:
            List[Dict[str, str]]: 匹配结果的列表，每个字典包含hs_code, year, description字段
        """
        found_results = []
        processed_lines = set()

        doc = open_packaged_pdf()

        # 正则表达式: 匹配 "Description (YYYY-YYYY)" 或 "Description (YYYY-now)"
        version_pattern = re.compile(r"Description\s*\((\d{4}-\d{4}|\d{4}-now)\)")

        # 正则表达式: 匹配HS Code行并捕获HS Code和描述
        hs_code_pattern = re.compile(r"^\s*\d+\s+(\d{8})\s+(.*)")

        # 遍历PDF的每一页
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")

            # 为当前页面独立查找版本信息
            page_version = "未在当前页找到年份"  # 为本页设置默认值
            version_match = version_pattern.search(text)
            if version_match:
                page_version = version_match.group(1)  # 如果找到，则更新本页的年份

            # 在当前页面内，逐行查找关键字
            lines = text.split("\n")
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped or line_stripped in processed_lines:
                    continue

                # 如果行内包含任一关键字
                if any(
                    keyword.lower() in line_stripped.lower() for keyword in keywords
                ):
                    hs_match = hs_code_pattern.match(line_stripped)
                    if hs_match:
                        hs_code = hs_match.group(1)
                        description = hs_match.group(2).strip()

                        # 使用为当前页找到的 'page_version' 来记录结果
                        result = {
                            "hs_code": hs_code,
                            "year": page_version,
                            "description": description,
                        }
                        found_results.append(result)
                        processed_lines.add(line_stripped)

        doc.close()
        return found_results


def open_packaged_pdf():
    """
    可靠地打开打包在 'bps_searcher' 包内的 PDF 文件。
    """
    doc = None
    try:
        # 1. 使用 importlib.resources.files() 定位资源
        #    这会返回一个可遍历的资源对象（Traversable）。
        # 2. .read_bytes() 直接将文件内容读入内存。
        pdf_bytes = (
            resources.files("bps_searcher")
            .joinpath("resources/hs-code/HSCode Master BPS.pdf")
            .read_bytes()
        )

        # 3. fitz.open() 可以直接从字节流打开文件
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        print("成功从包内资源读取PDF。")
        return doc

    except (FileNotFoundError, ModuleNotFoundError, AttributeError) as e:
        # FileNotFoundError: 资源不存在
        # ModuleNotFoundError: 'bps_searcher' 包找不到
        # AttributeError: 可能在旧版 Python 上 importlib.resources.files 不存在
        raise Exception(
            f"无法定位包内资源 'HSCode Master BPS.pdf'。请确保包已正确安装且资源路径无误。错误: {e}"
        )
    except Exception as e:
        # 捕获 fitz 可能抛出的其他异常
        raise Exception(f"打开PDF文件时发生错误。错误: {e}")


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
