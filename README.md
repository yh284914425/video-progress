# 视频进度条工具 (Video Progress Bar Tool)

这个工具可以在视频中添加可视化的进度条，让观看者清楚地看到视频播放进度和剩余时间。

## 功能特点

- ✅ 在视频底部或顶部添加进度条
- ✅ 可自定义进度条颜色、大小和位置
- ✅ 显示实时的百分比进度
- ✅ 支持多种视频格式
- ✅ 保持原视频质量和帧率

## 安装依赖

```bash
# 安装项目依赖
uv sync
```

## 使用方法

### 基本用法

```bash
# 为视频添加默认的绿色进度条（底部）
python main.py your_video.mp4

# 指定输出文件名
python main.py your_video.mp4 -o output_with_progress.mp4
```

### 自定义选项

```bash
# 设置进度条颜色为红色
python main.py your_video.mp4 --color red

# 将进度条放在视频顶部
python main.py your_video.mp4 --position top

# 调整进度条高度为30像素
python main.py your_video.mp4 --height 30

# 调整进度条边距为20像素
python main.py your_video.mp4 --margin 20

# 组合多个选项
python main.py your_video.mp4 --color blue --position top --height 25 --margin 15
```

### 可用选项

- `--color`: 进度条颜色 (`green`, `red`, `blue`, `yellow`)
- `--position`: 进度条位置 (`top`, `bottom`)
- `--height`: 进度条高度（像素）
- `--margin`: 进度条边距（像素）
- `-o, --output`: 输出文件路径

## 示例

假设你有一个名为 `wlzho-1956258806947831850-01.mp4` 的视频文件：

```bash
# 添加默认进度条
python main.py wlzho-1956258806947831850-01.mp4

# 这将生成 wlzho-1956258806947831850-01_with_progress.mp4
```

## 进度条效果

- 🟢 **进度条背景**: 灰色半透明背景
- 🟢 **进度填充**: 根据播放进度动态填充
- 🟢 **百分比文本**: 右上角显示精确的百分比
- 🟢 **实时更新**: 每一帧都会更新进度

## 技术细节

- 使用 OpenCV 进行视频处理和图形绘制
- 支持各种常见视频格式（MP4、AVI、MOV等）
- 保持原始视频的分辨率和帧率
- 内存友好的逐帧处理方式

## 错误处理

工具包含完整的错误处理：
- 检查视频文件是否存在
- 验证视频文件是否可读
- 确保输出文件可以正常创建

## 依赖项

- `opencv-python`: 视频处理和图形绘制
- `moviepy`: 视频文件操作（备用）
- `pillow`: 图像处理支持
- `numpy`: 数值计算

## 性能说明

处理时间取决于：
- 视频长度和分辨率
- 计算机性能
- 输出编码设置

一般来说，处理1分钟的1080p视频大约需要1-3分钟时间。
