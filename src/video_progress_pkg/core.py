#!/usr/bin/env python3
"""
灵活的视频进度条工具 - 核心模块

支持任意GIF角色，可调整所有视觉参数
作者: AI Assistant
版本: 1.0.0
"""

import cv2
import numpy as np
import os
import math
import json
from typing import Tuple, Optional, List, Dict, Any
from PIL import Image, ImageSequence
import tempfile

# 用于资源文件路径处理
from importlib.resources import files

# moviepy作为可选依赖
try:
    from moviepy import VideoFileClip, ImageSequenceClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️  moviepy未安装，将使用OpenCV模式（无音频）")

# 抑制OpenCV的FFmpeg警告信息
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'protocol_whitelist;file,rtp,udp'


class VideoProgressBar:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        灵活的进度条配置
        
        Args:
            config: 配置字典，包含所有可调整的参数。如果为None，使用默认配置。
        """
        # 如果没有提供配置，使用默认配置
        if config is None:
            config = {}
            
        # 进度条基本配置
        self.bar_height = config.get('bar_height', 40)
        self.bar_color = tuple(config.get('bar_color', [0, 255, 255]))  # BGR格式
        self.background_color = tuple(config.get('background_color', [50, 50, 50]))
        self.position = config.get('position', 'bottom')  # top/bottom
        self.margin = config.get('margin', 25)
        
        # 角色配置 - 使用包内资源的相对路径
        default_character = self._get_default_character_path()
        self.character_path = config.get('character_path', default_character)
        self.character_size = tuple(config.get('character_size', [60, 60]))
        self.character_offset_x = config.get('character_offset_x', 0)  # 角色X轴偏移
        self.character_offset_y = config.get('character_offset_y', -5)  # 角色Y轴偏移
        
        # 动画配置
        self.enable_bounce = config.get('enable_bounce', True)
        self.bounce_amplitude = config.get('bounce_amplitude', 8)
        self.bounce_speed = config.get('bounce_speed', 0.2)
        self.animation_speed = config.get('animation_speed', 3)  # GIF帧切换速度
        
        # 特效配置
        self.enable_lightning = config.get('enable_lightning', True)
        self.lightning_chance = config.get('lightning_chance', 0.3)  # 电光触发概率
        self.lightning_color = tuple(config.get('lightning_color', [0, 255, 255]))
        
        self.enable_particles = config.get('enable_particles', True)
        self.particle_color = tuple(config.get('particle_color', [0, 255, 255]))
        self.particle_lifetime = config.get('particle_lifetime', 60)
        
        # 文字配置
        self.text_color = tuple(config.get('text_color', [0, 255, 255]))
        self.text_size = config.get('text_size', 0.8)
        self.text_position = config.get('text_position', 'right')  # left/right/center
        self.text_offset_x = config.get('text_offset_x', 15)
        self.text_offset_y = config.get('text_offset_y', 0)
        
        # 进度条样式配置
        self.border_thickness = config.get('border_thickness', 3)
        self.border_color = tuple(config.get('border_color', [255, 255, 255]))
        self.gradient_enabled = config.get('gradient_enabled', True)
        self.glow_enabled = config.get('glow_enabled', True)
        
        # 内部变量
        self.frame_count = 0
        self.character_frames = self._load_character()
        self.total_frames = len(self.character_frames)
        self.lightning_particles = []
        self.trail_particles = []

    def _get_default_character_path(self) -> str:
        """获取默认角色路径 (使用 importlib.resources)"""
        try:
            # 直接从'video_progress_pkg'包中寻找资源文件路径
            # 这是最健壮的方式，无论包如何安装都能工作
            resource_path = files('video_progress_pkg').joinpath(
                'assets', 'characters', 'pikaqiu.gif')
            return str(resource_path)
        except (ImportError, AttributeError, FileNotFoundError):
            # 如果上面的方法因某种原因失败，提供一个最终的备用方案
            print("⚠️ 无法通过 importlib.resources 定位资源文件，将使用相对路径。")
            return 'assets/characters/pikaqiu.gif'

    def _load_character(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """加载角色GIF的所有帧，包含透明遮罩"""
        frames = []
        
        if not os.path.exists(self.character_path):
            print(f"❌ 角色文件不存在: {self.character_path}")
            return [(self._create_default_character(), np.ones(self.character_size[::-1], dtype=np.uint8) * 255)]
        
        try:
            with Image.open(self.character_path) as gif:
                print(f"🎮 加载角色GIF: {gif.size}, 帧数: {gif.n_frames}")
                
                for frame_idx in range(gif.n_frames):
                    gif.seek(frame_idx)
                    frame_rgba = gif.convert('RGBA')
                    frame_resized = frame_rgba.resize(self.character_size, Image.Resampling.LANCZOS)
                    frame_array = np.array(frame_resized)
                    
                    # 分离RGB和Alpha通道
                    rgb_channels = frame_array[:, :, :3]
                    alpha_channel = frame_array[:, :, 3]
                    
                    # 转换颜色空间 RGB -> BGR
                    frame_bgr = cv2.cvtColor(rgb_channels, cv2.COLOR_RGB2BGR)
                    frames.append((frame_bgr, alpha_channel))
                    
        except Exception as e:
            print(f"❌ 加载角色GIF出错: {e}")
            default_char = self._create_default_character()
            default_mask = np.ones(self.character_size[::-1], dtype=np.uint8) * 255
            frames = [(default_char, default_mask)]
            
        return frames

    def _create_default_character(self) -> np.ndarray:
        """创建默认角色"""
        size = self.character_size[0]
        char = np.zeros((self.character_size[1], self.character_size[0], 3), dtype=np.uint8)
        
        center = (size // 2, self.character_size[1] // 2)
        radius = min(size, self.character_size[1]) // 3
        
        # 绘制简单的圆形角色
        cv2.circle(char, center, radius, self.bar_color, -1)
        cv2.circle(char, (center[0] - radius//3, center[1] - radius//3), 3, (0, 0, 0), -1)
        cv2.circle(char, (center[0] + radius//3, center[1] - radius//3), 3, (0, 0, 0), -1)
        
        return char

    def _blend_with_alpha(self, background: np.ndarray, foreground: np.ndarray, 
                         alpha_mask: np.ndarray, x: int, y: int) -> np.ndarray:
        """使用Alpha通道混合前景和背景"""
        result = background.copy()
        h, w = foreground.shape[:2]
        
        if (y >= 0 and y + h <= background.shape[0] and 
            x >= 0 and x + w <= background.shape[1]):
            
            bg_region = background[y:y+h, x:x+w]
            alpha = alpha_mask.astype(float) / 255.0
            alpha = np.expand_dims(alpha, axis=2)
            
            blended = foreground * alpha + bg_region * (1 - alpha)
            result[y:y+h, x:x+w] = blended.astype(np.uint8)
        
        return result

    def _update_lightning_effects(self, char_x: int, char_y: int):
        """更新电光特效"""
        if not self.enable_lightning:
            return
            
        if self.frame_count % 15 == 0 and np.random.random() > (1 - self.lightning_chance):
            lightning = {
                'x': char_x + np.random.randint(-20, 20),
                'y': char_y + np.random.randint(-10, 10),
                'life': 10,
                'intensity': np.random.randint(5, 15)
            }
            self.lightning_particles.append(lightning)
        
        self.lightning_particles = [p for p in self.lightning_particles if p['life'] > 0]
        for particle in self.lightning_particles:
            particle['life'] -= 1

    def _draw_lightning_effects(self, frame: np.ndarray):
        """绘制电光特效"""
        for particle in self.lightning_particles:
            alpha = particle['life'] / 10.0
            
            start_point = (particle['x'], particle['y'])
            for i in range(3):
                end_x = particle['x'] + np.random.randint(-15, 15)
                end_y = particle['y'] + np.random.randint(-15, 15)
                end_point = (end_x, end_y)
                
                cv2.line(frame, start_point, end_point, self.lightning_color, 2)
                cv2.line(frame, start_point, end_point, (255, 255, 255), 1)

    def _update_trail_particles(self, char_x: int, char_y: int):
        """更新尾迹粒子"""
        if not self.enable_particles:
            return
            
        if self.frame_count % 5 == 0:
            particle = {
                'x': char_x + self.character_size[0] // 2 + np.random.randint(-5, 5),
                'y': char_y + self.character_size[1] // 2 + np.random.randint(-5, 5),
                'life': self.particle_lifetime,
                'drift_x': np.random.randint(-2, 1),
                'drift_y': np.random.randint(-2, 2),
                'size': np.random.randint(2, 5)
            }
            self.trail_particles.append(particle)
        
        self.trail_particles = [p for p in self.trail_particles if p['life'] > 0]
        for particle in self.trail_particles:
            particle['life'] -= 1
            particle['x'] += particle['drift_x']
            particle['y'] += particle['drift_y']

    def _draw_trail_particles(self, frame: np.ndarray):
        """绘制尾迹粒子"""
        for particle in self.trail_particles:
            alpha = particle['life'] / self.particle_lifetime
            color_intensity = int(255 * alpha)
            
            color = tuple(int(c * alpha) for c in self.particle_color)
            cv2.circle(frame, (int(particle['x']), int(particle['y'])), 
                      particle['size'], color, -1)

    def _draw_progress_bar(self, frame: np.ndarray, progress: float, width: int, height: int) -> np.ndarray:
        """绘制灵活配置的进度条"""
        frame_copy = frame.copy()
        self.frame_count += 1
        
        # 计算进度条位置
        bar_width = width - 2 * self.margin
        
        if self.position == "bottom":
            bar_y = height - self.margin - self.bar_height
        else:
            bar_y = self.margin
        
        bar_x = self.margin
        
        # 绘制边框
        if self.border_thickness > 0:
            cv2.rectangle(frame_copy, 
                         (bar_x - self.border_thickness, bar_y - self.border_thickness), 
                         (bar_x + bar_width + self.border_thickness, bar_y + self.bar_height + self.border_thickness),
                         self.border_color, self.border_thickness)
        
        # 绘制进度条背景
        cv2.rectangle(frame_copy, (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + self.bar_height),
                     self.background_color, -1)
        
        # 绘制进度
        progress_width = int(bar_width * progress)
        if progress_width > 0:
            if self.gradient_enabled:
                # 渐变进度条
                for i in range(progress_width):
                    ratio = i / progress_width if progress_width > 0 else 0
                    color = tuple(int(c * (0.6 + 0.4 * ratio)) for c in self.bar_color)
                    cv2.line(frame_copy, (bar_x + i, bar_y), 
                            (bar_x + i, bar_y + self.bar_height), color, 1)
            else:
                # 纯色进度条
                cv2.rectangle(frame_copy, (bar_x, bar_y),
                             (bar_x + progress_width, bar_y + self.bar_height),
                             self.bar_color, -1)
            
            # 发光效果
            if self.glow_enabled and self.frame_count % 20 < 10:
                shine_x = bar_x + progress_width - 20
                if shine_x > bar_x:
                    cv2.line(frame_copy, (shine_x, bar_y), 
                            (shine_x, bar_y + self.bar_height), (255, 255, 255), 3)
        
        # 计算角色位置
        base_char_x = bar_x + max(0, progress_width - self.character_size[0]) + self.character_offset_x
        base_char_y = bar_y + self.character_offset_y
        
        if self.position == "top":
            base_char_y = bar_y + self.bar_height + abs(self.character_offset_y)
        else:
            base_char_y = bar_y - self.character_size[1] + self.character_offset_y
        
        # 边界检查
        char_x = max(0, min(base_char_x, width - self.character_size[0]))
        char_y = max(0, min(base_char_y, height - self.character_size[1]))
        
        # 弹跳动画
        if self.enable_bounce:
            bounce = int(self.bounce_amplitude * abs(math.sin(self.frame_count * self.bounce_speed)))
            char_y -= bounce
        
        # 更新特效
        self._update_lightning_effects(char_x, char_y)
        self._update_trail_particles(char_x, char_y)
        
        # 绘制特效
        self._draw_lightning_effects(frame_copy)
        self._draw_trail_particles(frame_copy)
        
        # 绘制角色
        if self.total_frames > 0:
            current_frame_idx = (self.frame_count // self.animation_speed) % self.total_frames
            current_char, current_alpha = self.character_frames[current_frame_idx]
            
            try:
                frame_copy = self._blend_with_alpha(frame_copy, current_char, current_alpha, 
                                                  char_x, char_y)
            except Exception as e:
                print(f"绘制角色时出错: {e}")
        
        # 绘制进度文字
        progress_text = f"{progress*100:.1f}%"
        text_size_info = cv2.getTextSize(progress_text, cv2.FONT_HERSHEY_SIMPLEX, 
                                        self.text_size, 2)[0]
        
        # 计算文字位置 - 跟随进度条移动
        if self.text_position == 'follow':
            # 文字跟随进度条前端
            progress_end_x = bar_x + progress_width
            text_x = max(bar_x, min(progress_end_x - text_size_info[0] // 2, 
                                   bar_x + bar_width - text_size_info[0]))
            text_x += self.text_offset_x
        elif self.text_position == 'left':
            text_x = bar_x + self.text_offset_x
        elif self.text_position == 'center':
            text_x = bar_x + (bar_width - text_size_info[0]) // 2 + self.text_offset_x
        else:  # right
            text_x = bar_x + bar_width - text_size_info[0] - self.text_offset_x
        
        text_y = bar_y + (self.bar_height + text_size_info[1]) // 2 + self.text_offset_y
        
        # 文字阴影
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            cv2.putText(frame_copy, progress_text, 
                       (text_x + offset[0], text_y + offset[1]),
                       cv2.FONT_HERSHEY_SIMPLEX, self.text_size, (0, 0, 0), 3)
        
        # 主文字
        cv2.putText(frame_copy, progress_text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, self.text_size, self.text_color, 2)
        
        return frame_copy

    def process_video(self, input_video: str, output_video: Optional[str] = None) -> str:
        """
        处理视频，添加进度条并保留音频
        
        Args:
            input_video: 输入视频文件路径
            output_video: 输出视频文件路径（可选，默认在输入文件同目录生成）
            
        Returns:
            str: 输出视频文件路径
            
        Raises:
            FileNotFoundError: 输入视频文件不存在
            ValueError: 视频处理过程中出错
        """
        if not os.path.exists(input_video):
            raise FileNotFoundError(f"视频文件不存在: {input_video}")
        
        # 改进输出路径处理
        if output_video is None:
            # 在原视频同目录生成，避免硬编码路径
            input_dir = os.path.dirname(input_video)
            if not input_dir:  # 如果输入视频在当前目录
                input_dir = "."
            name, ext = os.path.splitext(os.path.basename(input_video))
            output_video = os.path.join(input_dir, f"{name}_progress{ext}")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_video)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # 检查是否可以使用moviepy
        if not MOVIEPY_AVAILABLE:
            print("📺 使用OpenCV模式（无音频）")
            return self._process_video_opencv_fallback(input_video, output_video)
        
        try:
            # 使用moviepy加载视频并保留音频
            print("🎬 正在加载视频（包含音频）...")
            video_clip = VideoFileClip(input_video)
            
            fps = video_clip.fps
            width, height = video_clip.size
            duration = video_clip.duration
            total_frames = int(fps * duration)
            
            print(f"📊 视频信息:")
            print(f"  分辨率: {width}x{height}")
            print(f"  帧率: {fps:.1f} FPS")
            print(f"  时长: {duration:.2f} 秒")
            print(f"  总帧数: {total_frames}")
            print(f"  角色动画帧数: {self.total_frames}")
            print(f"  音频: {'✅ 包含' if video_clip.audio else '❌ 无音频'}")
            
            print("🎮 正在处理视频帧...")
            
            def process_frame(get_frame, t):
                """处理单个帧的函数"""
                frame = get_frame(t)
                # MoviePy 2.x 直接返回uint8格式(0-255)，无需乘以255
                if frame.dtype == np.float64 or frame.dtype == np.float32:
                    # 如果是浮点数(0-1)，转换为uint8
                    frame_bgr = cv2.cvtColor((frame * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
                else:
                    # 如果已经是uint8(0-255)，直接转换
                    frame_bgr = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2BGR)
                
                # 计算进度
                progress = t / duration if duration > 0 else 0
                
                # 添加进度条
                frame_with_progress = self._draw_progress_bar(frame_bgr, progress, width, height)
                
                # 转换回RGB给moviepy，MoviePy 2.x 期望uint8格式
                frame_rgb = cv2.cvtColor(frame_with_progress, cv2.COLOR_BGR2RGB)
                return frame_rgb.astype(np.uint8)
            
            # 创建新的视频剪辑，应用进度条处理 (MoviePy 2.x API)
            processed_clip = video_clip.transform(process_frame)
            
            # 保留原始音频 (MoviePy 2.x API)
            if video_clip.audio:
                processed_clip = processed_clip.with_audio(video_clip.audio)
                print("🔊 保留原始音频")
            
            print("💾 正在写入最终视频...")
            
            # 写入视频，并指定高质量参数 (MoviePy 2.x API)
            processed_clip.write_videofile(
                output_video,
                fps=fps,
                codec='libx264',      # 使用高质量和兼容性好的H.264编码器
                bitrate='10000k',     # 设置一个较高的码率 (例如 10000 kbps)。原视频码率越高，这里可以设得越高。
                preset='medium',      # 'slow'或'veryslow'可以获得更高压缩率（同等码率下质量更好），但耗时更长。'medium'是很好的平衡点。
                threads=4,            # 使用多个CPU核心来加速编码
                logger=None           # MoviePy 2.x: 使用logger代替verbose参数
            )
            
            # 清理资源
            processed_clip.close()
            video_clip.close()
            
            print(f"🎉 视频处理完成! 输出文件: {output_video}")
            
        except Exception as e:
            print(f"❌ 使用moviepy处理失败: {e}")
            print("🔄 降级到OpenCV处理（无音频）...")
            return self._process_video_opencv_fallback(input_video, output_video)
        
        return output_video
    
    def _process_video_opencv_fallback(self, input_video: str, output_video: str) -> str:
        """OpenCV降级处理（无音频，用作备选）"""
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {input_video}")
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"⚠️  降级模式 - 无音频输出")
        
        # 简化的编码器选择
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise ValueError("无法创建输出视频文件")
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            progress = frame_count / total_frames
            frame_with_progress = self._draw_progress_bar(frame, progress, width, height)
            out.write(frame_with_progress)
            
            frame_count += 1
            
            if frame_count % (fps * 2) == 0:
                print(f"📊 处理进度: {progress*100:.1f}% ({frame_count}/{total_frames})")
        
        cap.release()
        out.release()
        return output_video


def load_config(config_path: str) -> Dict[str, Any]:
    """从JSON文件加载配置"""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_default_config(config_path: str):
    """保存默认配置到JSON文件"""
    default_config = {
        "input_video": "assets/samples/sample_video.mp4",
        "output_video": "",
        
        "bar_height": 40,
        "bar_color": [0, 255, 255],
        "background_color": [50, 50, 50],
        "position": "bottom",
        "margin": 25,
        
        "character_path": "assets/characters/pikaqiu.gif",
        "character_size": [60, 60],
        "character_offset_x": 0,
        "character_offset_y": -5,
        
        "enable_bounce": True,
        "bounce_amplitude": 8,
        "bounce_speed": 0.2,
        "animation_speed": 3,
        
        "enable_lightning": True,
        "lightning_chance": 0.3,
        "lightning_color": [0, 255, 255],
        
        "enable_particles": True,
        "particle_color": [0, 255, 255],
        "particle_lifetime": 60,
        
        "text_color": [0, 255, 255],
        "text_size": 0.8,
        "text_position": "follow",
        "text_offset_x": 0,
        "text_offset_y": -10,
        
        "border_thickness": 3,
        "border_color": [255, 255, 255],
        "gradient_enabled": True,
        "glow_enabled": True
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    print(f"💾 默认配置已保存到: {config_path}")
