import os
from fastmcp import FastMCP
from .mcp_handlers import createLiteapp, uploadfile, execute
from .mcp_handlers import File

mcp = FastMCP("mcp-deploy")

print("=== 代码已更新：2025-08-12 16:43 ===")
api_token = os.environ.get("API_TOKEN")
if not api_token:
    raise ValueError("API_TOKEN environment variable is required")
region = os.environ.get("region", "ap-shanghai")

@mcp.tool()
def create_workspace(title: str) -> dict:
    """创建新的Cloud Studio工作空间 [MCP标准]

    功能说明:
    - 创建一个全新的Cloud Studio工作空间实例
    - 使用环境变量中的API_TOKEN进行认证
    - 返回包含工作空间ID的字典

    参数要求:
    {
        "title": "str" # 项目名称
    }
    - 依赖环境变量:
      * API_TOKEN: 有效的认证令牌(必填)
      * region: 工作空间所在区域，如'ap-shanghai'(可选)

    返回值:
    {
        "edit_url": "str",     # 编辑器访问地址
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
        "workspace_key": "kmhhvqnlogr0il1pyvc48",
        "lite_app_id": "1234566",
        "title": "xxx",
        "webIDE": "https://kmhhvqnlogr0il1pyvc48--ide.ap-shanghai.cloudstudio.club",
        "preview": "https://kmhhvqnlogr0il1pyvc48--8000.ap-shanghai.cloudstudio.club"

    }
    """
    result = createLiteapp(api_token,title)
    return result

@mcp.tool()
def write_files(workspace_key: str, region: str, directory: str = None, files: list[File]=[]) -> dict:
    """上传文件到指定工作空间

    将多个文件上传到Cloud Studio工作空间，支持文本文件内容的上传和目录上传。

    Args:
        workspace_key (str): 目标工作空间ID，格式如'xxxxxx'
        region (str): 工作空间所在区域，如'ap-shanghai'
        directory (str, optional): 本地目录路径，如果提供，将压缩并上传该目录下的所有文件，例如传递/example/demo,最终demo的所有文件都会在/workspace 下，不会额外创建demo文件夹
        files (list[File], optional): 要上传的文件列表，如果提供，将上传每个文件，每个File对象包含:
            - save_path: str 文件在workspace中的相对路径，例如/example/xxx.txt 最终路径是 /workspace/example/xxx.txt
            - file_content: str 文件内容(UTF-8编码)

    Returns:
        status: str # 上传结果信息 completed 代表完成
        total_operations: int # 总共文件数
        success_count: int # 成功文件数
        failed_count: int # 失败文件数
        details: array # 解压结果

    Raises:
        ValueError: 如果workspace_id格式无效
        IOError: 如果文件上传过程中出现错误
        TypeError: 如果files参数格式不正确
        FileNotFoundError: 如果指定的目录不存在

    Example:
        >>> write_files("123", "ap-shanghai", [{"save_path": "/example/test.txt", "file_content": "print(hello world"}])
        最终文件在/workspace/example/test.txt

        >>> write_files("123", "ap-shanghai", [], directory="/local/dir")
        将/local/dir目录下的所有文件上传到/workspace目录

    注意事项:
    directory参数和files参数不能为同时为空，至少需要提供一个。
    如果用户需要上传工程或者项目，优先提供directory参数，本接口会尝试将目录下的所有文件上传到/workspace目录下。一定不要遍历工程每个文件再上传。
    """

    if workspace_key is None:
        raise ValueError("Invalid workspace_id format")
    if not files and not directory:
        raise ValueError("No files to upload")

    success = uploadfile(api_token, workspace_key, region, files, directory)
    return success

@mcp.tool()
def execute_command(workspace_key: str, region: str, command: str) -> dict:
    """在工作空间中执行命令

    在指定的Cloud Studio工作空间中执行shell命令并返回结果。

    Args:
        workspace_key (str): 目标工作空间ID，格式如'xxxxxx'
        region (str): 工作空间所在区域，如'ap-shanghai'
        command (str): 要执行的shell命令，如果是为了启动服务,尽可能使用nohup后台运行，并额外使用lsof -i检查端口号是否运行成功

    Returns:
        exitCode: int # 进程退出码，0 表示成功，非 0 表示失败
        stdout: str # 进程的标准输出内容
        stderr: str # 进程的标准错误输出内容（若有错误）
        startTime: int # 进程开始时间(秒级时间戳)
        endTime: int # 进程结束时间（秒级时间戳）

    Raises:
        RuntimeError: 如果命令执行失败
        ConnectionError: 如果无法连接到工作空间

    Example:
        >>> execute_command("xxxx", "ap-shanghai", "ls -al")
        'total 4\n-rw-r--r-- 1 root root 12 Jan 1 00:00 test.txt'

    注意事项:
    如果执行的命令启动了本地服务并且对外开放了监听端口，则需要使用preview链接，所以上下文要知道preview链接的拼接规则。如果需要长期运行，需要使用nohup后台运行方式，并调用该接口使用lsof探测对应端口是否启动成功
    """

    if workspace_key is None:
        raise ValueError("Invalid workspace_id format")
    if not command:
        raise ValueError("Command cannot be empty")

    result = execute(api_token, workspace_key, region, command)
    return result

def main():
    mcp.run()

if __name__ == "__main__":
    main()
