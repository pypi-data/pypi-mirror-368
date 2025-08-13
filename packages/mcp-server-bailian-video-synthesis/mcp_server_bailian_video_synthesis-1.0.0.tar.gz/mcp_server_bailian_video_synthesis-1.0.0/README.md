# AliyunBailianMCP

用于调用阿里云百炼上模型接口的MCP工具集合。这里的模型主要是生文、生图、视频生成等模型，这些模型无法使用通用OpenAI协议调用。

## 🚀 快速开始

### 使用 uvx 直接运行（推荐）

```bash
# 安装并运行（需要先发布到PyPI）
uvx mcp-server-bailian-video-synthesis --help

# 使用API密钥启动服务
uvx mcp-server-bailian-video-synthesis your_api_key

# 或者通过环境变量
export DASHSCOPE_API_KEY=your_api_key
uvx mcp-server-bailian-video-synthesis
```

### 本地开发安装

```bash
# 克隆项目
git clone https://github.com/your-username/AliyunBailianMCP.git
cd AliyunBailianMCP

# 创建虚拟环境
python3.12 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .

# 测试命令
mcp-server-bailian-video-synthesis --help
```

## 📦 已实现的MCP工具

### 1. mcp-server-bailian-video-synthesis

阿里云百炼-通义万相视频编辑统一模型MCP服务器

**功能特性：**
- 多图参考视频生成
- 视频重绘
- 视频局部编辑
- 视频延展
- 视频画面扩展
- 任务结果查询

**使用方法：**
```bash
# 查看帮助
mcp-server-bailian-video-synthesis --help

# 启动服务
mcp-server-bailian-video-synthesis your_dashscope_api_key
```

详细文档请查看：[src/README.md](src/README.md)

## 🔧 开发环境

- Python 3.12+
- 依赖管理：pip
- 构建工具：setuptools
- MCP SDK：python-sdk

## 📁 项目结构

```
AliyunBailianMCP/
├── src/
│   ├── mcp_server_bailian_video_synthesis/
│   │   ├── __init__.py
│   │   └── server.py
│   ├── README.md
│   └── test_mcp_server.py
├── pyproject.toml
├── requirements.txt
├── PUBLISH.md
└── README.md
```

## 🚀 发布到PyPI

详细的发布指南请查看：[PUBLISH.md](PUBLISH.md)

### 快速发布步骤

```bash
# 1. 安装构建工具
pip install build twine

# 2. 构建包
python -m build

# 3. 上传到PyPI
twine upload dist/*
```

## 📖 API文档

- [通义万相视频编辑API文档](https://help.aliyun.com/zh/model-studio/wanx-vace-api-reference)
- [MCP Python SDK文档](https://github.com/modelcontextprotocol/python-sdk)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License


