#!/usr/bin/env python3
import sys
import json
import urllib.request
import os

def push_to_feishu(topic, session_dir, webhook_url):
    plan_path = os.path.join(session_dir, "FINAL_ACTION_PLAN.md")
    
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 飞书卡片 Markdown 模块有字数限制，我们做安全截断保护
        if len(content) > 4000:
            content = content[:4000] + "\n\n...\n*(报告过长已截断，请通过 VS Code Remote 登录服务器查看完整 Markdown 与 BibTeX 文件)*"

        # 构建飞书交互式卡片结构 (第一性原理：用最严谨的结构呈现逻辑)
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True,
                    "enable_forward": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"🔬 破壁行动指南: {topic}"
                    },
                    "template": "blue" # 核心高亮色
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**物理沙盒路径**: `{session_dir}`\n---\n"
                        }
                    },
                    {
                        "tag": "markdown",
                        "content": content
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "tag": "plain_text",
                                    "content": "收到，在服务器物理归档"
                                },
                                "type": "primary"
                            }
                        ]
                    }
                ]
            }
        }

        req = urllib.request.Request(
            webhook_url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
        print(f"[系统日志]: 已成功将降维打击指南通过 Webhook 注入飞书神经节点。")
        
    except Exception as e:
        print(f"[系统致命错误]: 飞书推送物理断层: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 push_to_feishu.py <Topic> <SessionDir>")
        sys.exit(1)
        
    topic = sys.argv[1]
    session_dir = sys.argv[2]
    
    # 【强制修改】：将这里替换为你刚才在飞书群里创建的机器人的真实 Webhook URL
    WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/a255f232-ae50-4c0a-82e8-ff2d98b0c9e0"
    
    push_to_feishu(topic, session_dir, WEBHOOK_URL)