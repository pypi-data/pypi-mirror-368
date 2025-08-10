# 舞蹈视频处理工具包 🎯

简洁高效的舞蹈视频处理工具包，专注于两个核心功能：过滤多人视频和切分舞蹈片段。

## 🚀 核心功能

### 功能1: 过滤多人视频
- **智能检测**: 自动识别视频中的舞者人数
- **批量过滤**: 标记多人视频，保留单人舞蹈
- **结果记录**: 自动生成过滤报告

### 功能2: 切分舞蹈视频
- **精准识别**: 基于上半身+臀部+大腿的严格检测
- **自动切分**: 智能识别舞蹈片段并提取
- **长度过滤**: 自动丢弃小于5秒的短片段
- **模型优化**: 支持多种YOLOv8模型，自动GPU加速

## 📦 安装

```bash
# 安装依赖
pip install -r requirements.in

# 确保FFmpeg已安装
ffmpeg -version
```

## 🎯 快速开始

### 功能1：过滤多人视频
```bash
# 过滤目录中的多人视频
python dance_toolkit.py /path/to/videos --mode filter

# 递归处理子目录
python dance_toolkit.py /path/to/videos --mode filter --recursive
```

### 功能2：切分舞蹈视频
```bash
# 切分舞蹈视频
python dance_toolkit.py /path/to/videos --mode split

# 同时过滤多人并切分
python dance_toolkit.py /path/to/videos --mode both

# 处理单个文件
python dance_toolkit.py video.mp4 --mode split
```

## ⚙️ 高级配置

```bash
# 自定义参数
python dance_toolkit.py /path/to/videos \
    --mode split \
    --model yolov8m-pose.pt \
    --min-duration 8.0 \
    --sample-interval 2 \
    --output my_output \
    --debug
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--mode` | split | 处理模式: filter/split/both |
| `--model` | yolov8n-pose.pt | 姿势检测模型 |
| `--min-duration` | 5.0 | 最小时长(秒)，小于此值丢弃 |
| `--sample-interval` | 3 | 采样间隔(秒) |
| `--recursive` | False | 递归处理子目录 |
| `--debug` | False | 启用调试模式 |

## 📊 检测逻辑

### 舞蹈检测标准
- **上半身**: 肩膀关键点有效
- **臀部**: 臀部关键点有效
- **大腿**: 臀部关键点有效（代表大腿出现）
- **置信度**: > 0.5

### 模型选择
- `yolov8n-pose.pt` - 超轻量，速度最快
- `yolov8s-pose.pt` - 小模型，平衡性能
- `yolov8m-pose.pt` - 中等模型，精度更好
- `yolov8l-pose.pt` - 大模型，高精度
- `yolov8x-pose.pt` - 超大模型，最高精度

## 📁 输出结构

```
output/
├── logs/
│   └── dance_toolkit_YYYYMMDD_HHMMSS.log
├── filter_results.json   # 过滤结果记录
├── 【视频名】/
│   ├── clip_001_0s-15s.mp4
│   ├── clip_002_25s-40s.mp4
│   └── processing_info.json
└── ...
```

## 🎬 使用场景

1. **舞蹈教学**: 提取干净的教学片段
2. **内容创作**: 准备舞蹈素材
3. **数据清洗**: 过滤掉多人干扰视频
4. **批量处理**: 大规模视频整理

## 📈 性能优化

- CPU/GPU自动选择
- 稀疏采样减少处理时间
- 流式复制保持视频质量
- 批处理支持

