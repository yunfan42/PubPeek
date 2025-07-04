# PubPeek - 个人学术文献分析工具

[English](README_EN.md) | 中文

PubPeek是一个用于分析学者文献的自动化工具，支持从DBLP导出的BibTeX文件进行期刊和会议分区分析，包括CCF分级和中科院分区匹配。

## 开发动机

📝 因为经常需要在申报、个人介绍以及等等场景下提交学术成果的分类汇总。每次手动整理这些数据都让人头大 🤯，耗时又费力。于是开发了这个小助手，相信很多科研工作者都能感同身受这个痛点。

🎯 无论你是要申请项目、评定奖项、申报基金，还是单纯想要了解其他学者的研究成果（比如开发者实验室里的大师兄就特别热衷于此 😏），PubPeek都能帮你轻松搞定！让繁琐的文献整理工作变得简单又有趣~ ✨

## 功能特点

- **🚀 交互式主程序**: 一键启动，引导式操作，无需复杂命令行参数
- **🔍 一键搜索处理**: 直接搜索DBLP作者，自动下载BibTeX文件并完成文献分析
- **🎯 智能作者匹配**: 显示多个候选作者，支持单位信息和别名辅助选择
- **📊 全面分析**: 同时支持期刊论文和会议论文分析
- **🏆 智能分级**: CCF分级（期刊+会议），中科院分区（仅期刊）
- **🔄 智能去重**: 自动去重，优先保留正式发表版本
- **🎨 多种匹配**: 支持DBLP缩写、ISSN、期刊名称匹配


## 快速开始

> **⚠️ 注意事项**: DBLP的访问经常不太稳定，如果你遇到了请求错误，也不要担心，可以过段时间再试试或者在config中配置你的代理。

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 一键启动（推荐）

**最简单的使用方式**：直接运行交互式主程序

```bash
python run.py
```

然后按照提示：
1. 输入要搜索的作者姓名
2. 从候选列表中选择正确的作者
3. 选择是否立即进行文献分析
4. 查看分析结果

#### 使用流程示例

```bash
$ python run.py

🔍 欢迎使用 PubPeek - 学者文献分析工具
==================================================

==================================================
请输入要搜索的作者姓名（输入 'q' 退出）: 张三

🔍 正在搜索作者: 张三
🌐 使用代理：http://127.0.0.1:33210

🎯 找到以下作者候选项：
================================================================================
1. 另一个张三
   ID: 87654321
   URL: https://dblp.org/pid/yy/yyyy
   别名: 张三别名
   单位: 未知
--------------------------------------------------------------------------------
2. 张三
   ID: 12345678
   URL: https://dblp.org/pid/xx/xxxx
   单位: 某某大学，某某学院，某某城市，某某国家
--------------------------------------------------------------------------------

请输入序号 (1-2) 或输入 'q' 退出: 2

✅ 您选择了: 张三

📋 最终选择的作者信息：
   姓名: 张三
   ID: 12345678
   URL: https://dblp.org/pid/xx/xxxx
   单位: 某某大学，某某学院，某某城市，某某国家

📁 创建作者目录: /path/to/PubPeek/users/Author_Name
📁 创建raw子目录: /path/to/PubPeek/users/Author_Name/raw
📥 正在下载bibtex文件: https://dblp.org/pid/xx/xxxx.bib?param=1
✅ bibtex文件保存成功: /path/to/PubPeek/users/Author_Name/raw/Author_Name_publications.bib
📊 下载了 180 个文献条目

🎉 作者 张三 的设置已完成！
📁 作者目录: /path/to/PubPeek/users/Author_Name
📄 bibtex文件: /path/to/PubPeek/users/Author_Name/raw/Author_Name_publications.bib

🤔 是否要立即进行文献分析处理？(y/n): y

📊 开始处理作者 张三 的文献...
成功加载CCF数据: 644 条记录
成功加载中科院数据: 21772 条记录
1. 解析BibTeX文件...
   解析完成: 180 篇论文
2. 论文去重处理...
   去重前: 180 篇论文
   去重后: 156 篇论文
3. 提取出版物信息...
   找到 45 个期刊，共 89 篇期刊论文
   找到 38 个会议，共 67 篇会议论文
4. 获取DBLP出版物信息...
   ...
5. 匹配出版物分区...
   ...
6. 生成统计摘要...
7. 保存结果和统计分析...

🎉 作者 张三 的文献处理完成！
📊 处理结果已保存到: /path/to/PubPeek/users/Author_Name/processed

==================================================
是否继续搜索其他作者？(y/n): n
👋 感谢使用 PubPeek！
```

