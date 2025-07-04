#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器工具
"""

import pandas as pd
import json
import os
from typing import Dict, Any, Tuple


class ReportGenerator:
    """报告生成器类，负责生成和保存分析报告"""
    
    def __init__(self):
        """初始化报告生成器"""
        pass
    
    def generate_and_save_complete_report(self, 
                                        df_with_rankings: pd.DataFrame,
                                        ranking_results: Dict[str, Any],
                                        publication_counts: Dict[str, int],
                                        detailed_summary: Dict[str, Any],
                                        output_dir: str,
                                        data_processor = None) -> Dict[str, Any]:
        """
        生成并保存完整的分析报告
        
        Args:
            df_with_rankings: 带分区信息的论文DataFrame
            ranking_results: 分区匹配结果
            publication_counts: 出版物数量统计
            detailed_summary: 详细统计摘要
            output_dir: 输出目录
            data_processor: DataProcessor实例（用于调用analyze_paper_rankings）
        
        Returns:
            Dict: 包含所有生成的文件路径和统计信息
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. 保存带有分区信息的论文列表
        ranked_files = self._save_ranked_papers(df_with_rankings, output_dir)
        
        # 2. 保存详细的分区匹配结果
        rankings_excel = self._save_detailed_rankings(ranking_results, publication_counts, detailed_summary, output_dir)
        
        # 3. 保存JSON格式的统计摘要
        summary_json = self._save_summary_json(detailed_summary, output_dir)
        
        # 4. 论文分区统计分析
        ranking_stats = None
        if data_processor:
            ranking_stats = data_processor.analyze_paper_rankings(df_with_rankings, verbose=False)
            
            # 保存不同分区的论文列表
            special_papers_files = self._save_special_paper_lists(ranking_stats, output_dir)
        else:
            special_papers_files = {}
        
        return {
            'ranked_files': ranked_files,
            'rankings_excel': rankings_excel,
            'summary_json': summary_json,
            'special_papers_files': special_papers_files,
            'ranking_stats': ranking_stats
        }
    
    def _save_ranked_papers(self, df_with_rankings: pd.DataFrame, output_dir: str) -> Dict[str, str]:
        """保存带有分区信息的论文列表"""
        ranked_csv_path = os.path.join(output_dir, 'papers_with_rankings.csv')
        ranked_excel_path = os.path.join(output_dir, 'papers_with_rankings.xlsx')
        
        df_with_rankings.to_csv(ranked_csv_path, index=False, encoding='utf-8-sig')
        df_with_rankings.to_excel(ranked_excel_path, index=False)
        
        return {
            'csv': ranked_csv_path,
            'excel': ranked_excel_path
        }
    
    def _save_detailed_rankings(self, ranking_results: Dict[str, Any], 
                              publication_counts: Dict[str, int],
                              detailed_summary: Dict[str, Any],
                              output_dir: str) -> str:
        """保存详细的分区匹配结果"""
        rankings_path = os.path.join(output_dir, 'journal_rankings.xlsx')
        
        with pd.ExcelWriter(rankings_path, engine='openpyxl') as writer:
            # 详细匹配结果
            results_df = pd.DataFrame([
                {
                    'abbr': abbr,
                    'publication_type': ranking_results[abbr].get('type', 'unknown'),
                    'paper_count': publication_counts.get(abbr, 0),
                    'ccf_matched': ranking_results[abbr].get('ccf', {}).get('matched', False),
                    'ccf_rank': ranking_results[abbr].get('ccf', {}).get('rank', ''),
                    'ccf_name': ranking_results[abbr].get('ccf', {}).get('name', ''),
                    'cas_matched': ranking_results[abbr].get('cas', {}).get('matched', False),
                    'cas_zone': ranking_results[abbr].get('cas', {}).get('zone', ''),
                    'cas_top': ranking_results[abbr].get('cas', {}).get('top', ''),
                    'cas_name': ranking_results[abbr].get('cas', {}).get('name', ''),
                }
                for abbr in ranking_results.keys()
            ])
            results_df.to_excel(writer, sheet_name='详细结果', index=False)
            
            # 统计摘要
            summary_data = [
                ['总论文数', detailed_summary.get('total_papers', sum(publication_counts.values()))],
                ['总出版物数', detailed_summary['total_publications']],
                ['期刊数', detailed_summary.get('journal_count', sum(1 for r in ranking_results.values() if r.get('type', 'unknown') == 'journal'))],
                ['会议数', detailed_summary.get('conference_count', sum(1 for r in ranking_results.values() if r.get('type', 'unknown') == 'conference'))],
                ['CCF匹配数', detailed_summary['ccf_matches']],
                ['中科院匹配数', detailed_summary['cas_matches']],
                ['CCF期刊A类论文数', detailed_summary.get('ccf_journal_papers', {}).get('A', 0)],
                ['CCF期刊B类论文数', detailed_summary.get('ccf_journal_papers', {}).get('B', 0)],
                ['CCF期刊C类论文数', detailed_summary.get('ccf_journal_papers', {}).get('C', 0)],
                ['CCF会议A类论文数', detailed_summary.get('ccf_conference_papers', {}).get('A', 0)],
                ['CCF会议B类论文数', detailed_summary.get('ccf_conference_papers', {}).get('B', 0)],
                ['CCF会议C类论文数', detailed_summary.get('ccf_conference_papers', {}).get('C', 0)],
                ['中科院1区论文数', detailed_summary.get('cas_papers', {}).get('1区', 0)],
                ['中科院2区论文数', detailed_summary.get('cas_papers', {}).get('2区', 0)],
                ['中科院3区论文数', detailed_summary.get('cas_papers', {}).get('3区', 0)],
                ['中科院4区论文数', detailed_summary.get('cas_papers', {}).get('4区', 0)],
                ['中科院Top期刊论文数', detailed_summary.get('cas_top_papers', 0)],
            ]
            summary_df = pd.DataFrame(summary_data, columns=['项目', '数量'])
            summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
        
        return rankings_path
    
    def _save_summary_json(self, detailed_summary: Dict[str, Any], output_dir: str) -> str:
        """保存JSON格式的统计摘要"""
        summary_path = os.path.join(output_dir, 'summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_summary, f, ensure_ascii=False, indent=2)
        return summary_path
    
    def _save_special_paper_lists(self, ranking_stats: Dict[str, Any], output_dir: str) -> Dict[str, Dict[str, str]]:
        """保存不同分区的论文列表"""
        special_files = {}
        
        # 保存CCF-A类+中科院1区论文
        if ranking_stats['ccf_a_or_cas_1_count'] > 0:
            ccf_a_cas_1_csv = os.path.join(output_dir, 'ccf_a_cas_1_papers.csv')
            ccf_a_cas_1_excel = os.path.join(output_dir, 'ccf_a_cas_1_papers.xlsx')
            
            ranking_stats['ccf_a_or_cas_1_papers'].to_csv(ccf_a_cas_1_csv, index=False, encoding='utf-8-sig')
            ranking_stats['ccf_a_or_cas_1_papers'].to_excel(ccf_a_cas_1_excel, index=False)
            
            special_files['ccf_a_cas_1'] = {
                'csv': ccf_a_cas_1_csv,
                'excel': ccf_a_cas_1_excel
            }
        
        # 保存CCF-A/B类+中科院1/2区论文
        if ranking_stats['ccf_ab_or_cas_12_count'] > 0:
            ccf_ab_cas_12_csv = os.path.join(output_dir, 'ccf_ab_cas_12_papers.csv')
            ccf_ab_cas_12_excel = os.path.join(output_dir, 'ccf_ab_cas_12_papers.xlsx')
            
            ranking_stats['ccf_ab_or_cas_12_papers'].to_csv(ccf_ab_cas_12_csv, index=False, encoding='utf-8-sig')
            ranking_stats['ccf_ab_or_cas_12_papers'].to_excel(ccf_ab_cas_12_excel, index=False)
            
            special_files['ccf_ab_cas_12'] = {
                'csv': ccf_ab_cas_12_csv,
                'excel': ccf_ab_cas_12_excel
            }
        
        return special_files
    
    def print_processing_summary(self, 
                               df_original: pd.DataFrame,
                               df_deduplicated: pd.DataFrame,
                               publication_counts: Dict[str, int],
                               publication_types: Dict[str, str],
                               detailed_summary: Dict[str, Any],
                               ranking_stats: Dict[str, Any] = None):
        """
        打印处理过程的摘要信息
        
        Args:
            df_original: 原始论文DataFrame
            df_deduplicated: 去重后的论文DataFrame
            publication_counts: 出版物数量统计
            publication_types: 出版物类型统计
            detailed_summary: 详细统计摘要
            ranking_stats: 排名统计（可选）
        """
        # 计算去重信息
        duplicates_removed = len(df_original) - len(df_deduplicated)
        
        # 计算出版物分布
        journal_count = sum(1 for t in publication_types.values() if t == 'journal')
        conference_count = sum(1 for t in publication_types.values() if t == 'conference')
        journal_papers = sum(count for abbr, count in publication_counts.items() if publication_types[abbr] == 'journal')
        conference_papers = sum(count for abbr, count in publication_counts.items() if publication_types[abbr] == 'conference')
        
        print(f"   去重完成: 原始 {len(df_original)} 篇 → 去重后 {len(df_deduplicated)} 篇")
        if duplicates_removed > 0:
            print(f"   去除重复: {duplicates_removed} 篇")
        
        print(f"   找到 {len(publication_counts)} 个出版物: {journal_count} 个期刊，{conference_count} 个会议")
        print(f"   论文分布: {journal_papers} 篇期刊论文，{conference_papers} 篇会议论文")
    
    def print_final_statistics(self, 
                             detailed_summary: Dict[str, Any],
                             ranking_stats: Dict[str, Any] = None):
        """
        打印最终统计结果
        
        Args:
            detailed_summary: 详细统计摘要
            ranking_stats: 排名统计（可选）
        """
        print("\n=== 分区匹配结果统计 ===")
        print(f"CCF分级统计 (论文数量):")
        print(f"  总匹配: {detailed_summary['ccf_matches']}/{detailed_summary['total_publications']} 个出版物")
        print(f"  期刊论文: A类={detailed_summary['ccf_journal_papers']['A']}篇, B类={detailed_summary['ccf_journal_papers']['B']}篇, C类={detailed_summary['ccf_journal_papers']['C']}篇")
        print(f"  会议论文: A类={detailed_summary['ccf_conference_papers']['A']}篇, B类={detailed_summary['ccf_conference_papers']['B']}篇, C类={detailed_summary['ccf_conference_papers']['C']}篇")
        
        print(f"\n中科院分区统计 (期刊论文数量):")
        print(f"  总匹配: {detailed_summary['cas_matches']} 个期刊")
        print(f"  期刊论文: 1区={detailed_summary['cas_papers']['1区']}篇, 2区={detailed_summary['cas_papers']['2区']}篇, 3区={detailed_summary['cas_papers']['3区']}篇, 4区={detailed_summary['cas_papers']['4区']}篇")
        print(f"  Top期刊论文: {detailed_summary['cas_top_papers']}篇")
        
        if ranking_stats:
            print(f"\n=== 论文分区统计总结 ===")
            print(f"📊 总论文数: {ranking_stats['total_papers']}")
            print(f"🏆 CCF-A类+中科院1区: {ranking_stats['ccf_a_or_cas_1_count']}篇")
            print(f"🌟 CCF-A/B类+中科院1/2区: {ranking_stats['ccf_ab_or_cas_12_count']}篇")
            print(f"🎯 CCF-A类: {ranking_stats['ccf_a_count']}篇 | CCF-B类: {ranking_stats['ccf_b_count']}篇 | CCF-C类: {ranking_stats['ccf_c_count']}篇")
            print(f"⭐ 中科院TOP: {ranking_stats['cas_top_count']}篇")
            print(f"🔬 中科院1区: {ranking_stats['cas_1_count']}篇 | 2区: {ranking_stats['cas_2_count']}篇 | 3区: {ranking_stats['cas_3_count']}篇 | 4区: {ranking_stats['cas_4_count']}篇")
    
    def print_detailed_paper_statistics(self, ranking_stats: Dict[str, Any]):
        """
        打印详细的论文统计分析（类似notebook中的格式）
        
        Args:
            ranking_stats: 排名统计
        """
        print("=== 论文分区统计分析 ===")
        print(f"\n📊 总论文数: {ranking_stats['total_papers']}")
        
        print(f"\n=== CCF分区统计 ===")
        print(f"🅰️  CCF-A类论文: {ranking_stats['ccf_a_count']}篇 ({ranking_stats['ccf_a_ratio']:.1f}%)")
        print(f"🅱️  CCF-B类论文: {ranking_stats['ccf_b_count']}篇 ({ranking_stats['ccf_b_ratio']:.1f}%)")
        print(f"🅲  CCF-C类论文: {ranking_stats['ccf_c_count']}篇 ({ranking_stats['ccf_c_ratio']:.1f}%)")
        
        print(f"\n=== 中科院分区统计 ===")
        print(f"🥇 中科院1区论文: {ranking_stats['cas_1_count']}篇 ({ranking_stats['cas_1_ratio']:.1f}%)")
        print(f"⭐ 中科院TOP论文: {ranking_stats['cas_top_count']}篇 ({ranking_stats['cas_top_ratio']:.1f}%)")
        print(f"🥈 中科院2区论文: {ranking_stats['cas_2_count']}篇 ({ranking_stats['cas_2_ratio']:.1f}%)")
        print(f"🥉 中科院3区论文: {ranking_stats['cas_3_count']}篇 ({ranking_stats['cas_3_ratio']:.1f}%)")
        print(f"🏅 中科院4区论文: {ranking_stats['cas_4_count']}篇 ({ranking_stats['cas_4_ratio']:.1f}%)")
        
        print(f"\n=== 组合统计 (去重) ===")
        print(f"🏆 CCF-A类 + 中科院1区 (并集): {ranking_stats['ccf_a_or_cas_1_count']}篇 ({ranking_stats['ccf_a_or_cas_1_ratio']:.1f}%)")
        print(f"🌟 CCF-A/B类 + 中科院1/2区 (并集): {ranking_stats['ccf_ab_or_cas_12_count']}篇 ({ranking_stats['ccf_ab_or_cas_12_ratio']:.1f}%)") 