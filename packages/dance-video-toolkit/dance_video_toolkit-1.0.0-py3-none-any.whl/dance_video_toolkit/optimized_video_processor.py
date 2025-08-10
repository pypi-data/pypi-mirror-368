import cv2
import os
import subprocess
from pathlib import Path
from typing import List, Tuple
from datetime import datetime
from .log import get_logger


class OptimizedVideoProcessor:
    """优化版视频处理器 - 使用大腿和髋部检测"""

    def __init__(
        self,
        model_path: str = "yolov8n-pose.pt",
        output_dir: str = "output",
        sample_interval: int = 3,
        min_duration: float = 5.0,
        debug: bool = True,
        buffer_size: int = 2,  # buffer大小（采样点数）
    ):
        self.model_path = model_path
        self.output_dir = Path(output_dir)
        self.sample_interval = sample_interval
        self.min_duration = min_duration
        self.debug = debug

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 设置日志
        self.logger = self._setup_logging()

        # 初始化检测器
        try:
            from .optimized_pos import OptimizedDanceDetector

            self.detector = OptimizedDanceDetector(
                model_path=model_path, output_dir=str(output_dir), debug=debug
            )
            self.logger.info(f"优化舞蹈检测器初始化成功 - 模型: {model_path}")
        except ImportError:
            # 回退到旧版本
            from pos import Pos

            self.detector = Pos(model_path, output_dir=str(output_dir), debug=debug)
            self.logger.info("使用兼容舞蹈检测器")

    def _setup_logging(self):
        """使用统一的日志系统"""
        return get_logger("optimized_video_processor")

    def process_video(
        self, video_path: str, output_subdir: str = None
    ) -> List[Tuple[float, float]]:
        """处理单个视频"""
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        self.logger.info(f"开始处理视频: {video_path}")

        # 设置输出目录
        if output_subdir is None:
            output_subdir = video_path.stem
        current_output_dir = self.output_dir / output_subdir
        current_output_dir.mkdir(parents=True, exist_ok=True)

        # 检测舞蹈片段
        segments = self._detect_dance_segments(str(video_path))
        self.logger.info(f"检测到 {len(segments)} 个舞蹈片段")

        # 过滤短时片段
        valid_segments = [
            (start, end)
            for start, end in segments
            if (end - start) >= self.min_duration
        ]
        self.logger.info(f"过滤后 {len(valid_segments)} 个有效片段")

        # 提取视频片段
        if valid_segments:
            self._extract_clips(str(video_path), valid_segments, current_output_dir)
            self._save_processing_info(video_path, valid_segments, current_output_dir)

        return valid_segments

    def _detect_dance_segments(self, video_path: str) -> List[Tuple[float, float]]:
        """检测舞蹈片段时间段"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        # 计算采样间隔
        sample_frames = max(1, int(fps * self.sample_interval))

        self.logger.info(f"视频信息: {Path(video_path).name}")
        self.logger.info(f"FPS: {fps}, 总帧数: {total_frames}, 时长: {duration:.1f}s")
        self.logger.info(f"采样间隔: {self.sample_interval}s ({sample_frames}帧)")

        # 状态序列
        state_sequence = []
        detection_stats = {"total_samples": 0, "dance_count": 0, "no_dance_count": 0}

        frame_idx = 0
        sample_idx = 0
        while frame_idx < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()

            if not ret:
                break

            current_time = frame_idx / fps

            # 使用优化检测器
            is_dancing = self.detector.detect_dance(frame, frame_number=frame_idx)

            detection_stats["total_samples"] += 1
            if is_dancing:
                detection_stats["dance_count"] += 1
            else:
                detection_stats["no_dance_count"] += 1

            self.logger.debug(
                f"采样点 {sample_idx+1}: 时间={current_time:.2f}s, "
                f"帧={frame_idx}, 跳舞={is_dancing}"
            )
            state_sequence.append((current_time, is_dancing))

            frame_idx += sample_frames
            sample_idx += 1

        cap.release()

        # 记录统计
        if detection_stats["total_samples"] > 0:
            dance_ratio = (
                detection_stats["dance_count"] / detection_stats["total_samples"]
            )
            self.logger.info(
                f"检测统计: 总采样={detection_stats['total_samples']}, "
                f"跳舞={detection_stats['dance_count']}, "
                f"不跳舞={detection_stats['no_dance_count']}, "
                f"跳舞比例={dance_ratio:.2%}"
            )

        # 转换为时间段
        return self._state_to_segments(state_sequence)

    def _state_to_segments(
        self, states: List[Tuple[float, bool]]
    ) -> List[Tuple[float, float]]:
        """回退到第一版严格算法的状态转换"""
        if not states:
            return []

        # 将所有状态转换为二进制序列
        binary_sequence = [1 if is_dancing else 0 for _, is_dancing in states]
        
        self.logger.debug(f"原始状态序列: {binary_sequence}")
        
        # 第一版：严格状态转换，无平滑处理
        segments = []
        current_start = None
        
        for time_stamp, is_dancing in states:
            if is_dancing and current_start is None:
                # 开始新的舞蹈片段
                current_start = time_stamp
            elif not is_dancing and current_start is not None:
                # 结束当前舞蹈片段
                segments.append((current_start, time_stamp))
                current_start = None
        
        # 处理最后一个舞蹈片段
        if current_start is not None:
            segments.append((current_start, states[-1][0]))
        
        # 第一版：不进行任何合并，保持原始分割
        final_segments = []
        for start, end in segments:
            if end - start >= self.min_duration:
                final_segments.append((start, end))
                self.logger.debug(
                    f"提取舞蹈片段: {start:.1f}s-{end:.1f}s (时长: {end-start:.1f}s)"
                )
        
        self.logger.info(f"第一版算法得到 {len(final_segments)} 个舞蹈片段")
        return final_segments
    

    def _merge_segments(
        self, segments: List[Tuple[float, float]]
    ) -> List[Tuple[float, float]]:
        """合并相邻的时间段"""
        if not segments:
            return []

        # 排序
        segments = sorted(segments, key=lambda x: x[0])

        merged = [list(segments[0])]

        for start, end in segments[1:]:
            last_start, last_end = merged[-1]

            # 如果间隔小于采样间隔，则合并
            if start - last_end <= self.sample_interval:
                merged[-1][1] = max(last_end, end)
            else:
                merged.append([start, end])

        return [tuple(seg) for seg in merged]

    def _extract_clips(
        self, video_path: str, segments: List[Tuple[float, float]], output_dir: Path
    ):
        """提取视频片段"""
        for idx, (start, end) in enumerate(segments, 1):
            output_path = output_dir / f"clip_{idx:03d}_{start:.0f}s-{end:.0f}s.mp4"

            cmd = [
                "ffmpeg",
                "-y",
                "-ss",
                str(start),
                "-i",
                video_path,
                "-t",
                str(end - start),
                "-c",
                "copy",
                "-avoid_negative_ts",
                "1",
                str(output_path),
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                self.logger.info(f"已提取片段: {output_path.name}")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"提取片段失败: {e.stderr}")
                raise

    def _save_processing_info(
        self, video_path: Path, segments: List[Tuple[float, float]], output_dir: Path
    ):
        """保存处理信息"""
        import json

        info = {
            "original_file": str(video_path),
            "processed_at": datetime.now().isoformat(),
            "segments": [
                {"start": start, "end": end, "duration": end - start}
                for start, end in segments
            ],
            "total_segments": len(segments),
            "total_duration": sum(end - start for start, end in segments),
            "boundary_stripping": True,
            "sample_interval": self.sample_interval,
            "min_duration": self.min_duration,
        }

        info_path = output_dir / "processing_info.json"
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        self.logger.info(f"处理信息已保存: {info_path}")


def get_video_files(input_path: Path, recursive: bool = False) -> List[Path]:
    """获取视频文件列表"""
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".ts", ".wmv"}

    if input_path.is_file():
        return [input_path] if input_path.suffix.lower() in video_extensions else []

    if recursive:
        return [
            f for f in input_path.rglob("*") if f.suffix.lower() in video_extensions
        ]
    else:
        return [f for f in input_path.iterdir() if f.suffix.lower() in video_extensions]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="优化版视频舞蹈检测")
    parser.add_argument("input", help="输入视频或目录路径")
    parser.add_argument("-o", "--output", default="output", help="输出目录")
    parser.add_argument("--model", default="yolov8n-pose.pt", help="模型路径")
    parser.add_argument("-d", "--debug", action="store_true", help="启用调试")
    parser.add_argument("--recursive", action="store_true", help="递归处理")

    args = parser.parse_args()

    input_path = Path(args.input)

    processor = OptimizedVideoProcessor(
        model_path=args.model, output_dir=args.output, debug=args.debug
    )

    video_files = get_video_files(input_path, args.recursive)

    if not video_files:
        print("未找到视频文件")
        sys.exit(1)

    print(f"找到 {len(video_files)} 个视频文件")

    for video_file in video_files:
        try:
            segments = processor.process_video(str(video_file))
            print(f"{video_file.name}: {len(segments)} 个片段")
        except Exception as e:
            print(f"{video_file.name}: 处理失败 - {e}")

