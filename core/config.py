#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
import json


class Config:
    """配置管理类"""
    
    def __init__(self, config_file=None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self.load_default_config()
        
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_default_config(self):
        """加载默认配置"""
        return {
            'network': {
                'timeout': 120,
                'sleep_interval': 3,
                'proxy': {
                    'enabled': False,
                    'http': 'http://127.0.0.1:33210',
                    'https': 'http://127.0.0.1:33210'
                }
            },
            'data': {
                'ccf_file': 'data/CCF2022-UTF8.csv',
                'cas_file': 'data/FQBJCR2025-UTF8.csv'
            },
            'paths': {
                'users_dir': 'users',
                'data_dir': 'data'
            }
        }
    
    def load_config(self, config_file):
        """从文件加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self.merge_config(file_config)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
    
    def merge_config(self, new_config):
        """合并配置"""
        def merge_dict(base, new):
            for key, value in new.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self.config, new_config)
    
    def get(self, key, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_proxies(self):
        """获取代理配置"""
        if self.get('network.proxy.enabled', False):
            return {
                'http': self.get('network.proxy.http'),
                'https': self.get('network.proxy.https')
            }
        return None
    
    def get_user_dir(self, user_id):
        """获取用户目录"""
        users_dir = self.get('paths.users_dir', 'users')
        return os.path.join(users_dir, user_id)
    
    def get_user_paths(self, user_id):
        """获取用户相关路径"""
        user_dir = self.get_user_dir(user_id)
        return {
            'base_dir': user_dir,
            'raw_dir': os.path.join(user_dir, 'raw'),
            'processed_dir': os.path.join(user_dir, 'processed'),
            'bib_file': os.path.join(user_dir, 'raw', 'references.bib'),
            'parsed_csv': os.path.join(user_dir, 'processed', 'parsed_bibliography.csv'),
            'parsed_excel': os.path.join(user_dir, 'processed', 'parsed_bibliography.xlsx'),
            'rankings_excel': os.path.join(user_dir, 'processed', 'journal_rankings.xlsx'),
            'summary_json': os.path.join(user_dir, 'processed', 'summary.json')
        }
    
    def save_config(self, config_file=None):
        """保存配置到文件"""
        if config_file is None:
            config_file = self.config_file
        
        if config_file:
            try:
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存配置文件失败: {str(e)}")
    
    def get_global_cache_file(self):
        """获取全局DBLP缓存文件路径"""
        return self.get('cache.dblp_cache_file', 'cache/dblp_cache.json')
    
    def create_user_directories(self, user_id):
        """创建用户目录结构"""
        paths = self.get_user_paths(user_id)
        
        # 创建用户目录
        for dir_path in [paths['base_dir'], paths['raw_dir'], paths['processed_dir']]:
            os.makedirs(dir_path, exist_ok=True)
        
        # 创建全局缓存目录
        global_cache_dir = self.get('paths.cache_dir', 'cache')
        os.makedirs(global_cache_dir, exist_ok=True)
        
        return paths 