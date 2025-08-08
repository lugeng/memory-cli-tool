# Basic Memory CLI 工具使用说明文档

本文档详细介绍了 `uv run basic-memory tool` 命令的所有子命令功能和使用方法。所有示例都已经过验证，确保能够正常工作。

## 概述

Basic Memory CLI 工具提供了 7 个核心子命令，用于管理知识库中的笔记、搜索内容、创建画布和构建上下文信息。所有命令都直接调用后台服务，提供高性能的知识管理体验。

## 安装和设置

### 前置要求
- Python 3.12+
- uv (Python 包管理器)

### 安装步骤
```bash
# 进入项目目录
cd complete-basic-memory-with-cli

# 安装依赖
uv sync

# 验证安装
uv run basic-memory tool --help
```

## 子命令详细说明

### 1. write-note - 创建或更新笔记

**功能描述：** 创建新笔记或更新现有笔记，支持从标准输入读取内容。

**命令语法：**
```bash
uv run basic-memory tool write-note [OPTIONS]
```

**参数说明：**
- `--title TEXT`: 笔记标题（必需）
- `--folder TEXT`: 存储文件夹路径（必需）
- `--project TEXT`: 项目名称（可选，默认使用当前项目）

**使用示例：**

1. **创建基本笔记：**
```bash
echo "# 我的笔记
这是笔记内容。

## 要点
- 第一个要点
- 第二个要点

#标签1 #标签2" | uv run basic-memory tool write-note --title "测试文档" --folder "docs"
```

2. **从文件创建笔记：**
```bash
cat content.md | uv run basic-memory tool write-note --title "项目计划" --folder "projects"
```

3. **创建会议记录：**
```bash
echo "# 团队会议 2025-08-08

## 参与者
- 张三
- 李四

## 讨论要点
- 项目进度回顾
- 下周计划

## 行动项
- [ ] 完成功能开发
- [ ] 准备演示

#会议 #团队" | uv run basic-memory tool write-note --title "团队会议记录" --folder "meetings"
```

**预期输出：**
```
# Created: docs/测试文档.md

The note is ready and has been indexed for search.
```

### 2. read-note - 读取笔记内容

**功能描述：** 读取指定笔记的完整内容，支持通过文件路径或永久链接访问。

**命令语法：**
```bash
uv run basic-memory tool read-note [PERMALINK]
```

**参数说明：**
- `PERMALINK`: 笔记的永久链接或文件路径（必需）

**使用示例：**

1. **通过永久链接读取：**
```bash
uv run basic-memory tool read-note "docs/测试文档"
```

2. **通过文件路径读取：**
```bash
uv run basic-memory tool read-note "projects/项目计划"
```

3. **读取会议记录：**
```bash
uv run basic-memory tool read-note "meetings/团队会议记录"
```

**预期输出：**
```
---
title: 测试文档
type: note
permalink: docs/测试文档
---

# 测试文档
这是一个测试文档，用于验证 CLI 功能。

## 内容
- 这是第一个要点
- 这是第二个要点
- 包含一些中文内容

## 标签
#测试 #文档 #CLI
```

### 3. search-notes - 搜索笔记

**功能描述：** 在知识库中搜索笔记内容，支持全文搜索和元数据过滤。

**命令语法：**
```bash
uv run basic-memory tool search-notes [OPTIONS] [QUERY]
```

**参数说明：**
- `QUERY`: 搜索关键词（可选）
- `--permalink TEXT`: 按永久链接搜索
- `--title TEXT`: 按标题搜索
- `--types TEXT`: 按类型过滤
- `--entity-types TEXT`: 按实体类型过滤
- `--after-date TEXT`: 按日期过滤

**使用示例：**

1. **基本文本搜索：**
```bash
uv run basic-memory tool search-notes "测试"
```

2. **按标题搜索：**
```bash
uv run basic-memory tool search-notes --title "会议"
```

