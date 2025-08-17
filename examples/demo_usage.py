#!/usr/bin/env python3
"""
演示如何在其他项目中使用 video-progress-pkg 包
"""

from video_progress_pkg import VideoProgressBar, save_default_config, load_config
import os

def check_sample_video():
    """检查示例视频是否存在"""
    try:
        # 使用标准的importlib.resources方式
        from importlib.resources import files
        resource_path = files('video_progress_pkg').joinpath(
            'assets', 'samples', 'KRITIKAQUEEN2-1956650788194783326-01.mp4')
        if resource_path.is_file():
            return str(resource_path)
    except (ImportError, AttributeError, FileNotFoundError):
        pass
    
    print(f"❌ 示例视频不存在，请确保有可用的视频文件")
    print("💡 请将您的视频文件放在 video_progress_pkg/assets/samples/ 目录")
    return None

def demo_basic_usage():
    """演示基本使用方法"""
    print("🎯 演示1: 基本使用")
    
    # 检查是否有示例视频
    sample_video = check_sample_video()
    if not sample_video:
        return
    
    # 最简单的使用方式
    processor = VideoProgressBar()
    
    try:
        output_path = processor.process_video(sample_video)
        print(f"✅ 基本使用成功！输出文件: {output_path}")
    except Exception as e:
        print(f"❌ 处理失败: {e}")

def demo_custom_config():
    """演示自定义配置"""
    print("\n🎨 演示2: 自定义配置")
    
    sample_video = check_sample_video()
    if not sample_video:
        return
    
    # 自定义配置
    custom_config = {
        "bar_color": [255, 0, 0],  # 红色进度条 (BGR格式)
        "character_size": [80, 80],  # 更大的角色
        "position": "top",  # 顶部位置
        "enable_bounce": True,
        "bounce_amplitude": 12,  # 更大的弹跳幅度
        "enable_lightning": True,
        "lightning_chance": 0.5,  # 更频繁的电光
        "text_color": [0, 255, 0],  # 绿色文字
        "text_position": "follow",
        "border_thickness": 4,
        "border_color": [255, 255, 255]
    }
    
    processor = VideoProgressBar(custom_config)
    
    try:
        output_path = processor.process_video(
            input_video=sample_video,
            output_video="output/videos/custom_demo.mp4"
        )
        print(f"✅ 自定义配置成功！输出文件: {output_path}")
    except Exception as e:
        print(f"❌ 处理失败: {e}")

def demo_config_file():
    """演示使用预设配置文件"""
    print("\n📄 演示3: 使用预设配置")
    
    sample_video = check_sample_video()
    if not sample_video:
        return
    
    # 测试不同的预设配置
    configs = ["fancy"]
    
    for config_name in configs:
        print(f"\n🎨 测试配置: {config_name}")
        config_path = f"configs/{config_name}.json"
        
        if os.path.exists(config_path):
            config = load_config(config_path)
            config["input_video"] = sample_video
            
            processor = VideoProgressBar(config)
            try:
                output_path = processor.process_video(
                    sample_video,
                    f"output/{config_name}_demo.mp4"
                )
                print(f"✅ {config_name} 风格完成: {output_path}")
            except Exception as e:
                print(f"❌ {config_name} 处理失败: {e}")
        else:
            print(f"❌ 配置文件不存在: {config_path}")

def demo_api_integration():
    """演示如何集成到现有项目中"""
    print("\n🔧 演示4: API集成示例")
    
    def your_video_generation_function():
        """模拟您的视频生成功能"""
        # 这里是您现有的视频生成逻辑
        # 返回生成的视频路径
        return "assets/samples/KRITIKAQUEEN2-1956650788194783326-01.mp4"
    
    def add_progress_bar_to_video(video_path, output_path=None):
        """为视频添加进度条的封装函数"""
        config = {
            "bar_color": [0, 255, 255],  # 青色
            "character_size": [70, 70],
            "enable_bounce": True,
            "enable_particles": True,
            "text_position": "follow"
        }
        
        processor = VideoProgressBar(config)
        return processor.process_video(video_path, output_path)
    
    # 完整的工作流程
    try:
        # 第一步：生成您的视频
        print("1️⃣ 生成视频...")
        source_video = your_video_generation_function()
        print(f"   视频已生成: {source_video}")
        
        # 第二步：添加进度条
        print("2️⃣ 添加进度条...")
        final_video = add_progress_bar_to_video(
            video_path=source_video,
            output_path="output/videos/final_with_progress.mp4"
        )
        print(f"   ✅ 最终视频: {final_video}")
        
    except Exception as e:
        print(f"❌ 工作流程失败: {e}")

def main():
    """主演示函数"""
    print("🎬 video-progress-pkg 使用演示")
    print("=" * 50)
    
    # 确保输出目录存在
    os.makedirs("output/videos", exist_ok=True)
    
    # 运行各种演示
    demo_basic_usage()
    demo_custom_config()
    demo_config_file()
    demo_api_integration()
    
    print("\n🎉 演示完成！")
    print("\n📚 更多使用方法请查看 PACKAGE_USAGE.md")

if __name__ == "__main__":
    main()
