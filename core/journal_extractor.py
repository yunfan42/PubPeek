#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术出版物信息提取器（支持期刊和会议）
"""

import pandas as pd
import requests
import re
import time
import json
import os
from .issn_extractor import ISSNExtractor


class PublicationExtractor:
    """学术出版物信息提取器（支持期刊和会议）"""
    
    def __init__(self, config=None):
        """
        初始化出版物提取器
        
        Args:
            config: 配置对象
        """
        self.config = config or {}
        self.issn_extractor = ISSNExtractor()
        
        # 默认配置
        self.timeout = self.config.get('timeout', 120)
        self.sleep_interval = self.config.get('sleep_interval', 3)
        self.proxies = self.config.get('proxies', None)
    
    def extract_publication_abbr_from_id(self, dblp_id):
        """
        从DBLP ID中提取出版物缩写
        
        Args:
            dblp_id: DBLP ID，格式如 DBLP:journals/aei/... 或 DBLP:conf/aaai/...
        
        Returns:
            tuple: (缩写, 类型)，如 ('aei', 'journal') 或 ('aaai', 'conference')
        """
        if not dblp_id or pd.isna(dblp_id):
            return None, None
        
        # 匹配期刊模式: DBLP:journals/缩写/论文ID
        journal_match = re.search(r'DBLP:journals/([^/]+)/', dblp_id)
        if journal_match:
            return journal_match.group(1), 'journal'
        
        # 匹配会议模式: DBLP:conf/缩写/论文ID
        conf_match = re.search(r'DBLP:conf/([^/]+)/', dblp_id)
        if conf_match:
            return conf_match.group(1), 'conference'
        
        return None, None
    
    def extract_journal_abbr_from_id(self, dblp_id):
        """
        从DBLP ID中提取期刊缩写（保持向后兼容）
        
        Args:
            dblp_id: DBLP ID，格式如 DBLP:journals/aei/FengDMWZW25
        
        Returns:
            期刊缩写，如 'aei'，如果不是期刊则返回None
        """
        abbr, pub_type = self.extract_publication_abbr_from_id(dblp_id)
        return abbr if pub_type == 'journal' else None
    
    def extract_unique_journal_abbrs(self, df):
        """
        从DataFrame中提取唯一的期刊缩写（保持向后兼容）
        
        Args:
            df: 包含ID列的DataFrame
        
        Returns:
            tuple: (有效期刊论文DataFrame, 期刊缩写计数字典)
        """
        # 筛选期刊论文
        journal_papers = df[df['Type'] == 'article'].copy()
        
        # 提取期刊缩写
        journal_papers['journal_abbr'] = journal_papers['ID'].apply(self.extract_journal_abbr_from_id)
        
        # 移除无法提取缩写的记录
        valid_journal_papers = journal_papers[journal_papers['journal_abbr'].notna()]
        
        # 获取唯一的期刊缩写及其论文数量
        abbr_counts = valid_journal_papers['journal_abbr'].value_counts().to_dict()
        
        return valid_journal_papers, abbr_counts
    
    def extract_unique_publication_abbrs(self, df):
        """
        从DataFrame中提取唯一的出版物缩写（期刊和会议）
        
        Args:
            df: 包含ID列的DataFrame
        
        Returns:
            tuple: (有效出版物论文DataFrame, 出版物缩写计数字典, 出版物类型字典)
        """
        # 复制DataFrame以避免修改原始数据
        valid_papers = df.copy()
        
        # 提取出版物缩写和类型
        extraction_results = valid_papers['ID'].apply(self.extract_publication_abbr_from_id)
        valid_papers['raw_abbr'] = extraction_results.apply(lambda x: x[0] if x else None)
        valid_papers['publication_type'] = extraction_results.apply(lambda x: x[1] if x else None)
        
        # 移除无法提取缩写的记录
        valid_papers = valid_papers[valid_papers['raw_abbr'].notna()]
        
        # 创建带前缀的缩写以避免期刊和会议冲突
        # 例如：journal_www, conference_www
        def create_prefixed_abbr(row):
            if row['publication_type'] == 'journal':
                return f"journal_{row['raw_abbr']}"
            elif row['publication_type'] == 'conference':
                return f"conference_{row['raw_abbr']}"
            else:
                return row['raw_abbr']
        
        valid_papers['publication_abbr'] = valid_papers.apply(create_prefixed_abbr, axis=1)
        
        # 获取唯一的出版物缩写及其论文数量
        abbr_counts = valid_papers['publication_abbr'].value_counts().to_dict()
        
        # 获取出版物类型字典
        abbr_types = valid_papers.groupby('publication_abbr')['publication_type'].first().to_dict()
        
        return valid_papers, abbr_counts, abbr_types
    
    def extract_journal_only_abbrs(self, df):
        """
        从DataFrame中提取仅期刊的缩写（用于中科院分区）
        
        Args:
            df: 包含ID列的DataFrame
        
        Returns:
            tuple: (有效期刊论文DataFrame, 期刊缩写计数字典)
        """
        # 筛选期刊论文
        journal_papers = df[df['Type'] == 'article'].copy()
        
        # 提取期刊缩写
        journal_papers['journal_abbr'] = journal_papers['ID'].apply(self.extract_journal_abbr_from_id)
        
        # 移除无法提取缩写的记录
        valid_journal_papers = journal_papers[journal_papers['journal_abbr'].notna()]
        
        # 获取唯一的期刊缩写及其论文数量
        abbr_counts = valid_journal_papers['journal_abbr'].value_counts().to_dict()
        
        return valid_journal_papers, abbr_counts
    
    def clean_cache(self, cache_file):
        """
        清理缓存文件中的失败条目
        
        Args:
            cache_file: 缓存文件路径
        """
        if not cache_file or not os.path.exists(cache_file):
            return
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            # 只保留成功的条目
            cleaned_cache = {k: v for k, v in cache.items() if v.get('success', False)}
            
            # 如果有清理的条目，保存回文件
            if len(cleaned_cache) != len(cache):
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cleaned_cache, f, ensure_ascii=False, indent=2)
                print(f"已清理缓存文件，移除了 {len(cache) - len(cleaned_cache)} 个失败条目")
        
        except Exception as e:
            print(f"清理缓存文件失败: {str(e)}")
    
    def get_dblp_journal_info(self, journal_abbr, cache_file=None):
        """
        从DBLP获取期刊信息，包括标题和ISSN
        
        Args:
            journal_abbr: 期刊缩写
            cache_file: 缓存文件路径
            
        Returns:
            dict: 包含期刊信息的字典
        """
        # 加载缓存
        cache = {}
        if cache_file and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            except:
                cache = {}
        
        # 检查缓存，只使用成功的缓存条目
        if journal_abbr in cache and cache[journal_abbr].get('success', False):
            return cache[journal_abbr]
        
        # 构造DBLP URL
        url = f"https://dblp.org/db/journals/{journal_abbr}/"
        
        try:
            # 添加延时避免被封
            time.sleep(self.sleep_interval)
            
            # 发送请求
            if self.proxies:
                try:
                    response = requests.get(url, timeout=self.timeout, proxies=self.proxies)
                except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError):
                    # 如果代理失败，尝试直接连接
                    print(f"代理连接失败，尝试直接连接: {journal_abbr}")
                    response = requests.get(url, timeout=self.timeout)
            else:
                response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                # 获取期刊标题
                title = self.issn_extractor.extract_journal_title(response.text)
                
                # 获取ISSN列表
                issn_list = self.issn_extractor.extract_issn_list(response.text)
                
                # 检查是否成功提取到有效信息
                if title or issn_list:
                    journal_info = {
                        'title': title,
                        'issn_list': issn_list,
                        'success': True
                    }
                    
                    # 只有成功时才保存到缓存
                    if cache_file:
                        cache[journal_abbr] = journal_info
                        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            json.dump(cache, f, ensure_ascii=False, indent=2)
                else:
                    # 响应成功但没有提取到有效信息，不保存到缓存
                    journal_info = {
                        'title': None,
                        'issn_list': [],
                        'success': False
                    }
            else:
                # HTTP状态码不是200，不保存到缓存
                journal_info = {
                    'title': None,
                    'issn_list': [],
                    'success': False
                }
            
            return journal_info
            
        except Exception as e:
            print(f"获取 {journal_abbr} 信息失败: {str(e)}")
            # 异常时不保存到缓存，下次重新尝试
            journal_info = {
                'title': None,
                'issn_list': [],
                'success': False,
                'error': str(e)
            }
            
            return journal_info
    

    
    def batch_extract_journal_info(self, journal_abbrs, cache_file=None, progress_callback=None):
        """
        批量提取期刊信息
        
        Args:
            journal_abbrs: 期刊缩写列表或字典(缩写->论文数量)
            cache_file: 缓存文件路径
            progress_callback: 进度回调函数
            
        Returns:
            dict: 期刊信息字典
        """
        # 先清理缓存中的失败条目
        if cache_file:
            self.clean_cache(cache_file)
        
        results = {}
        
        if isinstance(journal_abbrs, dict):
            abbr_list = list(journal_abbrs.items())
        else:
            abbr_list = [(abbr, 1) for abbr in journal_abbrs]
        
        for i, (journal_abbr, count) in enumerate(abbr_list):
            if progress_callback:
                progress_callback(i + 1, len(abbr_list), journal_abbr, count)
            
            result = self.get_dblp_journal_info(journal_abbr, cache_file)
            results[journal_abbr] = result
        
        return results
    
    def batch_extract_publication_info(self, publication_abbrs, abbr_types, cache_file=None, progress_callback=None):
        """
        批量提取出版物信息（期刊和会议）
        
        注意：只有期刊需要从DBLP获取ISSN信息用于中科院分区匹配，
        会议论文不需要，因为CCF分级直接通过缩写匹配。
        
        Args:
            publication_abbrs: 出版物缩写列表或字典(缩写->论文数量)
            abbr_types: 出版物类型字典(缩写->类型)
            cache_file: 缓存文件路径
            progress_callback: 进度回调函数
            
        Returns:
            dict: 出版物信息字典
        """
        # 先清理缓存中的失败条目
        if cache_file:
            self.clean_cache(cache_file)
        
        results = {}
        
        if isinstance(publication_abbrs, dict):
            abbr_list = list(publication_abbrs.items())
        else:
            abbr_list = [(abbr, 1) for abbr in publication_abbrs]
        
        # 只处理期刊，会议不需要DBLP信息
        # 先统计期刊总数
        journal_list = [(pub_abbr, count) for pub_abbr, count in abbr_list if abbr_types.get(pub_abbr, 'unknown') == 'journal']
        total_journals = len(journal_list)
        
        journal_count = 0
        
        for i, (pub_abbr, count) in enumerate(abbr_list):
            pub_type = abbr_types.get(pub_abbr, 'unknown')
            
            if pub_type == 'journal':
                journal_count += 1
                if progress_callback:
                    progress_callback(journal_count, total_journals, pub_abbr, count)
                
                # 从带前缀的键中提取原始缩写
                # 例如：journal_www -> www
                if pub_abbr.startswith('journal_'):
                    raw_abbr = pub_abbr[8:]  # 移除 'journal_' 前缀
                else:
                    raw_abbr = pub_abbr  # 向后兼容
                
                # 只有期刊需要获取DBLP信息（包括ISSN）
                result = self.get_dblp_journal_info(raw_abbr, cache_file)
                result['publication_type'] = 'journal'
                results[pub_abbr] = result
                
            elif pub_type == 'conference':
                # 会议不需要DBLP信息，CCF分级直接通过缩写匹配
                results[pub_abbr] = {
                    'title': None,
                    'issn_list': [],
                    'success': True,  # 标记为成功，因为会议不需要额外信息
                    'publication_type': 'conference',
                    'skip_reason': '会议论文不需要DBLP信息，CCF分级直接通过缩写匹配'
                }
            else:
                results[pub_abbr] = {
                    'title': None,
                    'issn_list': [],
                    'success': False,
                    'publication_type': 'unknown',
                    'error': f'Unknown publication type: {pub_type}'
                }
        
        return results


# 保持向后兼容
JournalExtractor = PublicationExtractor 