3. **按类型搜索：**
```bash
uv run basic-memory tool search-notes --entity-types "note"
```

4. **组合搜索：**
```bash
uv run basic-memory tool search-notes "项目" --after-date "2025-08-01"
```

**预期输出：**
```json
{
  "results": [
    {
      "title": "note: #测试 #文档 #CLI...",
      "type": "observation",
      "score": -0.4419336839203991,
      "entity": "docs/测试文档",
      "permalink": "docs/测试文档/observations/note/测试文档-cli",
      "content": "#测试 #文档 #CLI",
      "file_path": "docs/测试文档.md",
      "metadata": {
        "tags": ["测试", "文档", "CLI"]
      },
      "category": "note",
      "from_entity": "docs/测试文档"
    },
    {
      "title": "测试文档",
      "type": "entity",
      "score": -0.3567416484658643,
      "entity": "docs/测试文档",
      "permalink": "docs/测试文档",
      "content": "# 测试文档\n这是一个测试文档，用于验证 CLI 功能。...",
      "file_path": "docs/测试文档.md",
      "metadata": {
        "entity_type": "note"
      },
      "from_entity": "docs/测试文档"
    }
  ],
  "current_page": 1,
  "page_size": 10
}
```

### 4. canvas - 创建 Obsidian 画布

**功能描述：** 创建与 Obsidian Canvas 功能兼容的 .canvas 文件，用于可视化概念和连接关系。

**命令语法：**
```bash
uv run basic-memory tool canvas [OPTIONS]
```

**参数说明：**
- `--nodes TEXT`: JSON 格式的节点数组（必需）
- `--edges TEXT`: JSON 格式的边数组（必需）
- `--title TEXT`: 画布标题（必需）
- `--folder TEXT`: 存储文件夹路径（必需）
- `--project TEXT`: 项目名称（可选）

**使用示例：**

1. **创建简单画布：**
```bash
uv run basic-memory tool canvas \
  --nodes '[{"id":"node1","type":"text","text":"核心概念","x":0,"y":0,"width":200,"height":100}]' \
  --edges '[]' \
  --title "概念图" \
  --folder "diagrams"
```

2. **创建包含连接的复杂画布：**
```bash
uv run basic-memory tool canvas \
  --nodes '[
    {"id":"concept1","type":"text","text":"人工智能","x":0,"y":0,"width":200,"height":100},
    {"id":"concept2","type":"text","text":"机器学习","x":300,"y":0,"width":200,"height":100},
    {"id":"concept3","type":"text","text":"深度学习","x":600,"y":0,"width":200,"height":100}
  ]' \
  --edges '[
    {"id":"edge1","fromNode":"concept1","toNode":"concept2","label":"包含"},
    {"id":"edge2","fromNode":"concept2","toNode":"concept3","label":"包含"}
  ]' \
  --title "AI知识图谱" \
  --folder "knowledge-maps"
```

3. **创建项目规划画布：**
```bash
uv run basic-memory tool canvas \
  --nodes '[
    {"id":"phase1","type":"text","text":"需求分析","x":0,"y":0,"width":150,"height":80},
    {"id":"phase2","type":"text","text":"设计阶段","x":200,"y":0,"width":150,"height":80},
    {"id":"phase3","type":"text","text":"开发阶段","x":400,"y":0,"width":150,"height":80},
    {"id":"phase4","type":"text","text":"测试阶段","x":600,"y":0,"width":150,"height":80}
  ]' \
  --edges '[
    {"id":"flow1","fromNode":"phase1","toNode":"phase2"},
    {"id":"flow2","fromNode":"phase2","toNode":"phase3"},
    {"id":"flow3","fromNode":"phase3","toNode":"phase4"}
  ]' \
  --title "项目流程图" \
  --folder "project-planning"
```

**预期输出：**
```
# Created: diagrams/概念图.canvas

The canvas is ready to open in Obsidian.
```

### 5. build-context - 构建上下文信息

