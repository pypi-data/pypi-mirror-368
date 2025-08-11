# Bilibili API MCP Server

用于哔哩哔哩 API 的 MCP（模型上下文协议）服务器，支持多种操作。

## 环境要求

- [uv](https://docs.astral.sh/uv/) - 一个项目管理工具，可以很方便管理依赖。

## 使用方法

1. clone 本项目

2. 使用 uv 安装依赖

```bash
uv sync
```

3. 在任意 mcp client 中配置本 Server

```json
{
  "mcpServers": {
    "bilibili": {
      "command": "uv",
      "args": [
        "--directory",
        "/your-project-path/bilibili-mcp-server",
        "run",
        "bilibili.py"
      ]
    }
  }
}
```

4. 在 client 中使用

## 支持的操作

支持以下操作：

1. `general_search`: 基础搜索功能，使用关键词在哔哩哔哩进行搜索。
2. `search_user`: 专门用于搜索哔哩哔哩用户的功能，可以按照粉丝数排序。
3. `get_precise_results`: 精确搜索功能，可以过滤掉不必要的信息，支持多种搜索类型：
   - 用户搜索 (`user`)：精确匹配用户名，只返回完全匹配的结果。例如搜索"双雷"只会返回用户名为"双雷"的账号信息，不会返回其他相关用户
   - 视频搜索 (`video`)
   - 直播搜索 (`live`)
   - 专栏搜索 (`article`)
返回结果包含 `exact_match` 字段，标识是否找到精确匹配的结果。
4. `get_video_danmaku·`: 获取视频弹幕信息。

## 如何为本项目做贡献

1. Fork 本项目
2. 新建分支，并在新的分支上做改动
3. 提交 PR

## 🎉 更新内容

本项目现在包含了完整的打包和部署解决方案：

### 📦 打包选项

1. **Python包打包**（推荐）
   ```bash
   python build.py
   pip install dist/*.whl
   ```

2. **Docker容器化**
   ```bash
   docker build -t bilibili-mcp-server .
   docker-compose up -d
   ```

3. **自动化安装**
   ```bash
   python install.py
   ```

### 🚀 快速开始

```bash
# 1. 自动安装和配置
python install.py

# 2. 或者手动构建
python build.py

# 3. 运行演示
python example.py
```

### 📋 生成的配置文件

- `mcp_config.json` - 开发模式配置 (uv run)
- `mcp_config_pip.json` - pip安装模式配置
- `mcp_config_uvx.json` - uvx运行配置 (推荐)
- `mcp_config_wheel.json` - 直接从wheel包运行
- `docker-compose.yml` - Docker部署配置
- `Dockerfile` - 容器构建文件

### 📚 详细文档

查看 [`PACKAGING.md`](./PACKAGING.md) 获取完整的打包指南和使用说明。

## License

MIT
