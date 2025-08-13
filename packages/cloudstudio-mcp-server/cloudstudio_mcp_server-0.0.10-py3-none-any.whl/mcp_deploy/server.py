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
    """在工作空间中执行命令（nohup后台运行，当前目录为/workspace）

    在指定的Cloud Studio工作空间中执行shell命令并返回结果，适用于需要长期运行的服务启动场景，且无需保留输出日志。
    注意：当前工作目录（cwd）已默认设置为 `/workspace`，无需在命令中额外添加 `cd /workspace`。

    Args:
        workspace_key (str): 目标工作空间ID，格式如'xxxxxx'
        region (str): 工作空间所在区域，如'ap-shanghai'
        command (str): 要执行的shell命令。
            关键要求：若命令用于启动服务（如npm start、python server.py等长期运行的进程），**必须使用`nohup`进行持久化后台运行**，且不生成日志文件，格式为：
            `nohup [服务命令] > /dev/null 2>&1 &`
            其中：
            - `nohup`：确保终端关闭后进程不终止；
            - `> /dev/null`：将标准输出丢弃（不生成日志文件）；
            - `2>&1`：将错误输出合并到标准输出，一同丢弃；
            - `&`：将进程放入后台运行，不阻塞命令返回。
            服务启动后，**必须执行`lsof -i:端口号`（替换为实际端口）检查端口是否处于监听状态**，确认服务启动成功。
            （无需包含`cd /workspace`，当前目录已默认为此路径）

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
        # 错误示例（多余添加cd /workspace）
        >>> execute_command("xxxx", "ap-shanghai", "cd /workspace && nohup npm start > /dev/null 2>&1 &")  # 错误：无需cd，当前目录已为/workspace

        # 正确示例（直接执行命令，无需cd）
        >>> # 1. 用nohup启动服务（3000端口），当前目录为/workspace
        >>> execute_command("xxxx", "ap-shanghai", "nohup npm start > /dev/null 2>&1 &")
        >>> # 2. 等待服务初始化（根据启动速度调整秒数，如3秒）
        >>> execute_command("xxxx", "ap-shanghai", "sleep 3")
        >>> # 3. 检查3000端口是否监听成功
        >>> execute_command("xxxx", "ap-shanghai", "lsof -i:3000")
        'COMMAND  PID  USER   FD   TYPE DEVICE SIZE/OFF NODE NAME\nnode    1234 root    5u  IPv4  12345      0t0  TCP *:3000 (LISTEN)'

    注意事项:
    1. 当前工作目录固定为 `/workspace`，所有命令默认在此路径下执行，无需额外添加 `cd /workspace`，避免多余操作。
    2. 长期运行的服务必须用`nohup ... > /dev/null 2>&1 &`启动，确保进程在终端关闭后不终止且不生成日志文件。
    3. 若服务启动失败（端口检查无结果），可临时去掉`> /dev/null 2>&1`（即`nohup [服务命令] &`），通过默认生成的nohup.out日志排查错误（如`cat nohup.out`），排查后恢复原格式。
    4. 端口检查前需添加`sleep N`（如3-10秒），等待服务完成初始化，避免因检查过早导致误判。
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
