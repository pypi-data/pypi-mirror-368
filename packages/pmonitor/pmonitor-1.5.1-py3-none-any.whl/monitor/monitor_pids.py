import psutil
import time
import json
from monitor.get_process_name import *
import sys
import asyncio
import platform
import ctypes
import os
from PyLibreHardwareMonitor.computer import Computer

from monitor.monitor_mac_vmmap import VmMapMemory

if platform.system() != 'Windows':
    from monitor.mac_gpu import get_gpu_memory


class PidsPerf:

    def __init__(self, process_name, interval=1):
        self.process_name = process_name
        self.interval = interval
        self.processUtil = ProcessName()

    async def get_mac_perf(self):
        current_pid = self.processUtil.find_main_process_pid(self.process_name)
        vm = VmMapMemory()
        next_time = time.time()  # 初始化下一次执行的时间点
        first_iteration = True  # 标志变量，用于跳过第一次循环
        while True:
            start_time = time.time()  # 记录循环开始时间
            minor_cpu_sum = 0
            minor_real_mem_sum = 0
            minor_mem_percent_sum = 0
            minor_thread_count_sum = 0
            gpu_memory_usage = 0
            gpu_memory_total = 0
            gpu_memory_free = 0
            current_pids = self.processUtil.get_children_pids(current_pid)  # 获取所有子进程
            current_pids.add(current_pid)  # 将主进程及子进程添加到list中
            pids_process = self.processUtil.get_pids_process(current_pids)  # 获取所有进程

            mem_info = psutil.virtual_memory()
            mem_total = round(mem_info.total / 1024 / 1024, 2)  # 总虚拟内存
            mem_available = round(mem_info.available / 1024 / 1024, 2)  # 剩余虚拟内存

            gpu_memory_usage, gpu_memory_total, gpu_memory_free = get_gpu_memory()
            # 使用 asyncio.gather 并发获取内存数据
            vm.update_pids(current_pids)

            if first_iteration:
                first_iteration = False  # 第一次循环后将标志置为 False
                await asyncio.sleep(self.interval / 1000)  # 等待一段时间以确保数据稳定
                continue  # 跳过第一次循环

            for process in pids_process:
                try:
                    cpu_percent = process.cpu_percent()
                    mem_percent = u'%.2f' % (process.memory_percent())  # 内存利用率
                    vm_memory_data = json.loads(vm.get_current_json())
                    real_mem = vm_memory_data.get(str(process.pid), 0)  # 默认值为 0（如果未找到对应 PID）
                    thread_count = process.num_threads()  # 线程总数
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    cpu_percent = 0
                    mem_percent = 0
                    real_mem = 0
                    thread_count = 0

                # 将性能数据保存到对应PID的数据列表中
                if process.pid == current_pid:  # 主进程数据处理
                    main_cpu = cpu_percent
                    main_real_mem = real_mem
                    main_mem_percent = round(float(mem_percent), 2)
                    main_thread_count = thread_count
                    main_data = {'cpu': main_cpu, 'memory': main_real_mem, 'memory percent': main_mem_percent,
                                 'thread count': main_thread_count}
                    # print('主进程', pid_name, main_cpu, main_real_mem, main_mem_percent, main_thread_count)
                else:  # 子进程数据处理
                    minor_cpu_sum += cpu_percent
                    minor_real_mem_sum += real_mem
                    minor_mem_percent_sum += float(mem_percent)
                    minor_thread_count_sum += thread_count
                # pid_data[process.pid].append((cpu_percent, real_mem, mem_percent, thread_count))
            minor_data = {'cpu': round(float(minor_cpu_sum), 2), 'memory': round(float(minor_real_mem_sum), 2),
                          'memory percent': round(float(minor_mem_percent_sum), 2),
                          'thread count': minor_thread_count_sum}
            # print('其他子进程', pid_name, minor_cpu_sum, minor_real_mem_sum, minor_mem_percent_sum,
            #       minor_thread_count_sum)
            # 获取磁盘IO
            io_read_bytes_start, io_write_bytes_start = self.get_disk_usage()
            time.sleep(0.1)
            io_read_bytes_end, io_write_bytes_end = self.get_disk_usage()  # io read/write
            io_read_bytes = io_read_bytes_end - io_read_bytes_start  # io read/byte
            io_write_bytes = io_write_bytes_end - io_write_bytes_start  # io write/byte
            disk_data = {'io read': io_read_bytes, 'io write': io_write_bytes}
            gpu_data = {'gpu memory usage': gpu_memory_usage, 'gpu memory total': gpu_memory_total,
                        'gpu memory free': gpu_memory_free}
            data = {'main': main_data, 'other': minor_data, 'disk': disk_data, "gpu": gpu_data,
                    "memory_total": mem_total, "memory_available": mem_available}
            json_data = json.dumps(data)
            print(json_data)
            # 精确控制间隔
            next_time += self.interval
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            else:
                next_time = time.time()  # 如果超时，重置时间点
            sys.stdout.flush()

    def get_disk_usage(self):
        '''
        Mac 获取进程磁盘读写情况
        :return:
        '''
        try:
            io_counters = psutil.disk_io_counters()
            io_read_bytes = io_counters.read_bytes
            io_write_bytes = io_counters.write_bytes
            return io_read_bytes, io_write_bytes
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        return 0, 0

    def get_win_perf(self):
        from monitor.WinPidUtil import PidWinPerformance, FILETIME
        from ctypes import CDLL, c_int, c_char_p, byref
        pidWinPerf = PidWinPerformance()
        system_time_pre = pidWinPerf.filetime_to_100nano_seconds(FILETIME())
        p_pid = self.processUtil.find_main_process_pid(self.process_name)
        child_pids = self.processUtil.get_children_pids(p_pid)
        child_pids.add(p_pid)  # app内所有pid

        process_cpu_times_pre = {pid: pidWinPerf.get_process_cpu_time(pid) for pid in child_pids}
        process_io_counters_pre = {pid: pidWinPerf.get_io_counters(pid) for pid in child_pids}

        dll_path = os.path.join(os.path.dirname(__file__), 'DLL', 'GpuMonitorLib.dll')
        gpu_monitor_dll = ctypes.CDLL(dll_path)
        gpu_monitor_dll.GetGPUDataForProcess.argtypes = [ctypes.c_ulong]
        gpu_monitor_dll.GetGPUDataForProcess.restype = ctypes.c_char_p
        # 获取GPU物理内存
        computer = Computer()
        gpu_key = list(computer.gpu.keys())[0]
        next_time = time.time()  # 初始化下一次执行的时间点
        while True:
            minor_cpu_sum = 0
            minor_workSet_mem_sum = 0
            minor_private_mem_sum = 0
            minor_mem_percent_sum = 0
            minor_thread_count_sum = 0
            minor_io_read_sum = 0
            minor_io_write_sum = 0
            minor_gpu_dedicated_sum = 0  # （专用内存）
            minor_gpu_system_sum = 0  # (共享内存)
            minor_gpu_committed_sum = 0  # (总使用内存)
            minor_gpu_percent_sum = 0  # (GPU内存占比)
            main_gpu_dedicated_sum = 0  # （专用内存）
            main_gpu_system_sum = 0  # (共享内存)
            main_gpu_committed_sum = 0  # (总使用内存)
            main_gpu_percent_sum = 0  # (GPU内存占比)

            start_time = time.time()  # 记录循环开始的时间
            system_idle_time = FILETIME()
            system_kernel_time = FILETIME()
            system_user_time = FILETIME()
            ctypes.windll.kernel32.GetSystemTimes(byref(system_idle_time),
                                                  byref(system_kernel_time),
                                                  byref(system_user_time))
            system_time_post = pidWinPerf.filetime_to_100nano_seconds(
                system_kernel_time) + pidWinPerf.filetime_to_100nano_seconds(system_user_time)
            p_pid = self.processUtil.find_main_process_pid(self.process_name)
            child_pids = self.processUtil.get_children_pids(p_pid)
            child_pids.add(p_pid)  # app内所有pid
            child_pids = {pid for pid in child_pids if psutil.pid_exists(pid)}  # 移除不存在的进程

            small_data = computer.gpu[gpu_key]['SmallData']  # 获取GPU物理内存信息
            try:
                new_pids_cpu_time_pre = {pid: pidWinPerf.get_process_cpu_time(pid) for pid in child_pids if
                                         pid not in process_cpu_times_pre}
                process_cpu_times_pre.update(new_pids_cpu_time_pre)
                new_process_io_counters_pre = {pid: pidWinPerf.get_io_counters(pid) for pid in child_pids}
                process_io_counters_pre.update(new_process_io_counters_pre)
            except psutil.Error as ex:
                print(f"Error updating counters: {ex}")

            # print('----------------------------------------------------------')
            # print('pid', child_pids)
            memory_total = round(psutil.virtual_memory().total / 1024 / 1024, 2)
            memory_available = round(psutil.virtual_memory().available / 1024 / 1024, 2)

            for pid in child_pids:
                try:
                    process = psutil.Process(pid)
                    pid_name = process.name()
                    mem_percent = round(process.memory_percent(), 2)
                    thread_count = process.num_threads()
                except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                    # print('pid is not found')
                    mem_percent = 0
                    thread_count = 0
                process_cpu_time_post = pidWinPerf.get_process_cpu_time(pid)
                memory_info = pidWinPerf.get_process_memory(pid)
                io_counters = pidWinPerf.get_io_counters(pid)
                if io_counters is None or pid not in process_io_counters_pre:
                    continue
                read_bytes_sec = (io_counters.ReadTransferCount - process_io_counters_pre[
                    pid].ReadTransferCount) / self.interval
                write_bytes_sec = (io_counters.WriteTransferCount - process_io_counters_pre[
                    pid].WriteTransferCount) / self.interval
                gpu_info_json = gpu_monitor_dll.GetGPUDataForProcess(pid).decode()
                gpu_info = json.loads(gpu_info_json)
                if process_cpu_time_post:
                    # 计算CPU使用率
                    cpu_usage = round((process_cpu_time_post - process_cpu_times_pre[pid]) / (
                            system_time_post - system_time_pre) * 100, 2)
                    # 更新之前的CPU时间
                    process_cpu_times_pre[pid] = process_cpu_time_post
                    workSet_mem = round(memory_info.WorkingSetSize / 1024 / 1024, 2)  # MB
                    private_mem = round(memory_info.PrivateUsage / 1024 / 1024, 2)  # MB
                    if pid == p_pid:

                        if gpu_info is not None:
                            for item in gpu_info:
                                if item['ProcessID'] == p_pid:
                                    main_gpu_dedicated_sum += item['GPUProcessMemoryLocalUsage']  # （专用内存）
                                    main_gpu_system_sum += item['GPUProcessMemorySharedUsage']  # (共享内存)
                                    main_gpu_committed_sum += item['GPUProcessMemoryTotalCommitted']  # (总使用内存)
                                    main_gpu_percent_sum += item['GPUUtilizationPercent']  # (GPU内存占比)
                            # print('主进程pid：', item['ProcessID'], 'Dedicated:',
                            #       main_gpu_dedicated_sum,
                            #       'System:', main_gpu_system_sum,
                            #       'Committed:', main_gpu_committed_sum, 'GPU Usage:',
                            #       main_gpu_percent_sum)
                        main_data = {'cpu': cpu_usage, 'private': private_mem, "workset": workSet_mem,
                                     'thread count': thread_count,
                                     'gpu_Dedicated': round(float(main_gpu_dedicated_sum), 2),
                                     'gpu_System': round(float(main_gpu_system_sum), 2),
                                     'gpu_Committed': round(float(main_gpu_committed_sum), 2),
                                     'gpu_Usage': round(float(main_gpu_percent_sum), 2)}

                        # print(
                        #     f'主进程数据：cpu：{cpu_usage}，workSet：{workSet_mem}，private：{private_mem}，mem_percent：{mem_percent}，thread_count：{thread_count}')
                    else:
                        minor_cpu_sum += cpu_usage  # 子进程总
                        minor_workSet_mem_sum += workSet_mem  # 子进程workSet内存
                        minor_private_mem_sum += private_mem  # 子进程private内存
                        minor_mem_percent_sum += mem_percent  # 子进程内存使用率
                        minor_thread_count_sum += thread_count  # 子进程线程总数
                        if gpu_info is not None:
                            for item in gpu_info:
                                if item['ProcessID'] != p_pid:
                                    # print('子进程pid：', item['ProcessID'], 'Dedicated:',
                                    #       item['GPUProcessMemoryDedicatedUsage'],
                                    #       'System:', item['GPUProcessMemorySharedUsage'],
                                    #       'Committed:', item['GPUProcessMemoryTotalCommitted'], 'GPU Usage:',
                                    #       item['GPUUtilizationPercent'])
                                    minor_gpu_dedicated_sum += item['GPUProcessMemoryLocalUsage']
                                    minor_gpu_system_sum += item['GPUProcessMemorySharedUsage']
                                    minor_gpu_committed_sum += item['GPUProcessMemoryTotalCommitted']
                                    minor_gpu_percent_sum += item['GPUUtilizationPercent']
                    minor_io_read_sum += read_bytes_sec  # 所有进程IO读取速率总数
                    minor_io_write_sum += write_bytes_sec  # 所有进程IO写入速率总数

                else:
                    # print(f"PID {pid}: Process not found or access denied")
                    continue
            disk_data = {'io read': minor_io_read_sum, 'io write': minor_io_write_sum}
            other_data = {'cpu': minor_cpu_sum, 'private': round(float(minor_private_mem_sum), 2),
                          'workset': round(float(minor_workSet_mem_sum), 2),
                          # 'memory percent': round(float(minor_mem_percent_sum), 2),
                          'thread count': minor_thread_count_sum,
                          'gpu_Dedicated': round(minor_gpu_dedicated_sum, 2),
                          'gpu_System': round(minor_gpu_system_sum, 2),
                          'gpu_Committed': round(minor_gpu_committed_sum, 2),
                          'gpu_Usage': round(minor_gpu_percent_sum, 2)}
            if 'GPU Memory Used' in small_data:
                gpu_data = {'gpu memory usage': round(small_data['GPU Memory Used'], 2),
                            'gpu memory total': round(small_data['GPU Memory Total'], 2),
                            'gpu memory free': round(small_data['GPU Memory Free'], 2)}
            else:
                gpu_data = {'gpu memory usage': round(small_data['D3D Shared Memory Used'], 2),
                            'gpu memory total': round(small_data['D3D Shared Memory Total'], 2),
                            'gpu memory free': round(small_data['D3D Shared Memory Free'], 2)}
            try:
                data = {'main': main_data, 'other': other_data, 'disk': disk_data,
                        'gpu': gpu_data,
                        'memory_total': memory_total,
                        'memory_available': memory_available}
                json_data = json.dumps(data)
                print(json_data)
            except UnboundLocalError:
                continue
            sys.stdout.flush()
            # 更新系统时间
            system_time_pre = system_time_post
            # 精确控制间隔
            next_time += self.interval
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                next_time = time.time()  # 如果超时，重置时间点v

    async def start_perf(self):
        if platform.system() == 'Windows':
            await asyncio.gather(self.get_win_perf())
        else:
            await asyncio.gather(self.get_mac_perf())
