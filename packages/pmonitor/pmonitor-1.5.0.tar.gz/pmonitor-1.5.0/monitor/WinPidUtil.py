import ctypes
from ctypes import wintypes, byref, windll

import psutil

# 定义以及初始化 API 函数和类型
GetSystemTimes = ctypes.windll.kernel32.GetSystemTimes
GetProcessTimes = ctypes.windll.kernel32.GetProcessTimes
OpenProcess = ctypes.windll.kernel32.OpenProcess
GetProcessIoCounters = ctypes.windll.kernel32.GetProcessIoCounters
# 权限
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
GetCurrentProcessId = ctypes.windll.kernel32.GetCurrentProcessId
CloseHandle = ctypes.windll.kernel32.CloseHandle


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [('ReadOperationCount', ctypes.c_ulonglong),
                ('WriteOperationCount', ctypes.c_ulonglong),
                ('OtherOperationCount', ctypes.c_ulonglong),
                ('ReadTransferCount', ctypes.c_ulonglong),
                ('WriteTransferCount', ctypes.c_ulonglong),
                ('OtherTransferCount', ctypes.c_ulonglong)]


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD),
                ("dwHighDateTime", wintypes.DWORD)]


# 定义保存进程内存信息结果
class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('PageFaultCount', wintypes.DWORD),
        ('PeakWorkingSetSize', ctypes.c_size_t),
        ('WorkingSetSize', ctypes.c_size_t),
        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
        ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
        ('PagefileUsage', ctypes.c_size_t),
        ('PeakPagefileUsage', ctypes.c_size_t),
        ('PrivateUsage', ctypes.c_size_t),
    ]


PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

# 定义关闭句柄所需的Windows函数
CloseHandle = windll.kernel32.CloseHandle
CloseHandle.restype = wintypes.BOOL
CloseHandle.argtypes = [wintypes.HANDLE]

# 函数签名
GetSystemTimes.restype = wintypes.BOOL
GetProcessTimes.restype = wintypes.BOOL
OpenProcess.restype = wintypes.HANDLE
CloseHandle.restype = wintypes.BOOL
GetProcessTimes.argtypes = [
    wintypes.HANDLE,  # hProcess
    ctypes.POINTER(FILETIME),  # lpCreationTime
    ctypes.POINTER(FILETIME),  # lpExitTime
    ctypes.POINTER(FILETIME),  # lpKernelTime
    ctypes.POINTER(FILETIME)  # lpUserTime
]


class PidWinPerformance:

    def filetime_to_100nano_seconds(self, filetime):
        return (filetime.dwHighDateTime << 32) + filetime.dwLowDateTime

    def get_process_cpu_time(self, pid):
        process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
        if not process_handle:
            return None

        kernel_time = FILETIME()
        user_time = FILETIME()
        if not ctypes.windll.kernel32.GetProcessTimes(process_handle,
                                                      byref(FILETIME()),  # ignore creation_time
                                                      byref(FILETIME()),  # ignore exit_time
                                                      byref(kernel_time),
                                                      byref(user_time)):
            ctypes.windll.kernel32.CloseHandle(process_handle)
            return None

        ctypes.windll.kernel32.CloseHandle(process_handle)
        return self.filetime_to_100nano_seconds(kernel_time) + self.filetime_to_100nano_seconds(user_time)

    def get_process_memory(self, pid):
        if not psutil.pid_exists(pid):
            return 0
        OpenProcess = ctypes.windll.kernel32.OpenProcess
        OpenProcess.restype = wintypes.HANDLE
        OpenProcess.argtypes = [wintypes.DWORD, ctypes.wintypes.BOOL, wintypes.DWORD]
        GetProcessMemoryInfo = ctypes.windll.psapi.GetProcessMemoryInfo
        GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX), wintypes.DWORD]
        GetProcessMemoryInfo.restype = ctypes.wintypes.BOOL
        process = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if psutil.Process(pid).is_running() and psutil.Process(pid).status() != psutil.STATUS_ZOMBIE:
            if not process:
                raise ctypes.WinError()
            counters = PROCESS_MEMORY_COUNTERS_EX()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)

            if not GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb):
                CloseHandle(process)
                raise ctypes.WinError()
            CloseHandle(process)
            return counters
        return 0

    def get_io_counters(self, pid):
        counters = IO_COUNTERS()
        hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
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


