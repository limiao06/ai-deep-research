#!/usr/bin/env python3
import sys
import os
import time
import requests

# ==========================================
# 物理硬编码区：请填入你在第一阶段获取的凭证
# ==========================================
APP_ID = "cli_a933b3ea67395bc8"
APP_SECRET = "HiAKJSngXpL1InFWgUwRit0ABbg0PXaH"
# 保留你之前的 Webhook URL，用于最终的卡片通知
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/a255f232-ae50-4c0a-82e8-ff2d98b0c9e0"

def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    res.raise_for_status()
    return res.json().get("tenant_access_token")

def merge_dossiers(session_dir, topic):
    """
    物理拼接引擎：将分散的档案融合成单体 Markdown 全案
    """
    master_path = os.path.join(session_dir, "MASTER_REPORT.md")
    
    # 按照 PI 审阅逻辑设定拼接顺序：先看终局结论，再看底层推演
    files_to_merge = [
        ("FINAL_ACTION_PLAN.md", "🎯 破壁行动指南 (核心结论)"),
        ("dossier_1_history.md", "🏛️ 附件一：历史债务与初始假设"),
        ("dossier_2_sota_boundary.md", "🚧 附件二：SOTA 渐进式死亡边界"),
        ("dossier_3_literature_graph.md", "🕸️ 附件三：学术结构洞文献图谱")
    ]

    print("[系统日志] 正在执行多维档案降维拼接...")
    with open(master_path, "w", encoding="utf-8") as master_file:
        master_file.write(f"# 🔬 深度科研全案总集：{topic}\n\n")
        
        for filename, title in files_to_merge:
            filepath = os.path.join(session_dir, filename)
            master_file.write(f"## {title}\n\n")
            
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    master_file.write(f.read() + "\n\n---\n\n")
            else:
                master_file.write("*(⚠️ 该物理切片未生成或已被熔断机制丢弃)*\n\n---\n\n")
                
    return master_path

def upload_and_convert_to_docx(master_md_path, topic, token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 上传全案总集到飞书云盘
    print("[系统日志] 正在将全案总集上传至飞书星港...")
    upload_url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all"
    file_name = f"🔬[全案总集] {topic}.md"
    
    with open(master_md_path, "rb") as f:
        files = {"file": (file_name, f, "text/markdown")}
        data = {"file_name": file_name, "parent_type": "explorer", "parent_node": ""}
        res_upload = requests.post(upload_url, headers=headers, files=files, data=data)
        res_upload.raise_for_status()
        file_token = res_upload.json()["data"]["file_token"]

    # 2. 触发转换引擎
    print("[系统日志] 文件已落盘，唤醒底层 Markdown 转换引擎...")
    import_url = "https://open.feishu.cn/open-apis/drive/v1/import_tasks"
    import_data = {
        "file_extension": "md",
        "file_token": file_token,
        "type": "docx"
    }
    res_import = requests.post(import_url, headers=headers, json=import_data)
    res_import.raise_for_status()
    ticket = res_import.json()["data"]["ticket"]

    # 3. 阻塞轮询
    print("[系统日志] 正在重构富文本树，计算绝对指针...")
    poll_url = f"https://open.feishu.cn/open-apis/drive/v1/import_tasks/{ticket}"
    
    for _ in range(15):  # 总集较长，增加轮询上限至 30 秒
        time.sleep(2)
        res_poll = requests.get(poll_url, headers=headers)
        status = res_poll.json()["data"]["result"]["job_status"]
        if status == 0:
            docx_url = res_poll.json()["data"]["result"]["url"]
            print(f"[系统日志] 矩阵转换完毕！云文档绝对路径: {docx_url}")
            return docx_url
        elif status not in (1, 2):
            raise Exception(f"飞书转换引擎异常熔断，状态码: {status}")
            
    raise Exception("等待飞书转换引擎超时。")

def push_notification(topic, session_dir, docx_url):
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True, "enable_forward": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"🎯 科研全案生成完毕: {topic}"},
                "template": "turquoise"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**物理沙盒节点**: `{session_dir}`\n---\n系统已将四维调查切片拼接为单体 **全案总集 (Master Dossier)**，并完成飞书富文本重构。"}
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {"tag": "plain_text", "content": "☁️ 查阅云端全案总集"},
                            "url": docx_url,
                            "type": "primary"
                        }
                    ]
                }
            ]
        }
    }
    requests.post(WEBHOOK_URL, json=payload)
    print("[系统日志] 低延迟决策卡片已注入通信总线。")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 push_to_feishu_docs.py <Topic> <SessionDir>")
        sys.exit(1)
        
    topic = sys.argv[1]
    session_dir = sys.argv[2]
    
    try:
        # 1. 在沙盒内执行物理拼接
        master_md_path = merge_dossiers(session_dir, topic)
        # 2. 获取通行证
        token = get_tenant_access_token()
        # 3. 上传单体全案并转码
        docx_url = upload_and_convert_to_docx(master_md_path, topic, token)
        # 4. 推送情报
        push_notification(topic, session_dir, docx_url)
    except Exception as e:
        print(f"❌ [系统致命错误] 云端映射协议断裂: {str(e)}")
        sys.exit(1)
