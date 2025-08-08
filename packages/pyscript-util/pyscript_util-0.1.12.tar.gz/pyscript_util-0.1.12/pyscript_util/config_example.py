#!/usr/bin/env python3
"""
配置管理器使用示例

这个示例展示了如何使用 ConfigManager 来：
1. 定义有序的配置模板
2. 加载多层优先级配置
3. 处理配置错误
4. 生成用户友好的错误报告
5. 生成有序且带注释的YAML配置
"""

import os
import sys
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import (
    ConfigManager, ConfigTemplate, ConfigNode, ConfigType, 
    ConfigurationError, ConfigFormat
)


def create_sample_config_template() -> ConfigTemplate:
    """创建示例配置模板（带有顺序）"""
    
    # 创建配置模板
    template = ConfigTemplate(
        name="MyApp配置",
        description="一个演示多层配置系统的示例应用",
        version="1.0.0"
    )
    
    # 应用基本信息 (order=1)
    template.add_node(ConfigNode(
        name="app_name",
        config_type=ConfigType.STRING,
        description="应用程序名称",
        required=True,
        default="MyApp",
        example="MyAwesomeApp",
        order=1
    ))
    
    template.add_node(ConfigNode(
        name="version",
        config_type=ConfigType.STRING,
        description="应用程序版本",
        required=False,
        default="1.0.0",
        example="2.1.0",
        order=2
    ))
    
    template.add_node(ConfigNode(
        name="debug",
        config_type=ConfigType.BOOLEAN,
        description="是否启用调试模式",
        required=False,
        default=False,
        example=True,
        order=3
    ))
    
    # 数据库配置节点 (order=10)
    db_node = ConfigNode(
        name="database",
        config_type=ConfigType.DICT,
        description="数据库连接配置",
        required=True,
        order=10
    )
    
    # 数据库子节点（按重要性排序）
    db_node.add_child(ConfigNode(
        name="host",
        config_type=ConfigType.STRING,
        description="数据库主机地址",
        required=True,
        default="localhost",
        example="127.0.0.1",
        order=1
    ))
    
    db_node.add_child(ConfigNode(
        name="port",
        config_type=ConfigType.INTEGER,
        description="数据库端口",
        required=True,
        default=5432,
        example=5432,
        order=2
    ))
    
    db_node.add_child(ConfigNode(
        name="database_name",
        config_type=ConfigType.STRING,
        description="数据库名称",
        required=True,
        example="myapp",
        order=3
    ))
    
    db_node.add_child(ConfigNode(
        name="username",
        config_type=ConfigType.STRING,
        description="数据库用户名",
        required=True,
        example="myuser",
        order=4
    ))
    
    db_node.add_child(ConfigNode(
        name="password",
        config_type=ConfigType.STRING,
        description="数据库密码",
        required=True,
        example="mypassword",
        order=5
    ))
    
    db_node.add_child(ConfigNode(
        name="pool_size",
        config_type=ConfigType.INTEGER,
        description="连接池大小",
        required=False,
        default=10,
        example=20,
        order=6
    ))
    
    db_node.add_child(ConfigNode(
        name="timeout",
        config_type=ConfigType.INTEGER,
        description="连接超时时间(秒)",
        required=False,
        default=30,
        example=60,
        order=7
    ))
    
    # 服务器配置节点 (order=20)
    server_node = ConfigNode(
        name="server",
        config_type=ConfigType.DICT,
        description="Web服务器配置",
        required=True,
        order=20
    )
    
    server_node.add_child(ConfigNode(
        name="host",
        config_type=ConfigType.STRING,
        description="服务器监听地址",
        required=False,
        default="0.0.0.0",
        example="127.0.0.1",
        order=1
    ))
    
    server_node.add_child(ConfigNode(
        name="port",
        config_type=ConfigType.INTEGER,
        description="服务器监听端口",
        required=True,
        default=8080,
        example=8080,
        order=2
    ))
    
    server_node.add_child(ConfigNode(
        name="workers",
        config_type=ConfigType.INTEGER,
        description="工作进程数量",
        required=False,
        default=4,
        example=8,
        order=3
    ))
    
    server_node.add_child(ConfigNode(
        name="ssl_enabled",
        config_type=ConfigType.BOOLEAN,
        description="是否启用SSL",
        required=False,
        default=False,
        example=True,
        order=4
    ))
    
    server_node.add_child(ConfigNode(
        name="ssl_cert_path",
        config_type=ConfigType.PATH,
        description="SSL证书文件路径",
        required=False,
        example="/etc/ssl/certs/server.crt",
        order=5
    ))
    
    server_node.add_child(ConfigNode(
        name="ssl_key_path",
        config_type=ConfigType.PATH,
        description="SSL私钥文件路径",
        required=False,
        example="/etc/ssl/private/server.key",
        order=6
    ))
    
    # 日志配置节点 (order=30)
    log_node = ConfigNode(
        name="logging",
        config_type=ConfigType.DICT,
        description="日志系统配置",
        required=False,
        order=30
    )
    
    log_node.add_child(ConfigNode(
        name="level",
        config_type=ConfigType.STRING,
        description="日志级别",
        required=False,
        default="INFO",
        example="DEBUG",
        validator=lambda x: x.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        order=1
    ))
    
    log_node.add_child(ConfigNode(
        name="file_path",
        config_type=ConfigType.PATH,
        description="日志文件路径",
        required=False,
        default="/var/log/myapp.log",
        example="/tmp/myapp.log",
        order=2
    ))
    
    log_node.add_child(ConfigNode(
        name="max_size",
        config_type=ConfigType.INTEGER,
        description="日志文件最大大小(MB)",
        required=False,
        default=10,
        example=50,
        order=3
    ))
    
    log_node.add_child(ConfigNode(
        name="backup_count",
        config_type=ConfigType.INTEGER,
        description="日志文件备份数量",
        required=False,
        default=5,
        example=10,
        order=4
    ))
    
    # 安全配置节点 (order=40)
    security_node = ConfigNode(
        name="security",
        config_type=ConfigType.DICT,
        description="安全相关配置",
        required=False,
        order=40
    )
    
    security_node.add_child(ConfigNode(
        name="allowed_ips",
        config_type=ConfigType.LIST,
        description="允许访问的IP地址列表",
        required=False,
        default=[],
        example=["127.0.0.1", "192.168.1.0/24"],
        order=1
    ))
    
    security_node.add_child(ConfigNode(
        name="api_key",
        config_type=ConfigType.STRING,
        description="API访问密钥",
        required=False,
        example="your-secret-api-key-here",
        order=2
    ))
    
    security_node.add_child(ConfigNode(
        name="token_expiry",
        config_type=ConfigType.INTEGER,
        description="访问令牌过期时间(分钟)",
        required=False,
        default=60,
        example=120,
        order=3
    ))
    
    # 缓存配置节点 (order=50)
    cache_node = ConfigNode(
        name="cache",
        config_type=ConfigType.DICT,
        description="缓存系统配置",
        required=False,
        order=50
    )
    
    cache_node.add_child(ConfigNode(
        name="enabled",
        config_type=ConfigType.BOOLEAN,
        description="是否启用缓存",
        required=False,
        default=True,
        order=1
    ))
    
    cache_node.add_child(ConfigNode(
        name="ttl",
        config_type=ConfigType.INTEGER,
        description="缓存生存时间(秒)",
        required=False,
        default=300,
        example=600,
        order=2
    ))
    
    cache_node.add_child(ConfigNode(
        name="max_entries",
        config_type=ConfigType.INTEGER,
        description="最大缓存条目数",
        required=False,
        default=1000,
        example=5000,
        order=3
    ))
    
    # 添加根节点到模板
    template.add_node(db_node)
    template.add_node(server_node)
    template.add_node(log_node)
    template.add_node(security_node)
    template.add_node(cache_node)
    
    return template


