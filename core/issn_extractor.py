#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISSN提取器
"""

import re
from bs4 import BeautifulSoup


class ISSNExtractor:
    """ISSN提取器"""
    
    def __init__(self):
        """初始化ISSN提取器"""
        # ISSN格式正则表达式
        self.issn_pattern = re.compile(r'\b\d{4}-\d{3}[\dxX]\b')
    
    def extract_issn_list(self, html_content):
        """
        从HTML内容中提取ISSN列表
        
        Args:
            html_content: HTML内容
            
        Returns:
            list: ISSN列表
        """
        if not html_content:
            return []
        
        # 使用正则表达式查找所有ISSN
        issn_matches = self.issn_pattern.findall(html_content)
        
        # 去重并返回
        return list(set(issn_matches))
    
    def extract_journal_title(self, html_content):
        """
        从HTML内容中提取期刊标题
        
        Args:
            html_content: HTML内容
            
        Returns:
            str: 期刊标题，如果未找到返回None
        """
        if not html_content:
            return None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找标题，通常在h1标签中
            title_tag = soup.find('h1')
            if title_tag:
                return title_tag.get_text(strip=True)
            
            # 如果没有h1，尝试title标签
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                # 清理标题，移除"dblp: "前缀
                title = re.sub(r'^dblp:\s*', '', title)
                return title
            
            return None
            
        except Exception as e:
            print(f"提取标题失败: {str(e)}")
            return None
    
    def extract_issn_from_text(self, text):
        """
        从文本中提取ISSN
        
        Args:
            text: 文本内容
            
        Returns:
            list: ISSN列表
        """
        if not text:
            return []
        
        issn_matches = self.issn_pattern.findall(text)
        return list(set(issn_matches))
    
    def validate_issn(self, issn):
        """
        验证ISSN格式
        
        Args:
            issn: ISSN字符串
            
        Returns:
            bool: 是否有效
        """
        if not issn:
            return False
        
        # 检查基本格式
        if not self.issn_pattern.match(issn):
            return False
        
        # 检查校验位
        try:
            digits = [int(d) for d in issn.replace('-', '') if d.isdigit()]
            if len(digits) != 7:
                return False
            
            # 计算校验位
            checksum = sum(d * (8 - i) for i, d in enumerate(digits))
            remainder = checksum % 11
            
            if remainder == 0:
                check_digit = '0'
            elif remainder == 1:
                check_digit = 'X'
            else:
                check_digit = str(11 - remainder)
            
            return issn[-1].upper() == check_digit
            
        except (ValueError, IndexError):
            return False
    
    def normalize_issn(self, issn):
        """
        规范化ISSN格式
        
        Args:
            issn: ISSN字符串
            
        Returns:
            str: 规范化后的ISSN
        """
        if not issn:
            return None
        
        # 移除所有非数字和非X的字符
        cleaned = re.sub(r'[^\dxX]', '', issn)
        
        # 如果长度不是8，返回None
        if len(cleaned) != 8:
            return None
        
        # 格式化为XXXX-XXXX
        formatted = f"{cleaned[:4]}-{cleaned[4:]}"
        
        return formatted if self.validate_issn(formatted) else None 