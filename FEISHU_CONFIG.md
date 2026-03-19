# 飞书文档推送引擎 - 安全配置指南

## 快速开始

### 1. 生成配置模板

```bash
python3 push_to_feishu_docs.py --init
```

这会在 `.secrets/` 目录下生成 `feishu_config.json` 模板文件。

### 2. 填写真实凭证

编辑 `.secrets/feishu_config.json`：

```json
{
  "APP_ID": "cli_xxxxxxxxxxxxxxxx",
  "APP_SECRET": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "WEBHOOK_URL": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "ROOT_FOLDER_TOKEN": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

### 3. 使用

```bash
python3 push_to_feishu_docs.py "Research Topic" "/path/to/session/dir"
```

## 安全说明

- `.secrets/` 目录已在 `.gitignore` 中，**不会被 git 追踪**
- 配置文件包含敏感信息，**切勿上传到公开仓库**
- 如需分享代码，请确保 `.gitignore` 正确配置

## 环境变量备选

如果不使用配置文件，可以设置环境变量：

```bash
export FEISHU_CONFIG_PATH=/path/to/your/config.json
```

## 获取飞书凭证

1. **APP_ID / APP_SECRET**: 飞书开放平台 → 企业自建应用 → 凭证与基础信息
2. **WEBHOOK_URL**: 飞书群组 → 设置 → 群机器人 → 添加机器人 → 自定义机器人
3. **ROOT_FOLDER_TOKEN**: 飞书云文档目录 URL 中的 token（如 `https://my.feishu.cn/drive/folder/XXXXX` 中的 `XXXXX`）
