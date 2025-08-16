import cv2
import numpy as np
import os
import argparse
import math
from typing import Tuple, Optional, List


class EnhancedVideoProgressBar:
    def __init__(self, 
                 bar_height: int = 30,
                 bar_color: Tuple[int, int, int] = (0, 255, 0),
                 background_color: Tuple[int, int, int] = (40, 40, 40),
                 position: str = "bottom",
                 margin: int = 20,
                 style: str = "modern",
                 character_path: str = None):
        """
        增强版视频进度条
        
        Args:
            bar_height: 进度条高度
            bar_color: 进度条颜色 (B, G, R)
            background_color: 进度条背景颜色 (B, G, R)
            position: 进度条位置 ("top" 或 "bottom")
            margin: 进度条边距
            style: 进度条风格 ("modern", "cute", "gaming")
            character_path: 角色图片路径
        """
        self.bar_height = bar_height
        self.bar_color = bar_color
        self.background_color = background_color
        self.position = position
        self.margin = margin
        self.style = style
        self.character_path = character_path
        
        # 动画相关
        self.frame_count = 0
        self.character_size = (40, 40)  # 角色大小
        
        # 加载角色图片
        self.character_img = self._load_character()
        
        # 粒子系统
        self.particles = []

    def _load_character(self) -> Optional[np.ndarray]:
        """加载角色图片"""
        if self.character_path and os.path.exists(self.character_path):
            try:
                img = cv2.imread(self.character_path, cv2.IMREAD_UNCHANGED)
                if img is not None:
                    return cv2.resize(img, self.character_size)
            except:
                pass
        return self._create_default_character()

    def _create_default_character(self) -> np.ndarray:
        """创建默认的卡通角色（简单的表情符号）"""
        size = self.character_size[0]
        char_img = np.zeros((size, size, 3), dtype=np.uint8)
        
        if self.style == "cute":
            # 绘制可爱的圆形角色
            center = (size // 2, size // 2)
            radius = size // 3
            
            # 主体 (黄色圆形)
            cv2.circle(char_img, center, radius, (0, 255, 255), -1)
            
            # 眼睛
            eye_y = center[1] - radius // 3
            cv2.circle(char_img, (center[0] - radius//3, eye_y), 3, (0, 0, 0), -1)
            cv2.circle(char_img, (center[0] + radius//3, eye_y), 3, (0, 0, 0), -1)
            
            # 嘴巴 (微笑)
            mouth_y = center[1] + radius // 4
            cv2.ellipse(char_img, (center[0], mouth_y), (radius//2, radius//4), 
                       0, 0, 180, (0, 0, 0), 2)
                       
        elif self.style == "gaming":
            # 像素风格角色
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            color = colors[self.frame_count % len(colors)]
            cv2.rectangle(char_img, (5, 5), (size-5, size-5), color, -1)
            cv2.rectangle(char_img, (10, 10), (size-10, size-10), (255, 255, 255), -1)
            
        else:  # modern
            # 现代简约风格
            center = (size // 2, size // 2)
            cv2.circle(char_img, center, size // 3, self.bar_color, -1)
            cv2.circle(char_img, center, size // 4, (255, 255, 255), 3)
            
        return char_img

    def _create_gradient_background(self, width: int, height: int) -> np.ndarray:
        """创建渐变背景"""
        gradient = np.zeros((height, width, 3), dtype=np.uint8)
        
        for i in range(width):
            ratio = i / width
            # 渐变从深色到浅色
            color = (
                int(self.background_color[0] * (1 - ratio * 0.3)),
                int(self.background_color[1] * (1 - ratio * 0.3)),
                int(self.background_color[2] * (1 - ratio * 0.3))
            )
            gradient[:, i] = color
            
        return gradient

    def _add_glow_effect(self, img: np.ndarray, rect: Tuple[int, int, int, int]) -> np.ndarray:
        """添加发光效果"""
        x, y, w, h = rect
        overlay = img.copy()
        
        # 创建发光遮罩
        glow = np.zeros_like(img)
        cv2.rectangle(glow, (x-2, y-2), (x+w+2, y+h+2), self.bar_color, -1)
        
        # 高斯模糊产生发光效果
        glow = cv2.GaussianBlur(glow, (15, 15), 0)
        
        # 混合原图和发光效果
        result = cv2.addWeighted(img, 0.7, glow, 0.3, 0)
        return result

    def _update_particles(self, char_x: int, char_y: int):
        """更新粒子系统"""
        # 添加新粒子
        if self.frame_count % 5 == 0:  # 每5帧添加一个粒子
            particle = {
                'x': char_x + np.random.randint(-10, 10),
                'y': char_y + np.random.randint(-5, 5),
                'life': 20,
                'size': np.random.randint(2, 5)
            }
            self.particles.append(particle)
        
        # 更新现有粒子
        self.particles = [p for p in self.particles if p['life'] > 0]
        for particle in self.particles:
            particle['life'] -= 1
            particle['y'] += np.random.randint(-2, 2)
            particle['x'] -= np.random.randint(1, 3)

    def _draw_particles(self, frame: np.ndarray):
        """绘制粒子效果"""
        for particle in self.particles:
            alpha = particle['life'] / 20.0
            color = tuple(int(c * alpha) for c in self.bar_color)
            cv2.circle(frame, (int(particle['x']), int(particle['y'])), 
                      particle['size'], color, -1)

    def _draw_progress_bar(self, frame: np.ndarray, progress: float, width: int, height: int) -> np.ndarray:
        """绘制增强版进度条"""
        frame_copy = frame.copy()
        self.frame_count += 1
        
        # 计算进度条位置
        bar_width = width - 2 * self.margin
        
        if self.position == "bottom":
            bar_y = height - self.margin - self.bar_height
        else:
            bar_y = self.margin
        
        bar_x = self.margin
        
        # 创建圆角矩形遮罩
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # 绘制圆角背景
        if self.style == "modern":
            # 现代风格：渐变背景 + 圆角
            gradient_bg = self._create_gradient_background(bar_width, self.bar_height)
            
            # 应用圆角效果
            cv2.rectangle(frame_copy, (bar_x, bar_y), 
                         (bar_x + bar_width, bar_y + self.bar_height),
                         self.background_color, -1)
            
            # 绘制进度
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                progress_rect = (bar_x, bar_y, progress_width, self.bar_height)
                
                # 渐变进度条
                for i in range(progress_width):
                    ratio = i / progress_width if progress_width > 0 else 0
                    color = (
                        int(self.bar_color[0] * (0.7 + 0.3 * ratio)),
                        int(self.bar_color[1] * (0.7 + 0.3 * ratio)),
                        int(self.bar_color[2] * (0.7 + 0.3 * ratio))
                    )
                    cv2.line(frame_copy, (bar_x + i, bar_y), 
                            (bar_x + i, bar_y + self.bar_height), color, 1)
                
                # 添加发光效果
                if self.style == "modern":
                    frame_copy = self._add_glow_effect(frame_copy, progress_rect)
        
        else:
            # 其他风格保持简单绘制
            cv2.rectangle(frame_copy, (bar_x, bar_y), 
                         (bar_x + bar_width, bar_y + self.bar_height),
                         self.background_color, -1)
            
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                cv2.rectangle(frame_copy, (bar_x, bar_y),
                             (bar_x + progress_width, bar_y + self.bar_height),
                             self.bar_color, -1)
        
        # 绘制角色
        if self.character_img is not None:
            char_x = bar_x + int((bar_width - self.character_size[0]) * progress)
            char_y = bar_y - self.character_size[1] - 5
            
            # 确保角色在画面内
            char_x = max(0, min(char_x, width - self.character_size[0]))
            char_y = max(0, min(char_y, height - self.character_size[1]))
            
            # 添加跳跃动画
            if self.style == "cute":
                bounce = int(5 * abs(math.sin(self.frame_count * 0.3)))
                char_y -= bounce
            
            # 更新粒子系统
            self._update_particles(char_x + self.character_size[0]//2, char_y + self.character_size[1])
            
            # 绘制粒子
            self._draw_particles(frame_copy)
            
            # 绘制角色（重新生成以实现动画效果）
            if self.style in ["cute", "gaming"]:
                self.character_img = self._create_default_character()
            
            # 叠加角色到画面
            try:
                y1, y2 = char_y, char_y + self.character_size[1]
                x1, x2 = char_x, char_x + self.character_size[0]
                
                if y1 >= 0 and y2 <= height and x1 >= 0 and x2 <= width:
                    # 简单叠加（不透明）
                    frame_copy[y1:y2, x1:x2] = self.character_img
            except:
                pass
        
        # 添加进度文本（更漂亮的样式）
        progress_text = f"{progress*100:.1f}%"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        
        text_size = cv2.getTextSize(progress_text, font, font_scale, thickness)[0]
        text_x = bar_x + bar_width - text_size[0] - 10
        text_y = bar_y + (self.bar_height + text_size[1]) // 2
        
        # 文本阴影效果
        cv2.putText(frame_copy, progress_text, (text_x + 2, text_y + 2),
                   font, font_scale, (0, 0, 0), thickness + 1)
        cv2.putText(frame_copy, progress_text, (text_x, text_y),
                   font, font_scale, (255, 255, 255), thickness)
        
        return frame_copy

    def add_progress_bar(self, input_video: str, output_video: str = None) -> str:
        """为视频添加增强版进度条"""
        if not os.path.exists(input_video):
            raise FileNotFoundError(f"视频文件不存在: {input_video}")
        
        if output_video is None:
            name, ext = os.path.splitext(input_video)
            output_video = f"{name}_enhanced_progress{ext}"
        
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {input_video}")
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"视频信息:")
        print(f"  分辨率: {width}x{height}")
        print(f"  帧率: {fps} FPS")
        print(f"  总帧数: {total_frames}")
        print(f"  时长: {total_frames/fps:.2f} 秒")
        print(f"  样式: {self.style}")
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise ValueError("无法创建输出视频文件")
        
        frame_count = 0
        print("正在处理增强版视频...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            progress = frame_count / total_frames
            frame_with_progress = self._draw_progress_bar(frame, progress, width, height)
            out.write(frame_with_progress)
            
            frame_count += 1
            
            if frame_count % (fps * 2) == 0:
                print(f"处理进度: {progress*100:.1f}% ({frame_count}/{total_frames})")
        
        cap.release()
        out.release()
        
        print(f"增强版视频处理完成! 输出文件: {output_video}")
        return output_video


def main():
    parser = argparse.ArgumentParser(description="为视频添加增强版进度条")
    parser.add_argument("input_video", help="输入视频文件路径")
    parser.add_argument("-o", "--output", help="输出视频文件路径")
    parser.add_argument("--height", type=int, default=30, help="进度条高度 (默认: 30)")
    parser.add_argument("--position", choices=["top", "bottom"], default="bottom", 
                       help="进度条位置 (默认: bottom)")
    parser.add_argument("--margin", type=int, default=20, help="进度条边距 (默认: 20)")
    parser.add_argument("--color", default="green", choices=["green", "red", "blue", "yellow"],
                       help="进度条颜色 (默认: green)")
    parser.add_argument("--style", default="modern", choices=["modern", "cute", "gaming"],
                       help="进度条风格 (默认: modern)")
    parser.add_argument("--character", help="自定义角色图片路径")
    
    args = parser.parse_args()
    
    color_map = {
        "green": (0, 255, 0),
        "red": (0, 0, 255),
        "blue": (255, 0, 0),
        "yellow": (0, 255, 255)
    }
    
    try:
        progress_bar = EnhancedVideoProgressBar(
            bar_height=args.height,
            bar_color=color_map[args.color],
            position=args.position,
            margin=args.margin,
            style=args.style,
            character_path=args.character
        )
        
        output_file = progress_bar.add_progress_bar(args.input_video, args.output)
        print(f"\n✅ 成功! 增强版带进度条的视频已保存为: {output_file}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
