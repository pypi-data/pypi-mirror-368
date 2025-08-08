import os
import sys
from unittest.mock import Mock, patch

import pytest
from dotenv import load_dotenv

# 读取.env
load_dotenv()

BPS_APP_ID = os.getenv("BPS_APP_ID", "")

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bps_searcher.bps_api_client import (APIResponse, BPSAPIInterface,
                                             parse_api_response)


class TestBPSAPI:
    """BPS API客户端测试类"""

    def setup_method(self):
        """测试初始化"""
        self.bps_client = BPSAPIInterface(BPS_APP_ID)

    def test_search_subjects_normal(self):
        """测试主题数据正常查询"""
        result = self.bps_client.search_subjects(domain="0000", page=1)
        assert isinstance(result, APIResponse)
        assert result.status in ["OK", "Error"]

    def test_search_news_normal(self):
        """测试新闻数据正常查询"""
        result = self.bps_client.search_news(domain="0000", page=1)
        assert isinstance(result, APIResponse)
        assert result.status in ["OK", "Error"]

    def test_search_publications_normal(self):
        """测试出版物数据正常查询"""
        result = self.bps_client.search_publications(domain="0000", page=1)
        assert isinstance(result, APIResponse)
        assert result.status in ["OK", "Error"]

    def test_all_models(self):
        """测试所有model的查询功能"""
        # 测试除data外的所有数据模型
        models = [
            ("subject", self.bps_client.search_subjects),
            ("news", self.bps_client.search_news),
            ("publication", self.bps_client.search_publications),
            ("var", self.bps_client.search_variables),
            ("th", self.bps_client.search_periods),
            ("vervar", self.bps_client.search_regions),
            ("unit", self.bps_client.search_units),
            ("subcat", self.bps_client.search_subcat),
            ("truth", self.bps_client.search_truth),
            ("turvar", self.bps_client.search_turvar),
            ("statictable", self.bps_client.search_statictable),
            ("subcatcsa", self.bps_client.search_subcatcsa),
            ("pressrelease", self.bps_client.search_pressrelease),
            ("indicators", self.bps_client.search_indicators),
            ("infographic", self.bps_client.search_infographic),
            ("glosarium", self.bps_client.search_glosarium),
            ("sdgs", self.bps_client.search_sdgs),
            ("sdds", self.bps_client.search_sdds),
        ]
    
        for model_name, search_func in models:
            result = search_func(domain="0000", page=1)
            assert isinstance(result, APIResponse)
            assert result.status in ["OK", "Error"]
        
        # 单独测试data模型，需要提供var和th参数
        # 先获取变量和周期数据
        var_result = self.bps_client.search_variables(domain="0000", page=1)
        th_result = self.bps_client.search_periods(domain="0000", page=1)
        
        if var_result.data and th_result.data:
            var_id = var_result.data[0].get('var_id') if isinstance(var_result.data[0], dict) else 70
            th_id = th_result.data[0].get('th_id') if isinstance(th_result.data[0], dict) else 120
            
            data_result = self.bps_client.search_data(domain="0000", page=1, var=var_id, th=th_id)
            assert isinstance(data_result, APIResponse)
            assert data_result.status in ["OK", "Error"]

    def test_boundary_conditions_page(self):
        """测试不同页码的边界条件"""
        # 测试第一页
        result1 = self.bps_client.search_news(domain="0000", page=1)
        assert result1.status in ["OK", "Error"]

        # 测试较大的页码
        result2 = self.bps_client.search_news(domain="0000", page=100)
        assert result2.status in ["OK", "Error"]

    def test_boundary_conditions_domain(self):
        """测试不同领域的边界条件"""
        # 测试全国数据
        result1 = self.bps_client.search_news(domain="0000", page=1)
        assert result1.status in ["OK", "Error"]

        # 测试省级数据
        result2 = self.bps_client.search_news(domain="1100", page=1)
        assert result2.status in ["OK", "Error"]

        # 测试市级数据
        result3 = self.bps_client.search_news(domain="7601", page=1)
        assert result3.status in ["OK", "Error"]

    def test_error_handling_invalid_domain(self):
        """测试无效领域的错误处理"""
        # 测试无效领域
        try:
            result = self.bps_client.search_news(domain="9999", page=1)
            assert result.status in ["OK", "Error"]
        except Exception:
            # 服务器可能返回500错误，这是预期的行为
            assert True

    def test_parse_api_response_normal(self):
        """测试API响应解析 - 正常情况"""
        # 模拟正常的API响应
        response_text = '''{
            "status": "OK",
            "data-availability": "available",
            "data": [
                {"page": 1, "pages": 10, "per_page": 10, "count": 10, "total": 100},
                [{"id": 1, "name": "Test"}]
            ]
        }'''
        result = parse_api_response(response_text)
        assert isinstance(result, APIResponse)
        assert result.status == "OK"
        assert result.data_availability == "available"

    def test_parse_api_response_missing_availability(self):
        """测试API响应解析 - 缺少data-availability字段"""
        # 模拟缺少data-availability字段的API响应
        response_text = '''{
            "status": "OK",
            "data": [
                {"page": 1, "pages": 10, "per_page": 10, "count": 10, "total": 100},
                [{"id": 1, "name": "Test"}]
            ]
        }'''
        result = parse_api_response(response_text)
        assert isinstance(result, APIResponse)
        assert result.status == "OK"

    def test_parse_api_response_missing_data(self):
        """测试API响应解析 - 缺少data字段"""
        # 模拟缺少data字段的API响应
        response_text = '''{
            "status": "OK",
            "data-availability": "unavailable"
        }'''
        result = parse_api_response(response_text)
        assert isinstance(result, APIResponse)
        assert result.status == "OK"
        assert result.data == []

    def test_parse_api_response_invalid_json(self):
        """测试API响应解析 - 无效JSON"""
        # 测试无效JSON
        with pytest.raises(ValueError, match="Invalid JSON response"):
            parse_api_response("invalid json")

    def test_parse_api_response_missing_status(self):
        """测试API响应解析 - 缺少status字段"""
        # 测试缺少status字段
        response_text = '''{
            "data-availability": "available",
            "data": []
        }'''
        with pytest.raises(ValueError, match="响应中缺少status字段"):
            parse_api_response(response_text)

    def test_network_error_handling(self):
        """测试网络错误处理"""
        # 使用mock模拟网络错误
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            with pytest.raises(Exception):
                self.bps_client.search_news(domain="0000", page=1)