import argparse

from monitor.sys_info import SysInfo
from monitor.monitor_pids import *
from monitor.get_process_name import *
import asyncio


def main():
    parser = argparse.ArgumentParser(description='指定进程名或进程Pid即可获取性能数据~')
    parser.add_argument('-n', '--name', required=True, help='进程名称')
    parser.add_argument('-t', '--time', help='采集间隔时间/s', type=float, default=1)
    parser.add_argument('-i', '--info', help='输出当前系统使用情况', action='store_true')
    args = parser.parse_args()
    print(args)

    if args.info:
        print(SysInfo().get_device_info())
        exit()
    process = None
    if args.name:
        process = args.name
    else:
        parser.print_help()
        exit()

    if args.time:
        interval = args.time

    # process = 'YunXiu-PC'
    # interval = 1
    process_name = ProcessName()
    if process is not None:
        print('监测进程<{}>，采集数据间隔<{}s>'.format(process, interval))
    else:
        parser.print_help()
        exit()

    pid = process_name.find_main_process_pid(process)
    if process is None:
        process = process_name.get_pid_find_pid(int(pid))

    if pid is None or process is None:
        print('进程列表中未找到<{}>，请检查应用是否启动！停止监测任务'.format(process))
        sys.exit(0)

    print('开始监测进程<{}>，主进程pid<{}>'.format(process, pid))
    pidsPerf = PidsPerf(process, interval)
    asyncio.run(pidsPerf.start_perf())


if __name__ == '__main__':
    main()
