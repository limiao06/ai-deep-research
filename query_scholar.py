#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.parse
import os
from datetime import datetime

def fetch_papers(query, year_range, sort_by=None, limit=10):
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "year": year_range,
        "limit": limit,
        "fields": "title,authors,year,citationCount,url,abstract,venue,journal"
    }
    if sort_by:
        params["sort"] = sort_by
        
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (OpenClaw-DeepResearch/2.0)'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("data", [])
    except Exception as e:
        print(f"API 请求物理断层: {str(e)}")
        return []

def generate_bibtex_entry(paper, cite_key):
    """确定性代码：将原生 JSON 转换为严格的 BibTeX 格式"""
    title = paper.get("title", "")
    year = paper.get("year", "")
    url = paper.get("url", "")
    
    # 提取并格式化作者组
    authors_list = paper.get("authors", [])
    author_names = " and ".join([a.get("name", "") for a in authors_list]) if authors_list else "Unknown"
    
    # 提取期刊或会议信息
    venue = paper.get("venue", "")
    if not venue and paper.get("journal"):
        venue = paper.get("journal", {}).get("name", "")
        
    bibtex = (
        f"@article{{{cite_key},\n"
        f"  title={{{title}}},\n"
        f"  author={{{author_names}}},\n"
        f"  year={{{year}}},\n"
        f"  journal={{{venue}}},\n"
        f"  url={{{url}}}\n"
        f"}}\n\n"
    )
    return bibtex

def format_paper_output(paper, cite_key):
    """供大模型阅读的降维文本"""
    title = paper.get("title", "未知标题")
    year = paper.get("year", "未知年份")
    citations = paper.get("citationCount", 0)
    url = paper.get("url", "无链接")
    authors_list = paper.get("authors", [])
    authors = ", ".join([a.get("name", "") for a in authors_list[:3]]) + (" et al." if len(authors_list) > 3 else "")
    abstract = paper.get("abstract", "")
    if abstract and len(abstract) > 500:
        abstract = abstract[:500] + "...(截断)"
    elif not abstract:
        abstract = "无摘要可用。"

    return (f"[{cite_key}] {title} ({year})\n"
            f"    - 核心指标: 引用量 {citations} | 第一作者群: {authors}\n"
            f"    - 原理摘要: {abstract}\n"
            f"    - 虫洞链接: {url}\n")

def execute_bipolar_search(topic, session_dir):
    current_year = datetime.now().year
    output_buffer = []
    bibtex_buffer = []
    
    output_buffer.append(f"### Deep Research 知识图谱双极点测绘: [{topic}] ###\n")

    # === 极点 A: 统治级共识 ===
    consensus_years = f"{current_year-5}-{current_year}"
    consensus_papers = fetch_papers(topic, consensus_years, sort_by="citationCount:desc", limit=3)
    
    output_buffer.append("=== 极点 A：统治级共识 (The Consensus Wall) ===")
    output_buffer.append("> 警告大模型：以下是你要击穿的靶子，找出它们共同的隐藏妥协。\n")
    for i, p in enumerate(consensus_papers, 1):
        cite_key = f"A{i}"
        output_buffer.append(format_paper_output(p, cite_key))
        bibtex_buffer.append(generate_bibtex_entry(p, cite_key))

    # === 极点 B: 边缘异类 ===
    anomaly_years = f"{current_year-2}-{current_year}"
    raw_recent_papers = fetch_papers(topic, anomaly_years, limit=20)
    
    anomalies = []
    for p in raw_recent_papers:
        if p.get("citationCount", 0) <= 15 and p.get("abstract"):
            anomalies.append(p)
        if len(anomalies) >= 3:
            break
            
    output_buffer.append("\n=== 极点 B：边缘异类 (The Edge Anomalies) ===")
    output_buffer.append("> 警告大模型：以下是引用量极低的近期文献。严禁盲从，提取其中与共识文献截然不同的『降维打击轴』。\n")
    for i, p in enumerate(anomalies, 1):
        cite_key = f"B{i}"
        output_buffer.append(format_paper_output(p, cite_key))
        bibtex_buffer.append(generate_bibtex_entry(p, cite_key))

    # === 物理持久化 BibTeX ===
    if session_dir and os.path.exists(session_dir):
        bib_path = os.path.join(session_dir, "references.bib")
        with open(bib_path, "w", encoding="utf-8") as f:
            f.writelines(bibtex_buffer)
        output_buffer.append(f"\n[系统日志]: 对应的 BibTeX 文件已硬编码至 {bib_path}")

    return "\n".join(output_buffer)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: 缺乏标量输入。用法: python3 query_scholar.py <Topic> [SessionDir]")
        sys.exit(1)
        
    topic = sys.argv[1]
    # 接收可选的沙盒路径参数
    session_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(execute_bipolar_search(topic, session_dir))
