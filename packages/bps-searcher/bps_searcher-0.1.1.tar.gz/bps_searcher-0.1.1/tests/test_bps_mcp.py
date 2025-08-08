import asyncio
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接从API客户端导入函数进行测试
from src.bps_searcher.bps_api_client import BPSAPIInterface


class TestMCPFunctionality:
    """测试MCP服务器功能"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """测试初始化"""
        # 使用模拟的APP_ID设置环境变量
        with patch.dict(os.environ, {"BPS_APP_ID": "test_app_id"}):
            # 重新导入模块以触发环境变量检查
            if "src.bps_searcher.bps_mcp_server" in sys.modules:
                del sys.modules["src.bps_searcher.bps_mcp_server"]

            # 导入MCP服务器模块
            import src.bps_searcher.bps_mcp_server

            self.mcp_server = src.bps_searcher.bps_mcp_server

    def test_missing_app_id(self):
        """测试未设置BPS_APP_ID环境变量时的错误处理"""
        # 保存原始环境变量
        original_app_id = os.environ.get("BPS_APP_ID")

        # 删除BPS_APP_ID环境变量
        with patch.dict(os.environ, {}, clear=True):
            # 重新导入模块以触发环境变量检查
            if "src.bps_searcher.bps_mcp_server" in sys.modules:
                del sys.modules["src.bps_searcher.bps_mcp_server"]

            # 导入MCP服务器模块
            import src.bps_searcher.bps_mcp_server

            # 调用main函数，应该抛出ValueError异常
            try:
                src.bps_searcher.bps_mcp_server.main()
                # 如果没有抛出异常，则测试失败
                assert False, "应该抛出ValueError异常"
            except ValueError as e:
                # 验证异常信息是否正确
                assert "BPS_APP_ID环境变量未设置" in str(e)

        # 恢复原始环境变量
        if original_app_id is not None:
            os.environ["BPS_APP_ID"] = original_app_id

    @pytest.mark.asyncio
    async def test_all_models(self):
        """测试所有model的查询功能"""
        print("开始测试所有model的查询功能...")

        # 初始化BPS接口用于测试
        from src.bps_searcher.bps_api_client import BPSAPIInterface

        bps_interface = BPSAPIInterface("test_app_id")

        # 测试主题数据
        print("\n1. 测试主题数据搜索...")
        result = bps_interface.search_subjects(domain="0000", page=1)
        print(f"主题数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试新闻数据
        print("\n2. 测试新闻数据搜索...")
        result = bps_interface.search_news(domain="0000", page=1)
        print(f"新闻数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试出版物数据
        print("\n3. 测试出版物数据搜索...")
        result = bps_interface.search_publications(domain="0000", page=1)
        print(f"出版物数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试变量数据
        print("\n4. 测试变量数据搜索...")
        result = bps_interface.search_variables(domain="0000", page=1)
        print(f"变量数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试时期数据
        print("\n5. 测试时期数据搜索...")
        result = bps_interface.search_periods(domain="0000", page=1)
        print(f"时期数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试地区数据
        print("\n6. 测试地区数据搜索...")
        result = bps_interface.search_regions(domain="0000", page=1)
        print(f"地区数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试单位数据
        print("\n7. 测试单位数据搜索...")
        result = bps_interface.search_units(domain="0000", page=1)
        print(f"单位数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试子主题数据
        print("\n8. 测试子主题数据搜索...")
        result = bps_interface.search_subcat(domain="0000", page=1)
        print(f"子主题数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试动态数据
        print("\n9. 测试动态数据搜索...")
        # 先获取变量和周期数据
        var_result = bps_interface.search_variables(domain="0000", page=1)
        th_result = bps_interface.search_periods(domain="0000", page=1)
        
        if var_result.data and th_result.data:
            var_id = var_result.data[0].get('var_id') if isinstance(var_result.data[0], dict) else 70
            th_id = th_result.data[0].get('th_id') if isinstance(th_result.data[0], dict) else 120
            
            result = bps_interface.search_data(domain="0000", page=1, var=var_id, th=th_id)
            print(f"动态数据搜索结果: {result.status}, 记录数: {len(result.data)}")
        else:
            print("无法获取变量或周期数据，跳过动态数据测试")

        # 测试衍生周期数据
        print("\n10. 测试衍生周期数据搜索...")
        result = bps_interface.search_truth(domain="0000", page=1)
        print(f"衍生周期数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试派生变量数据
        print("\n11. 测试派生变量数据搜索...")
        result = bps_interface.search_turvar(domain="0000", page=1)
        print(f"派生变量数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试静态表格数据
        print("\n12. 测试静态表格数据搜索...")
        result = bps_interface.search_statictable(domain="0000", page=1)
        print(f"静态表格数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试统计活动分类数据
        print("\n13. 测试统计活动分类数据搜索...")
        result = bps_interface.search_subcatcsa(domain="0000", page=1)
        print(f"统计活动分类数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试新闻稿数据
        print("\n14. 测试新闻稿数据搜索...")
        result = bps_interface.search_pressrelease(domain="0000", page=1)
        print(f"新闻稿数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试指标数据
        print("\n15. 测试指标数据搜索...")
        result = bps_interface.search_indicators(domain="0000", page=1)
        print(f"指标数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试信息图标数据
        print("\n16. 测试信息图标数据搜索...")
        result = bps_interface.search_infographic(domain="0000", page=1)
        print(f"信息图标数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试词汇表数据
        print("\n17. 测试词汇表数据搜索...")
        result = bps_interface.search_glosarium(domain="0000", page=1)
        print(f"词汇表数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试可持续发展数据
        print("\n18. 测试可持续发展数据搜索...")
        result = bps_interface.search_sdgs(domain="0000", page=1)
        print(f"可持续发展数据搜索结果: {result.status}, 记录数: {len(result.data)}")

        # 测试特殊数据发布标准数据
        print("\n19. 测试特殊数据发布标准数据搜索...")
        result = bps_interface.search_sdds(domain="0000", page=1)
        print(
            f"特殊数据发布标准数据搜索结果: {result.status}, 记录数: {len(result.data)}"
        )

        print("\n所有model的查询功能测试完成!")


if __name__ == "__main__":
    # 使用模拟的APP_ID设置环境变量
    with patch.dict(os.environ, {"BPS_APP_ID": "test_app_id"}):
        asyncio.run(TestMCPFunctionality().test_all_models())