**功能描述：** 从 memory:// URI 构建上下文信息，用于继续讨论或工作会话。

**命令语法：**
```bash
uv run basic-memory tool build-context [OPTIONS] URI
```

**参数说明：**
- `URI`: memory:// 格式的 URI（必需）
- `--depth INTEGER`: 搜索深度（默认：1）
- `--timeframe TEXT`: 时间范围（默认：7d）
- `--page INTEGER`: 页码（默认：1）
- `--page-size INTEGER`: 页面大小（默认：10）
- `--max-related INTEGER`: 最大相关项数量（默认：10）

**使用示例：**

1. **基本上下文构建：**
```bash
uv run basic-memory tool build-context "memory://docs/测试文档"
```

2. **带参数的详细上下文：**
```bash
uv run basic-memory tool build-context "memory://projects/项目计划" \
  --depth 2 \
  --timeframe "30d" \
  --page 1 \
  --page-size 20 \
  --max-related 15
```

3. **构建会议相关上下文：**
```bash
uv run basic-memory tool build-context "memory://meetings/团队会议记录" \
  --depth 1 \
  --timeframe "14d" \
  --max-related 5
```

**预期输出：**
```json
{
  "results": [
    {
      "primary_result": {
        "type": "entity",
        "permalink": "docs/测试文档",
        "title": "测试文档",
        "content": "# 测试文档\n这是一个测试文档，用于验证 CLI 功能。...",
        "file_path": "docs/测试文档.md",
        "created_at": "2025-08-08 08:33:13.224904"
      },
      "observations": [
        {
          "type": "observation",
          "title": "note: #测试 #文档 #CLI...",
          "file_path": "docs/测试文档.md",
          "permalink": "docs/测试文档/observations/note/测试文档-cli",
          "category": "note",
          "content": "#测试 #文档 #CLI",
          "created_at": "2025-08-08 08:33:13.224904"
        }
      ],
      "related_results": []
    }
  ],
  "metadata": {
    "uri": "docs/测试文档",
    "depth": 1,
    "timeframe": "2025-08-01T08:34:32.210652",
    "generated_at": "2025-08-08 08:34:32.221487+00:00",
    "primary_count": 1,
    "related_count": 0,
    "total_results": 1,
    "total_relations": 0,
    "total_observations": 1
  },
  "page": 1,
  "page_size": 10
}
```

### 6. recent-activity - 查看最近活动

**功能描述：** 显示知识库中的最近活动，包括新创建的笔记、更新和观察。

**命令语法：**
```bash
uv run basic-memory tool recent-activity [OPTIONS]
```

**参数说明：**
- `--type TEXT`: 活动类型过滤
- `--depth INTEGER`: 搜索深度（默认：1）
- `--timeframe TEXT`: 时间范围（默认：7d）
- `--page INTEGER`: 页码（默认：1）
- `--page-size INTEGER`: 页面大小（默认：10）
- `--max-related INTEGER`: 最大相关项数量（默认：10）

**使用示例：**

1. **查看最近 7 天活动：**
```bash
uv run basic-memory tool recent-activity
```

2. **查看最近 24 小时活动：**
```bash
uv run basic-memory tool recent-activity --timeframe "1d"
```

3. **查看最近 30 天活动（分页）：**
```bash
uv run basic-memory tool recent-activity --timeframe "30d" --page 1 --page-size 5
```

