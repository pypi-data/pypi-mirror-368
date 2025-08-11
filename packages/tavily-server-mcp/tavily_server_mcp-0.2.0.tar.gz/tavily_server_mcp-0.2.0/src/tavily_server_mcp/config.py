#!/usr/bin/env python

"""
配置加载模块，用于从配置文件加载设置。
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """加载配置文件
    
    Args:
        config_path: 配置文件路径，如果为None，则尝试从环境变量或默认位置加载
        
    Returns:
        配置字典
    """
    # 默认配置
    default_config = {
        "server": {
            "host": "0.0.0.0",
            "port": int(os.getenv("PORT", "8000")),
            "reload": False,
            "log_level": "info"
        },
        "tavily": {
            "host": "0.0.0.0",
            "port": 8083,
            "reload": False,
            "log_level": "info",
            "search_options": {
                "max_results": 5,
                "search_depth": "basic"
            }
        },
        "api": {
            "cors_origins": ["*"],
            "rate_limit": {
                "enabled": True,
                "max_requests": 100,
                "time_window": 60
            }
        }
    }
    
    # 如果未指定配置文件路径，尝试从环境变量获取
    if not config_path:
        config_path = os.getenv("MCP_CONFIG_PATH")
    
    # 如果环境变量未设置，尝试默认位置
    if not config_path:
        default_locations = [
            "./config.json",
            "~/.config/your-mcp-server/config.json",
            "/etc/your-mcp-server/config.json"
        ]
        
        for location in default_locations:
            expanded_path = os.path.expanduser(location)
            if os.path.exists(expanded_path):

                config_path = expanded_path
                break
    
    # 如果找到配置文件，加载它
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                logger.info(f"已从 {config_path} 加载配置")
                
                # 合并配置
                merged_config = deep_merge(default_config, user_config)
                return merged_config
        except Exception as e:
            logger.error(f"加载配置文件 {config_path} 时出错: {e}")
            logger.info("使用默认配置")
    else:
        logger.info("未找到配置文件，使用默认配置")
    
    return default_config

def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并两个字典
    
    Args:
        dict1: 基础字典
        dict2: 要合并的字典（优先级更高）
        
    Returns:
        合并后的字典
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result