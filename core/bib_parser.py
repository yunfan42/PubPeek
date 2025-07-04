#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BibTeX文件解析器
"""

import pandas as pd
import bibtexparser
from bibtexparser.bparser import BibTexParser as BibtexParserLib
from bibtexparser.customization import convert_to_unicode
import re
import os


class BibTexParser:
    """BibTeX文件解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.parser = BibtexParserLib()
        self.parser.customization = convert_to_unicode
    
    def clean_author_names(self, author_string):
        """清理作者姓名，处理多个作者的情况"""
        if not author_string:
            return ""
        
        # 移除换行符并规范化空格
        author_string = re.sub(r'\s+', ' ', author_string.strip())
        
        # 分割作者（通常用 'and' 分隔）
        authors = [author.strip() for author in author_string.split(' and ')]
        
        return '; '.join(authors)

    def clean_text(self, text):
        """清理文本，移除多余的空格和换行符"""
        if not text:
            return ""
        
        # 移除多余的空格和换行符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除花括号（BibTeX格式）
        text = re.sub(r'\{([^}]*)\}', r'\1', text)
        
        return text

    def parse_file(self, bib_file_path):
        """
        解析BibTeX文件并转换为Pandas DataFrame
        
        Args:
            bib_file_path: BibTeX文件路径
            
        Returns:
            DataFrame: 解析后的文献数据
        """
        # 检查文件是否存在
        if not os.path.exists(bib_file_path):
            raise FileNotFoundError(f"文件未找到: {bib_file_path}")
        
        # 读取并解析BibTeX文件
        with open(bib_file_path, 'r', encoding='utf-8') as bib_file:
            bib_database = bibtexparser.load(bib_file, self.parser)
        
        # 转换为DataFrame
        papers_data = []
        
        for entry in bib_database.entries:
            # 提取基本信息
            paper_info = {
                'ID': entry.get('ID', ''),
                'Type': entry.get('ENTRYTYPE', ''),
                'Title': self.clean_text(entry.get('title', '')),
                'Author': self.clean_author_names(entry.get('author', '')),
                'Year': entry.get('year', ''),
                'Journal': self.clean_text(entry.get('journal', '')),
                'Booktitle': self.clean_text(entry.get('booktitle', '')),
                'Volume': entry.get('volume', ''),
                'Number': entry.get('number', ''),
                'Pages': entry.get('pages', ''),
                'DOI': entry.get('doi', ''),
                'URL': entry.get('url', ''),
                'Publisher': self.clean_text(entry.get('publisher', '')),
                'Editor': self.clean_author_names(entry.get('editor', '')),
                'Abstract': self.clean_text(entry.get('abstract', '')),
                'Keywords': self.clean_text(entry.get('keywords', '')),
            }
            
            # 添加其他字段
            for key, value in entry.items():
                if key not in ['ID', 'ENTRYTYPE'] and key.lower() not in [field.lower() for field in paper_info.keys()]:
                    paper_info[key] = self.clean_text(str(value))
            
            papers_data.append(paper_info)
        
        # 创建DataFrame
        df = pd.DataFrame(papers_data)
        
        return df

    def analyze_dataframe(self, df):
        """对DataFrame进行基本分析"""
        analysis = {
            'total_papers': len(df),
            'columns_count': len(df.columns),
            'paper_types': df['Type'].value_counts().to_dict(),
            'year_distribution': df['Year'].value_counts().sort_index().to_dict(),
            'journal_count': len(df[df['Journal'] != '']['Journal'].unique()) if 'Journal' in df.columns else 0,
            'conference_count': len(df[df['Booktitle'] != '']['Booktitle'].unique()) if 'Booktitle' in df.columns else 0,
            'missing_data': df.isnull().sum().to_dict()
        }
        
        return analysis

    def save_results(self, df, output_dir, base_name="parsed_bibliography"):
        """
        保存解析结果
        
        Args:
            df: 解析后的DataFrame
            output_dir: 输出目录
            base_name: 基本文件名
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存为CSV
        csv_path = os.path.join(output_dir, f"{base_name}.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # 保存为Excel
        excel_path = os.path.join(output_dir, f"{base_name}.xlsx")
        df.to_excel(excel_path, index=False)
        
        return csv_path, excel_path 