import os
import json
import yaml
import configparser
from typing import Dict, Any, List, Optional, Union, Type
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import sys
from collections import OrderedDict


# 配置有序YAML输出
def represent_ordereddict(dumper, data):
    """自定义OrderedDict的YAML表示器"""
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

def represent_none(self, data):
    """自定义None值的表示器，输出为null而不是空"""
    return self.represent_scalar('tag:yaml.org,2002:null', 'null')

# 注册自定义表示器
yaml.add_representer(OrderedDict, represent_ordereddict)
yaml.add_representer(type(None), represent_none)


class ConfigType(Enum):
    """配置值类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    PATH = "path"


class ConfigFormat(Enum):
    """配置文件格式枚举"""
    JSON = "json"
    YAML = "yaml"
    INI = "ini"


@dataclass
class ConfigNode:
    """配置节点定义"""
    name: str
    config_type: ConfigType
    description: str
    required: bool = False
    default: Any = None
    children: Dict[str, 'ConfigNode'] = field(default_factory=dict)
    validator: Optional[callable] = None
    example: Optional[str] = None
    order: int = 0  # 添加排序字段

    def add_child(self, child: 'ConfigNode') -> 'ConfigNode':
        """添加子节点"""
        self.children[child.name] = child
        return self

    def validate_value(self, value: Any) -> bool:
        """验证值是否符合类型要求"""
        if self.validator:
            return self.validator(value)
        
        if self.config_type == ConfigType.STRING:
            return isinstance(value, str)
        elif self.config_type == ConfigType.INTEGER:
            return isinstance(value, int)
        elif self.config_type == ConfigType.FLOAT:
            return isinstance(value, (int, float))
        elif self.config_type == ConfigType.BOOLEAN:
            return isinstance(value, bool)
        elif self.config_type == ConfigType.LIST:
            return isinstance(value, list)
        elif self.config_type == ConfigType.DICT:
            return isinstance(value, dict)
        elif self.config_type == ConfigType.PATH:
            return isinstance(value, str) and (Path(value).exists() or not self.required)
        
        return True


@dataclass
class ConfigTemplate:
    """配置模板"""
    name: str
    description: str
    version: str
    root_nodes: Dict[str, ConfigNode] = field(default_factory=dict)

    def add_node(self, node: ConfigNode) -> 'ConfigTemplate':
        """添加根节点"""
        self.root_nodes[node.name] = node
        return self

    def get_node_by_path(self, path: str) -> Optional[ConfigNode]:
        """通过路径获取节点"""
        parts = path.split('.')
        current = self.root_nodes.get(parts[0])
        
        for part in parts[1:]:
            if not current or part not in current.children:
                return None
            current = current.children[part]
        
        return current

    def generate_example_config(self, format_type: ConfigFormat = ConfigFormat.YAML) -> str:
        """生成示例配置"""
        def build_example_dict(nodes: Dict[str, ConfigNode]) -> OrderedDict:
            result = OrderedDict()
            
            # 按照order字段和名称排序节点
            sorted_nodes = sorted(
                nodes.items(), 
                key=lambda x: (x[1].order, x[0])
            )
            
            for name, node in sorted_nodes:
                if node.children:
                    result[name] = build_example_dict(node.children)
                else:
                    if node.example is not None:
                        result[name] = node.example
                    elif node.default is not None:
                        result[name] = node.default
                    else:
                        # 根据类型生成默认示例
                        if node.config_type == ConfigType.STRING:
                            result[name] = f"example_{name}"
                        elif node.config_type == ConfigType.INTEGER:
                            result[name] = 0
                        elif node.config_type == ConfigType.FLOAT:
                            result[name] = 0.0
                        elif node.config_type == ConfigType.BOOLEAN:
                            result[name] = False
                        elif node.config_type == ConfigType.LIST:
                            result[name] = []
                        elif node.config_type == ConfigType.DICT:
                            result[name] = OrderedDict()
                        elif node.config_type == ConfigType.PATH:
                            result[name] = f"/path/to/{name}"
            return result

        example_dict = build_example_dict(self.root_nodes)
        
        if format_type == ConfigFormat.YAML:
            # 使用自定义的YAML输出，保持顺序和格式
            return self._generate_ordered_yaml(example_dict)
        elif format_type == ConfigFormat.JSON:
            return json.dumps(example_dict, indent=2, ensure_ascii=False)
        else:  # INI
            # INI格式相对简单，只支持单层结构
            config = configparser.ConfigParser()
            for section_name, section_data in example_dict.items():
                if isinstance(section_data, (dict, OrderedDict)):
                    config[section_name] = {k: str(v) for k, v in section_data.items()}
            
            import io
            output = io.StringIO()
            config.write(output)
            return output.getvalue()

    def _generate_ordered_yaml(self, data: OrderedDict, indent: int = 0, parent_nodes: Dict[str, ConfigNode] = None) -> str:
        """生成有序且带注释的YAML"""
        lines = []
        prefix = "  " * indent
        
        # 如果没有指定父节点，使用根节点
        if parent_nodes is None:
            parent_nodes = self.root_nodes
        
        for key, value in data.items():
            # 查找对应的配置节点以获取描述
            node = parent_nodes.get(key)
            
            # 添加注释
            if node and node.description:
                lines.append(f"{prefix}# {node.description}")
                if node.required:
                    lines.append(f"{prefix}# [必需]")
                if node.default is not None and node.default != value:
                    lines.append(f"{prefix}# 默认值: {node.default}")
            
            # 添加键值对
            if isinstance(value, (dict, OrderedDict)):
                lines.append(f"{prefix}{key}:")
                # 传递当前节点的子节点作为下一层的父节点
                child_nodes = node.children if node else {}
                sub_yaml = self._generate_ordered_yaml(value, indent + 1, child_nodes)
                if sub_yaml.strip():
                    lines.append(sub_yaml.rstrip())
                else:
                    lines[-1] += " {}"  # 空字典
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                if value:
                    for item in value:
                        lines.append(f"{prefix}  - {item}")
                else:
                    lines[-1] += " []"  # 空列表
            elif isinstance(value, str):
                # 处理特殊字符和多行字符串
                if '\n' in str(value) or any(c in str(value) for c in [':', '#', '[', ']', '{', '}', ',', '&', '*', '!', '|', '>', "'", '"', '%', '@', '`']):
                    lines.append(f"{prefix}{key}: '{value}'")
                else:
                    lines.append(f"{prefix}{key}: {value}")
            else:
                lines.append(f"{prefix}{key}: {value}")
            
            # 在不同的根级配置项之间添加空行
            if indent == 0:
                lines.append("")
        
        return "\n".join(lines)

    def _find_node_by_key(self, key: str, nodes: Dict[str, ConfigNode]) -> Optional[ConfigNode]:
        """在节点字典中查找指定key的节点"""
        return nodes.get(key)

    def print_template_structure(self, indent: int = 0) -> str:
        """打印模板结构"""
        def print_node(node: ConfigNode, level: int) -> str:
            prefix = "  " * level
            result = f"{prefix}- {node.name} ({node.config_type.value})"
            if node.required:
                result += " [必需]"
            result += f": {node.description}\n"
            
            if node.default is not None:
                result += f"{prefix}  默认值: {node.default}\n"
            if node.example is not None:
                result += f"{prefix}  示例: {node.example}\n"
            
            # 按order排序子节点
            sorted_children = sorted(
                node.children.values(),
                key=lambda x: (x.order, x.name)
            )
            
            for child in sorted_children:
                result += print_node(child, level + 1)
            
            return result

        result = f"配置模板: {self.name} (v{self.version})\n"
        result += f"描述: {self.description}\n\n"
        result += "配置结构:\n"
        
        # 按order排序根节点
        sorted_nodes = sorted(
            self.root_nodes.values(),
            key=lambda x: (x.order, x.name)
        )
        
        for node in sorted_nodes:
            result += print_node(node, 0)
        
        return result


class ConfigPathLevel(Enum):
    """配置路径层级"""
    GLOBAL = "全局"
    USER = "用户"
    INSTALL = "安装路径"


@dataclass
class ConfigPath:
    """配置路径信息"""
    level: ConfigPathLevel
    path: Path
    exists: bool
    readable: bool
    format_type: Optional[ConfigFormat] = None


class ConfigurationError(Exception):
    """配置错误异常"""
    def __init__(self, message: str, path: str = None, suggestions: List[str] = None):
        self.message = message
        self.path = path
        self.suggestions = suggestions or []
        super().__init__(message)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, 
                 app_name: str, 
                 template: ConfigTemplate,
                 config_filename: str = "config",
                 supported_formats: List[ConfigFormat] = None):
        self.app_name = app_name
        self.template = template
        self.config_filename = config_filename
        self.supported_formats = supported_formats or [ConfigFormat.YAML, ConfigFormat.JSON, ConfigFormat.INI]
        
        self._config_data = {}
        self._loaded_paths = []
        self._all_search_paths = []
        self._active_config_path = None
        
        self._setup_search_paths()

    def _setup_search_paths(self):
        """设置搜索路径"""
        # 全局配置路径
        global_paths = [
            Path(f"/etc/{self.app_name}"),
            Path("/etc/default"),
            Path("/usr/local/etc")
        ]
        
        # 用户配置路径
        home = Path.home()
        user_paths = [
            home / f".{self.app_name}",
            home / ".config" / self.app_name,
            home / f".{self.app_name}rc"
        ]
        
        # 安装路径配置
        install_paths = []
        if hasattr(sys, 'prefix'):
            install_paths.append(Path(sys.prefix) / "etc" / self.app_name)
        if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
            install_paths.append(Path(sys.base_prefix) / "etc" / self.app_name)
        
        # 当前工作目录
        install_paths.append(Path.cwd() / f".{self.app_name}")
        install_paths.append(Path.cwd())
        
        # 构建完整的搜索路径列表
        for paths, level in [(global_paths, ConfigPathLevel.GLOBAL),
                           (user_paths, ConfigPathLevel.USER),
                           (install_paths, ConfigPathLevel.INSTALL)]:
            for path in paths:
                self._all_search_paths.append(ConfigPath(
                    level=level,
                    path=path,
                    exists=path.exists(),
                    readable=path.exists() and os.access(path, os.R_OK)
                ))

    def _find_config_files(self) -> List[ConfigPath]:
        """查找配置文件"""
        found_configs = []
        
        for config_path in self._all_search_paths:
            if not config_path.exists:
                continue
                
            for format_type in self.supported_formats:
                if format_type == ConfigFormat.YAML:
                    extensions = ['.yaml', '.yml']
                elif format_type == ConfigFormat.JSON:
                    extensions = ['.json']
                else:  # INI
                    extensions = ['.ini', '.conf', '']
                
                for ext in extensions:
                    file_path = config_path.path / f"{self.config_filename}{ext}"
                    if file_path.is_file():
                        found_config = ConfigPath(
                            level=config_path.level,
                            path=file_path,
                            exists=True,
                            readable=os.access(file_path, os.R_OK),
                            format_type=format_type
                        )
                        found_configs.append(found_config)
        
        return found_configs

    def _load_config_file(self, config_path: ConfigPath) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path.path, 'r', encoding='utf-8') as f:
                if config_path.format_type == ConfigFormat.YAML:
                    return yaml.safe_load(f) or {}
                elif config_path.format_type == ConfigFormat.JSON:
                    return json.load(f)
                else:  # INI
                    config = configparser.ConfigParser()
                    config.read_string(f.read())
                    return {section: dict(config[section]) for section in config.sections()}
        except Exception as e:
            raise ConfigurationError(
                f"无法解析配置文件 {config_path.path}: {str(e)}",
                path=str(config_path.path)
            )

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        found_configs = self._find_config_files()
        
        if not found_configs:
            raise ConfigurationError(
                "未找到任何配置文件",
                suggestions=self._generate_config_suggestions()
            )
        
        # 按优先级排序：安装路径 < 用户 < 全局
        priority_order = [ConfigPathLevel.INSTALL, ConfigPathLevel.USER, ConfigPathLevel.GLOBAL]
        found_configs.sort(key=lambda x: priority_order.index(x.level))
        
        merged_config = {}
        
        for config_path in found_configs:
            if not config_path.readable:
                continue
                
            try:
                config_data = self._load_config_file(config_path)
                self._deep_merge(merged_config, config_data)
                self._loaded_paths.append(config_path)
                
                # 记录最高优先级的配置路径
                if self._active_config_path is None:
                    self._active_config_path = config_path
            except ConfigurationError:
                continue
        
        self._config_data = merged_config
        return merged_config

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """深度合并字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def validate_config(self, config_path: str = None) -> List[str]:
        """验证配置"""
        errors = []
        
        def validate_node(path: str, node: ConfigNode, data: Dict[str, Any]):
            full_path = f"{path}.{node.name}" if path else node.name
            
            if node.name not in data:
                if node.required:
                    errors.append(f"缺少必需配置项: {full_path}")
                return
            
            value = data[node.name]
            
            if not node.validate_value(value):
                errors.append(f"配置项类型错误: {full_path} (期望: {node.config_type.value})")
                return
            
            # 验证子节点
            if node.children and isinstance(value, dict):
                for child in node.children.values():
                    validate_node(full_path, child, value)
        
        config_data = self._config_data
        if config_path:
            # 验证特定路径
            node = self.template.get_node_by_path(config_path)
            if node:
                path_parts = config_path.split('.')
                current_data = config_data
                for part in path_parts[:-1]:
                    current_data = current_data.get(part, {})
                
                validate_node('.'.join(path_parts[:-1]), node, current_data)
        else:
            # 验证所有根节点
            for node in self.template.root_nodes.values():
                validate_node("", node, config_data)
        
        return errors

    def get_config_value(self, path: str, default: Any = None) -> Any:
        """获取配置值"""
        parts = path.split('.')
        current = self._config_data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current

    def print_config_error(self, error_path: str = None, custom_message: str = None) -> str:
        """打印配置错误信息"""
        result = []
        
        # 标题
        result.append("=" * 60)
        result.append(f"配置错误报告 - {self.app_name}")
        result.append("=" * 60)
        result.append("")
        
        # 自定义错误消息
        if custom_message:
            result.append(f"错误信息: {custom_message}")
            result.append("")
        
        # 配置路径查找情况
        result.append("配置文件查找路径:")
        result.append("-" * 30)
        
        for level in [ConfigPathLevel.GLOBAL, ConfigPathLevel.USER, ConfigPathLevel.INSTALL]:
            result.append(f"\n{level.value}配置:")
            level_paths = [p for p in self._all_search_paths if p.level == level]
            
            for config_path in level_paths:
                status = "✓" if config_path.exists else "✗"
                readable = "(可读)" if config_path.readable else "(不可读)" if config_path.exists else ""
                result.append(f"  {status} {config_path.path} {readable}")
        
        result.append("")
        
        # 已加载的配置文件
        if self._loaded_paths:
            result.append("已加载的配置文件:")
            result.append("-" * 20)
            for config_path in self._loaded_paths:
                marker = "★" if config_path == self._active_config_path else "○"
                result.append(f"  {marker} {config_path.path} ({config_path.level.value})")
            result.append("")
        else:
            result.append("⚠️  没有成功加载任何配置文件")
            result.append("")
        
        # 当前活动配置
        if self._active_config_path:
            result.append(f"当前使用配置: {self._active_config_path.path}")
            result.append("")
        
        # 特定路径错误信息
        if error_path:
            result.append(f"错误配置项路径: {error_path}")
            result.append("-" * 20)
            
            node = self.template.get_node_by_path(error_path)
            if node:
                result.append(f"参数名称: {node.name}")
                result.append(f"参数类型: {node.config_type.value}")
                result.append(f"参数描述: {node.description}")
                result.append(f"是否必需: {'是' if node.required else '否'}")
                
                if node.default is not None:
                    result.append(f"默认值: {node.default}")
                
                if node.example is not None:
                    result.append(f"示例值: {node.example}")
                
                result.append("")
        
        # 配置模板结构
        result.append("完整配置模板:")
        result.append("-" * 20)
        result.append(self.template.print_template_structure())
        
        # 生成建议
        result.append("\n建议解决方案:")
        result.append("-" * 15)
        suggestions = self._generate_config_suggestions(error_path)
        for i, suggestion in enumerate(suggestions, 1):
            result.append(f"{i}. {suggestion}")
        
        return "\n".join(result)

    def _generate_config_suggestions(self, error_path: str = None) -> List[str]:
        """生成配置建议"""
        suggestions = []
        
        # 检查是否有可写的配置目录
        writable_paths = []
        for config_path in self._all_search_paths:
            if config_path.path.parent.exists() and os.access(config_path.path.parent, os.W_OK):
                config_file = config_path.path / f"{self.config_filename}.yaml"
                writable_paths.append(config_file)
        
        if writable_paths:
            suggestions.append(f"在以下路径创建配置文件: {', '.join(str(p) for p in writable_paths[:2])}")
        
        # 生成示例配置
        suggestions.append("使用以下命令生成示例配置:")
        suggestions.append(f"  python -c \"from {self.__class__.__module__} import ConfigManager; print(ConfigManager.generate_example_config())\"")
        
        # 特定路径的建议
        if error_path:
            node = self.template.get_node_by_path(error_path)
            if node:
                if node.example:
                    suggestions.append(f"参数 {error_path} 的正确格式示例: {node.example}")
                
                if node.config_type == ConfigType.PATH:
                    suggestions.append(f"确保路径 {error_path} 存在且可访问")
        
        # 权限相关建议
        unreadable_configs = [p for p in self._all_search_paths if p.exists and not p.readable]
        if unreadable_configs:
            suggestions.append(f"检查以下配置文件的读取权限: {', '.join(str(p.path) for p in unreadable_configs)}")
        
        return suggestions

    def generate_example_config(self, format_type: ConfigFormat = ConfigFormat.YAML) -> str:
        """生成示例配置文件"""
        return self.template.generate_example_config(format_type) 