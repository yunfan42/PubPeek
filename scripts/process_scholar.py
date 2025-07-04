#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理单个学者的文献分析脚本
"""

import os
import sys
import argparse
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Config, BibTexParser, PublicationExtractor, RankingMatcher
from utils import DataProcessor, ReportGenerator


class ScholarProcessor:
    """学者文献处理器"""
    
    def __init__(self, user_id, config_file=None):
        """
        初始化学者处理器
        
        Args:
            user_id: 用户ID（DBLP ID）
            config_file: 配置文件路径
        """
        self.user_id = user_id
        self.config = Config(config_file)
        self.paths = self.config.get_user_paths(user_id)
        
        # 创建用户目录
        self.config.create_user_directories(user_id)
        
        # 初始化各个组件
        self.bib_parser = BibTexParser()
        
        # 创建PublicationExtractor的配置字典
        extractor_config = {
            'timeout': self.config.get('network.timeout', 120),
            'sleep_interval': self.config.get('network.sleep_interval', 3),
            'proxies': self.config.get_proxies()
        }
        self.publication_extractor = PublicationExtractor(extractor_config)
        
        self.ranking_matcher = RankingMatcher(
            ccf_file=self.config.get('data.ccf_file'),
            cas_file=self.config.get('data.cas_file')
        )
        self.data_processor = DataProcessor()
        self.report_generator = ReportGenerator()
    
    def process_bibliography(self, bib_file_path=None):
        """
        处理文献信息
        
        Args:
            bib_file_path: BibTeX文件路径，如果为None则使用默认路径
        """
        if bib_file_path is None:
            bib_file_path = self.paths['bib_file']
        
        # 如果bib文件不存在，创建一个空的
        if not os.path.exists(bib_file_path):
            print(f"BibTeX文件不存在: {bib_file_path}")
            return None
        
        print(f"开始处理学者 {self.user_id} 的文献...")
        
        # 1. 解析BibTeX文件
        print("\n" + "-" * 50)
        print("📄 第一步：解析BibTeX文件")
        print("-" * 50)
        df = self.bib_parser.parse_file(bib_file_path)
        
        # 分析DataFrame
        analysis = self.bib_parser.analyze_dataframe(df)
        print(f"✅ 解析完成: {analysis['total_papers']} 篇论文")
        
        # 2. 去重处理
        print("\n" + "-" * 50)
        print("🔄 第二步：论文去重处理")
        print("-" * 50)
        df_deduplicated = self.data_processor.deduplicate_papers(df, verbose=False)
        
        # 保存去重后的解析结果
        self.bib_parser.save_results(df_deduplicated, self.paths['processed_dir'])
        
        # 3. 提取出版物信息
        print("\n" + "-" * 50)
        print("📊 第三步：提取出版物信息")
        print("-" * 50)
        valid_papers, publication_counts, publication_types = self.publication_extractor.extract_unique_publication_abbrs(df_deduplicated)
        
        if not publication_counts:
            print("❌ 未找到有效的出版物")
            return None
        
        # 打印处理摘要
        self.report_generator.print_processing_summary(
            df, df_deduplicated, publication_counts, publication_types, None
        )
        
        # 4. 获取DBLP出版物信息
        print("\n" + "-" * 50)
        print("🌐 第四步：获取DBLP出版物信息")
        print("-" * 50)
        
        # 计算需要查询的期刊数量
        journal_count = sum(1 for pub_abbr in publication_counts if publication_types.get(pub_abbr) == 'journal')
        
        if journal_count > 0:
            print(f"🔍 需要查询 {journal_count} 个期刊的标题和ISSN信息")
            print(f"📋 会议论文直接通过缩写匹配CCF分级，无需查询DBLP")
            print(f"⏱️  预计耗时: {journal_count * 3} 秒（每个期刊约3秒）")
        else:
            print("📋 全部为会议论文，无需查询DBLP")
        
        # 定义进度回调函数
        def progress_callback(current, total, pub_abbr, paper_count):
            """显示DBLP信息获取进度"""
            # 计算进度百分比
            progress = (current / total) * 100
            
            # 创建进度条
            bar_length = 30
            filled_length = int(bar_length * current // total)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            # 从带前缀的键中提取原始缩写
            if pub_abbr.startswith('journal_'):
                display_abbr = pub_abbr[8:]  # 移除 'journal_' 前缀
            else:
                display_abbr = pub_abbr
            
            # 显示进度信息
            print(f"\r🔍 进度: [{bar}] {progress:.1f}% | 期刊: {display_abbr} ({paper_count}篇) | 剩余: {total - current}", end="", flush=True)
            
            # 完成后换行
            if current == total:
                print()
        
        # 使用全局DBLP缓存文件
        global_cache_file = self.config.get_global_cache_file()
        publications_info = self.publication_extractor.batch_extract_publication_info(
            publication_counts, 
            publication_types,
            cache_file=global_cache_file,
            progress_callback=progress_callback
        )
        
        # 显示完成信息
        success_count = sum(1 for info in publications_info.values() if info.get('success', False))
        print(f"✅ DBLP信息获取完成: {success_count}/{len(publications_info)} 成功")
        
        # 5. 匹配出版物分区
        print("\n" + "-" * 50)
        print("🏆 第五步：匹配出版物分区")
        print("-" * 50)
        ranking_results = self.ranking_matcher.batch_match_publications(publications_info)
        
        # 6. 生成统计摘要
        print("\n" + "-" * 50)
        print("📈 第六步：生成统计摘要")
        print("-" * 50)
        detailed_summary = self.ranking_matcher.generate_detailed_summary(ranking_results, publication_counts)
        
        # 7. 保存结果和统计分析
        print("\n" + "-" * 50)
        print("💾 第七步：保存结果和统计分析")
        print("-" * 50)
        
        # 为每篇论文添加CCF和中科院分区信息
        df_with_rankings = self.data_processor.add_ranking_info_to_papers(df_deduplicated, ranking_results)
        
        # 使用报告生成器生成和保存完整报告
        report_results = self.report_generator.generate_and_save_complete_report(
            df_with_rankings,
            ranking_results,
            publication_counts,
            detailed_summary,
            self.paths['processed_dir'],
            self.data_processor
        )
        
        # 获取统计结果
        ranking_stats = report_results['ranking_stats']
        
        # 8. 打印最终统计结果
        print("\n" + "-" * 50)
        print("📋 第八步：生成最终统计报告")
        print("-" * 50)
        self.report_generator.print_final_statistics(detailed_summary, ranking_stats)
        
        print("\n" + "=" * 60)
        print("🎉 所有处理步骤完成！")
        print("=" * 60)
        print(f"📁 处理结果已保存到: {self.paths['processed_dir']}")
        print(f"📊 可查看生成的Excel报告和JSON统计文件")
        
        return {
            'df': df_deduplicated,
            'df_with_rankings': df_with_rankings,
            'publication_counts': publication_counts,
            'publication_types': publication_types,
            'publications_info': publications_info,
            'ranking_results': ranking_results,
            'detailed_summary': detailed_summary,
            'ranking_stats': ranking_stats,
            'report_results': report_results
        }
    
    def copy_bib_file(self, source_bib_file):
        """
        复制BibTeX文件到用户目录
        
        Args:
            source_bib_file: 源BibTeX文件路径
        """
        if not os.path.exists(source_bib_file):
            raise FileNotFoundError(f"源文件不存在: {source_bib_file}")
        
        # 检查源文件和目标文件是否相同
        source_abs_path = os.path.abspath(source_bib_file)
        target_abs_path = os.path.abspath(self.paths['bib_file'])
        
        if source_abs_path == target_abs_path:
            print(f"源文件和目标文件相同，跳过复制: {self.paths['bib_file']}")
            return
        
        shutil.copy2(source_bib_file, self.paths['bib_file'])
        print(f"已复制BibTeX文件到: {self.paths['bib_file']}")
    
    def get_user_status(self):
        """获取用户处理状态"""
        status = {
            'user_id': self.user_id,
            'directories_exist': all(os.path.exists(path) for path in [
                self.paths['base_dir'], 
                self.paths['raw_dir'], 
                self.paths['processed_dir']
            ]),
            'bib_file_exists': os.path.exists(self.paths['bib_file']),
            'processed': os.path.exists(self.paths['summary_json']),
            'global_cache_exists': os.path.exists(self.config.get_global_cache_file())
        }
        return status


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='处理学者文献分析')
    parser.add_argument('user_id', help='用户ID (DBLP ID)')
    parser.add_argument('--bib-file', help='BibTeX文件路径')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--status', action='store_true', help='查看用户状态')
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = ScholarProcessor(args.user_id, args.config)
    
    if args.status:
        # 查看状态
        status = processor.get_user_status()
        print(f"用户ID: {status['user_id']}")
        print(f"目录结构: {'已创建' if status['directories_exist'] else '未创建'}")
        print(f"BibTeX文件: {'存在' if status['bib_file_exists'] else '不存在'}")
        print(f"处理状态: {'已处理' if status['processed'] else '未处理'}")
        print(f"全局缓存: {'存在' if status['global_cache_exists'] else '不存在'}")
        return
    
    # 复制BibTeX文件（如果提供了）
    if args.bib_file:
        processor.copy_bib_file(args.bib_file)
    
    # 处理文献
    results = processor.process_bibliography()
    
    if results:
        print("处理成功完成！")
    else:
        print("处理失败或无有效数据")


if __name__ == '__main__':
    main() 