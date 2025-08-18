# 🎮 灵活视频进度条工具

高度可配置的视频进度条工具，支持任意GIF角色，所有参数都可以自由调整。

## ✨ 核心特色

- 🎯 **任意GIF角色** - 支持任何透明背景的GIF动画
- 🎨 **完全自定义** - 所有视觉参数都可调整
- 📍 **精确定位** - 角色位置、偏移量、大小任意设置
- ⚡ **丰富特效** - 电光、粒子、弹跳动画可开关
- 🔧 **配置文件** - JSON配置，方便保存和分享设置
- 🔊 **音频保留** - 自动保留原视频音频（需要moviepy）

## 📁 项目结构

```
video-progress/
├── video_progress_pkg/      # 📦 Python包
│   ├── __init__.py         # 包接口
│   ├── core.py            # 核心功能
│   ├── cli.py             # 命令行接口
│   └── assets/            # 📦 包内资源
│       ├── characters/    # 角色GIF
│       └── samples/      # 示例视频
├── configs/                # 🔧 配置文件（2个预设）
│   ├── default.json       # 默认配置
│   └── fancy.json         # 华丽效果
├── examples/               # 📝 使用示例
│   └── demo_usage.py      # 完整演示
├── output/                 # 📤 输出目录
├── pyproject.toml         # 包配置
└── README.md              # 完整文档
```

## 🚀 快速开始

### 1. 安装项目
```bash
# 安装包（开发模式）
uv pip install -e .

# 或完整安装（包含音频支持）
uv pip install -e .[full]
```

### 2. 快速测试
```bash
# 运行完整演示
uv run python examples/demo_usage.py
```

### 3. 两种使用方式

#### 方式1：Python包API（推荐）
```python
from video_progress_pkg import VideoProgressBar

# 基本使用
processor = VideoProgressBar()
output_path = processor.process_video("your_video.mp4")

# 使用预设配置
from video_progress_pkg import load_config
config = load_config("configs/fancy.json")
config["input_video"] = "your_video.mp4"
processor = VideoProgressBar(config)
output_path = processor.process_video(config["input_video"])
```

#### 方式2：命令行使用
```bash
# 使用默认配置
video-progress your_video.mp4

# 使用预设配置文件
video-progress --config configs/fancy.json

# 自定义参数
video-progress video.mp4 --character assets/characters/panda_running.gif --size 80 80
```

### 4. 两种预设风格
```bash
# 默认风格（平衡效果，适合大多数场景）
video-progress --config configs/default.json

# 华丽风格（丰富特效，适合娱乐视频）
video-progress --config configs/fancy.json
```

## ⚙️ 灵活配置

### 快速参数调整
- `--character` 角色GIF路径
- `--size W H` 角色大小（宽 高）
- `--position top/bottom` 进度条位置
- `--color B G R` 进度条颜色（BGR格式）
- `--offset X Y` 角色偏移（X Y像素）
- `--no-effects` 禁用所有特效

### 配置文件说明

现有两个预设配置：
- **default.json** - 默认配置，青色主题，适中特效  
- **fancy.json** - 华丽风格，橙色主题，丰富特效

```json
{
  "input_video": "assets/samples/sample_video.mp4",  // 输入视频路径
  "output_video": "",                                // 输出视频路径（空为自动）
  
  "bar_height": 40,              // 进度条高度
  "bar_color": [0, 255, 255],    // 进度条颜色 (BGR)
  "position": "bottom",          // 位置: top/bottom
  "margin": 25,                  // 边距
  
  "character_path": "assets/characters/pikaqiu.gif",
  "character_size": [60, 60],    // 角色大小 [宽, 高]
  "character_offset_x": 0,       // X轴偏移
  "character_offset_y": -5,      // Y轴偏移
  
  "enable_bounce": true,         // 弹跳动画
  "bounce_amplitude": 8,         // 弹跳幅度
  "bounce_speed": 0.2,          // 弹跳速度
  "animation_speed": 3,         // GIF播放速度
  
  "enable_lightning": true,      // 电光特效
  "lightning_chance": 0.3,      // 电光概率
  "lightning_color": [0, 255, 255],
  
  "enable_particles": true,      // 粒子特效
  "particle_color": [0, 255, 255],
  "particle_lifetime": 60,
  
  "text_color": [0, 255, 255],   // 文字颜色
  "text_size": 0.8,             // 文字大小
  "text_position": "follow",    // 文字位置: left/center/right/follow
  "text_offset_x": 0,           // 文字X偏移
  "text_offset_y": -10,         // 文字Y偏移
  
  "border_thickness": 3,         // 边框厚度
  "border_color": [255, 255, 255],
  "gradient_enabled": true,      // 渐变效果
  "glow_enabled": true          // 发光效果
}
```

## 🎨 自定义角色

### 添加新角色
1. 准备透明背景的GIF文件
2. 放入 `assets/characters/` 目录
3. 使用 `--character` 指定路径