**预期输出：**
```json
{
  "results": [
    {
      "primary_result": {
        "type": "entity",
        "title": "测试画布.canvas",
        "file_path": "diagrams/测试画布.canvas",
        "created_at": "2025-08-08 08:34:13.796907"
      },
      "observations": [],
      "related_results": []
    },
    {
      "primary_result": {
        "type": "entity",
        "permalink": "docs/测试文档",
        "title": "测试文档",
        "content": "# 测试文档\n这是一个测试文档，用于验证 CLI 功能。...",
        "file_path": "docs/测试文档.md",
        "created_at": "2025-08-08 08:33:13.224904"
      },
      "observations": [
        {
          "type": "observation",
          "title": "note: #测试 #文档 #CLI...",
          "file_path": "docs/测试文档.md",
          "permalink": "docs/测试文档/observations/note/测试文档-cli",
          "category": "note",
          "content": "#测试 #文档 #CLI",
          "created_at": "2025-08-08 08:33:13.224904"
        }
      ],
      "related_results": []
    }
  ],
  "metadata": {
    "types": ["entity", "relation", "observation"],
    "depth": 1,
    "timeframe": "2025-08-01T08:34:44.995204",
    "generated_at": "2025-08-08T08:34:45.005413Z",
    "primary_count": 6,
    "related_count": 0,
    "total_results": 6,
    "total_relations": 0,
    "total_observations": 1
  },
  "page": 1,
  "page_size": 10
}
```

### 7. continue-conversation - 继续对话

**功能描述：** 基于指定主题生成对话继续提示，包含相关的记忆和上下文信息。

**命令语法：**
```bash
uv run basic-memory tool continue-conversation [OPTIONS]
```

**参数说明：**
- `--topic TEXT`: 搜索主题或关键词（可选）
- `--timeframe TEXT`: 回溯时间范围（可选）

**使用示例：**

1. **基于主题继续对话：**
```bash
uv run basic-memory tool continue-conversation --topic "项目规划"
```

2. **基于最近活动继续对话：**
```bash
uv run basic-memory tool continue-conversation --timeframe "3d"
```

3. **基于特定主题和时间范围：**
```bash
uv run basic-memory tool continue-conversation --topic "会议" --timeframe "1w"
```

**预期输出：**
```
# Continuing conversation on: 测试

This is a memory retrieval session. 

Please use the available basic-memory tools to gather relevant context before responding. Start by executing one of the suggested commands below to retrieve content.

> **Knowledge Capture Recommendation:** As you continue this conversation, actively look for opportunities to record new information, decisions, or insights that emerge. Use `write_note()` to document important context.

Here's what I found from previous conversations:

<memory>
--- memory://docs/测试文档

## 测试文档
- **Type**: entity
- **Created**: 2025-08-08 08:33

**Excerpt**:
<excerpt>
# 测试文档
这是一个测试文档，用于验证 CLI 功能。

## 内容
- 这是第一个要点
- 这是第二个要点
- 包含一些中文内容

## 标签
#测试 #文档 #CLI
</excerpt>

You can read this document with: `read_note("docs/测试文档")`

</memory>

## Next Steps
<instructions>
You can:
- Explore more with: `search_notes("测试")`
- See what's changed: `recent_activity(timeframe="1d")`
- **Record new learnings or decisions from this conversation:** `write_note(folder="[Choose a folder]" title="[Create a meaningful title]", content="[Content with observations and relations]")`

## Knowledge Capture Recommendation

As you continue this conversation, **actively look for opportunities to:**
1. Record key information, decisions, or insights that emerge
2. Link new knowledge to existing topics 
3. Suggest capturing important context when appropriate
4. Create forward references to topics that might be created later

Remember that capturing knowledge during conversations is one of the most valuable aspects of Basic Memory.
</instructions>
```

## 工作流程示例

### 典型的知识管理工作流程

1. **创建项目笔记：**
```bash
echo "# 新项目启动

## 项目目标
- 开发知识管理系统
- 提升团队协作效率

## 关键里程碑
- [ ] 需求分析完成
- [ ] 原型设计
- [ ] 开发实现
- [ ] 测试部署

#项目 #规划" | uv run basic-memory tool write-note --title "新项目规划" --folder "projects"
```

