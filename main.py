import cv2
import numpy as np
import os
import argparse
from typing import Tuple, Optional


class VideoProgressBar:
    def __init__(self, 
                 bar_height: int = 20,
                 bar_color: Tuple[int, int, int] = (0, 255, 0),  # Green in BGR
                 background_color: Tuple[int, int, int] = (128, 128, 128),  # Gray in BGR
                 position: str = "bottom",
                 margin: int = 10):
        """
        初始化视频进度条
        
        Args:
            bar_height: 进度条高度
            bar_color: 进度条颜色 (B, G, R)
            background_color: 进度条背景颜色 (B, G, R)
            position: 进度条位置 ("top" 或 "bottom")
            margin: 进度条边距
        """
        self.bar_height = bar_height
        self.bar_color = bar_color
        self.background_color = background_color
        self.position = position
        self.margin = margin

    def add_progress_bar(self, input_video: str, output_video: str = None) -> str:
        """
        为视频添加进度条
        
        Args:
            input_video: 输入视频文件路径
            output_video: 输出视频文件路径，如果为None则自动生成
            
        Returns:
            输出视频文件路径
        """
        if not os.path.exists(input_video):
            raise FileNotFoundError(f"视频文件不存在: {input_video}")
        
        # 如果没有指定输出文件名，自动生成
        if output_video is None:
            name, ext = os.path.splitext(input_video)
            output_video = f"{name}_with_progress{ext}"
        
        # 获取视频信息
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {input_video}")
        
        # 视频属性
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"视频信息:")
        print(f"  分辨率: {width}x{height}")
        print(f"  帧率: {fps} FPS")
        print(f"  总帧数: {total_frames}")
        print(f"  时长: {total_frames/fps:.2f} 秒")
        
        # 设置输出视频编码器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise ValueError("无法创建输出视频文件")
        
        frame_count = 0
        
        print("正在处理视频...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 计算进度
            progress = frame_count / total_frames
            
            # 添加进度条
            frame_with_progress = self._draw_progress_bar(frame, progress, width, height)
            
            # 写入帧
            out.write(frame_with_progress)
            
            frame_count += 1
            
            # 显示进度
            if frame_count % (fps * 2) == 0:  # 每2秒显示一次进度
                print(f"处理进度: {progress*100:.1f}% ({frame_count}/{total_frames})")
        
        # 清理资源
        cap.release()
        out.release()
        
        print(f"视频处理完成! 输出文件: {output_video}")
        return output_video

    def _draw_progress_bar(self, frame: np.ndarray, progress: float, width: int, height: int) -> np.ndarray:
        """
        在帧上绘制进度条
        
        Args:
            frame: 原始帧
            progress: 进度 (0-1)
            width: 视频宽度
            height: 视频高度
            
        Returns:
            带进度条的帧
        """
        # 复制帧避免修改原始数据
        frame_copy = frame.copy()
        
        # 计算进度条位置
        bar_width = width - 2 * self.margin
        
        if self.position == "bottom":
            bar_y = height - self.margin - self.bar_height
        else:  # top
            bar_y = self.margin
        
        bar_x = self.margin
        
        # 绘制进度条背景
        cv2.rectangle(frame_copy, 
                     (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + self.bar_height),
                     self.background_color, 
                     -1)
        
        # 绘制进度条
        progress_width = int(bar_width * progress)
        if progress_width > 0:
            cv2.rectangle(frame_copy,
                         (bar_x, bar_y),
                         (bar_x + progress_width, bar_y + self.bar_height),
                         self.bar_color,
                         -1)
        
        # 添加进度文本
        progress_text = f"{progress*100:.1f}%"
        text_size = cv2.getTextSize(progress_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = bar_x + bar_width - text_size[0] - 5
        text_y = bar_y + self.bar_height - 5
        
        # 绘制文本背景
        cv2.rectangle(frame_copy,
                     (text_x - 2, text_y - text_size[1] - 2),
                     (text_x + text_size[0] + 2, text_y + 2),
                     (0, 0, 0),
                     -1)
        
        # 绘制文本
        cv2.putText(frame_copy, progress_text,
                   (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.6,
                   (255, 255, 255),
                   2)
        
        return frame_copy


def main():
    parser = argparse.ArgumentParser(description="为视频添加进度条")
    parser.add_argument("input_video", help="输入视频文件路径")
    parser.add_argument("-o", "--output", help="输出视频文件路径")
    parser.add_argument("--height", type=int, default=20, help="进度条高度 (默认: 20)")
    parser.add_argument("--position", choices=["top", "bottom"], default="bottom", 
                       help="进度条位置 (默认: bottom)")
    parser.add_argument("--margin", type=int, default=10, help="进度条边距 (默认: 10)")
    parser.add_argument("--color", default="green", choices=["green", "red", "blue", "yellow"],
                       help="进度条颜色 (默认: green)")
    
    args = parser.parse_args()
    
    # 颜色映射 (BGR格式)
    color_map = {
        "green": (0, 255, 0),
        "red": (0, 0, 255),
        "blue": (255, 0, 0),
        "yellow": (0, 255, 255)
    }
    
    try:
        # 创建进度条对象
        progress_bar = VideoProgressBar(
            bar_height=args.height,
            bar_color=color_map[args.color],
            position=args.position,
            margin=args.margin
        )
        
        # 添加进度条
        output_file = progress_bar.add_progress_bar(args.input_video, args.output)
        print(f"\n✅ 成功! 带进度条的视频已保存为: {output_file}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
