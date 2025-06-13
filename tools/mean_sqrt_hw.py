import os
import cv2
import numpy as np

def calculate_mean_sqrt_hw(folder_path):
    total_sum = 0
    count = 0
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                file_path = os.path.join(root, file)
                try:
                    img = cv2.imread(file_path)
                    if img is not None:
                        height, width = img.shape[:2]
                        value = int(np.sqrt(height * width))
                        total_sum += value
                        count += 1
                except Exception as e:
                    print(f"无法处理文件 {file_path}: {e}")
    
    if count == 0:
        return 0
    
    mean_value = total_sum / count
    return mean_value

# 示例用法
folder_path = '/home/yf-wrj/yuefan/original_ROI/FPC_压伤/washed/N46LAT2/img'
mean_sqrt_hw = calculate_mean_sqrt_hw(folder_path)
print(f"所有图片 h*w 开方后的均值为: {mean_sqrt_hw}")
