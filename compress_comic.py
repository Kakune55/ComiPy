import cv2
import zipfile
import argparse
import os
import re
import numpy as np
from io import BytesIO
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import threading

# 线程锁，用于安全写入 ZIP 和打印
output_zip_lock = threading.Lock()
print_lock = threading.Lock()

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def resize_long_image(img, max_short_edge=640):
    """
    专为长图优化：限制短边（通常是宽度），保持比例
    例如：宽 1000px, 高 5000px → 缩放为 宽 640px, 高 3200px
    """
    h, w = img.shape[:2]
    short_edge = min(w, h)
    if short_edge <= max_short_edge:
        return img  # 不需要缩放

    scale = max_short_edge / short_edge
    new_w = int(w * scale)
    new_h = int(h * scale)

    # 使用高质量插值缩小
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    return resized

def convert_to_webp_data(img, quality=95):
    encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), quality]
    success, buffer = cv2.imencode('.webp', img, encode_param)
    if not success:
        raise RuntimeError("WebP 编码失败")
    return buffer.tobytes()

def process_image(args):
    """单张图像处理函数（用于多线程）"""
    filename, img_data = args
    try:
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            with print_lock:
                tqdm.write(f"⚠️ 无法解码图像: {filename}")
            return None

        # 缩放长图（限制短边）
        img = resize_long_image(img, max_short_edge=640)

        # 转为 WebP
        webp_bytes = convert_to_webp_data(img, quality=95)

        webp_name = os.path.splitext(filename)[0] + '.webp'
        return (webp_name, webp_bytes)

    except Exception as e:
        with print_lock:
            tqdm.write(f"❌ 处理 {filename} 失败: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="压缩漫画ZIP：长图优化 + 多线程加速")
    parser.add_argument('-i', '--input', required=True, help='输入的ZIP文件路径')
    parser.add_argument('--workers', type=int, default=4, help='并行线程数（默认4）')
    args = parser.parse_args()

    input_zip_path = args.input
    if not os.path.isfile(input_zip_path):
        print(f"❌ 错误：文件 {input_zip_path} 不存在")
        return

    base_name = os.path.splitext(input_zip_path)[0]
    output_zip_path = f"{base_name}-lite.zip"

    with zipfile.ZipFile(input_zip_path, 'r') as input_zip:
        image_files = [f for f in input_zip.namelist() if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
        image_files.sort(key=natural_sort_key)

        if not image_files:
            print("⚠️ 警告：ZIP中未找到图片文件")
            return

        print(f"📦 找到 {len(image_files)} 张图片（包括长图），使用 {args.workers} 个线程处理...")

        # 读取所有图像数据用于多线程处理
        img_data_list = [(filename, input_zip.read(filename)) for filename in image_files]

    # 多线程处理
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # 提交所有任务
        futures = [executor.submit(process_image, item) for item in img_data_list]
        # 使用 tqdm 显示进度
        for future in tqdm(futures, desc="🚀 压缩中", unit="img"):
            result = future.result()
            if result is not None:
                results.append(result)

    # 写入输出 ZIP（主线程完成，避免并发写 ZIP）
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as output_zip:
        for webp_name, webp_bytes in results:
            output_zip.writestr(webp_name, webp_bytes)

    print(f"✅ 压缩完成！输出文件：{output_zip_path}")

if __name__ == '__main__':
    main()