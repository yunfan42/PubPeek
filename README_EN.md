# PubPeek - Scholar Literature Analysis Tool

English | [中文](README.md)

PubPeek is an automated tool for analyzing scholarly literature that supports journal and conference ranking analysis from BibTeX files exported from DBLP, including CCF rankings and Chinese Academy of Sciences (CAS) zone matching.

## Development Motivation

Because we often need to submit categorized and summarized academic achievements in various projects, award applications, or introductions, having experienced several rounds of manual processing that was time-consuming and laborious, we developed this small tool. Many academic workers probably face the same difficulties.

Whether for project applications, award submissions, funding applications, or other scenarios, PubPeek can help you. Perhaps you want to use this tool to background check other researchers - that's certainly possible too. (The senior student in the author's lab is very enthusiastic about this 🤔)

## Features

- **🚀 Interactive Main Program**: One-click startup with guided operations, no complex command line parameters needed
- **🔍 One-click Search & Processing**: Directly search DBLP authors, automatically download BibTeX files and complete literature analysis
- **🎯 Intelligent Author Matching**: Display multiple author candidates with institutional information and aliases to assist selection
- **📊 Comprehensive Analysis**: Support for both journal and conference paper analysis
- **🏆 Intelligent Ranking**: CCF rankings (journals + conferences), CAS zones (journals only)
- **🔄 Smart Deduplication**: Automatic deduplication, prioritizing official publication versions
- **🎨 Multiple Matching**: Support for DBLP abbreviations, ISSN, and journal name matching

## Quick Start

> **⚠️ Note**: DBLP access is often unstable. If you encounter request errors, don't worry - try again later or configure a proxy in the config.

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. One-click Launch (Recommended)

**The simplest way to use**: Run the interactive main program directly

```bash
python run.py
```

Then follow the prompts:
1. Enter the author name to search
2. Select the correct author from the candidate list
3. Choose whether to perform literature analysis immediately
4. View analysis results

#### Usage Flow Example

```bash
$ python run.py

🔍 Welcome to PubPeek - Scholar Literature Analysis Tool
==================================================

==================================================
Please enter the author name to search (type 'q' to quit): John Smith

🔍 Searching for author: John Smith
🌐 Using proxy: http://127.0.0.1:33210

🎯 Found the following author candidates:
================================================================================
1. Another John Smith
   ID: 87654321
   URL: https://dblp.org/pid/yy/yyyy
   Aliases: John Smith Alias
   Affiliation: Unknown
--------------------------------------------------------------------------------
2. John Smith
   ID: 12345678
   URL: https://dblp.org/pid/xx/xxxx
   Affiliation: University Name, College Name, City, Country
--------------------------------------------------------------------------------

Please enter a number (1-2) or type 'q' to quit: 2

✅ You selected: John Smith

📋 Final selected author information:
   Name: John Smith
   ID: 12345678
   URL: https://dblp.org/pid/xx/xxxx
   Affiliation: University Name, College Name, City, Country

📁 Creating author directory: /path/to/PubPeek/users/Author_Name
📁 Creating raw subdirectory: /path/to/PubPeek/users/Author_Name/raw
📥 Downloading bibtex file: https://dblp.org/pid/xx/xxxx.bib?param=1
✅ Bibtex file saved successfully: /path/to/PubPeek/users/Author_Name/raw/Author_Name_publications.bib
📊 Downloaded 180 literature entries

🎉 Setup for author John Smith completed!
📁 Author directory: /path/to/PubPeek/users/Author_Name
📄 Bibtex file: /path/to/PubPeek/users/Author_Name/raw/Author_Name_publications.bib

🤔 Would you like to perform literature analysis immediately? (y/n): y

📊 Starting literature processing for author John Smith...
Successfully loaded CCF data: 644 records
Successfully loaded CAS data: 21772 records
1. Parsing BibTeX file...
   Parsing completed: 180 papers
2. Paper deduplication processing...
   Before deduplication: 180 papers
   After deduplication: 156 papers
3. Extracting publication information...
   Found 45 journals with 89 journal papers
   Found 38 conferences with 67 conference papers
4. Retrieving DBLP publication information...
   ...
5. Matching publication rankings...
   ...
6. Generating statistical summary...
7. Saving results and statistical analysis...

🎉 Literature processing for author John Smith completed!
📊 Processing results saved to: /path/to/PubPeek/users/Author_Name/processed

==================================================
Would you like to continue searching for other authors? (y/n): n
👋 Thank you for using PubPeek!
```

