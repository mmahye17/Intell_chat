from loguru import logger
import sys
import os

# 防止重复初始化
_logger_initialized = False


def setup_logger():
    global _logger_initialized

    if _logger_initialized:
        return logger

    logger.remove()

    # ==================== 控制台输出 ====================
    logger.add(
        sys.stdout,
        level="DEBUG",
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # ==================== 文件输出（固定在 app/logs） ====================
    # 获取 app 目录的绝对路径
    current_file = __file__  # 当前 logger_config.py 的路径
    app_dir = os.path.dirname(os.path.dirname(current_file))  # 上两级 = app 目录
    log_dir = os.path.join(app_dir, "logs")

    # 确保 logs 文件夹存在
    os.makedirs(log_dir, exist_ok=True)

    logger.add(
        os.path.join(log_dir, "app_{time:YYYY-MM-DD}.log"),  # 日志文件路径
        rotation="00:00",  # 每天 0 点切割新文件
        retention="15 days",  # 保留15天日志
        level="INFO",  # 文件只记录 INFO 及以上级别
        encoding="utf-8",
        enqueue=True,  # 异步写入，防止阻塞
        backtrace=True,  # 错误时打印详细堆栈
        diagnose=True  # 打印更详细的诊断信息
    )

    _logger_initialized = True
    logger.info(f"📁 日志系统初始化完成，日志目录: {log_dir}")
    return logger


# 模块被导入时自动执行
logger = setup_logger()