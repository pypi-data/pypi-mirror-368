try:
    import wmi
except:
    pass
import time
import ctypes
import asyncio
import psutil

# 定义Win32 API函数
GetLastError = ctypes.windll.kernel32.GetLastError
GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
OpenProcess = ctypes.windll.kernel32.OpenProcess
GetSystemTimes = ctypes.windll.kernel32.GetSystemTimes
GetProcessTimes = ctypes.windll.kernel32.GetProcessTimes
GetProcessIoCounters = ctypes.windll.kernel32.GetProcessIoCounters
PROCESS_VM_READ = 0x0010
# 权限
PROCESS_QUERY_INFORMATION = 0x0400


class WinPerformance:

    def __init__(self, pid, interval=1):
        if pid is None or not psutil.pid_exists(pid):
            print(f'进程{pid}不存在，停止监测')
            return
        self.pid = pid
        self.interval = interval
        self.app_cpu_percent = 0
        self.system_cpu_percent = 0
        self.memory_private = 0
        self.memory_workset = 0
        self.memory_percent = 0
        self.thread_count = 0
        self.io_read_speed = 0
        self.io_write_speed = 0
        self.header = ['时间',
                       'App CPU/%',
                       'System CPU/%',
                       '内存(Private)/MB',
                       '内存(WorkSet)/MB',
                       'App内存使用率/%',
                       '线程数',
                       'IO(Read)/b',
                       'IO(Write)/b',
                       ]

    def get_cpu_percent(self):
        hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, False, self.pid)
        if hProcess == 0:
            print(f"Error: {GetLastError()}")
            return None
        FILETIME = ctypes.c_longlong * 2
        lpCreationTime, lpExitTime = FILETIME(), FILETIME()
        lpKernelTime, lpUserTime = FILETIME(), FILETIME()
        lpIdleTime, lpKernelTime2 = FILETIME(), FILETIME()
        # 获取前1s数据
        GetProcessTimes(hProcess, ctypes.byref(lpCreationTime), ctypes.byref(lpExitTime),
                        ctypes.byref(lpKernelTime), ctypes.byref(lpUserTime))
        GetSystemTimes(ctypes.byref(lpIdleTime), ctypes.byref(lpKernelTime2), None)
        kernel_time_start = lpKernelTime[0] + (lpKernelTime[1] << 32)
        user_time_start = lpUserTime[0] + (lpUserTime[1] << 32)
        idle_time_start = lpIdleTime[0] + (lpIdleTime[1] << 32)

        io_counters_start = self.get_io_counters()
        time.sleep(self.interval)
        # 获取当前数据
        GetProcessTimes(hProcess, ctypes.byref(lpCreationTime), ctypes.byref(lpExitTime),
                        ctypes.byref(lpKernelTime), ctypes.byref(lpUserTime))
        GetSystemTimes(ctypes.byref(lpIdleTime), ctypes.byref(lpKernelTime2), None)
        kernel_time_end = lpKernelTime[0] + (lpKernelTime[1] << 32)
        user_time_end = lpUserTime[0] + (lpUserTime[1] << 32)
        idle_time_end = lpIdleTime[0] + (lpIdleTime[1] << 32)
        # CPU总时间
        total_time = (kernel_time_end - kernel_time_start) + (user_time_end - user_time_start)
        # 系统空闲时间
        idle_time = idle_time_end - idle_time_start
        # 计算进程占用的CPU使用率（百分比）
        self.app_cpu_percent = round(100.0 * total_time / (total_time + idle_time), 2)  # app cpu/%
        system_times = psutil.cpu_times_percent()
        self.system_cpu_percent = round(100 - system_times.idle, 2)  # system cpu/%

        if io_counters_start:
            io_counters_end = self.get_io_counters()
            if io_counters_end:
                self.io_read_speed = (
                                             io_counters_end.ReadTransferCount - io_counters_start.ReadTransferCount) / self.interval
                self.io_write_speed = (
                                              io_counters_end.WriteTransferCount - io_counters_start.WriteTransferCount) / self.interval

        return self.app_cpu_percent, self.system_cpu_percent, self.io_read_speed, self.io_write_speed

    def get_memory_usage(self):
        w = wmi.WMI()
        process = w.Win32_Process(ProcessId=self.pid)[0]
        self.memory_private = round(int(process.PrivatePageCount) / 1024 / 1024, 2)  # MB
        self.memory_workset = round(int(process.WorkingSetSize) / 1024 / 1024, 2)  # MB
        try:
            process = psutil.Process(self.pid)
            self.memory_percent = u'%.2f' % process.memory_percent()  # 内存使用率
            self.thread_count = process.num_threads()  # 线程数
        except:
            self.memory_percent = 0
            self.thread_count = 0
        return self.memory_private, self.memory_workset, self.memory_percent, self.thread_count

    def get_io_counters(self):
        counters = IO_COUNTERS()
        hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, False, self.pid)
        if hProcess == 0:
            error_code = ctypes.windll.kernel32.GetLastError()
            print(f"Error opening process (code: {error_code})")
            return None
        if not GetProcessIoCounters(hProcess, ctypes.byref(counters)):
            error_code = ctypes.windll.kernel32.GetLastError()
            print(f"Error getting IO counters (code: {error_code})")
            return None
        ctypes.windll.kernel32.CloseHandle(hProcess)
        return counters

    def get_all_usage(self):
        return [
            self.app_cpu_percent,  # 0
            self.system_cpu_percent,  # 1
            self.memory_private,  # 2
            self.memory_workset,  # 3
            self.memory_percent,  # 6
            self.thread_count,  # 7
            self.io_read_speed,  # 4
            self.io_write_speed,  # 5
        ]

    async def get_all_monitor(self):
        await asyncio.gather(self.get_cpu_percent(), self.get_memory_usage())
        return self.get_all_usage()


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [('ReadOperationCount', ctypes.c_ulonglong),
                ('WriteOperationCount', ctypes.c_ulonglong),
                ('OtherOperationCount', ctypes.c_ulonglong),
                ('ReadTransferCount', ctypes.c_ulonglong),
                ('WriteTransferCount', ctypes.c_ulonglong),
                ('OtherTransferCount', ctypes.c_ulonglong)]