### 3. 使用Jupyter Notebook（可选）

```bash
# 启动jupyter notebook
jupyter notebook

# 打开并运行 tests/quick_start.ipynb
```

### 4. 高级命令行使用（可选）

当您已经有BibTeX文件时，可以直接使用处理脚本：

```bash
# 处理单个学者
python scripts/process_scholar.py <user_id> --bib-file path/to/references.bib

# 查看用户状态
python scripts/process_scholar.py <user_id> --status

# 直接处理已有的BibTeX文件（文件已在正确位置）
python scripts/process_scholar.py <user_id>
```

#### 完整使用示例

```bash
# 1. 准备数据 - 将BibTeX文件放入用户目录
mkdir -p users/john_doe/raw
cp /path/to/your/references.bib users/john_doe/raw/

# 2. 处理学者文献（从外部文件）
python scripts/process_scholar.py john_doe --bib-file /path/to/references.bib

# 3. 或者直接处理用户目录中的文件
python scripts/process_scholar.py john_doe --bib-file users/john_doe/raw/references.bib

# 4. 如果BibTeX文件已经在正确位置，可以直接处理
python scripts/process_scholar.py john_doe

# 5. 查看处理状态
python scripts/process_scholar.py john_doe --status

# 6. 查看处理结果
ls -la users/john_doe/processed/
```


#### 常见使用场景

```bash
# 场景1：初次处理学者数据
python scripts/process_scholar.py new_scholar --bib-file downloaded_references.bib

# 场景2：更新已有学者数据
python scripts/process_scholar.py existing_scholar --bib-file updated_references.bib

# 场景3：重新处理已有数据（无需重新复制文件）
python scripts/process_scholar.py existing_scholar

# 场景4：批量处理多个学者
for scholar in scholar1 scholar2 scholar3; do
    python scripts/process_scholar.py $scholar --bib-file "data/${scholar}_references.bib"
done

# 场景5：检查所有用户的处理状态
for user_dir in users/*/; do
    if [ -d "$user_dir" ]; then
        user_id=$(basename "$user_dir")
        echo "=== $user_id ==="
        python scripts/process_scholar.py $user_id --status
        echo
    fi
done
```

## 使用方法

### Python API使用

#### 完整流程示例

```python
from core import Config, BibTexParser, PublicationExtractor, RankingMatcher
from utils import DataProcessor
import pandas as pd

# 1. 初始化组件
config = Config()
bib_parser = BibTexParser()
publication_extractor = PublicationExtractor(config.config)
ranking_matcher = RankingMatcher(
    ccf_file='data/CCF2022-UTF8.csv',
    cas_file='data/FQBJCR2025-UTF8.csv'
)
data_processor = DataProcessor()

# 2. 解析BibTeX文件
df = bib_parser.parse_file('references.bib')

# 3. 论文去重处理
df_deduplicated = data_processor.deduplicate_papers(df, verbose=True)

# 4. 提取期刊和会议信息
valid_papers, publication_counts, publication_types = publication_extractor.extract_unique_publication_abbrs(df_deduplicated)

# 5. 获取DBLP信息
publications_info = publication_extractor.batch_extract_publication_info(
    publication_counts, 
    publication_types,
    cache_file='cache/dblp_cache.json'
)

# 6. 匹配分区
ranking_results = ranking_matcher.batch_match_publications(publications_info)

# 7. 生成统计摘要
detailed_summary = ranking_matcher.generate_detailed_summary(ranking_results, publication_counts)

# 8. 查看结果
print(f"总论文数: {detailed_summary['total_papers']}")
print(f"CCF期刊: A类={detailed_summary['ccf_journal_papers']['A']}篇")
print(f"CCF会议: A类={detailed_summary['ccf_conference_papers']['A']}篇")
print(f"中科院1区期刊: {detailed_summary['cas_papers']['1区']}篇")
```

#### 为论文添加分区信息

```python
# 为每篇论文添加CCF和中科院分区信息
df_with_rankings = data_processor.add_ranking_info_to_papers(df_deduplicated, ranking_results)

# 保存带有分区信息的论文列表
df_with_rankings.to_csv('papers_with_rankings.csv', index=False, encoding='utf-8-sig')
df_with_rankings.to_excel('papers_with_rankings.xlsx', index=False)
```

#### 论文分区统计功能

