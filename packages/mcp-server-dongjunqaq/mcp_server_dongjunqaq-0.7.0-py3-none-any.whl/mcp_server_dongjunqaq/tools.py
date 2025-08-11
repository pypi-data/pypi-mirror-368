import os
import platform
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import psutil
from openai import OpenAI
from yt_dlp import YoutubeDL


def get_platform_info() -> dict:
    """获取平台的相关信息"""
    platform_info: dict[str:str] = {
        "操作系统": platform.system(),
        "系统发行版本": platform.release(),
        "系统版本信息": platform.version(),
        "平台网络名": platform.node(),
        "平台架构": platform.machine(),
        "CPU信息": platform.processor(),
        "总内存(GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),  # round(...,2)将一个数四舍五入并保留2位小数
    }
    return platform_info


def get_env(key: str) -> str:
    """获取指定环境变量的值"""
    path_env = os.getenv(key)
    return path_env


def get_compress_format() -> dict:
    """获取支持的压缩格式"""
    return {".zip": "zip", ".tar": "tar", ".tar.gz": "gztar", ".tar.bz": "bztar", ".tar.xz": "xztar"}


def make_archive(src: str, compress_format: str) -> str:
    """
    打包并压缩指定内容；
    :param src:需要打包的文件或目录
    :param compress_format:压缩格式
    :return:打包后文件的完整路径
    """
    src_abs = os.path.abspath(src)  # 获取源文件/目录的绝对路径
    if os.path.isfile(src_abs):  # 判断源路径是否为文件，压缩单个文件时需要传递4个参数
        dir_path = os.path.dirname(src_abs)
        file_name = os.path.basename(src_abs)
        shutil.make_archive(src_abs, compress_format, dir_path, file_name)
    else:
        shutil.make_archive(src_abs, compress_format, src_abs)
    return f'已打包为{src_abs}.{compress_format}文件'


def decompress(src: str) -> str:
    """解压缩指定的压缩文件，返回解压后存放文件的目录"""
    src_abs = os.path.abspath(src)
    parent_dir = os.path.dirname(src_abs)
    file_basename = os.path.splitext(os.path.basename(src_abs))[0]  # 获取压缩文件的文件名（不含后缀）
    while Path(file_basename).suffix:  # 处理多重后缀（如.tar.gz、.tar.bz2等）
        file_basename = os.path.splitext(file_basename)[0]  # 确保只获取纯文件名
    # 解压前先在同级目录下创建一个与该压缩包同名的目录，然后将解压后的内容存放至该目录中
    target_dir = os.path.join(parent_dir, file_basename)
    os.makedirs(target_dir, exist_ok=True)
    file_suffix = Path(src_abs).suffix  # 获取文件后缀，判断压缩类型
    if file_suffix == ".zip":
        with zipfile.ZipFile(src_abs, 'r') as zip_ref:
            # 解决解压后中文文件名乱码的问题
            for file_info in zip_ref.infolist():
                file_info.filename = file_info.filename.encode('utf-8').decode('utf-8')
                zip_ref.extract(file_info, target_dir)  # 解压文件到指定目录
    else:
        with tarfile.open(src_abs, 'r') as tar:
            tar.extractall(path=target_dir)
    return f"所有文件均已解压到 {target_dir} 目录"


def download_video(url: str) -> str:
    """下载指定URL的视频至用户的家目录的Downloads文件夹中，并返回下载后文件的绝对路径"""
    download_dir = Path.home() / "Downloads"  # 会自动处理不同系统的路径分隔符
    os.makedirs(download_dir, exist_ok=True)  # 确保有系统中存在Downloads目录，没有则自动创建
    ydl_opts = {
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),  # 格式化为"Downloads目录/视频标题.扩展名"
    }
    with YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(url, download=True)  # 获取视频信息并执行下载
        video_file_name = ydl.prepare_filename(video_info)  # 获取下载文件的文件名（包含路径）
        video_absolute_path = os.path.abspath(video_file_name)  # 将文件名转换为绝对路径
        return video_absolute_path


def query_command(require: str) -> str:
    # """根据用户输入的需求通过大模型去查询相应的命令并返回此命令（仅返回命令无需返回其他的文本）"""
    """根据用户输入的需求通过大模型去查询Windows或Linux操作系统的命令并返回此命令以及完整的命令说明"""
    client = OpenAI(api_key=os.environ.get("API_KEY"), base_url=os.environ.get("BASE_URL"), )
    response = client.chat.completions.create(
        model=os.environ.get("MODEL"),
        messages=[
            {"role": "system",
             # "content": "你现在是一名运维工程师，你负责保障系统和服务的正常运行。你熟悉各种监控工具，能够高效地处理故障和进行系统优化。你还懂得如何进行数据备份和恢复，以保证数据安全。请在这个角色下为我解答以下问题。当我问你有关Linux或Windows命令的问题时，你只需告诉我具体的命令即可无需多余的文字。"},
             "content": "你现在是一名运维工程师，你负责保障系统和服务的正常运行。你熟悉各种监控工具，能够高效地处理故障和进行系统优化。你还懂得如何进行数据备份和恢复，以保证数据安全。请在这个角色下为我解答以下问题。只需返回相关命令以及命令说明无需返回图形化界面的内容"},
            {"role": "user", "content": f"在{platform.system()}系统中{require}"},  # 提问前先获取平台系统
        ],
        stream=False
    )
    results = response.choices[0].message.content
    return results


def execute_command(command: str) -> str:
    """提取出query_command工具返回的命令（只提取对应主机系统的命令无需任何多余文字）并自动执行读取类命令，无法自动执行写入、删除之类的命令并警告用户后果，最后返回命令执行的结果"""
    run_result = "未知系统，无法执行命令"
    if platform.system() == "Windows":
        result = subprocess.run(["powershell", "-Command", command], text=True,
                                capture_output=True)  # text=True：命令的输出结果将以字符串形式返回，否则以字节流形式返回，capture_output=True：表示捕获命令的标准输出（stdout）和标准错误（stderr）
        run_result = f"标准输出:\n{result.stdout}\n标准错误:\n{result.stderr}"
    elif platform.system() == "Linux":
        result = subprocess.run(command, shell=True, text=True, capture_output=True)  # 若命令通过空格相连则需加上shell=True
        run_result = f"标准输出:\n{result.stdout}\n标准错误:\n{result.stderr}"
    return run_result
