import asyncio
import time

try:
    from monitor.get_process_name import *
except:
    from get_process_name import *
import psutil
import subprocess


class MacPerformance:

    def __init__(self, pid, interval=1):
        super(MacPerformance, self).__init__()
        if pid is None or not psutil.pid_exists(pid):
            print(f'进程{pid}不存在，停止监测')
            return
        self.interval = interval
        self.pid = pid
        self.process = self.get_process(pid)
        self.process_cpu_percent = 0
        self.system_cpu_percent = 0
        self.real_mem = 0
        self.private_mem = 0
        self.mem_percent = 0
        self.thread_count = 0
        self.io_read_bytes = 0
        self.io_write_bytes = 0
        self.header = ['时间',
                       'App CPU/%',
                       'System CPU/%',
                       '专用内存/MB',
                       '实际内存/MB',
                       'App内存使用率/%',
                       '线程数',
                       'IO(Read)/kb',
                       'IO(Write)/kb']

    def get_all_data(self):
        if self.process is not None:
            self.get_system_cpu_percent_usage()  # system cpu
            self.get_app_cpu_percent_usage()  # app cpu
            self.get_app_memory_usage()  # app memory
            io_read_bytes_1, io_write_bytes_1 = self.get_disk_usage()  # io read/write
            time.sleep(self.interval)
            io_read_bytes_2, io_write_bytes_2 = self.get_disk_usage()  # io read/write
            self.io_read_bytes = round((io_read_bytes_2 - io_read_bytes_1) / 1024, 2)  # io read/kb
            self.io_write_bytes = round((io_write_bytes_2 - io_write_bytes_1) / 1024, 2)  # io write/kb

    def get_system_cpu_percent_usage(self):
        '''
        获取系统cpu占比
        :return:
        '''
        system_times = psutil.cpu_times_percent()
        self.system_cpu_percent = round(100 - system_times.idle, 2)
        return self.system_cpu_percent

    def get_app_cpu_percent_usage(self):
        '''
        获取进程cpu占比
        :param pid:
        :return:
        '''
        try:
            self.process_cpu_percent = self.process.cpu_percent()
            return self.process_cpu_percent
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return 0

    def get_app_memory_usage(self):
        '''
        获取进程的内存使用情况
        :return:
        '''
        process_memory = self.process.memory_info()
        self.mem_percent = u'%.2f' % (self.process.memory_percent())  # 内存利用率
        self.real_mem = round(process_memory.rss / 1024 / 1024, 2)  # 实际内存
        self.private_mem = self.get_private_memory()  # 专用内存/MB
        self.thread_count = self.process.num_threads()  # 线程总数
        return self.real_mem, self.private_mem, self.mem_percent, self.thread_count

    def get_private_memory(self):
        try:
            command = "top -pid {} -l 1 | tail -n 1 | awk '{{print $8}}'".format(self.pid)
            memory_info = subprocess.check_output(command, shell=True).decode().strip().replace('M', '')
            return int(memory_info)
        except:
            return 0

    def get_disk_usage(self):
        '''
        获取进程磁盘读写情况
        :return:
        '''
        if self.process is not None:
            try:
                io_counters = psutil.disk_io_counters()
                io_read_bytes = io_counters.read_bytes
                io_write_bytes = io_counters.write_bytes
                return io_read_bytes, io_write_bytes
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                return 0, 0

    async def get_all_monitor(self):
        await asyncio.gather(self.get_all_data())
        return self.get_all_usage()

    def get_all_usage(self):
        return [
            self.process_cpu_percent,  # 0
            self.system_cpu_percent,  # 1
            self.private_mem,  # 2
            self.real_mem,  # 3
            self.mem_percent,  # 4
            self.thread_count,  # 5
            self.io_read_bytes,  # 7
            self.io_write_bytes  # 8
        ]

    def get_process(self, pid):
        '''
        通过pid实例化process
        :param pid:
        :return:
        '''
        if pid is None:
            print(f'进程{pid}为None')
            return None
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            return process
        else:
            print(f'进程{pid}不存在')
            return None
