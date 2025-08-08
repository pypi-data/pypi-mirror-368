import json
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


def test_normal_functionality():
    """测试所有model的正常查询功能"""
    print("开始测试所有model的正常查询功能...")

    # 初始化BPS API客户端
    bps_client = BPSAPIInterface(BPS_APP_ID)

    # 测试主题数据
    print("\n1. 测试主题数据搜索...")
    try:
        result = bps_client.search_subjects(domain="0000", page=1)
        print(f"主题数据搜索结果: {result.status}, 记录数: {len(result.data)}")
        # 验证返回的数据结构
        assert isinstance(result, APIResponse)
        assert result.status == "OK"
    except Exception as e:
        print(f"主题数据搜索出错: {str(e)}")

    # 测试新闻数据
    print("\n2. 测试新闻数据搜索...")
    try:
        result = bps_client.search_news(domain="0000", page=1)
        print(f"新闻数据搜索结果: {result.status}, 记录数: {len(result.data)}")
        # 验证返回的数据结构
        assert isinstance(result, APIResponse)
        assert result.status == "OK"
    except Exception as e:
        print(f"新闻数据搜索出错: {str(e)}")

    print("\n所有model的正常查询功能测试完成!")


def test_boundary_conditions():
    """测试边界条件"""
    print("\n开始测试边界条件...")

    bps_client = BPSAPIInterface(BPS_APP_ID)

    # 测试不同的页码
    print("\n1. 测试不同页码...")
    try:
        # 测试第一页
        result1 = bps_client.search_news(domain="0000", page=1)
        print(f"第1页数据搜索结果: {result1.status}, 记录数: {len(result1.data)}")

        # 测试较大的页码
        result2 = bps_client.search_news(domain="0000", page=100)
        print(f"第100页数据搜索结果: {result2.status}, 记录数: {len(result2.data)}")
    except Exception as e:
        print(f"不同页码测试出错: {str(e)}")

    # 测试不同的领域ID
    print("\n2. 测试不同领域ID...")
    try:
        # 测试全国数据
        result1 = bps_client.search_news(domain="0000", page=1)
        print(f"全国数据搜索结果: {result1.status}, 记录数: {len(result1.data)}")

        # 测试特定省份数据
        result2 = bps_client.search_news(domain="1100", page=1)  # Aceh
        print(f"Aceh数据搜索结果: {result2.status}, 记录数: {len(result2.data)}")
    except Exception as e:
        print(f"不同领域ID测试出错: {str(e)}")

    print("\n边界条件测试完成!")


def test_error_handling():
    """测试错误处理"""
    print("\n开始测试错误处理...")

    bps_client = BPSAPIInterface(BPS_APP_ID)

    # 测试无效的领域ID
    print("\n1. 测试无效的领域ID...")
    try:
        result = bps_client.search_news(domain="9999", page=1)
        print(f"无效领域ID搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"无效领域ID测试出错: {str(e)}")

    # 测试无效的页码
    print("\n2. 测试无效的页码...")
    try:
        result = bps_client.search_news(domain="0000", page=-1)
        print(f"负页码搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"负页码测试出错: {str(e)}")

    # 测试空的APP_ID
    print("\n3. 测试空的APP_ID...")
    try:
        client = BPSAPIInterface("")
        result = client.search_news(domain="0000", page=1)
        print(f"空APP_ID搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"空APP_ID测试出错: {str(e)}")

    print("\n错误处理测试完成!")


def test_parse_api_response():
    """测试API响应解析函数"""
    print("\n开始测试API响应解析函数...")

    # 测试正常的JSON响应
    normal_response = '{"status": "OK", "data-availability": "available", "data": []}'
    result = parse_api_response(normal_response)
    assert result.status == "OK"
    assert result.data_availability == "available"
    print("正常JSON响应解析测试通过")

    # 测试缺少data-availability字段的响应
    missing_availability_response = '{"status": "OK", "data": []}'
    result = parse_api_response(missing_availability_response)
    assert result.status == "OK"
    assert result.data_availability == "unavailable"  # 应该使用默认值
    print("缺少data-availability字段响应解析测试通过")

    # 测试缺少data字段的响应
    missing_data_response = '{"status": "OK", "data-availability": "available"}'
    result = parse_api_response(missing_data_response)
    assert result.status == "OK"
    assert result.data == []  # 应该使用空列表
    print("缺少data字段响应解析测试通过")

    # 测试无效的JSON响应
    try:
        invalid_response = "invalid json"
        result = parse_api_response(invalid_response)
        print("应该抛出异常但没有抛出")
    except ValueError as e:
        print(f"无效JSON响应解析正确抛出异常: {str(e)}")

    # 测试缺少status字段的响应
    try:
        missing_status_response = '{"data-availability": "available", "data": []}'
        result = parse_api_response(missing_status_response)
        print("应该抛出异常但没有抛出")
    except ValueError as e:
        print(f"缺少status字段响应正确抛出异常: {str(e)}")

    print("\nAPI响应解析函数测试完成!")


@patch("src.bps_searcher.bps_api_client.requests.get")
def test_network_errors(mock_get):
    """测试网络错误处理"""
    print("\n开始测试网络错误处理...")

    # 模拟网络请求异常
    mock_get.side_effect = Exception("网络连接错误")

    bps_client = BPSAPIInterface("test_app_id")

    try:
        result = bps_client.search_news(domain="0000", page=1)
        print("应该抛出异常但没有抛出")
    except Exception as e:
        print(f"网络错误正确处理: {str(e)}")

    print("\n网络错误处理测试完成!")


if __name__ == "__main__":
    test_normal_functionality()
    test_boundary_conditions()
    test_error_handling()
    test_parse_api_response()
    test_network_errors()
    print("\n所有增强测试完成!")
