"""
Dance Video Toolkit - AI-powered dance video processing toolkit

A comprehensive toolkit for processing dance videos with AI-powered detection:
1. Filter multi-person videos (optional)
2. Split dance clips from videos

Features:
- Advanced pose detection using YOLOv8
- Automatic model downloading
- Rich video format support
- Configurable detection parameters
- GPU acceleration support
- Comprehensive logging
"""

from .dance_toolkit import DanceVideoToolkit
from .model_manager import list_available_models, ensure_model_exists

__version__ = "1.0.0"
__author__ = "Dance Toolkit Team"
__email__ = "dance@example.com"

__all__ = [
    "DanceVideoToolkit",
    "list_available_models",
    "ensure_model_exists",
]

def main():
    """主入口函数，用于命令行调用"""
    from .dance_toolkit import main
    main()

if __name__ == "__main__":
    main()