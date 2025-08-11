#!/usr/bin/env python3
import time

import cv2
import os
import sys


def extract_video(video_file, custom_output_dir=None):
    # 检查文件是否存在
    if not os.path.exists(video_file):
        print(f"错误：文件 '{video_file}' 不存在")
        return

    if custom_output_dir:
        output_dir = custom_output_dir
    else:
        tmp_dir = os.path.dirname(video_file)
        output_dir = os.path.join(tmp_dir, "tmp")

        if os.path.exists(output_dir):
            current_ms = int(time.time() * 1000)
            output_dir = os.path.join(tmp_dir, f"tmp_{current_ms}")

        os.makedirs(output_dir)
        print(f"创建目录: {output_dir}")

    # 打开视频文件
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print("错误：无法打开视频文件")
        return

    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    print(f"视频信息:")
    print(f"- 帧率: {fps:.2f} fps")
    print(f"- 总帧数: {total_frames}")
    print(f"- 时长: {duration:.2f} 秒")
    print(f"- 输出目录: {output_dir}")

    frame_count = 0
    print("正在提取帧...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        ms = round((frame_count - 1) / fps * 1000)  # 精确到毫秒

        filename = f"frame_{frame_count:06d}_{ms:06d}ms.png"
        filepath = os.path.join(output_dir, filename)

        cv2.imwrite(filepath, frame)
        print(f"保存: {filepath}")

        # 显示进度
        if frame_count % 100 == 0 or frame_count == total_frames:
            progress = (frame_count / total_frames) * 100
            print(f"进度: {progress:.1f}% ({frame_count}/{total_frames})")

    cap.release()
    print(f"完成！共提取 {frame_count} 帧")


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("用法: python script.py <video_file> [output_dir]")
        print("示例: python script.py video.mp4")
        print("示例: python script.py video.mp4 /path/to/output")
        sys.exit(1)

    video_file = sys.argv[1]

    # 如果提供了第三个参数，使用它作为输出目录
    if len(sys.argv) == 3:
        output_dir = sys.argv[2]
        extract_video(video_file, output_dir)
    else:
        # 使用默认输出目录
        extract_video(video_file)


if __name__ == '__main__':
    main()
