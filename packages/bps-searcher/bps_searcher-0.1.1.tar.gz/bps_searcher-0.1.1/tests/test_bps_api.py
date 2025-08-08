import asyncio
import json
import os
import sys

from dotenv import load_dotenv

# 读取.env
load_dotenv()

BPS_APP_ID = os.getenv("BPS_APP_ID", "")

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bps_searcher.bps_api_client import BPSAPIInterface


def test_all_models():
    """测试所有model的查询功能"""
    print("开始测试所有model的查询功能...")

    # 初始化BPS API客户端
    bps_client = BPSAPIInterface(BPS_APP_ID)

    # 测试主题数据
    print("\n1. 测试主题数据搜索...")
    try:
        result = bps_client.search_subjects(domain="0000", page=1)
        print(f"主题数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"主题数据搜索出错: {str(e)}")

    # 测试新闻数据
    print("\n2. 测试新闻数据搜索...")
    try:
        result = bps_client.search_news(domain="0000", page=1)
        print(f"新闻数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"新闻数据搜索出错: {str(e)}")

    # 测试出版物数据
    print("\n3. 测试出版物数据搜索...")
    try:
        result = bps_client.search_publications(domain="0000", page=1)
        print(f"出版物数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"出版物数据搜索出错: {str(e)}")

    # 测试变量数据
    print("\n4. 测试变量数据搜索...")
    try:
        result = bps_client.search_variables(domain="0000", page=1)
        print(f"变量数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"变量数据搜索出错: {str(e)}")

    # 测试时期数据
    print("\n5. 测试时期数据搜索...")
    try:
        result = bps_client.search_periods(domain="0000", page=1)
        print(f"时期数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"时期数据搜索出错: {str(e)}")

    # 测试地区数据
    print("\n6. 测试地区数据搜索...")
    try:
        result = bps_client.search_regions(domain="0000", page=1)
        print(f"地区数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"地区数据搜索出错: {str(e)}")

    # 测试单位数据
    print("\n7. 测试单位数据搜索...")
    try:
        result = bps_client.search_units(domain="0000", page=1)
        print(f"单位数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"单位数据搜索出错: {str(e)}")

    # 测试子主题数据
    print("\n8. 测试子主题数据搜索...")
    try:
        result = bps_client.search_subcat(domain="0000", page=1)
        print(f"子主题数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"子主题数据搜索出错: {str(e)}")

    # 测试动态数据
    print("\n9. 测试动态数据搜索...")
    try:
        result = bps_client.search_data(domain="0000", page=1)
        print(f"动态数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"动态数据搜索出错: {str(e)}")

    # 测试衍生周期数据
    print("\n10. 测试衍生周期数据搜索...")
    try:
        result = bps_client.search_truth(domain="0000", page=1)
        print(f"衍生周期数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"衍生周期数据搜索出错: {str(e)}")

    # 测试派生变量数据
    print("\n11. 测试派生变量数据搜索...")
    try:
        result = bps_client.search_turvar(domain="0000", page=1)
        print(f"派生变量数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"派生变量数据搜索出错: {str(e)}")

    # 测试静态表格数据
    print("\n12. 测试静态表格数据搜索...")
    try:
        result = bps_client.search_statictable(domain="0000", page=1)
        print(f"静态表格数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"静态表格数据搜索出错: {str(e)}")

    # 测试统计活动分类数据
    print("\n13. 测试统计活动分类数据搜索...")
    try:
        result = bps_client.search_subcatcsa(domain="0000", page=1)
        print(f"统计活动分类数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"统计活动分类数据搜索出错: {str(e)}")

    # 测试新闻稿数据
    print("\n14. 测试新闻稿数据搜索...")
    try:
        result = bps_client.search_pressrelease(domain="0000", page=1)
        print(f"新闻稿数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"新闻稿数据搜索出错: {str(e)}")

    # 测试指标数据
    print("\n15. 测试指标数据搜索...")
    try:
        result = bps_client.search_indicators(domain="0000", page=1)
        print(f"指标数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"指标数据搜索出错: {str(e)}")

    # 测试信息图标数据
    print("\n16. 测试信息图标数据搜索...")
    try:
        result = bps_client.search_infographic(domain="0000", page=1)
        print(f"信息图标数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"信息图标数据搜索出错: {str(e)}")

    # 测试词汇表数据
    print("\n17. 测试词汇表数据搜索...")
    try:
        result = bps_client.search_glosarium(domain="0000", page=1)
        print(f"词汇表数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"词汇表数据搜索出错: {str(e)}")

    # 测试可持续发展数据
    print("\n18. 测试可持续发展数据搜索...")
    try:
        result = bps_client.search_sdgs(domain="0000", page=1)
        print(f"可持续发展数据搜索结果: {result.status}, 记录数: {len(result.data)}")
    except Exception as e:
        print(f"可持续发展数据搜索出错: {str(e)}")

    # 测试特殊数据发布标准数据
    print("\n19. 测试特殊数据发布标准数据搜索...")
    try:
        result = bps_client.search_sdds(domain="0000", page=1)
        print(
            f"特殊数据发布标准数据搜索结果: {result.status}, 记录数: {len(result.data)}"
        )
    except Exception as e:
        print(f"特殊数据发布标准数据搜索出错: {str(e)}")

    print("\n所有model的查询功能测试完成!")


if __name__ == "__main__":
    test_all_models()
