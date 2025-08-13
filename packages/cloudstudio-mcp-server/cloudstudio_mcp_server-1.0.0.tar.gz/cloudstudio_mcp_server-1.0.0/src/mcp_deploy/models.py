
from dataclasses import dataclass
from typing import Optional, Dict, Any
from dataclasses import asdict
import json

@dataclass
class Connections:
    """连接信息"""
    webIDE: str        # web IDE访问入口
    ssh: Optional[str] = None     # ssh访问连接
    pty: Optional[str] = None     # 终端连接入口
    preview: Optional[str] = None # 端口预览访问入口
    api: Optional[str] = None      # API访问入口
    jupyterServer: Optional[str] = None     # Jupyter访问入口
    agent: Optional[str] = None    #  agent 访问入口

@dataclass
class StatusError:
    """错误信息"""
    code: int           # 错误码
    msg: str        # 错误的详细描述信息

@dataclass
class WorkspaceStatus:
    """工作空间状态"""
    status: str         # 当前状态：STOPPED/PENDDING/RUNNING/ERROR
    error: Optional[StatusError] = None  # 当状态为ERROR时的错误信息
    nodeName: Optional[str] = None     # 节点名
    nodeId: Optional[str] = None       # 节点id
    lastStartTime: Optional[str] = None      # 最后一次运行时间
    lastStopTime: Optional[str] = None       # 最后一次停止时间
    lastTransitionTime: Optional[str] = None # 最后一次状态变化时间

@dataclass
class RuntimePool:
    """资源池配置"""
    name: str
    ownerToken: str

@dataclass
class Runtime:
    """运行时配置"""
    pool: Optional[RuntimePool] = None

@dataclass
class VGPUConfig:
    """虚拟化共享型GPU配置"""
    core: str    # 核心数量，1代表1个GPU核心
    memory: str  # GPU内存

@dataclass
class GPUConfig:
    """虚拟化独享型GPU配置"""
    type: str    # GPU类型
    number: int  # 显卡数量，单位为张

@dataclass
class RuntimeSpec:
    """运行时规格配置"""
    cpu = None      # CPU资源规格，如"1"表示一个核心，"0.5"表示0.5核心
    memory = None   # 内存资源规格，如"2G"表示2G内存
    vgpu: Optional[VGPUConfig] = None  # 虚拟化共享型GPU配置
    gpu: Optional[GPUConfig] = None    # 虚拟化独享型GPU配置

@dataclass
class GitSource:
    """Git存储源配置"""
    url: str

@dataclass
class COSSource:
    """COS存储源配置"""
    bucket: str
    region: str
    secretId: Optional[str] = None
    secretKey: Optional[str] = None
    endpoint: Optional[str] = None

@dataclass
class CBDSource:
    """CBD存储源配置"""
    id: str

@dataclass
class StorageSource:
    """存储源配置"""
    type: str  # git/cos/cbd
    git: Optional[GitSource] = None
    cos: Optional[COSSource] = None
    cbd: Optional[CBDSource] = None

@dataclass
class CBDStorage:
    """CBD存储配置"""
    id: str           # 磁盘id
    quota: str        # 磁盘大小，如"0.5G"到"16G"

@dataclass
class Storage:
    """工作目录存储配置"""
    cbd: CBDStorage    # CBD存储配置
    type: str = "cbd"  # 存储类型，目前仅支持cbd

@dataclass
class AdditionalStorageItem:
    """额外存储项配置"""
    type: str  # cos/cbd/host
    readonly: bool = True
    cos: Optional[COSSource] = None
    cbd: Optional[CBDStorage] = None
    host: Optional[dict] = None  # 仅自定义算力支持

@dataclass
class WorkspaceRequest:
    """创建工作空间请求体"""
    runtime_spec: Optional[RuntimeSpec] = None
    storage: Optional[Storage] = None
    runtime: Optional[Runtime] = None
    additional_storage: Optional[Dict[str, AdditionalStorageItem]] = None

    def to_json(self) -> str:
        """将对象转换为JSON字符串"""
        return json.dumps(asdict(self))

@dataclass
class LiteAppRequest:
    """创建应用请求体"""
    title: str
    description = ""
    icon = ""
    cover = ""
    workspace: Optional[WorkspaceRequest] = None

    def to_json(self) -> str:
        """将对象转换为JSON字符串"""
        return json.dumps(asdict(self))

@dataclass
class WorkspaceResponseData:
    """工作空间响应数据"""
    spaceKey: str
    connections: Optional[Connections] = None
    runtime: Optional[Runtime] = None
    runtimeSpec: Optional[RuntimeSpec] = None
    storage: Optional[Storage] = None
    status: Optional[WorkspaceStatus] = None

@dataclass
class WorkspaceResponse:
    """创建工作空间响应"""
    code: int
    msg: str
    data: WorkspaceResponseData

    def to_json(self) -> str:
        """将对象转换为JSON字符串"""
        return json.dumps(asdict(self))

@dataclass
class LiteAppResponseData:
    """工作空间响应数据"""
    title: str
    id: str
    workspace: WorkspaceResponseData


@dataclass
class LiteAppResponse:
    """创建工作空间响应"""
    code: int
    msg: str
    data: LiteAppResponseData

    def to_json(self) -> str:
        """将对象转换为JSON字符串"""
        return json.dumps(asdict(self))

@dataclass
class CommandInput:
    """命令执行输入参数"""
    command: str           # 需要执行的命令字符串
    timeoutMs: Optional[int] = None  # 命令执行超时时间(毫秒)
    maxOutputSize: Optional[str] = None  # 命令最大输出size

    def to_json(self) -> str:
        """将对象转换为JSON字符串"""
        return json.dumps(asdict(self))

@dataclass
class CommandOutput:
    """命令执行输出结果"""
    exitCode: int          # 命令退出码
    stdout: str            # 标准输出
    stderr: str            # 标准错误
    startTime: str         # 命令开始时间
    endTime: str           # 命令结束时间

    @classmethod
    def from_json(cls, json_str: str):
        """从JSON字符串创建对象"""
        data = json.loads(json_str)
        return cls(**data)

@dataclass
class File:
    save_path: str  # 远端保存路径
    file_content: str   # 文件内容

@dataclass
class WriteFilesRequest:
    """写入文件请求"""
    workspace_key: str  # 工作空间key
    region: str  # 区域
    files: list[File]  # 文件列表
    directory: Optional[str] = None  # 本地目录路径，如果提供，将压缩并上传该目录下的所有文件
