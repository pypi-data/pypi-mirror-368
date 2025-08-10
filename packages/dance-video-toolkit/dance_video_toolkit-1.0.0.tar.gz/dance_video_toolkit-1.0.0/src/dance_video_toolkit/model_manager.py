"""
模型管理器 - 自动下载和管理YOLO模型
"""

import os
import requests
from pathlib import Path
from .log import get_logger

logger = get_logger("model_manager")

# 模型下载地址映射
MODEL_URLS = {
    "yolov8n-pose.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n-pose.pt",
    "yolov8s-pose.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8s-pose.pt",
    "yolov8m-pose.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8m-pose.pt",
    "yolov8l-pose.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8l-pose.pt",
    "yolov8x-pose.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8x-pose.pt",
    "yolov8n.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt",
    "yolov8s.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8s.pt",
    "yolov8m.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8m.pt",
    "yolov8l.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8l.pt",
    "yolov8x.pt": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8x.pt",
    "yolov5n.pt": "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt",
    "yolov5s.pt": "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt",
    "yolov5m.pt": "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5m.pt",
    "yolov5l.pt": "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5l.pt",
    "yolov5x.pt": "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5x.pt",
}


def download_file(url: str, destination: str, chunk_size: int = 8192) -> bool:
    """
    下载文件到指定位置
    
    Args:
        url: 下载地址
        destination: 保存路径
        chunk_size: 下载块大小
    
    Returns:
        bool: 下载是否成功
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # 显示进度
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        if downloaded % (1024 * 1024) == 0:  # 每1MB显示一次
                            logger.info(f"下载进度: {progress:.1f}%")
        
        logger.info(f"模型下载完成: {destination}")
        return True
        
    except Exception as e:
        logger.error(f"模型下载失败: {url} - {e}")
        return False


def ensure_model_exists(model_name: str, model_dir: str = "models") -> str:
    """
    确保模型文件存在，不存在则自动下载
    
    Args:
        model_name: 模型文件名
        model_dir: 模型存放目录
    
    Returns:
        str: 模型文件的完整路径
    """
    model_path = Path(model_dir) / model_name
    
    # 如果当前目录有模型，优先使用
    if Path(model_name).exists():
        logger.info(f"使用本地模型: {model_name}")
        return str(Path(model_name))
    
    # 如果模型已存在，直接返回路径
    if model_path.exists():
        logger.info(f"模型已存在: {model_path}")
        return str(model_path)
    
    # 创建模型目录
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 检查是否有对应的下载URL
    if model_name not in MODEL_URLS:
        available_models = ", ".join(MODEL_URLS.keys())
        logger.error(f"不支持的模型: {model_name}")
        logger.info(f"可用模型: {available_models}")
        raise ValueError(f"不支持的模型: {model_name}")
    
    # 下载模型
    url = MODEL_URLS[model_name]
    logger.info(f"开始下载模型: {model_name}")
    logger.info(f"下载地址: {url}")
    
    if download_file(url, str(model_path)):
        return str(model_path)
    else:
        raise RuntimeError(f"模型下载失败: {model_name}")


def list_available_models() -> dict:
    """列出所有可用的模型"""
    return {
        "pose_models": [k for k in MODEL_URLS.keys() if "pose" in k],
        "detection_models": [k for k in MODEL_URLS.keys() if "pose" not in k],
        "all_models": list(MODEL_URLS.keys())
    }


if __name__ == "__main__":
    # 测试模型管理器
    print("可用模型:")
    models = list_available_models()
    for category, model_list in models.items():
        print(f"{category}: {model_list}")
    
    # 测试下载
    try:
        path = ensure_model_exists("yolov8n-pose.pt")
        print(f"模型路径: {path}")
    except Exception as e:
        print(f"错误: {e}")