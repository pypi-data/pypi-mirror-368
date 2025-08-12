import os
from .bps_mcp_server import mcp


def main():
    """启动BPS MCP服务器"""
    # 检查是否设置了APP_ID环境变量
    app_id = os.environ.get("BPS_APP_ID")
    if not app_id:
        print("错误: BPS_APP_ID环境变量未设置。")
        print("请设置BPS_APP_ID环境变量以使用此MCP服务器。")
        print("例如: export BPS_APP_ID=your_app_id_here")
        return 1
    
    # 启动MCP服务器
    mcp.run()


if __name__ == "__main__":
    main()
