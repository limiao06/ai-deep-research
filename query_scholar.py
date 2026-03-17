#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

def fetch_papers(query, year_range, sort_by=None, limit=10):
    """底层请求器：严格控制请求头与参数"""
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "year": year_range,
        "limit": limit,
        "fields": "title,authors,year,citationCount,url,abstract"
    }
    if sort_by:
        params["sort"] = sort_by
        
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (OpenClaw-DeepResearch/1.0)'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("data", [])
    except Exception as e:
        print(f"API 请求物理断层: {str(e)}")
        return []

def format_paper_output(paper, index):
    """结构化信息降维输出"""
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

    return (f"[{index}] {title} ({year})\n"
            f"    - 核心指标: 引用量 {citations} | 第一作者群: {authors}\n"
            f"    - 原理摘要: {abstract}\n"
            f"    - 虫洞链接: {url}\n")

def execute_bipolar_search(topic):
    current_year = datetime.now().year
    output_buffer = []
    
    output_buffer.append(f"### Deep Research 知识图谱双极点测绘: [{topic}] ###\n")

    # ==========================================
    # 极点 A: 寻找“靶子” (统治级共识)
    # 逻辑: 过去 5 年内，被整个学术界奉为圭臬的高被引论文，它们代表了当前的物理/算力墙。
    # ==========================================
    consensus_years = f"{current_year-5}-{current_year}"
    consensus_papers = fetch_papers(topic, consensus_years, sort_by="citationCount:desc", limit=3)
    
    output_buffer.append("=== 极点 A：统治级共识 (The Consensus Wall) ===")
    output_buffer.append("> 警告大模型：以下是你要击穿的靶子，找出它们共同的隐藏妥协。\n")
    if not consensus_papers:
        output_buffer.append("未探测到高被引共识。该领域可能极度早期或查询词过于狭窄。\n")
    else:
        for i, p in enumerate(consensus_papers, 1):
            output_buffer.append(format_paper_output(p, f"A{i}"))

    # ==========================================
    # 极点 B: 寻找“异类” (边缘破局点)
    # 逻辑: 过去 2 年内发表，Semantic Scholar 认为语义高度相关（默认相关性排序），但引用量极低（< 15 次）。
    # 这些大概率是无人问津的垃圾，但也可能是刚刚引入新跨学科变量的微光。
    # ==========================================
    anomaly_years = f"{current_year-2}-{current_year}"
    # 扩大获取基数，利用本地算力进行条件过滤
    raw_recent_papers = fetch_papers(topic, anomaly_years, limit=20)
    
    anomalies = []
    for p in raw_recent_papers:
        # 排除掉已经被发现的明星论文，只找处于“学术盲区”的文献
        if p.get("citationCount", 0) <= 15 and p.get("abstract"):
            anomalies.append(p)
        if len(anomalies) >= 3:
            break
            
    output_buffer.append("\n=== 极点 B：边缘异类 (The Edge Anomalies) ===")
    output_buffer.append("> 警告大模型：以下是引用量极低的近期文献。严禁盲从，提取其中与共识文献截然不同的『降维打击轴』或『跨学科变量』。\n")
    if not anomalies:
        output_buffer.append("未探测到符合条件的边缘异类。\n")
    else:
        for i, p in enumerate(anomalies, 1):
            output_buffer.append(format_paper_output(p, f"B{i}"))

    return "\n".join(output_buffer)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: 缺乏标量输入。用法: python3 query_scholar.py <Topic>")
        sys.exit(1)
        
    topic = sys.argv[1]
    print(execute_bipolar_search(topic))