def demo_ordered_yaml():
    """演示有序YAML生成"""
    
    print("=" * 80)
    print("有序YAML配置生成演示")
    print("=" * 80)
    
    # 创建配置模板
    template = create_sample_config_template()
    
    print("\n1. 配置模板结构:")
    print("-" * 40)
    print(template.print_template_structure())
    
    print("\n2. 生成有序且带注释的YAML配置:")
    print("-" * 50)
    yaml_config = template.generate_example_config(ConfigFormat.YAML)
    print(yaml_config)
    
    print("\n3. 生成JSON配置:")
    print("-" * 20)
    json_config = template.generate_example_config(ConfigFormat.JSON)
    print(json_config)
    
    # 保存到文件
    with open("example_config.yaml", "w", encoding="utf-8") as f:
        f.write(yaml_config)
    
    with open("example_config.json", "w", encoding="utf-8") as f:
        f.write(json_config)
    
    print(f"\n已保存配置文件:")
    print(f"  - example_config.yaml")
    print(f"  - example_config.json")


def test_config_loading():
    """测试配置加载"""
    
    print("\n" + "=" * 80)
    print("配置加载测试")
    print("=" * 80)
    
    template = create_sample_config_template()
    config_manager = ConfigManager(
        app_name="myapp",
        template=template,
        config_filename="example_config"
    )
    
    try:
        config_data = config_manager.load_config()
        print("✓ 配置加载成功!")
        
        # 验证配置
        errors = config_manager.validate_config()
        if errors:
            print(f"\n配置验证错误:")
            for error in errors:
                print(f"  - {error}")
            
            # 显示详细错误报告
            print("\n详细错误报告:")
            print("-" * 40)
            error_report = config_manager.print_config_error(
                custom_message="配置验证失败"
            )
            print(error_report)
        else:
            print("\n✓ 配置验证通过!")
            
            # 显示一些配置值
            print("\n配置值示例:")
            print(f"  应用名称: {config_manager.get_config_value('app_name')}")
            print(f"  数据库主机: {config_manager.get_config_value('database.host')}")
            print(f"  服务器端口: {config_manager.get_config_value('server.port')}")
            print(f"  日志级别: {config_manager.get_config_value('logging.level')}")
            print(f"  缓存启用: {config_manager.get_config_value('cache.enabled')}")
            
    except ConfigurationError as e:
        print(f"✗ 配置加载失败: {e.message}")
        print("\n详细错误报告:")
        print(config_manager.print_config_error(custom_message=e.message))


