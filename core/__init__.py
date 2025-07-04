#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PersonalScholar 核心模块

该模块包含了学者文献分析的核心功能：
- BibTeX文件解析
- 期刊和会议信息提取
- ISSN提取
- CCF和中科院分区匹配
- 配置管理
"""

from .bib_parser import BibTexParser
from .journal_extractor import JournalExtractor, PublicationExtractor
from .issn_extractor import ISSNExtractor
from .ranking_matcher import RankingMatcher
from .ccf_matcher import CCFMatcher
from .cas_matcher import CASMatcher
from .config import Config

__version__ = "1.0.0"
__author__ = "Personal Scholar Team"

__all__ = [
    'BibTexParser',
    'JournalExtractor',     # 保持向后兼容
    'PublicationExtractor', # 新的统一提取器
    'ISSNExtractor',
    'RankingMatcher',       # 统一接口
    'CCFMatcher',           # 独立的CCF匹配器
    'CASMatcher',           # 独立的中科院匹配器
    'Config'
] 