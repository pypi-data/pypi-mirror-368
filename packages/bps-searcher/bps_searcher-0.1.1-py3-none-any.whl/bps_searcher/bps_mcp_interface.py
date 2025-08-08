import json
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

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
class APIResponse:
    status: str
    data_availability: str
    data: List[Any]

@dataclass
class SearchResult:
    page: int
    pages: int
    per_page: int
    count: int
    total: int

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

# MCP工具接口定义
class BPSMCPInterface:
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.base_url = "https://webapi.bps.go.id/v1/api"
    
    def _make_request(self, endpoint: str) -> str:
        """发起API请求"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    
    def search_subjects(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索主题数据"""
        endpoint = f"list/model/subject/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_news(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索新闻数据"""
        endpoint = f"list/model/news/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_publications(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索出版物数据"""
        endpoint = f"list/model/publication/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_variables(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索变量数据"""
        endpoint = f"list/model/var/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_periods(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索时期数据"""
        endpoint = f"list/model/th/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_regions(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索地区数据"""
        endpoint = f"list/model/vervar/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_units(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索单位数据"""
        endpoint = f"list/model/unit/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_subcat(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索子主题数据"""
        endpoint = f"list/model/subcat/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_data(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索动态数据"""
        endpoint = f"list/model/data/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_truth(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索衍生周期数据"""
        endpoint = f"list/model/truth/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_turvar(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索派生变量数据"""
        endpoint = f"list/model/turvar/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_statictable(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索静态表格数据"""
        endpoint = f"list/model/statictable/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_subcatcsa(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索统计活动分类数据"""
        endpoint = f"list/model/subcatcsa/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_pressrelease(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索新闻稿数据"""
        endpoint = f"list/model/pressrelease/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_indicators(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索指标数据"""
        endpoint = f"list/model/indicators/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_infographic(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索信息图标数据"""
        endpoint = f"list/model/infographic/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_glosarium(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索词汇表数据"""
        endpoint = f"list/model/glosarium/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_sdgs(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索可持续发展数据"""
        endpoint = f"list/model/sdgs/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)
    
    def search_sdds(self, domain: str = "0000", page: int = 1) -> APIResponse:
        """搜索特殊数据发布标准数据"""
        endpoint = f"list/model/sdds/domain/{domain}/page/{page}/key/{self.app_id}/"
        response_text = self._make_request(endpoint)
        return parse_api_response(response_text)

# 工具函数
def parse_api_response(response_text: str) -> APIResponse:
    """解析API响应"""
    try:
        data = json.loads(response_text)
        return APIResponse(
            status=data["status"],
            data_availability=data["data-availability"],
            data=data["data"]
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
        total=meta["total"]
    )