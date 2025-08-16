import cv2
import numpy as np
import os
import argparse
import math
from typing import Tuple, Optional, List
from PIL import Image, ImageSequence


class PikachuProgressBar:
    def __init__(self, 
                 bar_height: int = 40,
                 bar_color: Tuple[int, int, int] = (0, 255, 255),  # 黄色 (BGR)
                 background_color: Tuple[int, int, int] = (50, 50, 50),
                 position: str = "bottom",
                 margin: int = 25,
                 pikachu_gif_path: str = "pikaqiu.gif"):
        """
        皮卡丘主题视频进度条
        
        Args:
            bar_height: 进度条高度
            bar_color: 进度条颜色 (B, G, R) - 默认皮卡丘黄色
            background_color: 进度条背景颜色
            position: 进度条位置 ("top" 或 "bottom") 
            margin: 进度条边距
            pikachu_gif_path: 皮卡丘GIF文件路径
        """
        self.bar_height = bar_height
        self.bar_color = bar_color
        self.background_color = background_color
        self.position = position
        self.margin = margin
        self.pikachu_gif_path = pikachu_gif_path
        
        # 动画相关
        self.frame_count = 0
        self.pikachu_size = (60, 60)  # 皮卡丘大小
        
        # 加载皮卡丘GIF动画
        self.pikachu_frames = self._load_pikachu_gif()
        self.total_pikachu_frames = len(self.pikachu_frames)
        
        # 电光效果
        self.lightning_particles = []
        
        # 音符效果（皮卡丘很喜欢音乐！）
        self.music_notes = []

    def _load_pikachu_gif(self) -> List[np.ndarray]:
        """加载皮卡丘GIF的所有帧"""
        frames = []
        
        if not os.path.exists(self.pikachu_gif_path):
            print(f"❌ 皮卡丘GIF文件不存在: {self.pikachu_gif_path}")
            return [self._create_default_pikachu()]
        
        try:
            # 使用PIL加载GIF
            with Image.open(self.pikachu_gif_path) as gif:
                print(f"🎮 加载皮卡丘GIF: {gif.size}, 帧数: {gif.n_frames}")
                
                for frame_idx in range(gif.n_frames):
                    gif.seek(frame_idx)
                    # 转换为RGBA确保透明度处理
                    frame_rgba = gif.convert('RGBA')
                    # 调整大小
                    frame_resized = frame_rgba.resize(self.pikachu_size, Image.Resampling.LANCZOS)
                    # 转换为numpy数组
                    frame_array = np.array(frame_resized)
                    # 转换颜色空间 RGBA -> BGR
                    frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGBA2BGR)
                    frames.append(frame_bgr)
                    
        except Exception as e:
            print(f"❌ 加载皮卡丘GIF出错: {e}")
            frames = [self._create_default_pikachu()]
            
        return frames

    def _create_default_pikachu(self) -> np.ndarray:
        """创建默认的皮卡丘（如果GIF加载失败）"""
        size = self.pikachu_size[0]
        pikachu = np.zeros((size, size, 3), dtype=np.uint8)
        
        center = (size // 2, size // 2)
        
        # 皮卡丘的黄色身体
        cv2.circle(pikachu, center, size // 3, (0, 255, 255), -1)
        
        # 眼睛
        eye_y = center[1] - size // 6
        cv2.circle(pikachu, (center[0] - size//6, eye_y), 3, (0, 0, 0), -1)
        cv2.circle(pikachu, (center[0] + size//6, eye_y), 3, (0, 0, 0), -1)
        
        # 红色脸颊
        cheek_y = center[1]
        cv2.circle(pikachu, (center[0] - size//4, cheek_y), 6, (0, 0, 255), -1)
        cv2.circle(pikachu, (center[0] + size//4, cheek_y), 6, (0, 0, 255), -1)
        
        # 嘴巴
        mouth_y = center[1] + size // 6
        cv2.ellipse(pikachu, (center[0], mouth_y), (size//6, size//8), 0, 0, 180, (0, 0, 0), 2)
        
        # 耳朵
        ear_tip_y = center[1] - size // 2
        cv2.fillPoly(pikachu, [np.array([
            [center[0] - size//6, center[1] - size//4],
            [center[0] - size//8, ear_tip_y],
            [center[0], center[1] - size//4]
        ])], (0, 200, 255))
        
        cv2.fillPoly(pikachu, [np.array([
            [center[0], center[1] - size//4],
            [center[0] + size//8, ear_tip_y], 
            [center[0] + size//6, center[1] - size//4]
        ])], (0, 200, 255))
        
        return pikachu

    def _update_lightning_effects(self, pikachu_x: int, pikachu_y: int):
        """更新电光效果"""
        # 随机生成电光
        if self.frame_count % 15 == 0 and np.random.random() > 0.7:
            lightning = {
                'x': pikachu_x + np.random.randint(-20, 20),
                'y': pikachu_y + np.random.randint(-10, 10),
                'life': 10,
                'intensity': np.random.randint(5, 15)
            }
            self.lightning_particles.append(lightning)
        
        # 更新现有电光
        self.lightning_particles = [p for p in self.lightning_particles if p['life'] > 0]
        for particle in self.lightning_particles:
            particle['life'] -= 1

    def _draw_lightning_effects(self, frame: np.ndarray):
        """绘制电光效果"""
        for particle in self.lightning_particles:
            alpha = particle['life'] / 10.0
            intensity = int(particle['intensity'] * alpha)
            
            # 绘制电光线条
            start_point = (particle['x'], particle['y'])
            for i in range(3):
                end_x = particle['x'] + np.random.randint(-15, 15)
                end_y = particle['y'] + np.random.randint(-15, 15)
                end_point = (end_x, end_y)
                
                # 黄色电光
                cv2.line(frame, start_point, end_point, (0, 255, 255), 2)
                # 白色核心
                cv2.line(frame, start_point, end_point, (255, 255, 255), 1)

    def _update_music_notes(self, pikachu_x: int, pikachu_y: int):
        """更新音符效果（皮卡丘很快乐！）"""
        if self.frame_count % 30 == 0:  # 每30帧添加一个音符
            note = {
                'x': pikachu_x + self.pikachu_size[0] + 10,
                'y': pikachu_y,
                'life': 60,
                'drift_x': np.random.randint(1, 3),
                'drift_y': np.random.randint(-2, 0)
            }
            self.music_notes.append(note)
        
        # 更新音符位置
        self.music_notes = [n for n in self.music_notes if n['life'] > 0]
        for note in self.music_notes:
            note['life'] -= 1
            note['x'] += note['drift_x']
            note['y'] += note['drift_y']

    def _draw_music_notes(self, frame: np.ndarray):
        """绘制音符"""
        for note in self.music_notes:
            alpha = note['life'] / 60.0
            color_intensity = int(255 * alpha)
            
            # 绘制简单的音符形状
            center = (int(note['x']), int(note['y']))
            cv2.circle(frame, center, 4, (color_intensity, color_intensity, 0), -1)
            cv2.line(frame, center, (center[0], center[1] - 10), (color_intensity, color_intensity, 0), 2)

    def _create_pokemon_style_progress_bar(self, frame: np.ndarray, progress: float, width: int, height: int) -> np.ndarray:
        """创建宝可梦风格的进度条"""
        frame_copy = frame.copy()
        self.frame_count += 1
        
        # 计算进度条位置
        bar_width = width - 2 * self.margin
        
        if self.position == "bottom":
            bar_y = height - self.margin - self.bar_height
        else:
            bar_y = self.margin
        
        bar_x = self.margin
        
        # 绘制更厚的边框（宝可梦游戏风格）
        border_thickness = 3
        cv2.rectangle(frame_copy, 
                     (bar_x - border_thickness, bar_y - border_thickness), 
                     (bar_x + bar_width + border_thickness, bar_y + self.bar_height + border_thickness),
                     (255, 255, 255), border_thickness)
        
        # 绘制进度条背景
        cv2.rectangle(frame_copy, (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + self.bar_height),
                     self.background_color, -1)
        
        # 绘制进度（带渐变效果）
        progress_width = int(bar_width * progress)
        if progress_width > 0:
            # 渐变黄色进度条
            for i in range(progress_width):
                ratio = i / progress_width if progress_width > 0 else 0
                # 从深黄到亮黄的渐变
                color = (
                    int(self.bar_color[0] * (0.6 + 0.4 * ratio)),  # B
                    int(self.bar_color[1] * (0.8 + 0.2 * ratio)),  # G  
                    int(self.bar_color[2] * (0.8 + 0.2 * ratio))   # R
                )
                cv2.line(frame_copy, (bar_x + i, bar_y), 
                        (bar_x + i, bar_y + self.bar_height), color, 1)
            
            # 添加闪光效果
            if self.frame_count % 20 < 10:  # 闪烁效果
                shine_x = bar_x + progress_width - 20
                if shine_x > bar_x:
                    cv2.line(frame_copy, (shine_x, bar_y), 
                            (shine_x, bar_y + self.bar_height), (255, 255, 255), 3)
        
        # 计算皮卡丘位置
        if progress_width > self.pikachu_size[0]:
            pikachu_x = bar_x + progress_width - self.pikachu_size[0]
        else:
            pikachu_x = bar_x
            
        pikachu_y = bar_y - self.pikachu_size[1] - 5
        
        # 确保皮卡丘在画面内
        pikachu_x = max(0, min(pikachu_x, width - self.pikachu_size[0]))
        pikachu_y = max(0, min(pikachu_y, height - self.pikachu_size[1]))
        
        # 添加跳跃动画（皮卡丘很活泼！）
        bounce = int(8 * abs(math.sin(self.frame_count * 0.2)))
        pikachu_y -= bounce
        
        # 更新特效
        self._update_lightning_effects(pikachu_x, pikachu_y)
        self._update_music_notes(pikachu_x, pikachu_y)
        
        # 绘制特效
        self._draw_lightning_effects(frame_copy)
        self._draw_music_notes(frame_copy)
        
        # 绘制皮卡丘
        if self.total_pikachu_frames > 0:
            # 根据帧数循环播放GIF动画
            current_frame_idx = (self.frame_count // 3) % self.total_pikachu_frames
            current_pikachu = self.pikachu_frames[current_frame_idx]
            
            try:
                y1, y2 = pikachu_y, pikachu_y + self.pikachu_size[1]
                x1, x2 = pikachu_x, pikachu_x + self.pikachu_size[0]
                
                if (y1 >= 0 and y2 <= height and x1 >= 0 and x2 <= width and 
                    current_pikachu.shape[0] == self.pikachu_size[1] and 
                    current_pikachu.shape[1] == self.pikachu_size[0]):
                    
                    # 叠加皮卡丘（简单替换，可以改进为alpha混合）
                    frame_copy[y1:y2, x1:x2] = current_pikachu
                    
            except Exception as e:
                print(f"绘制皮卡丘时出错: {e}")
        
        # 绘制宝可梦风格的进度文字
        progress_text = f"⚡ {progress*100:.1f}% ⚡"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        thickness = 2
        
        text_size = cv2.getTextSize(progress_text, font, font_scale, thickness)[0]
        text_x = bar_x + bar_width - text_size[0] - 15
        text_y = bar_y + (self.bar_height + text_size[1]) // 2
        
        # 文字外发光效果
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            cv2.putText(frame_copy, progress_text, 
                       (text_x + offset[0], text_y + offset[1]),
                       font, font_scale, (0, 0, 0), thickness + 2)
        
        # 主文字（黄色）
        cv2.putText(frame_copy, progress_text, (text_x, text_y),
                   font, font_scale, (0, 255, 255), thickness)
        
        return frame_copy

    def add_pikachu_progress_bar(self, input_video: str, output_video: str = None) -> str:
        """为视频添加皮卡丘主题进度条"""
        if not os.path.exists(input_video):
            raise FileNotFoundError(f"视频文件不存在: {input_video}")
        
        if output_video is None:
            name, ext = os.path.splitext(input_video)
            output_video = f"{name}_pikachu_progress{ext}"
        
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {input_video}")
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"🎮 皮卡丘进度条视频信息:")
        print(f"  分辨率: {width}x{height}")
        print(f"  帧率: {fps} FPS")
        print(f"  总帧数: {total_frames}")
        print(f"  时长: {total_frames/fps:.2f} 秒")
        print(f"  皮卡丘动画帧数: {self.total_pikachu_frames}")
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise ValueError("无法创建输出视频文件")
        
        frame_count = 0
        print("⚡ 皮卡丘正在奔跑，请稍候...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            progress = frame_count / total_frames
            frame_with_pikachu = self._create_pokemon_style_progress_bar(frame, progress, width, height)
            out.write(frame_with_pikachu)
            
            frame_count += 1
            
            if frame_count % (fps * 2) == 0:
                print(f"⚡ 皮卡丘奔跑进度: {progress*100:.1f}% ({frame_count}/{total_frames})")
        
        cap.release()
        out.release()
        
        print(f"🎉 皮卡丘视频处理完成! 输出文件: {output_video}")
        return output_video


def main():
    parser = argparse.ArgumentParser(description="为视频添加皮卡丘主题进度条")
    parser.add_argument("input_video", help="输入视频文件路径")
    parser.add_argument("-o", "--output", help="输出视频文件路径")
    parser.add_argument("--height", type=int, default=40, help="进度条高度 (默认: 40)")
    parser.add_argument("--position", choices=["top", "bottom"], default="bottom", 
                       help="进度条位置 (默认: bottom)")
    parser.add_argument("--margin", type=int, default=25, help="进度条边距 (默认: 25)")
    parser.add_argument("--pikachu", default="pikaqiu.gif", help="皮卡丘GIF文件路径")
    
    args = parser.parse_args()
    
    try:
        pikachu_bar = PikachuProgressBar(
            bar_height=args.height,
            position=args.position,
            margin=args.margin,
            pikachu_gif_path=args.pikachu
        )
        
        output_file = pikachu_bar.add_pikachu_progress_bar(args.input_video, args.output)
        print(f"\n🎉 皮卡丘成功! 带皮卡丘进度条的视频已保存为: {output_file}")
        print(f"⚡ 皮卡丘说: Pika pika! 视频处理完成!")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
