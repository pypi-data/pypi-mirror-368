# 抖音数据分析 MCP 服务器

基于原始抖音数据分析工具开发的 MCP (Model Context Protocol) 服务器，提供抖音视频和用户数据的采集、分析和导出功能。

## 功能特性

### 数据采集
- **视频搜索**: 根据关键词搜索抖音视频，采集标题、作者、点赞数、评论数等信息
- **用户搜索**: 根据关键词搜索抖音用户，采集用户名、抖音号、粉丝数、获赞数等信息
- **自定义参数**: 支持设置滚动次数和延迟时间，控制采集规模和速度

### 数据分析
- **互动数据分析**: 分析视频的点赞、评论、分享等互动数据，提供统计报告
- **内容长度分析**: 分析视频标题长度分布，了解内容特征
- **关键词分析**: 使用中文分词技术分析高频词汇，发现热门话题

### 数据导出
- **多格式支持**: 支持 JSON、Excel、CSV 格式导出
- **分类导出**: 可选择导出视频数据、用户数据或全部数据
- **时间戳**: 自动添加时间戳，避免文件覆盖

## 安装和配置

### 环境要求
- Python 3.13+
- uv 包管理器

### 安装步骤

1. **安装依赖**:
   ```bash
   uv sync
   ```

2. **配置 MCP 客户端**:
   将 `mcp_config.json` 中的配置添加到你的 MCP 客户端配置中。

3. **启动服务器**:
   ```bash
   uv run python douyin_mcp_server.py
   ```

## 可用工具

### 1. search_douyin_videos
搜索抖音视频数据

**参数**:
- `keyword` (必需): 搜索关键词
- `scroll_count` (可选): 滚动次数，默认为10
- `delay` (可选): 每次滚动的延迟时间（秒），默认为2.0

### 2. search_douyin_users
搜索抖音用户数据

### 3. analyze_interaction_data
分析视频互动数据（点赞、评论等）

### 4. analyze_content_length
分析视频标题长度分布

### 5. analyze_keywords
分析视频标题中的高频词汇

### 6. export_data
导出采集的数据

### 7. get_data_summary
获取当前采集数据的摘要信息

### 8. clear_data
清空当前采集的数据

## 可用资源

### 1. douyin://data/videos
当前采集的视频数据（JSON 格式）

### 2. douyin://data/users
当前采集的用户数据（JSON 格式）

### 3. douyin://analysis/summary
数据采集和分析摘要（文本格式）

## 使用示例

### 基本工作流程

1. **搜索视频数据**:
   使用 search_douyin_videos 工具搜索关键词

2. **分析数据**:
   使用 analyze_interaction_data 分析互动数据
   使用 analyze_keywords 分析高频词汇

3. **导出结果**:
   使用 export_data 导出为指定格式

## 注意事项

1. **网络环境**: 需要能够访问抖音网站
2. **浏览器依赖**: 使用 DrissionPage 需要 Chrome/Chromium 浏览器
3. **采集频率**: 建议设置适当的延迟时间，避免过于频繁的请求
4. **合规使用**: 请遵守抖音的使用条款和相关法律法规

## 技术架构

- **MCP 协议**: 基于 Model Context Protocol 实现
- **异步处理**: 使用 asyncio 进行异步操作
- **数据解析**: 使用 BeautifulSoup 解析 HTML
- **中文分词**: 使用 jieba 进行中文文本分析
- **数据处理**: 使用 pandas 进行数据操作和导出