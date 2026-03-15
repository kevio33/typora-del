import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_log_dir() -> Path:
    """获取日志目录路径，自动创建 /log/ 目录"""
    log_dir = Path(__file__).parent / "log"
    log_dir.mkdir(exist_ok=True)
    return log_dir


def generate_log_filename() -> str:
    """生成带时间戳的日志文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"typora_del_{timestamp}.log"


def setup_logger(log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    设置并返回 logger 实例
    
    Args:
        log_file: 日志文件路径，默认使用自动生成的文件名
        level: 日志级别，默认 INFO
    
    Returns:
        配置好的 logger 实例
    """
    logger = logging.getLogger("typora_del")
    logger.setLevel(level)
    
    if logger.handlers:
        return logger
    
    if log_file is None:
        log_dir = get_log_dir()
        log_file = str(log_dir / generate_log_filename())
    
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    
    formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger


def get_logger() -> logging.Logger:
    """
    获取已配置的 logger 实例
    
    Returns:
        logger 实例
    """
    logger = logging.getLogger("typora_del")
    if not logger.handlers:
        return setup_logger()
    return logger


def log_message(message: str, level: int = logging.INFO) -> None:
    """
    统一的日志记录接口
    
    Args:
        message: 日志消息
        level: 日志级别
    """
    logger = get_logger()
    logger.log(level, message)


def log_operation_start(operation: str) -> None:
    """记录操作开始时间"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message(f"[开始] {operation} - {timestamp}")


def log_operation_end(operation: str, duration: float) -> None:
    """记录操作结束时间和耗时"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message(f"[结束] {operation} - {timestamp} (耗时：{duration:.2f}秒)")


def log_input_path(path: str, description: str = "输入路径") -> None:
    """记录输入路径"""
    log_message(f"[{description}] {path}")


def log_processing_detail(detail: str) -> None:
    """记录处理详情"""
    log_message(f"[详情] {detail}")


def log_deleted_files(files: list[str]) -> None:
    """记录删除文件列表"""
    log_message(f"[删除文件] 共 {len(files)} 个文件:")
    for file in files:
        log_message(f"  - {file}")


def log_statistics(stats: dict) -> None:
    """记录统计信息"""
    log_message("[统计信息]")
    for key, value in stats.items():
        log_message(f"  - {key}: {value}")
