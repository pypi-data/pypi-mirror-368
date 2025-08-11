"""
Chatbox ModelScope MCP同步工具 - 命令行接口

该模块提供了命令行界面，用于从ModelScope平台同步MCP服务到Chatbox应用。
支持多种命令行参数配置，包括API密钥、配置文件路径、API地址等。

使用方式：
    基本使用：
        chatbox-modelscope-sync --token YOUR_API_KEY

    高级配置：
        chatbox-modelscope-sync --token YOUR_API_KEY --path /custom/config.json --url https://custom-api.com

    跳过备份：
        chatbox-modelscope-sync --token YOUR_API_KEY --no-backup

环境变量支持：
    MODELSCOPE_API_KEY: ModelScope API密钥
    CHATBOX_CONFIG: Chatbox配置文件路径

退出状态码：
    0: 同步成功
    1: 同步失败或用户取消
"""

import argparse
import sys
from .sync import ModelScopeMCPSync


def main():
    """
    命令行入口函数

    处理命令行参数解析并执行MCP服务同步操作。
    提供友好的命令行界面和错误处理。

    支持的命令行参数：
        --token, -t: ModelScope API密钥
        --path, -p: Chatbox配置文件路径
        --url: ModelScope MCP API地址
        --no-backup: 跳过配置文件备份

    错误处理：
        - 捕获KeyboardInterrupt异常（Ctrl+C）
        - 捕获所有其他异常并显示友好错误信息
        - 使用适当的退出状态码

    控制台输出：
        ✅ MCP服务器同步成功!
        ❌ MCP服务器同步失败
        ❌ 错误: [具体错误信息]

    Returns:
        None - 通过sys.exit()返回状态码

    Raises:
        所有异常都会被捕获并处理，不会抛出到外层
    """
    parser = argparse.ArgumentParser(
        description='Chatbox ModelScope MCP Sync Tool',
        prog='chatbox-modelscope-sync'
    )

    parser.add_argument(
        '--token', '-t',
        help='ModelScope API Token (也可以使用 MODELSCOPE_API_KEY 环境变量)'
    )

    parser.add_argument(
        '--path', '-p',
        help='Chatbox配置文件路径 (也可以使用 CHATBOX_CONFIG 环境变量)'
    )

    parser.add_argument(
        '--url',
        help='ModelScope MCP API URL (默认: https://www.modelscope.cn/api/v1/mcp/services/operational)'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='不创建配置文件备份'
    )

    args = parser.parse_args()

    try:
        syncer = ModelScopeMCPSync(
            api_key=args.token,
            config_path=args.path,
            api_url=args.url
        )

        success = syncer.sync(backup=not args.no_backup)

        if success:
            print("\n✅ MCP服务器同步成功!")
            print("重启Chatbox应用以应用新配置")
        else:
            print("\n❌ MCP服务器同步失败")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()