def demo_error_handling():
    """演示错误处理"""
    
    print("\n" + "=" * 80)
    print("错误处理演示")
    print("=" * 80)
    
    template = create_sample_config_template()
    config_manager = ConfigManager("myapp", template)
    
    # 模拟一个有问题的配置
    config_manager._config_data = {
        "app_name": "TestApp",
        "database": {
            "host": "localhost",
            "port": "invalid_port",  # 错误：应该是整数
            "username": "testuser"
            # 缺少必需的 password 和 database_name
        },
        "server": {
            "port": 8080,
            "workers": -1  # 错误：负数工作进程
        },
        "debug": "yes"  # 错误：应该是布尔值
    }
    
    # 验证配置
    errors = config_manager.validate_config()
    print("发现的配置错误:")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    
    # 演示特定路径的错误报告
    print("\n" + "=" * 60)
    print("数据库端口配置错误详细报告:")
    print("=" * 60)
    error_report = config_manager.print_config_error(
        error_path="database.port",
        custom_message="数据库端口配置类型错误，导致连接失败"
    )
    print(error_report)


if __name__ == "__main__":
    # 演示有序YAML生成
    demo_ordered_yaml()
    
    # 测试配置加载
    test_config_loading()
    
    # 演示错误处理
    demo_error_handling()
    
    # 清理文件
    print("\n" + "=" * 80)
    print("清理演示文件")
    print("=" * 80)
    
    files_to_clean = ["example_config.yaml", "example_config.json"]
    for filename in files_to_clean:
        try:
            os.remove(filename)
            print(f"✓ 已删除 {filename}")
        except FileNotFoundError:
            print(f"- {filename} 不存在")
    
    print("\n演示完成！") 