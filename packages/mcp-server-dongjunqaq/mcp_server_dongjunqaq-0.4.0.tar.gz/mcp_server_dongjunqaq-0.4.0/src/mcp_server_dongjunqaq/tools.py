import os
import platform
import shutil

import psutil
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


def download_video(url: str) -> str:
    """下载指定URL的视频至用户的家目录的Downloads文件夹中，并返回下载后文件的绝对路径"""
    download_dir = os.path.expanduser("~\Downloads")
    os.makedirs(download_dir, exist_ok=True)  # 确保有系统中存在Downloads目录，没有则自动创建
    ydl_opts = {
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),  # 格式化为"Downloads目录/视频标题.扩展名"
    }
    with YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(url, download=True)  # 获取视频信息并执行下载
        video_file_name = ydl.prepare_filename(video_info)  # 获取下载文件的文件名（包含路径）
        video_absolute_path = os.path.abspath(video_file_name)  # 将文件名转换为绝对路径
        return video_absolute_path
