import os
import sys
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

# 读取.env
load_dotenv()

BPS_APP_ID = os.getenv("BPS_APP_ID", "")

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bps_searcher.bps_api_client import BPSAPIInterface


class TestSearchDataStructure:
    """测试search_data返回的数据结构"""

    def setup_method(self):
        """测试初始化"""
        # 使用模拟的APP_ID设置环境变量
        self.bps_client = BPSAPIInterface(BPS_APP_ID)

    def test_search_data_return_structure(self):
        """测试search_data返回的数据结构"""
        print("开始测试search_data返回的数据结构...")
        
        # 先获取一个变量ID和周期ID用于测试
        try:
            # 获取变量数据
            var_result = self.bps_client.search_variables(domain="0000", page=1, keyword="nikel")
            print(f"变量搜索结果: {var_result.status}, 记录数: {len(var_result.data)}")
            
            # 获取周期数据
            if var_result.data:
                var_id = var_result.data[0].get('var_id') if isinstance(var_result.data[0], dict) else 2444
                th_result = self.bps_client.search_periods(domain="0000", page=1, var=var_id)
                print(f"周期搜索结果: {th_result.status}, 记录数: {len(th_result.data)}")
                
                if th_result.data:
                    th_id = th_result.data[0].get('th_id') if isinstance(th_result.data[0], dict) else 120
                    
                    # 测试search_data
                    data_result = self.bps_client.search_data(domain="0000", var=var_id, th=th_id)
                    print(f"动态数据搜索结果: {data_result.status}")
                    print(f"数据结构: {data_result}")
                    print(f"数据内容类型: {type(data_result.data)}")
                    print(f"数据内容: {data_result.data}")
                    
                    # 验证返回的数据结构
                    assert isinstance(data_result, object)  # 应该是APIResponse类型
                    assert hasattr(data_result, 'status')
                    assert hasattr(data_result, 'data_availability')
                    assert hasattr(data_result, 'data')
                    
                    # 检查data字段的结构
                    if isinstance(data_result.data, dict):
                        print("数据字段包含以下键:")
                        for key in data_result.data.keys():
                            print(f"  - {key}")
                        
                        # 检查是否包含期望的字段
                        expected_fields = ["status", "data-availability", "datacontent"]
                        missing_fields = [field for field in expected_fields if field not in data_result.data]
                        if missing_fields:
                            print(f"缺少字段: {missing_fields}")
                        else:
                            print("包含所有期望的字段")
                    else:
                        print(f"数据字段不是字典类型，而是: {type(data_result.data)}")
                else:
                    print("未能获取周期数据")
            else:
                print("未能获取变量数据，使用默认值进行测试")
                # 使用默认值进行测试
                data_result = self.bps_client.search_data(domain="0000", var=2444, th=120)
                print(f"动态数据搜索结果: {data_result.status}")
                print(f"数据结构: {data_result}")
                print(f"数据内容类型: {type(data_result.data)}")
                print(f"数据内容: {data_result.data}")
                
        except Exception as e:
            print(f"测试过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()

    # def test_search_data_mcp_tool_structure(self):
    #     """测试MCP工具中search_data的返回结构"""
    #     print("\n开始测试MCP工具中search_data的返回结构...")
    #     
    #     # 导入MCP服务器模块
    #     import src.bps_searcher.bps_mcp_server as mcp_server
    #     
    #     try:
    #         # 调用MCP工具函数
    #         result = mcp_server.search_data(domain="0000", var=2444, th=120)
    #         print(f"MCP工具返回结果: {result}")
    #         print(f"返回结果类型: {type(result)}")
    #         
    #         if isinstance(result, dict):
    #             print("返回结果包含以下键:")
    #             for key in result.keys():
    #                 print(f"  - {key}")
    #                 
    #             # 检查是否包含期望的字段
    #             if 'data' in result and isinstance(result['data'], dict):
    #                 print("数据字段包含以下键:")
    #                 for key in result['data'].keys():
    #                     print(f"  - {key}")
    #             else:
    #                 print(f"数据字段类型: {type(result.get('data', 'N/A'))}")
    #         
    #     except Exception as e:
    #         print(f"MCP工具测试过程中出错: {str(e)}")
    #         import traceback
    #         traceback.print_exc()


if __name__ == "__main__":
    test = TestSearchDataStructure()
    test.setup_method()
    test.test_search_data_return_structure()
    # test.test_search_data_mcp_tool_structure()
