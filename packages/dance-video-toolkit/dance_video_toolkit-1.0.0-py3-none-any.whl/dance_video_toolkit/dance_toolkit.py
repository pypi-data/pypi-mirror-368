#!/usr/bin/env python3
"""
舞蹈视频处理工具包
提供两个核心功能：
1. 过滤多人视频（可选）
2. 切分舞蹈视频
"""

import cv2
import os
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime
from .log import get_logger
from .model_manager import ensure_model_exists


class DanceVideoToolkit:
    """舞蹈视频处理工具包"""
    
    def __init__(
        self,
        model_path: str = "yolov8n-pose.pt",
        output_dir: str = "output",
        min_duration: float = 5.0,
        sample_interval: int = 3,
        debug: bool = False,
    ):
        self.model_path = model_path
        self.output_dir = Path(output_dir)
        self.min_duration = min_duration
        self.sample_interval = sample_interval
        self.debug = debug
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志
        self.logger = self._setup_logging()
        
        # 确保模型文件存在
        try:
            actual_model_path = ensure_model_exists(model_path)
            self.logger.info(f"使用模型: {actual_model_path}")
        except Exception as e:
            self.logger.error(f"模型准备失败: {e}")
            raise
        
        # 初始化检测器
        try:
            from .optimized_pos import OptimizedDanceDetector
            self.detector = OptimizedDanceDetector(
                model_path=actual_model_path, output_dir=str(output_dir), debug=debug
            )
            self.person_detector = self._init_person_detector()
        except ImportError as e:
            self.logger.error(f"检测器初始化失败: {e}")
            raise
    
    def _setup_logging(self):
        """使用统一的日志系统"""
        return get_logger("dance_toolkit")
    
    def _init_person_detector(self):
        """初始化人员检测器"""
        try:
            from ultralytics import YOLO
            detector = YOLO("yolov8n.pt")
            # 自动选择设备
            try:
                import torch
                if torch.cuda.is_available():
                    detector.to("cuda")
                else:
                    detector.to("cpu")
            except:
                detector.to("cpu")
            return detector
        except Exception as e:
            self.logger.warning(f"人员检测器初始化失败: {e}")
            return None
    
    def filter_multi_person_videos(
        self, 
        input_path: str, 
        recursive: bool = False
    ) -> List[Path]:
        """
        功能1：过滤多人视频
        检测视频中的人数，如果检测到多人则标记为需要删除
        """
        input_path = Path(input_path)
        video_files = self._get_video_files(input_path, recursive)
        
        single_person_videos = []
        multi_person_videos = []
        
        for video_file in video_files:
            person_count = self._count_persons_in_video(str(video_file))
            
            if person_count == 1:
                single_person_videos.append(video_file)
                self.logger.info(f"✅ 单人视频: {video_file.name}")
            elif person_count > 1:
                multi_person_videos.append(video_file)
                self.logger.warning(f"❌ 多人视频({person_count}人): {video_file.name}")
            else:
                self.logger.warning(f"⚠️  未检测到人物: {video_file.name}")
        
        # 保存过滤结果
        self._save_filter_results(single_person_videos, multi_person_videos)
        
        return single_person_videos, multi_person_videos
    
    def split_dance_videos(
        self, 
        input_path: str, 
        recursive: bool = False,
        filter_multi_person: bool = False
    ) -> dict:
        """
        功能2：切分舞蹈视频
        自动检测舞蹈片段并切分
        """
        input_path = Path(input_path)
        video_files = self._get_video_files(input_path, recursive)
        
        if filter_multi_person:
            video_files, _ = self.filter_multi_person_videos(input_path, recursive)
        
        results = {
            "processed_videos": 0,
            "total_clips": 0,
            "failed_videos": [],
            "clip_details": {}
        }
        
        for video_file in video_files:
            try:
                self.logger.info(f"开始处理: {video_file.name}")
                
                # 使用优化版视频处理器
                from .optimized_video_processor import OptimizedVideoProcessor
                
                processor = OptimizedVideoProcessor(
                    model_path=self.model_path,
                    output_dir=str(self.output_dir),
                    min_duration=self.min_duration,
                    sample_interval=self.sample_interval,
                    debug=self.debug
                )
                
                segments = processor.process_video(str(video_file))
                
                results["processed_videos"] += 1
                results["total_clips"] += len(segments)
                results["clip_details"][video_file.name] = {
                    "segments": segments,
                    "clip_count": len(segments)
                }
                
                self.logger.info(f"完成处理: {video_file.name} - 提取 {len(segments)} 个片段")
                
            except Exception as e:
                self.logger.error(f"处理失败: {video_file.name} - {e}")
                results["failed_videos"].append(str(video_file))
        
        return results
    
    def _get_video_files(self, input_path: Path, recursive: bool = False) -> List[Path]:
        """获取视频文件列表 - 支持丰富的视频格式"""
        video_extensions = {
            # 常见格式
            ".mp4", ".avi", ".mov", ".mkv", ".flv", ".ts", ".wmv",
            # 高清格式
            ".webm", ".m4v", ".3gp", ".ogv", ".mpg", ".mpeg",
            # 专业格式
            ".m2v", ".m2ts", ".mts", ".vob", ".rm", ".rmvb",
            # 新增格式
            ".f4v", ".divx", ".xvid", ".h264", ".h265", ".hevc"
        }
        
        if input_path.is_file():
            return [input_path] if input_path.suffix.lower() in video_extensions else []
        
        if recursive:
            return [
                f for f in input_path.rglob("*") 
                if f.suffix.lower() in video_extensions
            ]
        else:
            return [
                f for f in input_path.iterdir() 
                if f.suffix.lower() in video_extensions
            ]
    
    def _count_persons_in_video(self, video_path: str) -> int:
        """
        统计视频中的人数
        
        使用中间帧进行快速检测，避免逐帧处理提高性能
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            int: 检测到的人数，0表示无人，1表示单人，>1表示多人
        """
        if not self.person_detector:
            self.logger.warning("人员检测器未初始化，默认返回单人")
            return 1
            
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                self.logger.error(f"无法打开视频文件: {video_path}")
                return 0
            
            # 采样中间帧以提高检测效率和准确性
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                self.logger.warning(f"视频帧数为0: {video_path}")
                return 0
                
            # 选择中间帧作为采样点
            sample_frame = min(total_frames // 2, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, sample_frame)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                self.logger.error(f"无法读取视频帧: {video_path}")
                return 0
            
            # 使用YOLO检测人数（classes=[0]表示只检测person类别）
            results = self.person_detector(frame, classes=[0], verbose=False)
            person_count = len(results[0].boxes) if results and len(results) > 0 else 0
            
            self.logger.debug(f"视频 {Path(video_path).name} 检测到 {person_count} 人")
            return person_count
            
        except Exception as e:
            self.logger.error(f"人数检测失败: {video_path} - {e}")
            return 1  # 保守估计，避免误删
    
    def _save_filter_results(self, single_videos: List[Path], multi_videos: List[Path]):
        """保存过滤结果"""
        filter_result = {
            "timestamp": datetime.now().isoformat(),
            "single_person_videos": [str(v) for v in single_videos],
            "multi_person_videos": [str(v) for v in multi_videos],
            "summary": {
                "single_person_count": len(single_videos),
                "multi_person_count": len(multi_videos),
                "total_videos": len(single_videos) + len(multi_videos)
            }
        }
        
        result_file = self.output_dir / "filter_results.json"
        import json
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(filter_result, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"过滤结果已保存: {result_file}")


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description="舞蹈视频处理工具包")
    parser.add_argument("input", help="输入视频文件或目录路径")
    parser.add_argument("--mode", choices=["filter", "split", "both"], 
                       default="split", help="处理模式")
    parser.add_argument("-o", "--output", default="output", help="输出目录")
    parser.add_argument("--model", default="yolov8n-pose.pt", help="姿势检测模型")
    parser.add_argument("--person-model", default="yolov8n.pt", help="人员检测模型")
    parser.add_argument("--min-duration", type=float, default=5.0, 
                       help="最小时长（秒），小于此值的片段将被丢弃")
    parser.add_argument("--sample-interval", type=int, default=3, 
                       help="采样间隔（秒）")
    parser.add_argument("--recursive", action="store_true", help="递归处理子目录")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 初始化工具包
    toolkit = DanceVideoToolkit(
        model_path=args.model,
        output_dir=args.output,
        min_duration=args.min_duration,
        sample_interval=args.sample_interval,
        debug=args.debug
    )
    
    print(f"🎯 舞蹈视频处理工具包启动")
    print(f"📁 输入路径: {args.input}")
    print(f"🎭 处理模式: {args.mode}")
    print(f"📊 最小时长: {args.min_duration}s")
    
    if args.mode == "filter":
        # 功能1：过滤多人视频
        single, multi = toolkit.filter_multi_person_videos(args.input, args.recursive)
        print(f"\n📊 过滤完成:")
        print(f"✅ 单人视频: {len(single)} 个")
        print(f"❌ 多人视频: {len(multi)} 个")
        
    elif args.mode == "split":
        # 功能2：切分舞蹈视频
        results = toolkit.split_dance_videos(args.input, args.recursive)
        print(f"\n🎬 切分完成:")
        print(f"✅ 处理视频: {results['processed_videos']} 个")
        print(f"🎞️  提取片段: {results['total_clips']} 个")
        
        if results['failed_videos']:
            print(f"❌ 失败视频: {len(results['failed_videos'])} 个")
            
    elif args.mode == "both":
        # 同时执行两个功能
        single, multi = toolkit.filter_multi_person_videos(args.input, args.recursive)
        results = toolkit.split_dance_videos(args.input, args.recursive, 
                                           filter_multi_person=True)
        print(f"\n🎯 综合处理完成:")
        print(f"✅ 单人视频: {len(single)} 个")
        print(f"❌ 多人视频: {len(multi)} 个")
        print(f"🎞️  提取片段: {results['total_clips']} 个")


if __name__ == "__main__":
    main()