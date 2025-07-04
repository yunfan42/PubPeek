#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中科院分区匹配器（仅适用于期刊）
"""

import pandas as pd
import os
import re
from difflib import SequenceMatcher


class CASMatcher:
    """中科院分区匹配器（仅适用于期刊）"""
    
    def __init__(self, cas_file=None):
        """
        初始化中科院分区匹配器
        
        Args:
            cas_file: 中科院分区文件路径
        """
        self.cas_file = cas_file
        self.cas_data = None
        
        # 加载数据
        if cas_file:
            self.load_cas_data()
    
    def load_cas_data(self):
        """加载中科院分区数据"""
        try:
            self.cas_data = pd.read_csv(self.cas_file, encoding='utf-8')
            # 处理ISSN字段，从ISSN/EISSN中提取ISSN
            if 'ISSN/EISSN' in self.cas_data.columns:
                self.cas_data['ISSN'] = self.cas_data['ISSN/EISSN'].apply(
                    lambda x: x.split('/')[0] if pd.notna(x) and '/' in str(x) else x
                )
            # 处理分区字段，从"3 [224/758]"格式中提取数字
            if '大类分区' in self.cas_data.columns:
                self.cas_data['分区'] = self.cas_data['大类分区'].apply(
                    lambda x: f"{str(x).split()[0]}区" if pd.notna(x) and str(x).split()[0].isdigit() else x
                )
            print(f"成功加载中科院数据: {len(self.cas_data)} 条记录")
        except Exception as e:
            print(f"加载中科院数据失败: {str(e)}")
    
    def match_cas_by_issn(self, issn_list):
        """
        通过ISSN匹配中科院分区
        
        Args:
            issn_list: ISSN列表
            
        Returns:
            dict: 匹配结果
        """
        if self.cas_data is None:
            return {'matched': False, 'reason': '中科院数据未加载'}
        
        if not issn_list:
            return {'matched': False, 'reason': '无ISSN信息'}
        
        # 遍历ISSN列表寻找匹配
        for issn in issn_list:
            for _, row in self.cas_data.iterrows():
                if pd.notna(row.get('ISSN', '')):
                    if issn in row['ISSN']:
                        return {
                            'matched': True,
                            'name': row.get('Journal', ''),
                            'issn': row.get('ISSN', ''),
                            'zone': row.get('分区', ''),
                            'top': row.get('Top', ''),
                            'category': row.get('大类', ''),
                            'small_category': row.get('小类1', ''),
                            'match_type': 'ISSN'
                        }
        
        return {'matched': False, 'reason': '未找到匹配的中科院记录'}
    
    def match_cas_by_name(self, journal_title):
        """
        通过期刊名称匹配中科院分区
        
        Args:
            journal_title: 期刊标题
            
        Returns:
            dict: 匹配结果
        """
        if self.cas_data is None:
            return {'matched': False, 'reason': '中科院数据未加载'}
        
        if not journal_title:
            return {'matched': False, 'reason': '无期刊标题'}
        
        # 清理期刊标题
        title_clean = self.clean_journal_name(journal_title)
        
        # 精确匹配
        for _, row in self.cas_data.iterrows():
            if pd.notna(row.get('Journal', '')):
                name_clean = self.clean_journal_name(row['Journal'])
                if title_clean.lower() == name_clean.lower():
                    return {
                        'matched': True,
                        'name': row.get('Journal', ''),
                        'issn': row.get('ISSN', ''),
                        'zone': row.get('分区', ''),
                        'top': row.get('Top', ''),
                        'category': row.get('大类', ''),
                        'small_category': row.get('小类1', ''),
                        'match_type': 'Name_Exact'
                    }
        
        # 模糊匹配
        best_match = None
        best_score = 0.8  # 最小相似度阈值
        
        for _, row in self.cas_data.iterrows():
            if pd.notna(row.get('Journal', '')):
                name_clean = self.clean_journal_name(row['Journal'])
                score = SequenceMatcher(None, title_clean.lower(), name_clean.lower()).ratio()
                
                if score > best_score:
                    best_score = score
                    best_match = {
                        'matched': True,
                        'name': row.get('Journal', ''),
                        'issn': row.get('ISSN', ''),
                        'zone': row.get('分区', ''),
                        'top': row.get('Top', ''),
                        'category': row.get('大类', ''),
                        'small_category': row.get('小类1', ''),
                        'match_type': 'Name_Fuzzy',
                        'similarity': best_score
                    }
        
        return best_match or {'matched': False, 'reason': '名称匹配失败'}
    
    def clean_journal_name(self, name):
        """
        清理期刊名称
        
        Args:
            name: 期刊名称
            
        Returns:
            str: 清理后的名称
        """
        if not name:
            return ""
        
        # 转换为小写
        name = name.lower()
        
        # 移除常见的前缀和后缀
        prefixes = ['the ', 'journal of ', 'proceedings of ', 'ieee ', 'acm ']
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
        
        # 移除标点符号
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # 移除多余空格
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def match_journal_cas(self, journal_title=None, issn_list=None):
        """
        匹配期刊的中科院分区
        
        Args:
            journal_title: 期刊标题
            issn_list: ISSN列表
            
        Returns:
            dict: 匹配结果
        """
        # 优先使用ISSN匹配
        if issn_list:
            result = self.match_cas_by_issn(issn_list)
            if result['matched']:
                return result
        
        # 如果ISSN匹配失败，尝试名称匹配
        if journal_title:
            result = self.match_cas_by_name(journal_title)
            if result['matched']:
                return result
        
        return {'matched': False, 'reason': '未找到匹配的中科院记录'}
    
    def batch_match_cas(self, journals_info, progress_callback=None):
        """
        批量匹配中科院分区（仅处理期刊）
        
        Args:
            journals_info: 期刊信息字典 {abbr: {title, issn_list, ...}}
            progress_callback: 进度回调函数
            
        Returns:
            dict: 匹配结果字典
        """
        results = {}
        
        # 仅处理期刊类型的出版物
        journal_info = {}
        for abbr, info in journals_info.items():
            if info.get('publication_type') == 'journal':
                journal_info[abbr] = info
        
        for i, (journal_abbr, info) in enumerate(journal_info.items()):
            if progress_callback:
                progress_callback(i + 1, len(journal_info), journal_abbr)
            
            # 提取期刊信息
            journal_title = info.get('title')
            issn_list = info.get('issn_list', [])
            
            # 匹配中科院分区
            result = self.match_journal_cas(journal_title, issn_list)
            results[journal_abbr] = result
        
        return results
    
    def generate_cas_summary(self, results, journal_counts):
        """
        生成中科院分区统计摘要
        
        Args:
            results: 匹配结果字典
            journal_counts: 期刊论文数量字典
            
        Returns:
            dict: 统计摘要
        """
        summary = {
            'total_journals': len(results),
            'cas_matches': 0,
            'cas_stats': {'1区': 0, '2区': 0, '3区': 0, '4区': 0},
            'cas_papers': {'1区': 0, '2区': 0, '3区': 0, '4区': 0},
            'cas_top_journals': 0,
            'cas_top_papers': 0
        }
        
        for journal_abbr, result in results.items():
            paper_count = journal_counts.get(journal_abbr, 0)
            
            if result['matched']:
                summary['cas_matches'] += 1
                zone = result['zone']
                top = result.get('top', '')
                
                if zone in summary['cas_stats']:
                    summary['cas_stats'][zone] += 1
                    summary['cas_papers'][zone] += paper_count
                
                # 统计Top期刊（中科院数据中Top字段值为"是"或"否"）
                if top and str(top) == '是':
                    summary['cas_top_journals'] += 1
                    summary['cas_top_papers'] += paper_count
        
        return summary 