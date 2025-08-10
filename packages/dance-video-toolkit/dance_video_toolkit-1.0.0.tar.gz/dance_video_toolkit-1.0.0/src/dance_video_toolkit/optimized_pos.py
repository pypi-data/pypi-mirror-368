import cv2
import os
import numpy as np
from ultralytics import YOLO
from .log import get_logger
from datetime import datetime


class OptimizedDanceDetector:
    """优化版舞蹈检测器 - 基于大腿和髋部出现判断"""

    def __init__(
        self,
        model_path: str = "yolov8n-pose.pt",
        output_dir: str = "output",
        conf_thres: float = 0.5,
        debug: bool = True,
    ):
        self.model = YOLO(model_path)
        self.model.to("cpu").eval()  # 强制使用CPU模式
        self.conf_thres = conf_thres
        self.output_dir = output_dir
        self.debug = debug

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 使用统一日志系统
        self.logger = get_logger("optimized_dance_detector")

        self.logger.info(f"初始化优化舞蹈检测器 - 模型: {model_path}")
        self.logger.info("优化舞蹈检测器初始化完成")

        # 关键点索引
        self.keypoint_indices = {
            "nose": 0,
            "left_shoulder": 5,
            "right_shoulder": 6,
            "left_hip": 11,
            "right_hip": 12,
            "left_knee": 13,
            "right_knee": 14,
            "left_ankle": 15,
            "right_ankle": 16,
        }

    def detect_dance(self, frame, frame_number=None) -> bool:
        """基于腿+hips+上半身的舞蹈检测算法"""
        debug_frame = frame.copy()
        frame_height, frame_width = frame.shape[:2]

        # 执行模型推理
        results = self.model.track(
            frame,
            conf=self.conf_thres,
            classes=[0],  # 只检测人物
            device="cpu",
            verbose=False,
        )

        self.logger.debug(f"检测到的目标数量: {len(results)}")

        if len(results) != 1:
            self.logger.warning(f"跳过检测：检测到{len(results)}个人（需要单人场景）")
            if self.debug:
                self._save_debug_image(
                    debug_frame, suffix="_multi_person", frame_number=frame_number
                )
            return False

        # 获取关键点
        try:
            keypoints_data = results[0].keypoints.xy.tolist()
            if not keypoints_data:
                self.logger.warning("关键点数据为空")
                return False

            keypoints = keypoints_data[0]
            if len(keypoints) < 17:
                self.logger.warning(f"关键点不完整: {len(keypoints)} < 17")
                if self.debug:
                    self._save_debug_image(
                        debug_frame,
                        suffix="_incomplete_keypoints",
                        frame_number=frame_number,
                    )
                return False
        except (IndexError, AttributeError) as e:
            self.logger.warning(f"获取关键点失败: {e}")
            if self.debug:
                self._save_debug_image(
                    debug_frame, suffix="_keypoints_error", frame_number=frame_number
                )
            return False

        try:
            # 获取置信度
            keypoints_conf = results[0].keypoints.conf.tolist()
            if not keypoints_conf:
                return False

            conf = keypoints_conf[0]
            if len(conf) < 17:
                return False
        except:
            conf = [1.0] * len(keypoints)  # 默认置信度

        # 严格的关键点验证函数
        def is_valid_point(point, confidence, threshold=0.5):
            return (
                confidence > threshold
                and point[0] > 10
                and point[1] > 10
                and point[0] < frame_width - 10
                and point[1] < frame_height - 10
            )

        # 获取所有相关关键点
        left_shoulder = keypoints[self.keypoint_indices["left_shoulder"]]
        right_shoulder = keypoints[self.keypoint_indices["right_shoulder"]]
        left_hip = keypoints[self.keypoint_indices["left_hip"]]
        right_hip = keypoints[self.keypoint_indices["right_hip"]]
        left_knee = keypoints[self.keypoint_indices["left_knee"]]
        right_knee = keypoints[self.keypoint_indices["right_knee"]]

        # 获取对应的置信度
        shoulder_conf = [
            conf[self.keypoint_indices["left_shoulder"]],
            conf[self.keypoint_indices["right_shoulder"]],
        ]
        hip_conf = [
            conf[self.keypoint_indices["left_hip"]],
            conf[self.keypoint_indices["right_hip"]],
        ]
        knee_conf = [
            conf[self.keypoint_indices["left_knee"]],
            conf[self.keypoint_indices["right_knee"]],
        ]

        # 验证每个部位的有效性
        upper_body_valid = is_valid_point(
            left_shoulder, shoulder_conf[0]
        ) or is_valid_point(right_shoulder, shoulder_conf[1])
        hips_valid = is_valid_point(left_hip, hip_conf[0]) or is_valid_point(
            right_hip, hip_conf[1]
        )
        # 大腿判定：只要臀部关键点有效，就认为大腿出现
        thighs_valid = is_valid_point(left_hip, hip_conf[0]) or is_valid_point(
            right_hip, hip_conf[1]
        )

        # 舞蹈检测标准：需要上半身+hips+大腿都有效
        is_dancing = upper_body_valid and hips_valid and thighs_valid

        features = {
            "upper_body_valid": upper_body_valid,
            "hips_valid": hips_valid,
            "thighs_valid": thighs_valid,
            "confidence_threshold": 0.5,
            "algorithm": "leg+hips+upper_body",
        }

        self.logger.debug(f"检测特征: {features}")

        # 调试可视化
        if self.debug:
            self._add_debug_visualization(debug_frame, keypoints, features, is_dancing)
            self._save_debug_image(
                debug_frame, suffix="_new_detection", frame_number=frame_number
            )

        self.logger.info(f"新算法检测结果: {'跳舞' if is_dancing else '不跳舞'}")
        return is_dancing

    def _add_debug_visualization(self, frame, keypoints, features, is_dancing):
        """添加可视化调试信息"""
        frame_height, frame_width = frame.shape[:2]

        # 主要结果
        result_text = f"DANCING: {is_dancing}"
        color = (0, 255, 0) if is_dancing else (0, 0, 255)
        cv2.putText(frame, result_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # 特征信息
        y_offset = 60
        info_texts = [
            f"Hip: {features['hip_valid']}",
            f"Thigh: {features['thigh_valid']}",
            f"Left Hip: {int(features['left_hip_pos'][0])}, {int(features['left_hip_pos'][1])}",
            f"Right Hip: {int(features['right_hip_pos'][0])}, {int(features['right_hip_pos'][1])}",
        ]

        for text in info_texts:
            cv2.putText(
                frame,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
            )
            y_offset += 20

        # 绘制关键点和连线
        self._draw_hip_thigh_skeleton(frame, keypoints)

    def _draw_hip_thigh_skeleton(self, frame, keypoints):
        """绘制髋部和大腿的骨架"""
        # 定义髋部到大腿的连接
        connections = [
            (11, 13),  # 左髋到左膝
            (12, 14),  # 右髋到右膝
            (11, 12),  # 左髋到右髋
        ]

        # 绘制关键点
        keypoints_to_draw = [11, 12, 13, 14]  # 髋部和膝盖
        for idx in keypoints_to_draw:
            if idx < len(keypoints):
                x, y = int(keypoints[idx][0]), int(keypoints[idx][1])
                if x > 0 and y > 0:
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                    cv2.putText(
                        frame,
                        str(idx),
                        (x + 8, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 255, 255),
                        1,
                    )

        # 绘制连线
        for start_idx, end_idx in connections:
            if start_idx < len(keypoints) and end_idx < len(keypoints):
                start = (int(keypoints[start_idx][0]), int(keypoints[start_idx][1]))
                end = (int(keypoints[end_idx][0]), int(keypoints[end_idx][1]))
                if start[0] > 0 and start[1] > 0 and end[0] > 0 and end[1] > 0:
                    cv2.line(frame, start, end, (0, 255, 255), 2)

    def _save_debug_image(self, frame, suffix="", frame_number=None):
        """保存调试图像"""
        if frame_number is not None:
            debug_path = os.path.join(
                self.output_dir, f"debug_frame_{frame_number:06d}_{suffix}.jpg"
            )
        else:
            debug_path = os.path.join(self.output_dir, f"debug_{suffix}.jpg")

        cv2.imwrite(debug_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        self.logger.debug(f"保存调试图像: {debug_path}")


# 兼容旧接口
class Pos(OptimizedDanceDetector):
    """兼容旧接口的类"""

    def predict_np(self, frame, frame_number=None):
        """兼容旧接口的方法"""
        return self.detect_dance(frame, frame_number)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "test.jpg"

    detector = OptimizedDanceDetector(debug=False)

    try:
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"无法加载图像: {image_path}")
            sys.exit(1)

        result = detector.detect_dance(frame)
        print(f"检测结果: {'跳舞' if result else '不跳舞'}")

    except Exception as e:
        print(f"检测失败: {e}")
        sys.exit(1)
