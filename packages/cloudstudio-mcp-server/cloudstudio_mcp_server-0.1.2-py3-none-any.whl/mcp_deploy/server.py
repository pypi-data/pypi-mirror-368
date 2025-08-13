import os
from fastmcp import FastMCP
from .mcp_handlers import createworkspace, uploadfile, execute
from .mcp_handlers import File

mcp = FastMCP("mcp-deploy")

# api_token = os.environ.get("API_TOKEN")
api_token = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjM2NzI5NCwiaWF0IjoxNzUzMTY4NzQyLCJleHAiOjE3NjA4ODk2MDAsImp0aSI6Ijc1NTRmNmUxLTVjMWMtNDIwNC05YmJiLTdhZGNhZTBkZmQ3OCJ9.vulm8G70o2e7goDaxhwRnFIzz9tp8pJFQ48d8zUiLHA"
if not api_token:
    raise ValueError("API_TOKEN environment variable is required")
region = os.environ.get("region", "ap-shanghai")

@mcp.tool()
def create_workspace() -> dict:
    """创建新的Cloud Studio工作空间 [MCP标准]

    功能说明:
    - 创建一个全新的Cloud Studio工作空间实例
    - 使用环境变量中的API_TOKEN进行认证
    - 返回包含工作空间ID的字典

    参数要求:
    - 无直接输入参数
    - 依赖环境变量:
      * API_TOKEN: 有效的认证令牌(必填)
      * region: 工作空间所在区域，如'ap-shanghai'(可选)

    返回值:
    {
        "workspace_id": "str",  # 工作空间唯一ID(格式:ws-xxxxxx)
        "webIDE": "str",       # Web IDE访问链接
        "preview": "str"      # 预览链接
    }

    注意事项:
    1. 需要预先设置API_TOKEN环境变量
    2. 每个API_TOKEN有创建频率限制
    3. 返回的workspace_key需要妥善保存
    4. 关于预览链接的使用:
       - 预览链接通常格式为'https://{workspace_id}--{port}.{region}.cloudstudio.club'
       - 如果使用execution_command工具启动了一个服务，则使用改连接来调用服务。例如本地启动的服务监听8000端口，那么预览地址为'https://ws-sv0eammnlvdgemj8ke3en7--8000.ap-shanghai.cloudstudio.club'

    典型响应:
    {
        "workspace_key": "ws-kmhhvqnlogr0il1pyvc48",
        "webIDE": "https://ws-kmhhvqnlogr0il1pyvc48--ide.ap-shanghai.cloudstudio.club",
        "preview": "https://ws-kmhhvqnlogr0il1pyvc48--8000.ap-shanghai.cloudstudio.club"
    }
    """
    result = createworkspace(api_token)
    return result

@mcp.tool()
def write_files(workspace_key: str, region: str, directory: str = None, files: list[File]=[]) -> str:
    """上传文件到指定工作空间

    将多个文件上传到Cloud Studio工作空间，支持文本文件内容的上传和目录上传。

    Args:
        workspace_key (str): 目标工作空间ID，格式如'ws-xxxxxx'
        region (str): 工作空间所在区域，如'ap-shanghai'
        directory (str, optional): 本地目录路径，如果提供，将压缩并上传该目录下的所有文件
        files (list[File], optional): 要上传的文件列表，如果提供，将上传每个文件，每个File对象包含:
            - save_path: str 文件在workspace中的相对路径
            - file_content: str 文件内容(UTF-8编码)

    Returns:
        str: 上传结果信息("上传文件成功"或"上传文件失败")
        工具默认上传到/workspace目录下。例如: save_path="/example/test.txt"会上传到/workspace/example/test.txt

    Raises:
        ValueError: 如果workspace_id格式无效
        IOError: 如果文件上传过程中出现错误
        TypeError: 如果files参数格式不正确
        FileNotFoundError: 如果指定的目录不存在

    Example:
        >>> write_files("ws-123", "ap-shanghai", [{"save_path": "/example/test.txt", "file_content": "print(hello world"}])
        最终文件在/workspace/example/test.txt

        >>> write_files("ws-123", "ap-shanghai", [], directory="/path/to/local/dir")
        将/path/to/local/dir目录下的所有文件上传到/workspace目录

    注意事项:
    directory参数和files参数不能为同时为空，至少需要提供一个。
    如果要上传工程，需要优先提供directory参数，本接口会尝试将目录下的所有文件上传到/workspace目录下。一定不要遍历工程每个文件再上传。
    """

    if workspace_key is None or not workspace_key.startswith("ws-"):
        raise ValueError("Invalid workspace_id format")
    if not files and not directory:
        raise ValueError("No files to upload")

    success = uploadfile(api_token, workspace_key, region, files, directory)
    return success

@mcp.tool()
def execute_command(workspace_key: str, region: str, command: str) -> str:
    """在工作空间中执行命令

    在指定的Cloud Studio工作空间中执行shell命令并返回结果。

    Args:
        workspace_key (str): 目标工作空间ID，格式如'ws-xxxxxx'
        region (str): 工作空间所在区域，如'ap-shanghai'
        command (str): 要执行的shell命令

    Returns:
        str: 命令执行结果输出

    Raises:
        RuntimeError: 如果命令执行失败
        ConnectionError: 如果无法连接到工作空间

    Example:
        >>> execute_command("ws-xxxx", "ap-shanghai", "ls -al")
        'total 4\n-rw-r--r-- 1 root root 12 Jan 1 00:00 test.txt'

    注意事项:
    如果执行的命令启动了本地服务并且对外开放了监听端口，则需要使用preview链接，所以上下文要知道preview链接的拼接规则。
    """

    if workspace_key is None or not workspace_key.startswith("ws-"):
        raise ValueError("Invalid workspace_id format")
    if not command:
        raise ValueError("Command cannot be empty")

    result = execute(api_token, workspace_key, region, command)
    return result

def main():
    mcp.run()

if __name__ == "__main__":
    main()