2. **创建相关的概念图：**
```bash
uv run basic-memory tool canvas \
  --nodes '[
    {"id":"goal","type":"text","text":"项目目标","x":0,"y":0,"width":150,"height":100},
    {"id":"analysis","type":"text","text":"需求分析","x":200,"y":0,"width":150,"height":100},
    {"id":"design","type":"text","text":"原型设计","x":400,"y":0,"width":150,"height":100},
    {"id":"dev","type":"text","text":"开发实现","x":600,"y":0,"width":150,"height":100}
  ]' \
  --edges '[
    {"id":"e1","fromNode":"goal","toNode":"analysis"},
    {"id":"e2","fromNode":"analysis","toNode":"design"},
    {"id":"e3","fromNode":"design","toNode":"dev"}
  ]' \
  --title "项目流程图" \
  --folder "diagrams"
```

3. **搜索相关内容：**
```bash
uv run basic-memory tool search-notes "项目"
```

4. **构建项目上下文：**
```bash
uv run basic-memory tool build-context "memory://projects/新项目规划"
```

5. **查看最近活动：**
```bash
uv run basic-memory tool recent-activity --timeframe "1d"
```

## 高级使用技巧

### 1. 管道操作
```bash
# 从文件创建笔记
cat meeting-notes.md | uv run basic-memory tool write-note --title "会议记录" --folder "meetings"

# 搜索并保存结果
uv run basic-memory tool search-notes "重要" > search-results.json
```

### 2. 批量操作
```bash
# 创建多个相关笔记
for topic in "需求分析" "系统设计" "开发计划"; do
  echo "# $topic
  
## 概述
待完善的 $topic 内容

#项目 #$topic" | uv run basic-memory tool write-note --title "$topic" --folder "project-docs"
done
```

### 3. 上下文链接
```bash
# 先构建上下文
uv run basic-memory tool build-context "memory://projects/新项目规划" > context.json

# 基于上下文继续工作
uv run basic-memory tool continue-conversation --topic "项目规划" --timeframe "7d"
```

## 故障排除

### 常见问题

1. **命令找不到：**
   - 确保已运行 `uv sync` 安装依赖
   - 检查是否在正确的项目目录中

2. **权限错误：**
   - 确保对项目目录有写权限
   - 检查 `.basic-memory` 目录权限

3. **搜索结果为空：**
   - 确保已创建并索引了笔记
   - 尝试使用不同的搜索关键词

4. **JSON 格式错误（canvas 命令）：**
   - 验证 JSON 格式是否正确
   - 使用在线 JSON 验证器检查语法

### 调试技巧

1. **查看日志：**
```bash
tail -f ~/.basic-memory/basic-memory-api.log
```

2. **验证数据库状态：**
```bash
uv run basic-memory tool recent-activity --timeframe "1d"
```

3. **测试搜索索引：**
```bash
uv run basic-memory tool search-notes --entity-types "note"
```

## 性能优化

### 最佳实践

1. **合理使用分页：**
   - 对于大量结果，使用 `--page-size` 限制返回数量
   - 使用 `--page` 参数浏览多页结果

2. **优化搜索查询：**
   - 使用具体的关键词而不是通用词汇
   - 结合类型过滤提高搜索精度

3. **定期维护：**
   - 定期查看最近活动，了解知识库状态
   - 使用标签系统组织内容

## 总结

Basic Memory CLI 工具提供了完整的知识管理功能，从基本的笔记创建到复杂的上下文构建。所有命令都经过验证，可以可靠地用于日常知识管理工作。

### 核心优势
- **高性能：** 直接服务调用，避免 HTTP 开销
- **功能完整：** 涵盖创建、读取、搜索、可视化等全流程
- **易于使用：** 简洁的命令行接口，支持管道操作
- **可扩展：** 支持自定义项目和灵活的参数配置

### 推荐工作流程
1. 使用 `write-note` 创建内容
2. 使用 `canvas` 创建可视化图表
3. 使用 `search-notes` 查找相关信息
4. 使用 `build-context` 构建工作上下文
5. 使用 `continue-conversation` 继续深入讨论

通过合理使用这些工具，您可以构建一个高效的个人或团队知识管理系统。