### 3. Using Jupyter Notebook (Optional)

```bash
# Launch jupyter notebook
jupyter notebook

# Open and run tests/quick_start.ipynb
```

### 4. Advanced Command Line Usage (Optional)

When you already have BibTeX files, you can use the processing script directly:

```bash
# Process a single scholar
python scripts/process_scholar.py <user_id> --bib-file path/to/references.bib

# Check user status
python scripts/process_scholar.py <user_id> --status

# Process existing BibTeX file directly (file already in correct location)
python scripts/process_scholar.py <user_id>
```

#### Complete Usage Example

```bash
# 1. Prepare data - Place BibTeX file in user directory
mkdir -p users/john_doe/raw
cp /path/to/your/references.bib users/john_doe/raw/

# 2. Process scholar literature (from external file)
python scripts/process_scholar.py john_doe --bib-file /path/to/references.bib

# 3. Or directly process file in user directory
python scripts/process_scholar.py john_doe --bib-file users/john_doe/raw/references.bib

# 4. If BibTeX file is already in correct location, process directly
python scripts/process_scholar.py john_doe

# 5. Check processing status
python scripts/process_scholar.py john_doe --status

# 6. View processing results
ls -la users/john_doe/processed/
```

#### Common Usage Scenarios

```bash
# Scenario 1: First-time processing of scholar data
python scripts/process_scholar.py new_scholar --bib-file downloaded_references.bib

# Scenario 2: Update existing scholar data
python scripts/process_scholar.py existing_scholar --bib-file updated_references.bib

# Scenario 3: Reprocess existing data (no need to copy files again)
python scripts/process_scholar.py existing_scholar

# Scenario 4: Batch process multiple scholars
for scholar in scholar1 scholar2 scholar3; do
    python scripts/process_scholar.py $scholar --bib-file "data/${scholar}_references.bib"
done

# Scenario 5: Check processing status for all users
for user_dir in users/*/; do
    if [ -d "$user_dir" ]; then
        user_id=$(basename "$user_dir")
        echo "=== $user_id ==="
        python scripts/process_scholar.py $user_id --status
        echo
    fi
done
```

## Usage

### Python API Usage

#### Complete Workflow Example

```python
from core import Config, BibTexParser, PublicationExtractor, RankingMatcher
from utils import DataProcessor
import pandas as pd

# 1. Initialize components
config = Config()
bib_parser = BibTexParser()
publication_extractor = PublicationExtractor(config.config)
ranking_matcher = RankingMatcher(
    ccf_file='data/CCF2022-UTF8.csv',
    cas_file='data/FQBJCR2025-UTF8.csv'
)
data_processor = DataProcessor()

# 2. Parse BibTeX file
df = bib_parser.parse_file('references.bib')

# 3. Paper deduplication processing
df_deduplicated = data_processor.deduplicate_papers(df, verbose=True)

# 4. Extract journal and conference information
valid_papers, publication_counts, publication_types = publication_extractor.extract_unique_publication_abbrs(df_deduplicated)

# 5. Get DBLP information
publications_info = publication_extractor.batch_extract_publication_info(
    publication_counts, 
    publication_types,
    cache_file='cache/dblp_cache.json'
)

# 6. Match rankings
ranking_results = ranking_matcher.batch_match_publications(publications_info)

# 7. Generate statistical summary
detailed_summary = ranking_matcher.generate_detailed_summary(ranking_results, publication_counts)

# 8. View results
print(f"Total papers: {detailed_summary['total_papers']}")
print(f"CCF journals: Class A={detailed_summary['ccf_journal_papers']['A']} papers")
print(f"CCF conferences: Class A={detailed_summary['ccf_conference_papers']['A']} papers")
print(f"CAS Zone 1 journals: {detailed_summary['cas_papers']['1区']} papers")
```

#### Adding Ranking Information to Papers

```python
# Add CCF and CAS ranking information to each paper
df_with_rankings = data_processor.add_ranking_info_to_papers(df_deduplicated, ranking_results)

# Save paper list with ranking information
df_with_rankings.to_csv('papers_with_rankings.csv', index=False, encoding='utf-8-sig')
df_with_rankings.to_excel('papers_with_rankings.xlsx', index=False)
```

#### Paper Ranking Statistics

