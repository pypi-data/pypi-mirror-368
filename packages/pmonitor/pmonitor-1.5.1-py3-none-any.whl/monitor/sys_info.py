import psutil as ps
import socket
import uuid
import datetime


class SysInfo:

    def get_mac_address(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ':'.join([mac[e:e + 2] for e in range(0, 11, 2)])

    def get_device_info(self):
        # 主机名
        host_name = socket.gethostname()
        # ip地址
        ip = self.getIP()
        # 系统用户
        users_list = ','.join([u.name for u in ps.users()])
        # 系统启动时间
        start_time = datetime.datetime.fromtimestamp(ps.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
        sys_info = {'HostName': host_name,
                    'IP': ip,
                    'MAC': self.get_mac_address(),
                    'User': users_list,
                    'Start Time': start_time}

        # CPU物理核心
        cpu_count = ps.cpu_count(logical=False)
        # CPU逻辑数量
        cpu_logical = ps.cpu_count()
        cpu_info = {'Cpu Amount': cpu_count,
                    'Cpu Logical': cpu_logical}

        # 内存信息
        mem = ps.virtual_memory()
        # 内存总量
        mem_total = round(mem.total / 1024 / 1024 / 1024, 2)
        # 内存使用量
        mem_used = round(mem.used / 1024 / 1024 / 1024, 2)
        # 内存可用量
        mem_available = round(mem.available / 1024 / 1024 / 1024, 2)
        # 内存使用百分比
        mem_percent = mem.percent
        mem_info = {'Total Memory': str(mem_total) + 'GB',
                    'Memory Used': str(mem_used) + 'GB',
                    'Memory Free': str(mem_available) + 'GB',
                    'Memory Usage': str(mem_percent) + '%'}

        # 磁盘信息
        io = ps.disk_partitions()
        disk_info = []
        for i in io:
            disk = ps.disk_usage(i.mountpoint)
            disk_data = {'disk_name': i.mountpoint,
                         'total': str(round(disk.total / 1024 / 1024 / 1024, 1)) + 'GB',
                         'used': str(round(disk.used / 1024 / 1024 / 1024, 1)) + 'GB',
                         'surplus': str(round(disk.free / 1024 / 1024 / 1024, 1)) + 'GB',
                         'rate': str(ps.disk_usage(i.mountpoint).percent) + '%'}
            disk_info.append(disk_data)

        # 网卡信息
        net = ps.net_io_counters()
        bytes_sent = '{0:.2f}'.format(net.bytes_sent / 1024 / 1024)
        bytes_rcvd = '{0:.2f}'.format(net.bytes_recv / 1024 / 1024)
        net_info = {'bytes_sent': bytes_sent + 'MB',
                    'bytes_rcvd': bytes_rcvd + 'MB'}

        data = {'sys_info': sys_info, 'cpu_info': cpu_info,
                'mem_info': mem_info, 'disk_info': disk_info,
                'net_info': net_info}
        return data

    def getIP(self):
        """获取ipv4地址"""
        dic = ps.net_if_addrs()
        ipv4_list = []
        for adapter in dic:
            snicList = dic[adapter]
            for snic in snicList:
                if snic.family.name == 'AF_INET':
                    ipv4 = snic.address
                    if ipv4 != '127.0.0.1':
                        ipv4_list.append(ipv4)
        if len(ipv4_list) >= 1:
            return ipv4_list[0]
        else:
            return 'None'