```python
# 详细统计分析
ranking_stats = data_processor.analyze_paper_rankings(df_with_rankings)

# 简洁摘要报告
summary = data_processor.generate_scholar_summary(df_with_rankings)

# 静默获取摘要数据（不打印）
silent_summary = data_processor.generate_scholar_summary(df_with_rankings, print_summary=False)

# 访问特定统计数据
print(f"CCF-A类+中科院1区论文: {silent_summary['CCF-A类+中科院1区']}篇")
print(f"CCF-A类: {silent_summary['CCF分区']['A类']}篇")
print(f"中科院1区: {silent_summary['中科院分区']['1区']}篇")
```

## 配置文件

创建`config.json`文件来自定义设置：

```json
{
  "network": {
    "timeout": 120,
    "sleep_interval": 3,
    "proxy": {
      "enabled": false,
      "http": "http://127.0.0.1:7890",
      "https": "http://127.0.0.1:7890"
    }
  },
  "data": {
    "ccf_file": "data/CCF2022-UTF8.csv",
    "cas_file": "data/FQBJCR2025-UTF8.csv"
  },
  "paths": {
    "users_dir": "users",
    "data_dir": "data",
    "cache_dir": "cache"
  }
}
```

### 网络代理设置

如果需要通过代理访问DBLP，通常会更快，请设置：

```python
# 方法1：修改配置文件
{
  "network": {
    "proxy": {
      "enabled": true,
      "http": "http://127.0.0.1:7890",
      "https": "http://127.0.0.1:7890"
    }
  }
}

# 方法2：动态设置
config.set('network.proxy.enabled', True)
config.set('network.proxy.http', 'http://127.0.0.1:7890')
```

## 输出文件说明

### 主要输出文件

- `parsed_bibliography.csv/xlsx`: 解析后的完整文献数据
- `papers_with_rankings.csv/xlsx`: 带有分区信息的论文列表
- `ccf_a_cas_1_papers.csv/xlsx`: CCF-A类+中科院1区论文列表
- `ccf_ab_cas_12_papers.csv/xlsx`: CCF-A/B类+中科院1/2区论文列表
- `journal_rankings.xlsx`: 详细的分区匹配结果（包含统计摘要）
- `paper_ranking_report.json`: 详细的论文分区统计报告
- `summary.json`: 机器可读的统计摘要文件

### 结果字段说明

#### 论文分区信息字段
- `CCF_Rank`: CCF分级（A类/B类/C类）
- `CCF_Name`: CCF对应的期刊或会议名称
- `CAS_Zone`: 中科院分区（1区/2区/3区/4区）
- `CAS_Name`: 中科院对应的期刊名称
- `CAS_Top`: 是否为Top期刊（是/否）

#### 统计摘要字段
- `total_papers`: 总论文数
- `ccf_journal_papers`: CCF期刊论文统计
- `ccf_conference_papers`: CCF会议论文统计
- `cas_papers`: 中科院期刊论文统计
- `ccf_a_or_cas_1_count`: CCF-A类或中科院1区论文数量
- `ccf_ab_or_cas_12_count`: CCF-A/B类或中科院1/2区论文数量

## 项目结构

```
PubPeek/
├── core/                    # 核心功能模块
│   ├── bib_parser.py       # BibTeX解析器
│   ├── journal_extractor.py # 出版物信息提取器
│   ├── ccf_matcher.py      # CCF分级匹配器
│   ├── cas_matcher.py      # 中科院分区匹配器
│   ├── ranking_matcher.py  # 统一分区匹配接口
│   └── config.py          # 配置管理
├── data/                   # 数据文件
│   ├── CCF2022-UTF8.csv    # CCF分区数据
│   └── FQBJCR2025-UTF8.csv # 中科院分区数据
├── utils/                  # 工具模块
│   └── data_processor.py   # 数据处理工具
├── tests/                  # 测试和示例
│   ├── quick_start_notebook.ipynb # 快速开始示例
│   └── test_fixes.py       # 功能测试脚本
├── scripts/                # 执行脚本
│   └── process_scholar.py  # 处理单个学者
├── run.py                  # 主入口文件（交互式）
└── users/                  # 用户数据目录
    └── {user_id}/         # 用户目录
        ├── raw/           # 原始数据
        └── processed/     # 处理结果
```

## 主要功能

### 交互式主程序（run.py）

`run.py` 是 PubPeek 的主入口文件，提供了完整的交互式学者文献分析解决方案。主要特性包括：