### 角色要求
- ✅ GIF格式，支持透明背景
- ✅ 建议尺寸：64x64 到 128x128
- ✅ 帧数不限，工具会自动循环

## 📝 使用示例

### 示例1: 大号熊猫，顶部位置
```bash
python video_progress.py video.mp4 \
  --character assets/characters/panda_running.gif \
  --size 100 100 \
  --position top \
  --offset 0 10
```

### 示例2: 蓝色主题，无特效
```bash
python video_progress.py video.mp4 \
  --color 255 0 0 \
  --no-effects
```

### 示例3: 使用配置文件
```bash
# 1. 使用预设配置
video-progress --config configs/fancy.json

# 2. 或者复制并修改配置文件
cp configs/default.json configs/my_theme.json
# 编辑 my_theme.json 修改颜色、大小等

# 3. 使用自定义配置
video-progress --config configs/my_theme.json
```

## 🔧 高级定制

### 坐标系统
- **X轴**: 左到右，正值向右偏移
- **Y轴**: 上到下，负值向上偏移
- **原点**: 进度条上的角色默认位置

### 颜色格式
所有颜色使用BGR格式（蓝-绿-红）：
- 红色: `[0, 0, 255]`
- 绿色: `[0, 255, 0]`
- 蓝色: `[255, 0, 0]`
- 黄色: `[0, 255, 255]`

### 特效控制
可以单独控制每种特效：
- `enable_bounce` - 角色弹跳
- `enable_lightning` - 电光效果
- `enable_particles` - 粒子尾迹
- `glow_enabled` - 进度条发光
- `gradient_enabled` - 渐变填充

### 文字位置选项
- `left` - 固定在左侧
- `center` - 固定在中央
- `right` - 固定在右侧
- `follow` - 跟随进度条移动 ⭐ 推荐

## 📊 文件大小说明

由于视频重新编码，文件大小会显著增加（10-20倍），这是正常现象。原因：
- OpenCV重新编码降低压缩率
- 添加动画增加每帧复杂度
- 逐帧处理无法使用高效编码

## 🛠️ 故障排除

**角色显示有黑边**：确保GIF有透明背景
**角色太大/太小**：调整 `character_size` 参数  
**位置不对**：使用 `character_offset_x/y` 微调
**特效太多**：使用 `--no-effects` 或在配置中关闭
**VSCode无法预览生成的视频**：已优化编码器选择，应该可以正常预览
**生成的视频没有声音**：需要安装moviepy (`uv add moviepy`)，否则使用无音频模式

## 🔗 在其他项目中使用

要在你的另一个项目中使用 `video-progress-pkg`，推荐遵循标准的 Python 开发流程，即为新项目创建独立的虚拟环境。

**强烈不推荐**直接复制文件夹或使用 `sys.path`，这两种方法都容易出错且难以维护。

下面是标准的使用步骤：

### 第一步：为你的新项目创建并激活虚拟环境

假设你的新项目位于 `/path/to/your/other/project`。

```bash
# 1. 进入你的新项目目录
cd /path/to/your/other/project

# 2. 创建一个虚拟环境 (通常命名为 .venv)
python3 -m venv .venv

# 3. 激活虚拟环境
# 在 macOS / Linux 上:
source .venv/bin/activate
# 在 Windows 上，使用: .venv\Scripts\activate
```
> 激活后，你的终端提示符前会出现 `(.venv)` 字样。

### 第二步：安装 `video-progress-pkg`

在**已激活虚拟环境**的终端中，使用 `pip` 从本地路径安装 `video-progress-pkg`。

推荐使用“可编辑模式” (`-e`) 进行安装，这样你在 `video-progress-pkg` 源码中所做的任何修改，都会立刻在新项目中生效，无需重装。

```bash
# -e 表示 "editable" (可编辑)
# /Users/sheng/Desktop/code/video-progress 是你这个包的存放路径
pip install -e /Users/sheng/Desktop/code/video-progress
```

### 第三步：在新项目代码中使用

现在，你可以在新项目的 Python 文件中，像使用任何其他库一样导入并使用它。

**示例 (`/path/to/your/other/project/main.py`):**

```python
from video_progress_pkg import VideoProgressBar
import os

# 你的视频文件路径
video_file = "path/to/some/video.mp4" 
output_dir = "output_videos"
os.makedirs(output_dir, exist_ok=True)

if not os.path.exists(video_file):
    print(f"错误：找不到视频文件 {video_file}")
else:
    print("🚀 开始处理视频...")
    try:
        # 初始化处理器
        processor = VideoProgressBar()

        # 定义输出路径
        output_path = os.path.join(output_dir, "processed_video.mp4")

        # 添加进度条
        final_video = processor.process_video(video_file, output_path)
        
        print(f"🎉 视频处理完成！文件保存在: {final_video}")

    except Exception as e:
        print(f"❌ 处理过程中发生错误: {e}")
```

这个流程确保了你的项目依赖清晰、环境隔离，是 Python 开发的最佳实践。

---

**尽情发挥创意，制作独特的进度条！** 🎉
