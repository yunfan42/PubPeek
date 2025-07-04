#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期刊分区匹配器 - 统一接口
"""

import pandas as pd
import os
import re
from difflib import SequenceMatcher
from .ccf_matcher import CCFMatcher
from .cas_matcher import CASMatcher


class RankingMatcher:
    """期刊分区匹配器 - 统一接口"""
    
    def __init__(self, ccf_file=None, cas_file=None):
        """
        初始化分区匹配器
        
        Args:
            ccf_file: CCF分区文件路径
            cas_file: 中科院分区文件路径
        """
        self.ccf_file = ccf_file
        self.cas_file = cas_file
        
        # 初始化子匹配器
        self.ccf_matcher = CCFMatcher(ccf_file) if ccf_file else None
        self.cas_matcher = CASMatcher(cas_file) if cas_file else None
    
    def match_ccf_by_dblp_abbr(self, publication_abbr, publication_type='journal'):
        """
        通过DBLP缩写匹配CCF分区（保持向后兼容）
        
        Args:
            publication_abbr: 出版物缩写
            publication_type: 出版物类型 ('journal' 或 'conference')
            
        Returns:
            dict: 匹配结果
        """
        if self.ccf_matcher is None:
            return {'matched': False, 'reason': 'CCF匹配器未初始化'}
        
        return self.ccf_matcher.match_ccf_by_dblp_abbr(publication_abbr, publication_type)
    
    def match_cas_by_issn(self, issn_list):
        """
        通过ISSN匹配中科院分区（保持向后兼容）
        
        Args:
            issn_list: ISSN列表
            
        Returns:
            dict: 匹配结果
        """
        if self.cas_matcher is None:
            return {'matched': False, 'reason': '中科院匹配器未初始化'}
        
        return self.cas_matcher.match_cas_by_issn(issn_list)
    
    def match_cas_by_name(self, journal_title):
        """
        通过期刊名称匹配中科院分区（保持向后兼容）
        
        Args:
            journal_title: 期刊标题
            
        Returns:
            dict: 匹配结果
        """
        if self.cas_matcher is None:
            return {'matched': False, 'reason': '中科院匹配器未初始化'}
        
        return self.cas_matcher.match_cas_by_name(journal_title)
    
    def match_journal_rankings(self, journal_abbr, journal_title=None, issn_list=None):
        """
        匹配期刊的CCF和中科院分区（保持向后兼容）
        
        Args:
            journal_abbr: 期刊缩写
            journal_title: 期刊标题
            issn_list: ISSN列表
            
        Returns:
            dict: 匹配结果
        """
        result = {
            'abbr': journal_abbr,
            'title': journal_title,
            'issn_list': issn_list or [],
            'ccf': {'matched': False, 'reason': '未尝试匹配'},
            'cas': {'matched': False, 'reason': '未尝试匹配'}
        }
        
        # CCF分区匹配
        if self.ccf_matcher:
            result['ccf'] = self.ccf_matcher.match_publication_ccf(
                journal_abbr, 'journal', journal_title
            )
        
        # 中科院分区匹配
        if self.cas_matcher:
            result['cas'] = self.cas_matcher.match_journal_cas(journal_title, issn_list)
        
        return result
    
    def match_publication_rankings(self, publication_abbr, publication_type='journal', 
                                   publication_title=None, issn_list=None):
        """
        匹配出版物的CCF和中科院分区（新接口）
        
        Args:
            publication_abbr: 出版物缩写
            publication_type: 出版物类型 ('journal' 或 'conference')
            publication_title: 出版物标题
            issn_list: ISSN列表（仅期刊有）
            
        Returns:
            dict: 匹配结果
        """
        result = {
            'abbr': publication_abbr,
            'title': publication_title,
            'type': publication_type,
            'issn_list': issn_list or [],
            'ccf': {'matched': False, 'reason': '未尝试匹配'},
            'cas': {'matched': False, 'reason': '未尝试匹配'}
        }
        
        # CCF分区匹配（期刊和会议都支持）
        if self.ccf_matcher:
            result['ccf'] = self.ccf_matcher.match_publication_ccf(
                publication_abbr, publication_type, publication_title
            )
        
        # 中科院分区匹配（仅期刊支持）
        if self.cas_matcher and publication_type == 'journal':
            result['cas'] = self.cas_matcher.match_journal_cas(publication_title, issn_list)
        elif publication_type == 'conference':
            result['cas'] = {'matched': False, 'reason': '会议不支持中科院分区'}
        
        return result
    
    def batch_match_journals(self, journal_info_dict, progress_callback=None):
        """
        批量匹配期刊分区（保持向后兼容）
        
        Args:
            journal_info_dict: 期刊信息字典
            progress_callback: 进度回调函数
            
        Returns:
            dict: 匹配结果字典
        """
        results = {}
        
        for i, (journal_abbr, info) in enumerate(journal_info_dict.items()):
            if progress_callback:
                progress_callback(i + 1, len(journal_info_dict), journal_abbr)
            
            # 提取期刊信息
            journal_title = info.get('title')
            issn_list = info.get('issn_list', [])
            
            # 匹配分区
            result = self.match_journal_rankings(journal_abbr, journal_title, issn_list)
            results[journal_abbr] = result
        
        return results
    
    def batch_match_publications(self, publications_info, progress_callback=None):
        """
        批量匹配出版物的CCF和中科院分区
        
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
            
            # 从带前缀的键中提取原始缩写和类型
            # 例如：journal_www -> www, journal
            # 或：conference_www -> www, conference
            if pub_abbr.startswith('journal_'):
                raw_abbr = pub_abbr[8:]  # 移除 'journal_' 前缀
                pub_type = 'journal'
            elif pub_abbr.startswith('conference_'):
                raw_abbr = pub_abbr[11:]  # 移除 'conference_' 前缀
                pub_type = 'conference'
            else:
                raw_abbr = pub_abbr  # 向后兼容
                pub_type = info.get('publication_type', 'journal')
            
            # 提取其他信息
            pub_title = info.get('title')
            issn_list = info.get('issn_list', [])
            
            # 匹配出版物分区
            result = self.match_publication_rankings(
                raw_abbr, pub_type, pub_title, issn_list
            )
            
            results[pub_abbr] = result
        
        return results
    
    def generate_summary(self, results, publication_counts):
        """
        生成分区统计摘要（保持向后兼容）
        
        Args:
            results: 匹配结果字典
            publication_counts: 出版物论文数量字典
            
        Returns:
            dict: 统计摘要
        """
        summary = {
            'total_publications': len(results),
            'ccf_matches': 0,
            'cas_matches': 0,
            'ccf_stats': {'A': 0, 'B': 0, 'C': 0},
            'cas_stats': {'1区': 0, '2区': 0, '3区': 0, '4区': 0},
            'ccf_papers': {'A': 0, 'B': 0, 'C': 0},
            'cas_papers': {'1区': 0, '2区': 0, '3区': 0, '4区': 0}
        }
        
        for pub_abbr, result in results.items():
            paper_count = publication_counts.get(pub_abbr, 0)
            
            # CCF统计
            if result['ccf']['matched']:
                summary['ccf_matches'] += 1
                rank = result['ccf']['rank']
                # 处理"A类"、"B类"、"C类"格式
                if rank.endswith('类'):
                    rank = rank[:-1]
                if rank in summary['ccf_stats']:
                    summary['ccf_stats'][rank] += 1
                    summary['ccf_papers'][rank] += paper_count
            
            # 中科院统计
            if result['cas']['matched']:
                summary['cas_matches'] += 1
                zone = result['cas']['zone']
                if zone in summary['cas_stats']:
                    summary['cas_stats'][zone] += 1
                    summary['cas_papers'][zone] += paper_count
        
        return summary
    
    def generate_detailed_summary(self, results, publication_counts):
        """
        生成详细分区统计摘要（新接口）
        
        Args:
            results: 匹配结果字典
            publication_counts: 出版物论文数量字典
            
        Returns:
            dict: 详细统计摘要
        """
        # 先生成基本统计
        summary = self.generate_summary(results, publication_counts)
        
        # 计算总论文数
        total_papers = sum(publication_counts.values())
        
        # 计算期刊和会议的数量
        journal_count = sum(1 for result in results.values() if result.get('type', 'journal') == 'journal')
        conference_count = sum(1 for result in results.values() if result.get('type', 'journal') == 'conference')
        
        # 添加详细统计
        detailed_summary = {
            **summary,
            'total_papers': total_papers,
            'journal_count': journal_count,
            'conference_count': conference_count,
            'ccf_journal_stats': {'A': 0, 'B': 0, 'C': 0},
            'ccf_conference_stats': {'A': 0, 'B': 0, 'C': 0},
            'ccf_journal_papers': {'A': 0, 'B': 0, 'C': 0},
            'ccf_conference_papers': {'A': 0, 'B': 0, 'C': 0},
            'cas_top_journals': 0,
            'cas_top_papers': 0
        }
        
        for pub_abbr, result in results.items():
            paper_count = publication_counts.get(pub_abbr, 0)
            pub_type = result.get('type', 'journal')
            
            # CCF详细统计
            if result['ccf']['matched']:
                rank = result['ccf']['rank']
                # 处理"A类"、"B类"、"C类"格式
                if rank.endswith('类'):
                    rank = rank[:-1]
                
                if rank in detailed_summary['ccf_stats']:
                    # 按类型分类统计
                    if pub_type == 'journal':
                        detailed_summary['ccf_journal_stats'][rank] += 1
                        detailed_summary['ccf_journal_papers'][rank] += paper_count
                    elif pub_type == 'conference':
                        detailed_summary['ccf_conference_stats'][rank] += 1
                        detailed_summary['ccf_conference_papers'][rank] += paper_count
            
            # 中科院详细统计
            if result['cas']['matched']:
                top = result['cas'].get('top', '')
                # 统计Top期刊（中科院数据中Top字段值为"是"或"否"）
                if top and str(top) == '是':
                    detailed_summary['cas_top_journals'] += 1
                    detailed_summary['cas_top_papers'] += paper_count
        
        return detailed_summary
    
    # 保持向后兼容的清理函数
    def clean_journal_name(self, name):
        """
        清理期刊名称（保持向后兼容）
        
        Args:
            name: 期刊名称
            
        Returns:
            str: 清理后的名称
        """
        if self.cas_matcher:
            return self.cas_matcher.clean_journal_name(name)
        
        # 如果没有CAS匹配器，提供基本的清理功能
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