#!/usr/bin/env python3
"""
video-progress-pkg CLI工具

命令行接口，提供与原始脚本相同的功能
"""

import argparse
import os
import sys
from .core import VideoProgressBar, load_config, save_default_config


def main():
    """CLI入口点"""
    parser = argparse.ArgumentParser(
        description="灵活的视频进度条工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
配置示例:
  # 生成默认配置文件
  video-progress --save-config my_config.json
  
  # 使用配置文件（包含输入视频路径）
  video-progress --config my_config.json
  
  # 配置文件 + 命令行参数覆盖
  video-progress --config config.json --size 80 80
  
  # 纯命令行使用
  video-progress video.mp4 --character assets/characters/panda_running.gif
        """
    )
    
    parser.add_argument('input_video', nargs='?', help='输入视频文件路径')
    parser.add_argument('-o', '--output', help='输出视频文件路径')
    parser.add_argument('--config', help='配置文件路径 (JSON格式)')
    parser.add_argument('--save-config', help='保存默认配置到指定文件')
    
    # 快速配置选项
    parser.add_argument('--character', help='角色GIF文件路径')
    parser.add_argument('--size', nargs=2, type=int, help='角色大小 (宽 高)')
    parser.add_argument('--position', choices=['top', 'bottom'], help='进度条位置')
    parser.add_argument('--color', nargs=3, type=int, help='进度条颜色 (B G R)')
    parser.add_argument('--offset', nargs=2, type=int, help='角色偏移 (X Y)')
    parser.add_argument('--no-effects', action='store_true', help='禁用所有特效')
    
    args = parser.parse_args()
    
    # 保存默认配置
    if args.save_config:
        save_default_config(args.save_config)
        return 0
    
    # --- 配置加载逻辑 ---
    config_path = args.config
    
    # 如果用户未指定配置文件，则尝试加载默认的 config.json
    if not config_path and os.path.exists('config.json'):
        print("💡 未指定配置文件，自动加载 'config.json'")
        config_path = 'config.json'

    config = {}
    if config_path:
        if os.path.exists(config_path):
            config = load_config(config_path)
        else:
            # 如果用户指定了但文件不存在，给出错误提示
            print(f"⚠️  警告: 指定的配置文件 '{config_path}' 不存在，将使用代码内置默认值。")
    
    # 确定输入视频路径
    input_video = args.input_video
    if not input_video:
        # 如果命令行没有指定，从配置文件读取
        input_video = config.get('input_video')
        if not input_video:
            print("❌ 请指定输入视频文件路径或在配置文件中设置 'input_video'")
            parser.print_help()
            return 1
    
    # 确定输出视频路径
    output_video = args.output
    if not output_video:
        output_video = config.get('output_video')
        if not output_video:
            output_video = None  # 使用默认生成规则
    
    # 快速参数覆盖
    if args.character:
        config['character_path'] = args.character
    if args.size:
        config['character_size'] = args.size
    if args.position:
        config['position'] = args.position
    if args.color:
        config['bar_color'] = args.color
    if args.offset:
        config['character_offset_x'] = args.offset[0]
        config['character_offset_y'] = args.offset[1]
    if args.no_effects:
        config['enable_lightning'] = False
        config['enable_particles'] = False
        config['enable_bounce'] = False
    
    try:
        progress_bar = VideoProgressBar(config)
        output_file = progress_bar.process_video(input_video, output_video)
        print(f"\n🎉 成功! 视频已保存为: {output_file}")
        
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e}")
        print("💡 请检查视频文件路径是否正确")
        return 1
    except ValueError as e:
        print(f"❌ 视频处理错误: {e}")
        print("💡 请检查视频文件是否损坏或格式不支持")
        return 1
    except PermissionError as e:
        print(f"❌ 权限错误: {e}")
        print("💡 请检查输出目录的写入权限")
        return 1
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        print("💡 如果问题持续，请尝试使用不同的视频文件或检查依赖安装")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
