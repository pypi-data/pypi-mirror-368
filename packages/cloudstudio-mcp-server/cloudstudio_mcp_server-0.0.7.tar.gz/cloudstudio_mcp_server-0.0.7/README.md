# Cloud Studio MCP 部署服务

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)

Cloud Studio MCP 部署服务是一个基于FastMCP的服务器，提供Cloud Studio工作空间的管理功能，包括创建工作空间、上传文件和执行命令等操作。

## 功能特性

- **创建工作空间**：创建新的Cloud Studio工作空间实例
- **文件管理**：上传文件到指定工作空间
- **命令执行**：在工作空间中执行shell命令
- **MCP集成**：通过MCP协议提供标准化接口

## 安装指南

### 前置要求

- Python 3.8+
- API_TOKEN环境变量（Cloud Studio API访问令牌）

### 安装步骤

1. 克隆仓库：
   ```bash
   git clone <repository-url>
   cd mcp_deploy
   ```

2. 创建并激活虚拟环境：
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .\.venv\Scripts\activate   # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -e .
   ```

## 配置说明

在运行服务前，需要设置以下环境变量：

```bash
export API_TOKEN="your_cloud_studio_api_token"
export region="ap-shanghai"  # 可选，默认为ap-shanghai
```

## 使用说明

### 启动服务

```bash
python -m mcp_deploy
```

### API 文档

服务提供以下MCP工具：

#### 1. 创建工作空间

```python
create_workspace() -> dict
```
返回示例：
```json
{
    "workspace_key": "kmhhvqnlogr48",
    "webIDE": "https://kmhhv1pyvc48--ide.ap-shanghai.cloudstudio.club"
}
```

#### 2. 上传文件

```python
write_files(workspace_key: str, region: str, files: list[File]) -> str
```
文件格式：
```python
class File:
    save_path: str    # 文件保存路径
    file_content: str # 文件内容(UTF-8编码)
```

#### 3. 执行命令

```python
execute_command(workspace_key: str, region: str, command: str) -> str
```
示例：
```python
execute_command("xxxx", "ap-shanghai", "ls -al")
```

## 开发指南

### 项目结构

```
mcp_deploy/
├── __init__.py
├── __main__.py
├── mcp_handlers.py    # 核心业务逻辑
├── models.py          # 数据模型定义
└── server.py          # FastMCP服务器实现
```

### 测试

1. 确保已设置API_TOKEN环境变量
2. 运行测试命令：
   ```bash
   python -m pytest
   ```

## 贡献

欢迎提交Pull Request或Issue报告问题。

## 许可证

[MIT License](LICENSE)