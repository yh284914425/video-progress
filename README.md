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
video_cut/
├── video_progress.py         # 主程序
├── config.json              # 配置文件
├── assets/                  # 素材
│   ├── characters/         # 角色GIF
│   │   ├── pikaqiu.gif
│   │   └── panda_running.gif
│   └── samples/           # 示例视频
│       └── sample_video.mp4
└── output/                # 输出目录
    └── videos/           # 生成的视频
```

## 🚀 快速使用

### 1. 安装依赖
```bash
uv sync
```

### 2. 基本使用
```bash
# 使用默认皮卡丘
python video_progress.py assets/samples/sample_video.mp4

# 使用熊猫角色
python video_progress.py video.mp4 --character assets/characters/panda_running.gif

# 调整角色大小
python video_progress.py video.mp4 --size 80 80

# 调整角色位置
python video_progress.py video.mp4 --offset 10 -20
```

### 3. 配置文件使用
```bash
# 生成默认配置（包含输入视频路径）
python video_progress.py --save-config my_config.json

# 使用配置文件（无需指定视频路径）
python video_progress.py --config my_config.json

# 配置文件 + 参数覆盖
python video_progress.py --config my_config.json --size 100 100
```

## ⚙️ 灵活配置

### 快速参数调整
- `--character` 角色GIF路径
- `--size W H` 角色大小（宽 高）
- `--position top/bottom` 进度条位置
- `--color B G R` 进度条颜色（BGR格式）
- `--offset X Y` 角色偏移（X Y像素）
- `--no-effects` 禁用所有特效

### 配置文件参数（config.json）

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
# 1. 生成配置模板
python video_progress.py --save-config blue_theme.json

# 2. 编辑配置文件 (修改视频路径、颜色、大小等)
# {
#   "input_video": "my_video.mp4",
#   "character_path": "assets/characters/panda_running.gif",
#   "bar_color": [255, 0, 0],
#   ...
# }

# 3. 使用配置（无需指定视频）
python video_progress.py --config blue_theme.json
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

---

**尽情发挥创意，制作独特的进度条！** 🎉
