#!/usr/bin/env python3
"""
演示如何在其他项目中使用 video-progress-pkg 包
展示API集成和两套预设配置的使用
"""

from video_progress_pkg import VideoProgressBar
import os
from importlib.resources import files

def get_character_path(character_name):
    """获取角色文件路径，支持包安装后的使用"""
    try:
        # 使用importlib.resources获取包内资源路径
        resource_path = files('video_progress_pkg').joinpath('assets', 'characters', f'{character_name}.gif')
        if resource_path.exists():
            return str(resource_path)
        else:
            raise FileNotFoundError(f"角色文件不存在: {resource_path}")
    except (ImportError, AttributeError, FileNotFoundError):
        # 开发环境备用方案
        dev_path = f"src/video_progress_pkg/assets/characters/{character_name}.gif"
        if os.path.exists(dev_path):
            print(f"⚠️ 使用开发环境路径: {dev_path}")
            return dev_path
        else:
            # 如果都找不到，返回None，让VideoProgressBar使用默认角色
            print(f"⚠️ 找不到角色文件 {character_name}.gif，将使用默认角色")
            return None

def check_sample_video():
    """检查测试视频是否存在"""
    # 检查常见的测试视频路径
    test_video_paths = [
        "test_video.mp4",
        "sample.mp4",
        "input.mp4",
        "video.mp4"
    ]

    for path in test_video_paths:
        if os.path.exists(path):
            print(f"✅ 找到测试视频: {path}")
            return path

    print("❌ 未找到测试视频文件")
    print("💡 请在项目根目录放置一个测试视频文件，命名为以下任一名称：")
    for path in test_video_paths:
        print(f"   - {path}")
    print("\n🎬 或者修改 demo_usage.py 中的路径指向您的视频文件")
    return None

