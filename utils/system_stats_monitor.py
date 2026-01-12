import psutil
from utils.logger import log_debug

def log_system_usage():
    process = psutil.Process()
    mem = process.memory_info()
    log_debug(f"Memory usage: {mem.rss / 1024 ** 2:.2f} MB")
