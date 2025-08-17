"""
video-progress-pkg: 灵活的视频进度条工具包

这个包提供了一个可以在视频上添加动画进度条的工具，支持：
- 任意GIF角色动画
- 丰富的视觉特效（电光、粒子、弹跳等）
- 完全可配置的样式参数
- 音频保留

使用示例:
    from video_progress_pkg import VideoProgressBar
    
    # 基本使用
    processor = VideoProgressBar()
    output_path = processor.process_video("input.mp4")
    
    # 自定义配置
    config = {
        "character_path": "path/to/character.gif",
        "bar_color": [0, 255, 255],
        "enable_bounce": True
    }
    processor = VideoProgressBar(config)
    output_path = processor.process_video("input.mp4", "output.mp4")
"""

from .core import VideoProgressBar, load_config, save_default_config

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = ""
__description__ = "灵活的视频进度条工具包"

__all__ = [
    "VideoProgressBar",
    "load_config", 
    "save_default_config"
]