- **🔍 DBLP作者搜索**: 通过作者姓名搜索DBLP数据库
- **🎯 智能候选匹配**: 显示多个候选作者，支持单位信息和别名
- **📁 自动目录创建**: 自动创建规范的用户目录结构
- **📥 BibTeX下载**: 自动下载作者的完整BibTeX文件
- **📊 一键处理**: 可选择自动进行文献分析处理
- **🌐 灵活配置**: 支持代理设置和自定义配置
- **🔄 批量处理**: 支持连续处理多个作者

### 基本使用方法

```bash
# 启动交互式程序
python run.py

# 然后按照提示操作：
# 1. 输入作者姓名搜索
# 2. 选择正确的作者候选项
# 3. 选择是否立即分析处理
# 4. 查看结果或继续搜索其他作者
```

### 输出说明

程序会创建以下目录结构：
```
users/
└── 作者姓名_清理后/
    ├── raw/
    │   └── 作者姓名_清理后_publications.bib
    └── processed/           # 如果选择了自动处理
        ├── parsed_bibliography.xlsx
        ├── papers_with_rankings.xlsx
        ├── journal_rankings.xlsx
        └── summary.json
```

### 与专业脚本的关系

- **`run.py`**: 新用户友好的交互式主程序
- **`process_scholar.py`**: 专业的批量处理脚本，功能保持不变
- **两者互补**: 可以混合使用，先用主程序搜索下载，再用专业脚本处理

### 错误处理

- 如果搜索失败，会显示错误信息并允许重新搜索
- 如果没有找到匹配的作者，会提示尝试不同的搜索词
- 如果网络连接失败，会显示具体的错误信息
- 可以按 `q` 键随时退出搜索过程
- 可以按 `Ctrl+C` 随时中断程序

## 常见问题

### 1. 如何避免文件复制错误？

如果遇到 `SameFileError` 错误，说明源文件和目标文件是同一个文件：

```bash
# 错误示例：源文件和目标文件相同
python scripts/process_scholar.py default_user --bib-file users/default_user/raw/references.bib

# 正确做法1：直接处理（不指定--bib-file）
python scripts/process_scholar.py default_user

# 正确做法2：使用不同的源文件路径
python scripts/process_scholar.py default_user --bib-file /path/to/external/references.bib
```

### 2. 如何处理代理问题？

如果访问DBLP时遇到网络问题，可以启用代理：

```python
# 常见代理端口
# Clash: http://127.0.0.1:7890
# V2Ray: http://127.0.0.1:10809
# Shadowsocks: http://127.0.0.1:1080
```

### 3. 如何更新分区数据？

定期更新CCF和中科院分区数据文件：
- 替换`data/CCF2022-UTF8.csv`
- 替换`data/FQBJCR2025-UTF8.csv`

### 4. 如何清理缓存？

如需重新获取DBLP信息，删除缓存文件：
```bash
rm cache/dblp_cache.json
```

### 5. 支持哪些论文类型？

- **期刊论文**: 支持CCF分级和中科院分区
- **会议论文**: 支持CCF分级

### 6. 如何跳过去重？

如果不需要去重处理，可以跳过：
```python
# 跳过去重，直接使用原始数据
# df_deduplicated = data_processor.deduplicate_papers(df, verbose=True)
df_deduplicated = df  # 直接使用原始数据
```

## 依赖项

- pandas: 数据处理
- bibtexparser: BibTeX文件解析
- requests: 网络请求
- beautifulsoup4: HTML解析
- openpyxl: Excel文件处理

## 未来工作

目前这个版本已经能基本满足我们日常填报信息的需求。

因为，我们也想看看社区对这种工具的需求，以便我们更好的决策，所以如果你对这个工作感兴趣或者有帮到您缓解填表时候的痛苦，欢迎给我们点个Star。

未来的可能方向（不保证实现）：

### 1. 前端平台
目前是通过python代码来启动，对于不那么熟悉编程的人来说，可能会希望有一个前端页面。

### 2. 更多的领域和分区基准
目前的版本只适合计算机社区，分区基准也只覆盖了CCF和中科院分区（这对我们来说就足够了）。也许其他领域的研究人员也正面临着相同的苦恼。

### 3. 增加Google Scholar 文章和引用
这也是我们一直想要去做的，只是由于Google Scholar 没有提供官方的API，也无法一键下载用户所有的著作。当然我们也注意到SerpAPI这样付费订阅的第三方工具。但是，这仍然需要不少的工作量，我们先将这个列为Todo吧！

## 许可证

本项目采用MIT许可证。

## 致谢

本项目中使用的CCF和中科院分区资料来自于 [https://github.com/hitfyd/ShowJCR](https://github.com/hitfyd/ShowJCR)，特此感谢。