```python
# Detailed statistical analysis
ranking_stats = data_processor.analyze_paper_rankings(df_with_rankings)

# Concise summary report
summary = data_processor.generate_scholar_summary(df_with_rankings)

# Silent summary data acquisition (no printing)
silent_summary = data_processor.generate_scholar_summary(df_with_rankings, print_summary=False)

# Access specific statistical data
print(f"CCF Class A + CAS Zone 1 papers: {silent_summary['CCF-A类+中科院1区']} papers")
print(f"CCF Class A: {silent_summary['CCF分区']['A类']} papers")
print(f"CAS Zone 1: {silent_summary['中科院分区']['1区']} papers")
```

#### Year-based Filtering Analysis

Support for filtering papers by year range for analysis, commonly used to evaluate scholars' academic performance in different periods:

```python
# 1. Recent 3 years analysis
stats_recent = data_processor.analyze_paper_rankings(df_with_rankings, years_filter=3)

# 2. Recent 5 years analysis
stats_mid = data_processor.analyze_paper_rankings(df_with_rankings, years_filter=5)

# 3. Custom year range analysis
stats_custom = data_processor.analyze_paper_rankings(df_with_rankings, years_filter=(2020, 2023))

# 4. Comparative analysis example
print(f"Overall: {stats_all['total_papers']} papers, {stats_all['ccf_a_or_cas_1_ratio']:.1f}% high-quality")
print(f"Recent 3 years: {stats_recent['total_papers']} papers, {stats_recent['ccf_a_or_cas_1_ratio']:.1f}% high-quality")

# 5. Trend analysis
current_year = 2025
for years in [3, 5, 10]:
    stats = data_processor.analyze_paper_rankings(df_with_rankings, 
                                                  verbose=False, 
                                                  years_filter=years)
    print(f"Past {years} years: {stats['total_papers']} papers, "
          f"CCF-A {stats['ccf_a_count']} papers, "
          f"CAS Zone 1 {stats['cas_1_count']} papers")
```

**Year Filter Parameters:**
- `years_filter=None`: No filtering, analyze all years (default)
- `years_filter=3`: Past 3 years (commonly used for recent performance evaluation)
- `years_filter=5`: Past 5 years (commonly used for mid-term performance evaluation)
- `years_filter=(2020, 2023)`: Custom year range



## Configuration File

Create a `config.json` file to customize settings:

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

### Network Proxy Settings

If you need to access DBLP through a proxy (usually faster), please configure:

```python
# Method 1: Modify configuration file
{
  "network": {
    "proxy": {
      "enabled": true,
      "http": "http://127.0.0.1:7890",
      "https": "http://127.0.0.1:7890"
    }
  }
}

# Method 2: Dynamic setting
config.set('network.proxy.enabled', True)
config.set('network.proxy.http', 'http://127.0.0.1:7890')
```

## Output Files Description

### Main Output Files

- `parsed_bibliography.csv/xlsx`: Complete parsed literature data
- `papers_with_rankings.csv/xlsx`: Paper list with ranking information
- `ccf_a_cas_1_papers.csv/xlsx`: CCF Class A + CAS Zone 1 papers list
- `ccf_ab_cas_12_papers.csv/xlsx`: CCF Class A/B + CAS Zone 1/2 papers list
- `journal_rankings.xlsx`: Detailed ranking match results (including statistical summary)
- `paper_ranking_report.json`: Detailed paper ranking statistics report
- `summary.json`: Machine-readable statistical summary file

### Field Descriptions

#### Paper Ranking Information Fields
- `CCF_Rank`: CCF ranking (Class A/B/C)
- `CCF_Name`: CCF corresponding journal or conference name
- `CAS_Zone`: CAS zone (Zone 1/2/3/4)
- `CAS_Name`: CAS corresponding journal name
- `CAS_Top`: Whether it's a Top journal (Yes/No)

#### Statistical Summary Fields
- `total_papers`: Total number of papers
- `ccf_journal_papers`: CCF journal paper statistics
- `ccf_conference_papers`: CCF conference paper statistics
- `cas_papers`: CAS journal paper statistics
- `ccf_a_or_cas_1_count`: CCF Class A or CAS Zone 1 paper count
- `ccf_ab_or_cas_12_count`: CCF Class A/B or CAS Zone 1/2 paper count

## Project Structure