# import time
# from monitor.get_process import *
#
# # 示例使用：
# system_time_pre = PidWinPerformance().filetime_to_100nano_seconds(FILETIME())
#
# monitor_duration_seconds = 60  # 监控持续时长（秒）
# monitor_interval_seconds = 1  # 监控间隔（秒）
# # 开始监控
# end_time = time.time() + monitor_duration_seconds
#
# app_name = "chrome.exe"
# ppid = find_main_process_pid(app_name)
# child_pids = get_children_pids(ppid)
# child_pids.add(ppid)
# print('pid', child_pids)
# process_cpu_times_pre = {pid: PidWinPerformance().get_process_cpu_time(pid) for pid in child_pids}
# process_io_counters_pre = {pid: PidWinPerformance().get_io_counters(pid) for pid in child_pids}
# while True:
#     start_time = time.time()  # 记录循环开始的时间
#     system_idle_time = FILETIME()
#     system_kernel_time = FILETIME()
#     system_user_time = FILETIME()
#     ctypes.windll.kernel32.GetSystemTimes(byref(system_idle_time),
#                                           byref(system_kernel_time),
#                                           byref(system_user_time))
#     system_time_post = PidWinPerformance().filetime_to_100nano_seconds(
#         system_kernel_time) + PidWinPerformance().filetime_to_100nano_seconds(system_user_time)
#
#     child_pids = get_children_pids(ppid)
#     child_pids.add(ppid)
#     print('pid', child_pids)
#     new_pids_cpu_time_pre = {pid: PidWinPerformance().get_process_cpu_time(pid) for pid in child_pids if
#                              pid not in process_cpu_times_pre}
#     process_cpu_times_pre.update(new_pids_cpu_time_pre)
#
#     print('----------------------------------------------------------')
#     for pid in child_pids:
#         process_cpu_time_post = PidWinPerformance().get_process_cpu_time(pid)
#         memory_info = PidWinPerformance().get_process_memory(pid)
#         # 获取磁盘I/O信息
#         io_counters = PidWinPerformance().get_io_counters(pid)
#         if process_cpu_time_post:
#             # 计算CPU使用率
#             cpu_usage = (process_cpu_time_post - process_cpu_times_pre[pid]) / (
#                     system_time_post - system_time_pre) * 100
#             print(
#                 f"({time.strftime('%H:%M:%S')}) PID {pid}: CPU Usage = {cpu_usage:.2f}%， Memory Info:{memory_info.WorkingSetSize},{memory_info.PrivateUsage}")
#             # 更新之前的CPU时间
#             process_cpu_times_pre[pid] = process_cpu_time_post
#         else:
#             print(f"PID {pid}: Process not found or access denied")
#
#         if io_counters and pid in process_io_counters_pre:
#             # 计算I/O变化量
#             read_bytes_sec = (io_counters.ReadTransferCount - process_io_counters_pre[
#                 pid].ReadTransferCount) / monitor_interval_seconds
#             write_bytes_sec = (io_counters.WriteTransferCount - process_io_counters_pre[
#                 pid].WriteTransferCount) / monitor_interval_seconds
#             print(f"PID {pid}: Read Bytes/sec = {read_bytes_sec}, Write Bytes/sec = {write_bytes_sec}")
#             # 更新之前的I/O计数器
#             process_io_counters_pre[pid] = io_counters
#         else:
#             print(f"PID {pid}: Could not get IO counters")
#
#     # 更新系统时间
#     system_time_pre = system_time_post
#     # 等待以确保大约每秒更新一次
#     elapsed = time.time() - start_time
#     time.sleep(max(0, monitor_interval_seconds - elapsed))
# print("监控完毕。")