def add_progress_bar_to_video(video_path, output_path=None, style="default"):
    """
    为视频添加进度条的封装函数

    Args:
        video_path: 输入视频路径
        output_path: 输出视频路径（可选）
        style: 风格选择 "default" 或 "fancy"

    Returns:
        str: 输出视频路径
    """
    if not video_path or not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在: {video_path}")

    # 定义两套预设配置
    configs = {
        "default": {
            # 默认风格 - 青色主题，皮卡丘，适中特效

            # 进度条基本设置
            "bar_height": 40,                    # 进度条高度（像素）
            "bar_color": [0, 255, 255],          # 进度条颜色（BGR格式：蓝,绿,红）
            "background_color": [50, 50, 50],    # 进度条背景颜色
            "position": "bottom",                # 进度条位置：top/bottom
            "margin": 0,                         # 进度条边距（像素，0=贴边）

            # 角色设置
            "character_path": get_character_path("pikaqiu") or "default",  # 角色GIF路径，如果找不到使用默认
            "character_size": [60, 60],          # 角色大小 [宽, 高]（像素）
            "character_offset_x": 0,             # 角色X轴偏移（像素，正值向右）
            "character_offset_y": -5,            # 角色Y轴偏移（像素，负值向上）

            # 动画效果
            "enable_bounce": True,               # 是否启用弹跳动画
            "bounce_amplitude": 8,               # 弹跳幅度（像素）
            "bounce_speed": 0.2,                 # 弹跳速度（数值越大越快）
            "animation_speed": 3,                # GIF播放速度（帧间隔）

            # 电光特效
            "enable_lightning": True,            # 是否启用电光特效
            "lightning_chance": 0.3,             # 电光触发概率（0-1）
            "lightning_color": [0, 255, 255],    # 电光颜色（BGR格式）

            # 粒子特效
            "enable_particles": True,            # 是否启用粒子特效
            "particle_color": [0, 255, 255],     # 粒子颜色（BGR格式）
            "particle_lifetime": 60,             # 粒子生命周期（帧数）

            # 文字设置
            "text_color": [0, 255, 255],         # 文字颜色（BGR格式）
            "text_size": 0.8,                   # 文字大小（倍数）
            "text_position": "follow",           # 文字位置：left/center/right/follow
            "text_offset_x": 0,                  # 文字X轴偏移（像素）
            "text_offset_y": 0,                  # 文字Y轴偏移（像素，0=进度条内居中）

            # 文字描边设置
            "text_outline": True,                # 是否启用文字描边
            "text_outline_color": [0, 0, 0],     # 描边颜色（BGR格式：黑色）
            "text_outline_thickness": 2,         # 描边厚度（像素）

            # 边框和效果
            "border_thickness": 3,               # 边框厚度（像素）
            "border_color": [255, 255, 255],     # 边框颜色（BGR格式）
            "gradient_enabled": True,            # 是否启用渐变效果
            "glow_enabled": True,                # 是否启用发光效果

            # 多色渐变配置
            "gradient_type": "multi",            # 渐变类型：linear/multi
            "gradient_colors": [                 # 多色渐变颜色序列（BGR格式）
                [0, 255, 255],                   # 起始色：青色
                [0, 200, 255],                   # 中间色：浅蓝
                [0, 150, 255],                   # 结束色：蓝色
                [50, 100, 255]                   # 深蓝色
            ]
        },

        "fancy": {
            # 华丽风格 - 橙色主题，熊猫，丰富特效

            # 进度条基本设置
            "bar_height": 50,                    # 进度条高度（像素）
            "bar_color": [255, 100, 0],          # 进度条颜色（BGR格式：橙色）
            "background_color": [30, 30, 30],    # 进度条背景颜色（深灰）
            "position": "bottom",                # 进度条位置：top/bottom
            "margin": 0,                         # 进度条边距（像素，0=贴边）

            # 角色设置
            "character_path": get_character_path("panda_running") or "default",  # 角色GIF路径，如果找不到使用默认
            "character_size": [90, 90],          # 角色大小 [宽, 高]（像素）
            "character_offset_x": 5,             # 角色X轴偏移（像素，正值向右）
            "character_offset_y": -10,           # 角色Y轴偏移（像素，负值向上）

            # 动画效果
            "enable_bounce": True,               # 是否启用弹跳动画
            "bounce_amplitude": 15,              # 弹跳幅度（像素）
            "bounce_speed": 0.3,                 # 弹跳速度（数值越大越快）
            "animation_speed": 2,                # GIF播放速度（帧间隔）

            # 电光特效
            "enable_lightning": True,            # 是否启用电光特效
            "lightning_chance": 0.4,             # 电光触发概率（0-1）
            "lightning_color": [255, 255, 0],    # 电光颜色（BGR格式：黄色）

            # 粒子特效
            "enable_particles": True,            # 是否启用粒子特效
            "particle_color": [255, 100, 0],     # 粒子颜色（BGR格式：橙色）
            "particle_lifetime": 80,             # 粒子生命周期（帧数）

            # 文字设置
            "text_color": [255, 255, 255],       # 文字颜色（BGR格式：白色）
            "text_size": 1.0,                   # 文字大小（倍数）
            "text_position": "follow",           # 文字位置：left/center/right/follow
            "text_offset_x": 10,                 # 文字X轴偏移（像素）
            "text_offset_y": 0,                  # 文字Y轴偏移（像素，0=进度条内居中）

            # 文字描边设置（华丽风格）
            "text_outline": True,                # 是否启用文字描边
            "text_outline_color": [0, 0, 0],     # 描边颜色（BGR格式：黑色）
            "text_outline_thickness": 3,         # 描边厚度（像素，华丽风格更粗）

            # 边框和效果
            "border_thickness": 4,               # 边框厚度（像素）
            "border_color": [255, 255, 255],     # 边框颜色（BGR格式：白色）
            "gradient_enabled": True,            # 是否启用渐变效果
            "glow_enabled": True,                # 是否启用发光效果

            # 多色渐变配置（华丽风格）
            "gradient_type": "multi",            # 渐变类型：linear/multi
            "gradient_colors": [                 # 华丽的橙红渐变（BGR格式）
                [0, 100, 255],                   # 起始色：橙色
                [0, 150, 255],                   # 中间色：橙红
                [0, 200, 255],                   # 亮橙色
                [0, 255, 255],                   # 黄色
                [100, 255, 200]                  # 结束色：浅黄绿
            ]
        }
    }

    if style not in configs:
        raise ValueError(f"不支持的风格: {style}，支持的风格: {list(configs.keys())}")

    config = configs[style]
    print(f"✅ 使用 {style} 风格配置")

    processor = VideoProgressBar(config)
    return processor.process_video(video_path, output_path)

def demo_api_integration():
    """演示如何在其他项目中集成使用"""
    print("🔧 API集成演示")
    print("=" * 50)

    # 检查是否有测试视频
    source_video = check_sample_video()
    if not source_video:
        return

    print(f"📹 使用视频: {source_video}")

    # 完整的工作流程
    try:
        # 第一步：使用默认风格添加进度条
        print("\n1️⃣ 添加进度条 - 默认风格...")
        default_video = add_progress_bar_to_video(
            video_path=source_video,
            output_path="output/final_default_style.mp4",
            style="default"
        )
        print(f"   ✅ 默认风格视频: {default_video}")

        # 第二步：使用华丽风格添加进度条
        print("\n2️⃣ 添加进度条 - 华丽风格...")
        fancy_video = add_progress_bar_to_video(
            video_path=source_video,
            output_path="output/final_fancy_style.mp4",
            style="fancy"
        )
        print(f"   ✅ 华丽风格视频: {fancy_video}")

        print(f"\n🎉 集成演示完成！")
        print(f"📁 生成了两个不同风格的视频：")
        print(f"   - 默认风格: {default_video}")
        print(f"   - 华丽风格: {fancy_video}")

    except Exception as e:
        print(f"❌ 工作流程失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主演示函数"""
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)

    # 运行API集成演示
    demo_api_integration()

if __name__ == "__main__":
    main()
