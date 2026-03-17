---
name: ai_deep_research
description: 基于 Brave、arXiv 和 Semantic Scholar 的多智能体 AI 深度调研助手。
metadata: {"openclaw":{"emoji":"🔬"}}
---
# AI 深度科研助手 (Deep Research)

当用户要求对某个 AI 主题、算法或方向进行“深度研究”、“深度调研”或“寻找创新点”时，你需要启动 OpenProse 并行研究工作流。

请严格执行以下命令来启动后台研究：
`/prose run {baseDir}/research_workflow.prose`

**操作注意事项：**
1. 将用户指定的具体研究主题传递给 `{topic}` 参数。
2. `{baseDir}` 占位符会自动解析为当前技能目录的绝对路径，请直接在指令中保留并使用它。
3. 启动指令发送后，请立刻礼貌地回复用户：“🔬 深度研究工作流已启动。后台正在并行调度历史梳理、arXiv PDF 阅读以及 Semantic Scholar 文献检索任务。请耐心等待几分钟，完成后将自动为您发送完整的创新点分析报告。”
