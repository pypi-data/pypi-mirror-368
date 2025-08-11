# Bilibili MCP Server - SSE 模式使用说明

## 从 UVX 切换到 SSE

您的 MCP 服务器现在支持 SSE (Server-Sent Events) 传输方式。以下是切换步骤：

## 新增文件

1. **bilibili_sse.py** - 支持 SSE 传输的服务器主文件
2. **mcp_config_sse.json** - SSE 模式的 MCP 配置文件
3. **start_sse_server.py** - 便捷的启动脚本

## 启动方式

### 方法一：使用启动脚本（推荐）
```bash
python start_sse_server.py
```

自定义端口：
```bash
python start_sse_server.py --port 9000
```

自定义主机和端口：
```bash
python start_sse_server.py --host 0.0.0.0 --port 8080
```

### 方法二：直接启动 SSE 服务器
```bash
python bilibili_sse.py
```

指定端口：
```bash
python bilibili_sse.py --port 9000
```

指定主机和端口：
```bash
python bilibili_sse.py --host 0.0.0.0 --port 8080
```

## 配置说明

SSE 模式的配置文件 `mcp_config_sse.json`：
```json
{
  "mcpServers": {
    "bilibili": {
      "command": "python",
      "args": [
        "bilibili_sse.py",
        "--host", "localhost",
        "--port", "8000"
      ],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## 服务器访问

启动后，服务器将在以下地址可用：
- **HTTP 端点**: `http://localhost:8000`
- **SSE 端点**: `http://localhost:8000/sse`

## UVX vs SSE 对比

| 特性 | UVX 模式 | SSE 模式 |
|------|----------|----------|
| 传输方式 | stdio | HTTP SSE |
| 网络访问 | 否 | 是 |
| 端口配置 | 不需要 | 需要指定端口 |
| 调试方便性 | 一般 | 更好（可通过 HTTP 访问） |
| 部署方式 | 本地 | 支持远程访问 |

## 功能测试

启动服务器后，您可以使用以下功能：

- **搜索用户**: `search_user`
- **搜索视频**: `general_search`
- **获取精确结果**: `get_precise_results`
- **获取视频弹幕**: `get_video_danmaku`
- **提取视频弹幕**: `extract_video_danmaku`
- **清洗数据**: `clean_travel_data`

## 故障排除

### 端口占用
如果默认端口 8000 被占用，请使用其他端口：
```bash
python start_sse_server.py --port 8001
```

### 依赖问题
确保安装了所需的依赖：
```bash
pip install -r requirements.txt
```

### 防火墙设置
如需远程访问，请确保防火墙允许相应端口的连接。

## 生产环境部署

对于生产环境，建议：
1. 使用 `--host 0.0.0.0` 允许外部访问
2. 配置反向代理（如 nginx）
3. 使用 systemd 或 supervisor 管理服务进程
4. 启用日志记录和监控

## 切换回 UVX

如需切换回 UVX 模式，请使用原始的配置文件：
```bash
# 使用原来的 mcp_config_uvx.json 配置
