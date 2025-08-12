import platform

try:
    import objc
    import Foundation
except:
    pass

if platform.system() != 'Windows':
    IOKit = Foundation.NSBundle.bundleWithIdentifier_("com.apple.framework.IOKit")

    functions = [
        ("IOServiceGetMatchingService", b"II@"),
        ("IOServiceMatching", b"@*"),
        ("IORegistryEntryCreateCFProperties", b"IIo^@@I"),
    ]

    objc.loadBundleFunctions(IOKit, globals(), functions)


    def accelerator_performance_statistics() -> dict[str, int]:
        accelerator_info = IOServiceGetMatchingService(
            0, IOServiceMatching(b"IOAccelerator")
        )
        if accelerator_info == 0:
            raise RuntimeError("IOAccelerator not found")
        # else...
        err, props = IORegistryEntryCreateCFProperties(accelerator_info, None, None, 0)
        if err != 0:
            raise RuntimeError("IOAccelerator properties not found")
        # else...
        return dict(props)


    def get_gpu_memory():
        try:
            gpu_info = accelerator_performance_statistics()
            use_gpu_memory = 0
            total_gpu_memory = 0
            free_gpu_memory = 0
            for key, value in gpu_info["PerformanceStatistics"].items():
                if key == "In use system memory" or key == "gartUsedBytes":
                    use_gpu_memory = int(value)
                elif key == "gartSizeBytes":
                    total_gpu_memory = int(value)
                elif key == "gartFreeBytes":
                    free_gpu_memory = int(value)
                elif key == "Alloc system memory":
                    total_gpu_memory = int(value)
                    # print('device usage', device_usage)
            # use_gpu_memory = gpu_info["PerformanceStatistics"]["In use system memory"]
            # total_gpu_memory = gpu_info["PerformanceStatistics"]["Alloc system memory"]
        except Exception as e:
            print(f"Mac端在arm64平台通过接口获取Gpu Memory失败：{e}")
            use_gpu_memory = 0
            total_gpu_memory = 0
            free_gpu_memory = 0
        if free_gpu_memory == 0:
            free_gpu_memory = total_gpu_memory - use_gpu_memory
        return round(use_gpu_memory / 1024 / 1024, 2), round(total_gpu_memory / 1024 / 1024, 2), round(
            free_gpu_memory / 1024 / 1024, 2)
