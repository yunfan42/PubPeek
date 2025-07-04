#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PubPeek - 学者文献分析工具
交互式入口脚本
"""

import os
import sys
import requests
import json
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.process_scholar import ScholarProcessor


class PubPeekApp:
    """PubPeek应用程序主类"""
    
    def __init__(self):
        """初始化应用程序"""
        self.config = self.load_config()
        print("\n✨ 欢迎使用 PubPeek - 个人学术论文统计工具 ✨")
        print("📚 基于 DBLP 数据库")
        print("🏆 支持 2022 CCF 推荐目录")
        print("🌟 支持 2025 中科院分区")
        print("=" * 50)
    
    def load_config(self):
        """加载配置文件"""
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  配置文件未找到，使用默认设置")
            return {}
    
    def search_author(self, author_name):
        """搜索作者"""
        # dblp author 搜索 API 的基础 URL
        base_url = "https://dblp.org/search/author/api"
        
        # 设置查询参数
        params = {
            "q": author_name,  # 查询的作者名称
            "format": "json",  # 返回结果的格式为 JSON
            "h": 10,          # 最多返回 10 个结果
            "f": 0             # 从第 0 个结果开始
        }
        
        # 根据配置决定是否使用代理
        proxies = None
        if self.config.get('network', {}).get('proxy', {}).get('enabled', False):
            proxy_http = self.config['network']['proxy']['http']
            proxy_https = self.config['network']['proxy']['https']
            proxies = {
                'http': proxy_http,
                'https': proxy_https
            }
            print(f"🌐 使用代理：{proxy_http}")
        
        try:
            # 发送 GET 请求
            response = requests.get(base_url, params=params, proxies=proxies)
            
            # 检查请求是否成功
            if response.status_code == 200:
                # 解析返回的 JSON 数据
                data = response.json()
                return data
            else:
                print(f"❌ 请求失败，状态码：{response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 搜索时发生网络错误: {e}")
            return None
    
    def parse_authors(self, result):
        """解析作者信息并创建候选项"""
        if not result or 'result' not in result:
            return []
        
        authors = []
        hits = result['result'].get('hits', {})
        
        if 'hit' in hits:
            hit_list = hits['hit']
            # 如果只有一个结果，hit可能不是list
            if not isinstance(hit_list, list):
                hit_list = [hit_list]
            
            for hit in hit_list:
                info = hit.get('info', {})
                author_name = info.get('author', '未知')
                author_id = hit.get('@id', '未知')
                dblp_url = info.get('url', '未知')
                
                # 提取单位信息
                affiliations = []
                notes = info.get('notes', {})
                if 'note' in notes:
                    note_list = notes['note']
                    if not isinstance(note_list, list):
                        note_list = [note_list]
                    
                    for note in note_list:
                        if note.get('@type') == 'affiliation':
                            affiliations.append(note.get('text', ''))
                
                # 提取别名
                aliases = []
                if 'aliases' in info:
                    alias_info = info['aliases']
                    if 'alias' in alias_info:
                        alias_list = alias_info['alias']
                        if not isinstance(alias_list, list):
                            alias_list = [alias_list]
                        aliases = alias_list
                
                authors.append({
                    'name': author_name,
                    'id': author_id,
                    'url': dblp_url,
                    'affiliations': affiliations,
                    'aliases': aliases
                })
        
        return authors
    
    def display_and_select_author(self, authors):
        """显示候选项并让用户选择"""
        if not authors:
            print("❌ 没有找到任何作者信息")
            return None
        
        print(f"\n🎯 找到以下作者候选项：")
        print("=" * 80)
        
        for i, author in enumerate(authors, 1):
            print(f"{i}. {author['name']}")
            print(f"   ID: {author['id']}")
            print(f"   URL: {author['url']}")
            
            if author['aliases']:
                print(f"   别名: {', '.join(author['aliases'])}")
            
            if author['affiliations']:
                print(f"   单位: {'; '.join(author['affiliations'])}")
            else:
                print(f"   单位: 未知")
            
            print("-" * 80)
        
        # 让用户选择
        while True:
            try:
                choice = input(f"\n请输入序号 (1-{len(authors)}) 或输入 'q' 退出: ").strip()
                if choice.lower() == 'q':
                    return None
                
                if not choice:
                    print("⚠️  请输入有效的序号")
                    continue
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(authors):
                    selected_author = authors[choice_num - 1]
                    print(f"\n✅ 您选择了: {selected_author['name']}")
                    return selected_author
                else:
                    print(f"⚠️  请输入有效的序号 (1-{len(authors)})")
            except ValueError:
                print("⚠️  请输入有效的数字")
    
    def create_author_directories(self, author_name):
        """创建作者文件夹和raw子文件夹"""
        # 清理作者姓名，替换空格为下划线，移除特殊字符
        clean_name = author_name.replace(' ', '_').replace('-', '_')
        # 移除可能导致文件系统问题的字符
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c in ('_', '.'))
        
        # 获取项目根目录
        root_dir = os.path.dirname(os.path.abspath(__file__))
        users_dir = os.path.join(root_dir, 'users')
        author_dir = os.path.join(users_dir, clean_name)
        raw_dir = os.path.join(author_dir, 'raw')
        
        # 创建目录
        try:
            os.makedirs(raw_dir, exist_ok=True)
            print(f"📁 创建作者目录: {author_dir}")
            print(f"📁 创建raw子目录: {raw_dir}")
            return clean_name, author_dir, raw_dir
        except Exception as e:
            print(f"❌ 创建目录失败: {e}")
            return None, None, None
    
    def download_bibtex(self, author_url, raw_dir, author_name):
        """下载bibtex文件，带重试机制"""
        # 构造bibtex下载URL
        bibtex_url = author_url + ".bib?param=1"
        
        # 根据配置决定是否使用代理
        proxies = None
        if self.config.get('network', {}).get('proxy', {}).get('enabled', False):
            proxy_http = self.config['network']['proxy']['http']
            proxy_https = self.config['network']['proxy']['https']
            proxies = {
                'http': proxy_http,
                'https': proxy_https
            }
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/plain,application/x-bibtex,*/*',
            'Accept-Language': 'en-US,en;q=0.9,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 创建session并配置重试策略
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 手动重试次数
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"🔄 第 {attempt + 1} 次尝试下载...")
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    print(f"📥 正在下载bibtex文件: {bibtex_url}")
                
                # 发送GET请求下载bibtex，设置较长超时，使用流式下载
                response = session.get(
                    bibtex_url, 
                    proxies=proxies, 
                    timeout=(30, 600),  # (连接超时, 读取超时)
                    stream=True,
                    headers=headers,
                    verify=True  # 启用SSL验证
                )
                
                if response.status_code == 200:
                    # 获取文件大小
                    total_size = response.headers.get('content-length')
                    if total_size:
                        total_size = int(total_size)
                        print(f"📊 文件大小: {total_size / 1024:.1f} KB")
                    else:
                        print("📊 文件大小: 未知")
                    
                    # 保存bibtex文件
                    clean_name = author_name.replace(' ', '_').replace('-', '_')
                    clean_name = ''.join(c for c in clean_name if c.isalnum() or c in ('_', '.'))
                    
                    bibtex_filename = f"{clean_name}_publications.bib"
                    bibtex_path = os.path.join(raw_dir, bibtex_filename)
                    
                    downloaded_size = 0
                    content_parts = []
                    
                    # 显示下载进度
                    print("📥 下载进度: ", end="", flush=True)
                    
                    try:
                        # 分块下载并显示进度
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                content_parts.append(chunk)
                                downloaded_size += len(chunk)
                                
                                # 显示进度条
                                if total_size:
                                    progress = (downloaded_size / total_size) * 100
                                    bar_length = 30
                                    filled_length = int(bar_length * downloaded_size // total_size)
                                    bar = '█' * filled_length + '-' * (bar_length - filled_length)
                                    print(f"\r📥 下载进度: [{bar}] {progress:.1f}% ({downloaded_size / 1024:.1f} KB)", end="", flush=True)
                                else:
                                    # 如果不知道总大小，只显示已下载的大小
                                    print(f"\r📥 下载进度: {downloaded_size / 1024:.1f} KB", end="", flush=True)
                        
                        print()  # 换行
                        
                        # 将所有内容写入文件
                        content = b''.join(content_parts).decode('utf-8')
                        with open(bibtex_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"✅ bibtex文件保存成功: {bibtex_path}")
                        
                        # 简单统计下载的条目数量
                        bib_entries = content.count('@')
                        print(f"📊 下载了 {bib_entries} 个文献条目")
                        
                        return bibtex_path
                        
                    except Exception as chunk_error:
                        print(f"\n⚠️  下载过程中出现错误: {chunk_error}")
                        if attempt < max_retries - 1:
                            continue
                        else:
                            raise chunk_error
                
                else:
                    print(f"❌ 下载失败，状态码: {response.status_code}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return None
                        
            except requests.exceptions.SSLError as ssl_error:
                print(f"🔒 SSL连接错误: {ssl_error}")
                if attempt < max_retries - 1:
                    print("💡 尝试解决SSL问题...")
                    continue
                else:
                    print("❌ SSL连接失败，请检查网络设置或尝试使用代理")
                    return None
                    
            except requests.exceptions.ConnectionError as conn_error:
                print(f"🌐 网络连接错误: {conn_error}")
                if attempt < max_retries - 1:
                    print("💡 网络连接不稳定，稍后重试...")
                    continue
                else:
                    print("❌ 网络连接失败，请检查网络连接")
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"⏰ 下载超时")
                if attempt < max_retries - 1:
                    print("💡 超时重试...")
                    continue
                else:
                    print("❌ 多次超时，请检查网络连接")
                    return None
                    
            except Exception as e:
                print(f"❌ 下载bibtex文件时发生错误: {e}")
                if attempt < max_retries - 1:
                    print("💡 发生未知错误，尝试重试...")
                    continue
                else:
                    print("❌ 多次尝试失败")
                    return None
        
        return None
    
    def ask_process_choice(self):
        """询问用户是否要进行文献处理"""
        while True:
            choice = input("\n🤔 是否要立即进行文献分析处理？(y/n): ").strip().lower()
            if choice in ['y', 'yes', '是', '要']:
                return True
            elif choice in ['n', 'no', '否', '不']:
                return False
            else:
                print("⚠️  请输入 'y' 或 'n'")
    
    def run(self):
        """运行主程序"""
        try:
            while True:
                print("\n" + "=" * 50)
                # 获取作者姓名
                author_name = input("请输入要搜索的作者姓名（输入 'q' 退出）: ").strip()
                
                if author_name.lower() == 'q':
                    print("👋 感谢使用 PubPeek！")
                    break
                
                if not author_name:
                    print("⚠️  作者姓名不能为空，请重新输入")
                    continue
                
                print(f"\n🔍 正在搜索作者: {author_name}")
                
                # 1. 搜索作者
                result = self.search_author(author_name)
                
                if not result:
                    print("❌ 搜索失败，请检查网络连接或稍后重试")
                    continue
                
                # 2. 解析作者信息
                authors = self.parse_authors(result)
                
                if not authors:
                    print("❌ 未找到相关作者信息，请尝试不同的搜索词")
                    continue
                
                # 限制最多10个候选项
                authors = authors[:10]
                
                # 3. 让用户选择
                selected_author = self.display_and_select_author(authors)
                
                if not selected_author:
                    print("❌ 未选择作者，返回搜索")
                    continue
                
                print(f"\n📋 最终选择的作者信息：")
                print(f"   姓名: {selected_author['name']}")
                print(f"   ID: {selected_author['id']}")
                print(f"   URL: {selected_author['url']}")
                if selected_author['affiliations']:
                    print(f"   单位: {'; '.join(selected_author['affiliations'])}")
                
                # 4. 创建作者文件夹和raw子文件夹
                user_id, author_dir, raw_dir = self.create_author_directories(selected_author['name'])
                
                if not user_id or not author_dir or not raw_dir:
                    print("❌ 创建作者目录失败")
                    continue
                
                # 5. 下载bibtex文件
                bibtex_path = self.download_bibtex(selected_author['url'], raw_dir, selected_author['name'])
                
                if not bibtex_path:
                    print("❌ bibtex文件下载失败")
                    continue
                
                print("\n" + "=" * 60)
                print("✅ 作者数据准备完成")
                print("=" * 60)
                print(f"🎉 作者 {selected_author['name']} 的设置已完成！")
                print(f"📁 作者目录: {author_dir}")
                print(f"📄 bibtex文件: {bibtex_path}")
                
                # 统计文献条目数量
                try:
                    with open(bibtex_path, 'r', encoding='utf-8') as f:
                        bib_content = f.read()
                        entry_count = bib_content.count('@')
                        print(f"📊 文献条目数量: {entry_count} 条")
                except:
                    print(f"📊 文献条目数量: 未知")
                
                # 6. 询问是否进行文献处理
                should_process = self.ask_process_choice()
                
                if should_process:
                    print("\n" + "=" * 60)
                    print("🚀 开始文献分析处理")
                    print("=" * 60)
                    print(f"📊 正在处理作者 {selected_author['name']} 的文献...")
                    
                    # 创建学者处理器
                    processor = ScholarProcessor(user_id)
                    
                    # 处理文献
                    results = processor.process_bibliography(bibtex_path)
                    
                    print("\n" + "=" * 60)
                    if results:
                        print("🎉 文献分析处理完成")
                        print("=" * 60)
                        print(f"✅ 作者 {selected_author['name']} 的文献处理成功！")
                        print(f"📊 处理结果已保存到: {processor.paths['processed_dir']}")
                        print(f"📋 可查看生成的Excel和JSON报告文件")
                        
                        # 显示详细的分区统计
                        print("\n" + "=" * 60)
                        print("📈 详细分区统计报告")
                        print("=" * 60)
                        if 'ranking_stats' in results:
                            ranking_stats = results['ranking_stats']
                            processor.report_generator.print_detailed_paper_statistics(ranking_stats)
                        else:
                            print("⚠️  详细统计数据不可用")
                    else:
                        print("❌ 文献分析处理失败")
                        print("=" * 60)
                        print(f"💔 作者 {selected_author['name']} 的文献处理失败")
                        print(f"请检查BibTeX文件格式或网络连接")
                else:
                    print(f"\n📝 您可以稍后使用以下命令进行文献处理：")
                    print(f"   python scripts/process_scholar.py {user_id}")
                
                # 询问是否继续
                print("\n" + "=" * 50)
                continue_choice = input("是否继续搜索其他作者？(y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes', '是', '要']:
                    print("👋 感谢使用 PubPeek！")
                    break
        
        except KeyboardInterrupt:
            print(f"\n\n👋 用户中断操作，感谢使用 PubPeek！")
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            print("请检查网络连接或稍后重试")


def main():
    """主函数"""
    app = PubPeekApp()
    app.run()


if __name__ == '__main__':
    main() 