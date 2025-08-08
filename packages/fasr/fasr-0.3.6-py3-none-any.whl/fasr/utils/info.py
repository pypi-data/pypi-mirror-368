from loguru import logger


def print_cuda_info():
    import torch

    # 检查CUDA是否可用
    cuda_available = torch.cuda.is_available()

    if cuda_available:
        # 获取GPU设备数量
        num_gpu = torch.cuda.device_count()

        # 获取当前使用的GPU索引
        current_gpu_index = torch.cuda.current_device()

        # 获取当前GPU的名称
        current_gpu_name = torch.cuda.get_device_name(current_gpu_index)

        # 获取GPU显存的总量和已使用量
        total_memory = torch.cuda.get_device_properties(
            current_gpu_index
        ).total_memory / (1024**3)  # 显存总量(GB)
        used_memory = torch.cuda.memory_allocated(current_gpu_index) / (
            1024**3
        )  # 已使用显存(GB)
        free_memory = total_memory - used_memory  # 剩余显存(GB)

        logger.info(f"CUDA可用，共有 {num_gpu} 个GPU设备可用。")
        logger.info(f"当前使用的GPU设备索引：{current_gpu_index}")
        logger.info(f"当前使用的GPU设备名称：{current_gpu_name}")
        logger.info(f"GPU显存总量：{total_memory:.2f} GB")
        logger.info(f"已使用的GPU显存：{used_memory:.2f} GB")
        logger.info(f"剩余GPU显存：{free_memory:.2f} GB")
    else:
        logger.info("CUDA不可用。")

    # 检查PyTorch版本
    logger.info(f"PyTorch版本：{torch.__version__}")

    import torch

    logger.info(f"CUDA版本：{torch.version.cuda}")
