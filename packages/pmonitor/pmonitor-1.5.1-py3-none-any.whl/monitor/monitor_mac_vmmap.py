import subprocess
import threading
import time
import json
import re
import os


class VmMapMemory:
    def __init__(self):
        """
        初始化实时内存监控器
        """
        self.pids = set()  # 当前监控的 PID
        self.current_data = {}  # 存储最新的内存数据 {pid: memory_mb}
        self.lock = threading.Lock()  # 线程锁
        self.running = True  # 控制线程运行状态
        self.thread = None  # 监控线程
        # 启动监控线程
        self.start_monitoring()

    def start_monitoring(self):
        """启动监控线程"""
        self.thread = threading.Thread(target=self._monitor_memory)
        self.thread.daemon = True  # 设置为守护线程
        self.thread.start()

    def update_pids(self, new_pids):
        """更新要监控的 PID 列表"""
        with self.lock:
            # 转换为字符串并更新集合
            self.pids = set(map(str, new_pids))

    def _convert_to_mb(self, mem_str):
        """
        将内存字符串转换为 MB
        支持格式: 123, 123K, 123M, 123G, 12G+, 12G-
        """
        # 移除逗号（如果存在）
        mem_str = mem_str.replace(',', '')

        # 检查单位并转换
        if 'G' in mem_str:
            return float(mem_str.replace('G', '').rstrip('+-')) * 1024
        elif 'M' in mem_str:
            return float(mem_str.replace('M', '').rstrip('+-'))
        elif 'K' in mem_str:
            return float(mem_str.replace('K', '').rstrip('+-')) / 1024
        else:
            # 假设为字节
            return float(mem_str.rstrip('+-')) / (1024 * 1024)

    def _monitor_memory(self):
        """线程函数：实时监控内存使用"""
        # macOS 专用 top 命令
        cmd = ["top", "-stats", "pid,mem"]

        # 启动 top 进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # 行缓冲
            universal_newlines=True  # 确保文本模式
        )

        try:
            while self.running:
                line = process.stdout.readline()  # 逐行读取

                if not line:  # 进程结束或无输出时退出
                    break

                # 匹配 PID 和内存行 (例如: "12345  123.4M")
                match = re.match(r'^\s*(\d+)\s+([\d,.]+[KMG][+-]?)\s*$', line.strip())
                if match:
                    pid = match.group(1)
                    mem_str = match.group(2)

                    # 检查是否在监控列表中
                    with self.lock:
                        if pid in self.pids:
                            mem_mb = self._convert_to_mb(mem_str)
                            # 直接更新当前数据，不保存历史
                            self.current_data[pid] = round(mem_mb, 2)

        except Exception as e:
            print(f"Monitoring error: {e}")
        finally:
            if process.poll() is None:  # 确保进程终止
                process.terminate()

    def get_current_data(self):
        """
        获取当前内存数据（线程安全）
        只返回当前监控的 PID 的最新内存值
        """
        with self.lock:
            # 只返回当前监控列表中的 PID 数据
            return {
                pid: self.current_data.get(pid, 0.0)
                for pid in self.pids
            }

    def get_current_json(self):
        """获取 JSON 格式的当前内存数据"""
        data = self.get_current_data()
        return json.dumps(data, indent=2)

    def stop(self):
        """停止监控"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        print("Memory monitor stopped")