import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import os

class Logger:
    def __init__(self, log_dir='log', log_file_prefix='main', backup_count=7):
        '''
        初始化日志系统

        :param log_dir: 日志文件保存目录，默认 "log"
        :param log_file_prefix: 日志文件名前缀，默认 "main"，最终日志文件形如 main.log、main.log.2024-06-02
        :param backup_count: 最多保留的历史日志文件数量
        '''
        self.log_dir = log_dir
        self.log_file_prefix = log_file_prefix
        self.backup_count = backup_count
        self.logger = logging.getLogger()  # 获取全局 root logger

        self._setup_logger()        # 设置日志输出文件、格式等
        self._redirect_streams()    # 将 print 输出重定向到日志系统
        self._setup_exception_hook() # 捕获未处理异常并记录日志

    class LoggerWriter:
        '''
        自定义流处理器，用于将 sys.stdout 和 sys.stderr 的输出重定向到 logger
        '''
        def __init__(self, level_func):
            self.level_func = level_func  # 日志等级函数，例如 logger.info / logger.error
            self.buffer = ""              # 缓冲区，用于按行处理日志

        def write(self, message):
            if not message:
                return
            lines = (self.buffer + message).splitlines(keepends=True)
            for line in lines:
                if line.endswith('\n'):
                    self.level_func(line.rstrip('\n'))
                else:
                    self.buffer = line
            if message.endswith('\n'):
                self.buffer = ''

        def flush(self):
            '''
            将缓存内容写入日志
            '''
            if self.buffer:
                self.level_func(self.buffer.strip())  # 写入日志
                self.buffer = ""  # 清空缓冲

        def isatty(self):
            '''
            用于兼容某些调用，如 tqdm 进度条判断是否是终端设备
            '''
            return False

        def fileno(self):
            '''
            获取底层文件描述符(file descriptor)，用于兼容如 subprocess、tqdm 等需要访问标准输出/错误的库。

            如果当前 LoggerWriter 是用来重定向到 logger.info，则返回原始标准输出 sys.__stdout__ 的文件描述符；
            否则返回原始标准错误 sys.__stderr__ 的文件描述符。

            这是为了让使用 sys.stdout.fileno() 或 sys.stderr.fileno() 的库不会报错。
            '''
            return sys.__stdout__.fileno() if self.level_func == logging.getLogger().info else sys.__stderr__.fileno()


    def _setup_logger(self):
        '''
        设置日志系统，启用按天自动切割日志，保留指定数量历史文件
        '''
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.logger.setLevel(logging.INFO)  # 设置日志级别为 INFO，可改为 DEBUG

        log_path = os.path.join(self.log_dir, f"{self.log_file_prefix}.log")

        # 设置按“每天”切分的日志处理器
        handler = TimedRotatingFileHandler(
            filename=log_path,      # 主日志文件
            when='midnight',        # 每天午夜创建新文件
            interval=1,             # 每 1 天切一次
            backupCount=self.backup_count,  # 最多保留多少份
            encoding='utf-8',
            utc=False               # 使用本地时间
        )
        handler.suffix = "%Y-%m-%d"  # 日志文件后缀格式

        # 日志输出格式：[时间] 等级: 消息
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        handler.setFormatter(formatter)

        # 防止重复添加 handler，清空旧的
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.logger.addHandler(handler)                     # 文件输出
        self.logger.addHandler(logging.StreamHandler(sys.__stdout__))  # 控制台输出

    def _redirect_streams(self):
        '''
        重定向标准输出和错误输出到日志系统中
        '''
        sys.stdout = self.LoggerWriter(self.logger.info)    # print 内容 → info 日志
        sys.stderr = self.LoggerWriter(self.logger.error)   # 异常、错误 → error 日志

    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        '''
        捕获未处理异常并写入日志
        '''
        if issubclass(exc_type, KeyboardInterrupt):
            # 如果是 Ctrl+C 中断，则不要记录日志，只输出原始信息
            sys.__stderr__.write("KeyboardInterrupt detected, exiting.\n")
            return
        self.logger.error("未处理异常：", exc_info=(exc_type, exc_value, exc_traceback))

    def _setup_exception_hook(self):
        '''
        设置全局异常捕获钩子
        '''
        sys.excepthook = self._handle_exception
