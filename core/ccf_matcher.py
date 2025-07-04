#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCF分级匹配器
"""

import pandas as pd
import os
import re
from difflib import SequenceMatcher


class CCFMatcher:
    """CCF分级匹配器"""
    
    def __init__(self, ccf_file=None):
        """
        初始化CCF分级匹配器
        
        Args:
            ccf_file: CCF分区文件路径
        """
        self.ccf_file = ccf_file
        self.ccf_data = None
        
        # 加载数据
        if ccf_file:
            self.load_ccf_data()
    
    def load_ccf_data(self):
        """加载CCF分区数据"""
        try:
            self.ccf_data = pd.read_csv(self.ccf_file, encoding='utf-8')
            print(f"成功加载CCF数据: {len(self.ccf_data)} 条记录")
        except Exception as e:
            print(f"加载CCF数据失败: {str(e)}")
    
    def match_ccf_by_dblp_abbr(self, publication_abbr, publication_type='journal'):
        """
        通过DBLP缩写匹配CCF分区
        
        Args:
            publication_abbr: 出版物缩写
            publication_type: 出版物类型 ('journal' 或 'conference')
            
        Returns:
            dict: 匹配结果
        """
        if self.ccf_data is None:
            return {'matched': False, 'reason': 'CCF数据未加载'}
        
        # 根据类型构造URL模式
        if publication_type == 'journal':
            url_pattern_with_slash = f'/journals/{publication_abbr}/'
            url_pattern_without_slash = f'/journals/{publication_abbr}'
        elif publication_type == 'conference':
            url_pattern_with_slash = f'/conf/{publication_abbr}/'
            url_pattern_without_slash = f'/conf/{publication_abbr}'
        else:
            return {'matched': False, 'reason': f'不支持的出版物类型: {publication_type}'}
        
        # 在CCF数据的网址字段中查找匹配
        for _, row in self.ccf_data.iterrows():
            if pd.notna(row.get('网址', '')):
                url = row['网址']
                # 匹配两种情况：
                # 1. /journals/www/ 或 /conf/www/ (有结尾斜杠)
                # 2. /journals/www 或 /conf/chi (无结尾斜杠)
                if url_pattern_with_slash in url or url.endswith(url_pattern_without_slash):
                    return {
                        'matched': True,
                        'name': row.get('刊物名称', ''),
                        'abbr': row.get('Journal', ''),
                        'type': row.get('CCF推荐类别（国际学术刊物/会议）', ''),
                        'rank': row.get('CCF推荐类型', ''),
                        'url': row.get('网址', ''),
                        'publication_type': publication_type
                    }
        
        return {'matched': False, 'reason': '未找到匹配的CCF记录'}
    
    def match_ccf_by_name(self, publication_name, publication_type='journal'):
        """
        通过名称匹配CCF分区（备用方法）
        
        Args:
            publication_name: 出版物名称
            publication_type: 出版物类型 ('journal' 或 'conference')
            
        Returns:
            dict: 匹配结果
        """
        if self.ccf_data is None:
            return {'matched': False, 'reason': 'CCF数据未加载'}
        
        if not publication_name:
            return {'matched': False, 'reason': '无出版物名称'}
        
        # 清理名称
        name_clean = self.clean_publication_name(publication_name)
        
        # 精确匹配
        for _, row in self.ccf_data.iterrows():
            if pd.notna(row.get('刊物名称', '')):
                ccf_name_clean = self.clean_publication_name(row['刊物名称'])
                if name_clean.lower() == ccf_name_clean.lower():
                    return {
                        'matched': True,
                        'name': row.get('刊物名称', ''),
                        'abbr': row.get('Journal', ''),
                        'type': row.get('CCF推荐类别（国际学术刊物/会议）', ''),
                        'rank': row.get('CCF推荐类型', ''),
                        'url': row.get('网址', ''),
                        'publication_type': publication_type,
                        'match_type': 'Name_Exact'
                    }
        
        # 模糊匹配
        best_match = None
        best_score = 0.8  # 最小相似度阈值
        
        for _, row in self.ccf_data.iterrows():
            if pd.notna(row.get('刊物名称', '')):
                ccf_name_clean = self.clean_publication_name(row['刊物名称'])
                score = SequenceMatcher(None, name_clean.lower(), ccf_name_clean.lower()).ratio()
                
                if score > best_score:
                    best_score = score
                    best_match = {
                        'matched': True,
                        'name': row.get('刊物名称', ''),
                        'abbr': row.get('Journal', ''),
                        'type': row.get('CCF推荐类别（国际学术刊物/会议）', ''),
                        'rank': row.get('CCF推荐类型', ''),
                        'url': row.get('网址', ''),
                        'publication_type': publication_type,
                        'match_type': 'Name_Fuzzy',
                        'similarity': best_score
                    }
        
        return best_match or {'matched': False, 'reason': '名称匹配失败'}
    
    def clean_publication_name(self, name):
        """
        清理出版物名称
        
        Args:
            name: 出版物名称
            
        Returns:
            str: 清理后的名称
        """
        if not name:
            return ""
        
        # 转换为小写
        name = name.lower()
        
        # 移除常见的前缀和后缀
        prefixes = [
            'the ', 'journal of ', 'proceedings of ', 'ieee ', 'acm ', 
            'international conference on ', 'conference on ', 'workshop on '
        ]
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
        
        # 移除标点符号
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # 移除多余空格
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def match_publication_ccf(self, publication_abbr, publication_type='journal', publication_name=None):
        """
        匹配出版物的CCF分级
        
        Args:
            publication_abbr: 出版物缩写
            publication_type: 出版物类型 ('journal' 或 'conference')
            publication_name: 出版物名称（可选，用于备用匹配）
            
        Returns:
            dict: 匹配结果
        """
        # 优先使用DBLP缩写匹配
        result = self.match_ccf_by_dblp_abbr(publication_abbr, publication_type)
        
        # 如果缩写匹配失败且有名称，尝试名称匹配
        if not result['matched'] and publication_name:
            result = self.match_ccf_by_name(publication_name, publication_type)
        
        return result
    
    def batch_match_ccf(self, publications_info, progress_callback=None):
        """
        批量匹配CCF分级
        
        Args:
            publications_info: 出版物信息字典 {abbr: {title, publication_type, ...}}
            progress_callback: 进度回调函数
            
        Returns:
            dict: 匹配结果字典
        """
        results = {}
        
        for i, (pub_abbr, info) in enumerate(publications_info.items()):
            if progress_callback:
                progress_callback(i + 1, len(publications_info), pub_abbr)
            
            # 提取出版物信息
            pub_name = info.get('title')
            pub_type = info.get('publication_type', 'journal')
            
            # 匹配CCF分级
            result = self.match_publication_ccf(pub_abbr, pub_type, pub_name)
            results[pub_abbr] = result
        
        return results
    
    def generate_ccf_summary(self, results, publication_counts):
        """
        生成CCF分级统计摘要
        
        Args:
            results: 匹配结果字典
            publication_counts: 出版物论文数量字典
            
        Returns:
            dict: 统计摘要
        """
        summary = {
            'total_publications': len(results),
            'ccf_matches': 0,
            'ccf_stats': {'A': 0, 'B': 0, 'C': 0},
            'ccf_papers': {'A': 0, 'B': 0, 'C': 0},
            'ccf_journal_stats': {'A': 0, 'B': 0, 'C': 0},
            'ccf_conference_stats': {'A': 0, 'B': 0, 'C': 0},
            'ccf_journal_papers': {'A': 0, 'B': 0, 'C': 0},
            'ccf_conference_papers': {'A': 0, 'B': 0, 'C': 0}
        }
        
        for pub_abbr, result in results.items():
            paper_count = publication_counts.get(pub_abbr, 0)
            
            if result['matched']:
                summary['ccf_matches'] += 1
                rank = result['rank']
                pub_type = result.get('publication_type', 'journal')
                
                # 处理"A类"、"B类"、"C类"格式
                if rank.endswith('类'):
                    rank = rank[:-1]
                
                if rank in summary['ccf_stats']:
                    summary['ccf_stats'][rank] += 1
                    summary['ccf_papers'][rank] += paper_count
                    
                    # 按类型分类统计
                    if pub_type == 'journal':
                        summary['ccf_journal_stats'][rank] += 1
                        summary['ccf_journal_papers'][rank] += paper_count
                    elif pub_type == 'conference':
                        summary['ccf_conference_stats'][rank] += 1
                        summary['ccf_conference_papers'][rank] += paper_count
        
        return summary 