```
PubPeek/
├── core/                    # Core function modules
│   ├── bib_parser.py       # BibTeX parser
│   ├── journal_extractor.py # Publication information extractor
│   ├── ccf_matcher.py      # CCF ranking matcher
│   ├── cas_matcher.py      # CAS zone matcher
│   ├── ranking_matcher.py  # Unified ranking match interface
│   └── config.py          # Configuration management
├── data/                   # Data files
│   ├── CCF2022-UTF8.csv    # CCF ranking data
│   └── FQBJCR2025-UTF8.csv # CAS zone data
├── utils/                  # Utility modules
│   └── data_processor.py   # Data processing tools
├── tests/                  # Tests and examples
│   ├── quick_start_notebook.ipynb # Quick start example
│   └── test_fixes.py       # Function test script
├── scripts/                # Execution scripts
│   └── process_scholar.py  # Process single scholar
├── run.py                  # Main entry file (interactive)
└── users/                  # User data directory
    └── {user_id}/         # User directory
        ├── raw/           # Raw data
        └── processed/     # Processing results
```

### Output Description

The program will create the following directory structure:
```
users/
└── Author_Name_Cleaned/
    ├── raw/
    │   └── Author_Name_Cleaned_publications.bib
    └── processed/           # If automatic processing was selected
        ├── parsed_bibliography.xlsx
        ├── papers_with_rankings.xlsx
        ├── journal_rankings.xlsx
        └── summary.json
```

### Relationship with Professional Scripts

- **`run.py`**: User-friendly interactive main program for new users
- **`process_scholar.py`**: Professional batch processing script, functionality remains unchanged
- **Complementary**: Can be used together - first use main program to search and download, then use professional script for processing

### Error Handling

- If search fails, error messages will be displayed and allow retry
- If no matching authors are found, suggests trying different search terms
- If network connection fails, displays specific error information
- Press `q` to exit the search process at any time
- Press `Ctrl+C` to interrupt the program at any time

## Frequently Asked Questions

### 1. How to avoid file copy errors?

If you encounter a `SameFileError`, it means the source and target files are the same:

```bash
# Wrong example: source and target files are the same
python scripts/process_scholar.py default_user --bib-file users/default_user/raw/references.bib

# Correct approach 1: Process directly (without --bib-file)
python scripts/process_scholar.py default_user

# Correct approach 2: Use different source file path
python scripts/process_scholar.py default_user --bib-file /path/to/external/references.bib
```

### 2. How to handle proxy issues?

If you encounter network issues when accessing DBLP, you can enable proxy:

```python
# Common proxy ports
# Clash: http://127.0.0.1:7890
# V2Ray: http://127.0.0.1:10809
# Shadowsocks: http://127.0.0.1:1080
```

### 3. How to update ranking data?

Regularly update CCF and CAS ranking data files:
- Replace `data/CCF2022-UTF8.csv`
- Replace `data/FQBJCR2025-UTF8.csv`

### 4. How to clear cache?

To re-fetch DBLP information, delete the cache file:
```bash
rm cache/dblp_cache.json
```

### 5. What paper types are supported?

- **Journal Papers**: Support CCF rankings and CAS zones
- **Conference Papers**: Support CCF rankings

### 6. How to skip deduplication?

If deduplication is not needed, you can skip it:
```python
# Skip deduplication, use original data directly
# df_deduplicated = data_processor.deduplicate_papers(df, verbose=True)
df_deduplicated = df  # Use original data directly
```

## Dependencies

- pandas: Data processing
- bibtexparser: BibTeX file parsing
- requests: Network requests
- beautifulsoup4: HTML parsing
- openpyxl: Excel file processing

## Future Work

This current version can basically meet our daily reporting needs.

Since we also want to see the community's demand for such tools to help us make better decisions, if you're interested in this work or it has helped alleviate your pain when filling out forms, please give us a Star.

Possible future directions:

### 1. Frontend Platform
Currently launched through Python code, which may be challenging for people less familiar with programming who might prefer a web interface.

### 2. More Domains and Ranking Standards
The current version only suits the computer science community, and the ranking standards only cover CCF and CAS zones (which is sufficient for us). Perhaps researchers in other fields are facing the same difficulties.

### 3. Adding Google Scholar Articles and Citations
This is something we've always wanted to do, but since Google Scholar doesn't provide an official API and doesn't support one-click download of all user publications, it remains challenging. Of course, we've also noticed paid third-party tools like SerpAPI. However, this still requires considerable work, so we'll list it as a Todo for now!

## License

This project is licensed under the MIT License.

## Acknowledgments

The CCF and CAS ranking data used in this project are sourced from [https://github.com/hitfyd/ShowJCR](https://github.com/hitfyd/ShowJCR). We sincerely appreciate their contribution.