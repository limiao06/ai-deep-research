#!/usr/bin/env python3
"""
飞书文档推送引擎 v8.0 (安全版)
- 敏感信息从配置文件读取
- 配置文件路径: .secrets/feishu_config.json
- 使用 Markdown 导入转换 API（完美格式）
- 文档保存到指定目录"🔬 深度科研报告"
"""
import sys
import os
import json
import time
import requests

# ==========================================
# 配置加载
# ==========================================
def load_config():
    """从配置文件加载敏感信息"""
    # 配置文件路径：脚本所在目录下的 .secrets/feishu_config.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, ".secrets", "feishu_config.json")
    
    # 备选路径：环境变量指定
    if not os.path.exists(config_path):
        config_path = os.environ.get("FEISHU_CONFIG_PATH", "")
    
    if not config_path or not os.path.exists(config_path):
        raise FileNotFoundError(
            f"❌ 配置文件未找到！\n"
            f"   请创建配置文件: {os.path.join(script_dir, '.secrets', 'feishu_config.json')}\n"
            f"   或设置环境变量: FEISHU_CONFIG_PATH=/path/to/config.json\n"
            f"   配置文件格式见 README.md"
        )
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 验证必要字段
    required_fields = ["APP_ID", "APP_SECRET", "WEBHOOK_URL", "ROOT_FOLDER_TOKEN"]
    missing = [k for k in required_fields if k not in config]
    if missing:
        raise ValueError(f"❌ 配置文件缺少必要字段: {missing}")
    
    return config

# 延迟加载配置（只在需要时加载）
_config = None

def get_config():
    global _config
    if _config is None:
        _config = load_config()
    return _config

# ==========================================
# 常量区（非敏感）
# ==========================================
DOCS_FOLDER_NAME = "🔬 深度科研报告"
DOCS_FOLDER_URL = "https://my.feishu.cn/drive/folder/NcG5fyRBVl8Ed6dlMgycrhW1n6b"

# ==========================================
# 核心函数
# ==========================================
def get_tenant_access_token():
    config = get_config()
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={
        "app_id": config["APP_ID"],
        "app_secret": config["APP_SECRET"]
    })
    res.raise_for_status()
    return res.json().get("tenant_access_token")

def merge_dossiers(session_dir, topic):
    """物理拼接引擎"""
    master_path = os.path.join(session_dir, "MASTER_REPORT.md")
    
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
    """上传 Markdown 并转换为飞书文档"""
    config = get_config()
    headers = {"Authorization": f"Bearer {token}"}
    headers_json = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    file_size = os.path.getsize(master_md_path)
    
    # Step 1: 上传 Markdown 到云盘
    print(f"[系统日志] 正在上传 Markdown 文件到「{DOCS_FOLDER_NAME}」目录...")
    upload_url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all"
    
    with open(master_md_path, "rb") as f:
        files = {"file": (f"{topic}.md", f, "text/markdown")}
        data = {
            "file_name": f"{topic}.md",
            "parent_type": "explorer",
            "parent_node": config["ROOT_FOLDER_TOKEN"],
            "size": str(file_size)
        }
        res = requests.post(upload_url, headers=headers, files=files, data=data)
        res.raise_for_status()
        result = res.json()
        
        if result.get("code") != 0:
            raise Exception(f"上传失败: {result}")
        
        file_token = result["data"]["file_token"]
        print(f"[系统日志] 文件上传成功: {file_token}")
    
    # Step 2: 创建导入任务
    print("[系统日志] 正在创建 Markdown -> Docx 转换任务...")
    import_url = "https://open.feishu.cn/open-apis/drive/v1/import_tasks"
    
    payload = {
        "file_extension": "md",
        "file_token": file_token,
        "type": "docx",
        "file_name": f"🔬 深度科研全案：{topic}",
        "point": {
            "mount_type": 1,
            "mount_key": config["ROOT_FOLDER_TOKEN"]
        }
    }
    
    res = requests.post(import_url, headers=headers_json, json=payload)
    res.raise_for_status()
    result = res.json()
    
    if result.get("code") != 0:
        raise Exception(f"导入任务创建失败: {result}")
    
    ticket = result["data"]["ticket"]
    print(f"[系统日志] 导入任务已创建: {ticket}")
    
    # Step 3: 轮询转换状态
    print("[系统日志] 正在等待转换完成...")
    poll_url = f"https://open.feishu.cn/open-apis/drive/v1/import_tasks/{ticket}"
    
    for i in range(15):
        time.sleep(2)
        res = requests.get(poll_url, headers=headers_json)
        result = res.json()
        
        if result.get("code") == 0:
            status = result["data"]["result"]["job_status"]
            if status == 0:
                doc_url = result["data"]["result"]["url"]
                print(f"[系统日志] Markdown 转换完成: {doc_url}")
                return doc_url
            elif status not in (1, 2):
                raise Exception(f"转换失败: {result}")
    
    raise Exception("转换超时")

def push_notification(topic, session_dir, doc_url):
    config = get_config()
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
                    "text": {"tag": "lark_md", "content": f"**物理沙盒节点**: `{session_dir}`\n**文档位置**: [{DOCS_FOLDER_NAME}]({DOCS_FOLDER_URL})\n---\n系统已将四维调查切片拼接为单体 **全案总集 (Master Dossier)**，Markdown 已转换为富文本格式并保存到指定目录。"}
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {"tag": "plain_text", "content": "☁️ 查阅云端全案总集"},
                            "url": doc_url,
                            "type": "primary"
                        }
                    ]
                }
            ]
        }
    }
    requests.post(config["WEBHOOK_URL"], json=payload)
    print("[系统日志] 低延迟决策卡片已注入通信总线。")

# ==========================================
# 配置模板生成
# ==========================================
def generate_config_template():
    """生成配置文件模板"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(script_dir, ".secrets")
    config_path = os.path.join(config_dir, "feishu_config.json")
    
    template = {
        "APP_ID": "your_app_id_here",
        "APP_SECRET": "your_app_secret_here",
        "WEBHOOK_URL": "https://open.feishu.cn/open-apis/bot/v2/hook/your_webhook_id",
        "ROOT_FOLDER_TOKEN": "your_folder_token_here"
    }
    
    os.makedirs(config_dir, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 配置模板已生成: {config_path}")
    print("   请编辑该文件，填入真实的飞书凭证")

# ==========================================
# 入口
# ==========================================
if __name__ == "__main__":
    # 支持生成配置模板
    if len(sys.argv) >= 2 and sys.argv[1] == "--init":
        generate_config_template()
        sys.exit(0)
    
    if len(sys.argv) < 3:
        print("用法:")
        print("  python3 push_to_feishu_docs.py <Topic> <SessionDir>  # 推送文档")
        print("  python3 push_to_feishu_docs.py --init                 # 生成配置模板")
        sys.exit(1)
        
    topic = sys.argv[1]
    session_dir = sys.argv[2]
    
    try:
        # 1. 在沙盒内执行物理拼接
        master_md_path = merge_dossiers(session_dir, topic)
        
        # 2. 获取通行证
        token = get_tenant_access_token()
        
        # 3. 上传并转换为飞书文档
        doc_url = upload_and_convert_to_docx(master_md_path, topic, token)
        
        # 4. 推送情报
        push_notification(topic, session_dir, doc_url)
        
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(f"❌ [系统致命错误] 云端映射协议断裂: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
