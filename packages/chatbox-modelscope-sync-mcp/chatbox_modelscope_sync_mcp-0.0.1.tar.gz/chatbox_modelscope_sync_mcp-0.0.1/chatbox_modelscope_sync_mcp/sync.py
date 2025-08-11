"""
ModelScope MCP同步工具

该模块提供了将ModelScope平台上的MCP服务同步到Chatbox应用配置中的功能。
通过调用ModelScope API获取最新的MCP服务列表，并更新本地配置文件。

主要功能：
1. 自动检测Chatbox配置文件路径
2. 调用ModelScope API获取MCP服务列表
3. 智能过滤和更新MCP服务器配置
4. 自动备份配置文件
5. 支持自定义API密钥和配置路径

示例：
    >>> syncer = ModelScopeMCPSync(api_key="your_api_key")
    >>> syncer.sync()  # 执行同步操作
"""

import os
import sys
import json
import uuid
import shutil
from pathlib import Path
import requests


class ModelScopeMCPSync:
    """
    ModelScope MCP同步工具类

    用于同步ModelScope平台上的MCP服务到Chatbox应用的配置文件中。

    Attributes:
        api_key (str): ModelScope API密钥
        config_path (str): Chatbox配置文件路径
        api_url (str): ModelScope API的URL地址

    Example:
        >>> syncer = ModelScopeMCPSync(api_key="your_key")
        >>> syncer.sync()  # 执行同步
    """

    def __init__(self, api_key=None, config_path=None, api_url=None):
        """
        初始化ModelScope MCP同步工具

        Args:
            api_key (str, optional): ModelScope API密钥。如果未提供，将尝试从环境变量MODELSCOPE_API_KEY获取
            config_path (str, optional): Chatbox配置文件路径。如果未提供，将自动检测系统默认路径
            api_url (str, optional): ModelScope API的URL地址。默认为官方API地址

        配置路径自动检测规则：
        - Windows: ~/AppData/Roaming/xyz.chatboxapp.app/config.json
        - macOS: ~/Library/Application Support/xyz.chatboxapp.app/config.json
        - Linux: ~/.config/xyz.chatboxapp.app/config.json
        """
        self.api_key = api_key
        self.config_path = config_path
        self.api_url = api_url or "https://www.modelscope.cn/api/v1/mcp/services/operational"

    def _get_config_path(self):
        """
        获取Chatbox配置文件路径

        根据操作系统类型自动检测Chatbox应用的默认配置文件路径。

        Returns:
            str: 配置文件完整路径

        Raises:
            无异常抛出，如果无法确定路径，返回'config.json'
        """
        if self.config_path:
            return self.config_path

        # 自动检测Chatbox配置路径
        if os.name == 'nt':  # Windows
            return os.path.expanduser('~/AppData/Roaming/xyz.chatboxapp.app/config.json')
        elif os.name == 'posix':
            if sys.platform == 'darwin':  # macOS
                return os.path.expanduser('~/Library/Application Support/xyz.chatboxapp.app/config.json')
            else:  # Linux
                return os.path.expanduser('~/.config/xyz.chatboxapp.app/config.json')

        return 'config.json'

    def _get_api_key(self):
        """
        获取ModelScope API密钥

        优先级：
        1. 构造函数中提供的api_key参数
        2. 环境变量MODELSCOPE_API_KEY

        Returns:
            str: API密钥

        Raises:
            ValueError: 如果未找到有效的API密钥
        """
        return self.api_key or os.getenv('MODELSCOPE_API_KEY')

    def call_modelscope_api(self):
        """
        调用ModelScope API获取MCP服务列表

        使用提供的API密钥调用ModelScope平台的MCP服务API，
        获取当前可用的MCP服务信息。

        Returns:
            dict: API响应的JSON数据

        Raises:
            ValueError: 如果未提供API密钥
            RuntimeError: 如果API调用失败（网络错误、认证失败等）

        API端点：
            GET https://www.modelscope.cn/api/v1/mcp/services/operational

        响应格式：
            {
                "Data": {
                    "Result": [
                        {
                            "id": "服务唯一标识",
                            "name": "服务名称",
                            "chinese_name": "中文名称",
                            "locales": {"zh": {"name": "本地化名称"}},
                            "operational_urls": [{"url": "服务URL"}]
                        }
                    ]
                }
            }
        """
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("未提供API密钥，请使用--token参数或设置MODELSCOPE_API_KEY环境变量")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }

        try:
            response = requests.get(self.api_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API调用失败: {e}")

    def load_config(self, config_path):
        """
        加载Chatbox配置文件

        从指定路径加载Chatbox应用的配置文件。
        如果文件不存在，会创建包含默认MCP服务器配置的新配置。

        Args:
            config_path (str): 配置文件路径

        Returns:
            dict: 配置数据的Python字典

        Raises:
            ValueError: 如果配置文件格式错误（JSON解析失败）
            RuntimeError: 如果文件读取失败

        默认配置结构：
            {
                "settings": {
                    "mcp": {
                        "servers": []
                    }
                }
            }
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果文件不存在，创建默认配置
            return {
                "settings": {
                    "mcp": {
                        "servers": []
                    }
                }
            }
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败: {e}")

    def backup_config(self, config_path):
        """
        备份配置文件

        在更新配置前创建配置文件的备份副本，
        备份文件命名为原文件名加.bak后缀。

        Args:
            config_path (str): 要备份的配置文件路径

        Returns:
            bool: 备份成功返回True，失败返回False

        备份文件命名：
            原文件: config.json
            备份文件: config.json.bak
        """
        backup_path = f"{config_path}.bak"
        try:
            shutil.copy2(config_path, backup_path)
            print(f"已备份配置文件到: {backup_path}")
            return True
        except Exception as e:
            print(f"备份配置文件失败: {e}")
            return False

    def save_config(self, config, config_path):
        """
        保存配置文件

        将更新后的配置数据保存到指定路径的配置文件中。
        如果目录不存在会自动创建。

        Args:
            config (dict): 要保存的配置数据
            config_path (str): 目标配置文件路径

        Returns:
            bool: 保存成功返回True

        Raises:
            RuntimeError: 如果保存失败

        文件格式：
            使用UTF-8编码，JSON格式，2空格缩进，保留非ASCII字符
        """
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"已更新配置文件: {config_path}")
            return True
        except Exception as e:
            raise RuntimeError(f"保存配置文件失败: {e}")

    def get_server_name(self, service):
        """
        智能获取服务器名称

        从服务信息中提取最合适的服务器名称。
        优先级：中文名称 > 本地化名称 > 英文名称 > 原始名称 > ID转换

        Args:
            service (dict): 服务信息字典，包含名称相关字段

        Returns:
            str: 服务器名称，如果无法确定返回None

        名称提取规则：
        1. chinese_name字段（中文名称）
        2. locales.zh.name或locales.en.name（本地化名称）
        3. name字段（原始名称）
        4. id字段（转换@和/为-）
        """
        name = service.get('chinese_name', '').strip()
        if name:
            return name

        locales = service.get('locales', {})
        for lang in ['zh', 'en']:
            if lang in locales:
                name = locales[lang].get('name', '').strip()
                if name:
                    return name

        name = service.get('name', '').strip()
        if name:
            return name

        server_id = service.get('id', '').strip()
        if server_id:
            return server_id.replace('@', '').replace('/', '-')

        return None

    def filter_valid_servers(self, api_response):
        """
        过滤有效服务器

        从API响应中过滤出有效的MCP服务器。
        有效服务器的定义：
        - 有有效的服务器名称
        - 有operational_urls列表
        - 第一个URL有效

        Args:
            api_response (dict): ModelScope API的响应数据

        Returns:
            list: 有效服务器列表，每个元素包含name、url、id字段

        返回格式：
            [
                {
                    "name": "服务器名称",
                    "url": "服务URL",
                    "id": "服务唯一标识"
                }
            ]
        """
        if not api_response or 'Data' not in api_response or 'Result' not in api_response['Data']:
            return []

        valid_servers = []
        for service in api_response['Data']['Result']:
            name = self.get_server_name(service)
            if not name:
                continue

            urls = service.get('operational_urls', [])
            if not urls:
                continue

            url = urls[0].get('url')
            if not url:
                continue

            valid_servers.append({
                'name': name,
                'url': url,
                'id': service.get('id', 'unknown')
            })

        return valid_servers

    def sync(self, backup=True):
        """
        执行MCP服务同步

        完整的同步流程：
        1. 调用ModelScope API获取最新服务列表
        2. 加载当前Chatbox配置
        3. 过滤有效的新服务器
        4. 对比并更新现有配置
        5. 备份并保存更新后的配置

        Args:
            backup (bool, optional): 是否在更新前备份配置文件，默认为True

        Returns:
            bool: 同步成功返回True，无更新返回True，失败返回False

        控制台输出：
        - 正在调用ModelScope API...
        - 正在加载配置文件...
        - 更新: 旧名称 -> 新名称
        - 新增: 新服务器名称
        - 同步完成: 更新X个, 新增Y个

        同步规则：
        - 同名URL：仅更新名称
        - 新URL：添加为新服务器
        - 现有服务器保持不变
        - 每个新服务器分配唯一UUID
        """
        config_path = self._get_config_path()

        print("正在调用ModelScope API...")
        api_response = self.call_modelscope_api()

        print("正在加载配置文件...")
        config = self.load_config(config_path)

        valid_servers = self.filter_valid_servers(api_response)
        if not valid_servers:
            print("没有找到有效的MCP服务器")
            return False

        # 获取现有服务器
        servers = config['settings']['mcp']['servers']
        existing_urls = {s['transport']['url']: s for s in servers
                         if s.get('transport', {}).get('type') == 'http'}

        updated_count = 0
        added_count = 0

        for server_info in valid_servers:
            url = server_info['url']
            name = server_info['name']

            if url in existing_urls:
                old_server = existing_urls[url]
                if old_server['name'] != name:
                    old_name = old_server['name']
                    old_server['name'] = name
                    updated_count += 1
                    print(f"更新: {old_name} -> {name}")
            else:
                new_server = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "enabled": True,
                    "transport": {
                        "type": "http",
                        "url": url
                    }
                }
                servers.append(new_server)
                added_count += 1
                print(f"新增: {name}")

        if updated_count == 0 and added_count == 0:
            print("配置已是最新，无需更新")
            return True

        # 备份并更新配置
        if backup and os.path.exists(config_path):
            self.backup_config(config_path)

        self.save_config(config, config_path)
        print(f"同步完成: 更新{updated_count}个, 新增{added_count}个")
        return True