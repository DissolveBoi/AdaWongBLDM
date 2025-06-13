import os
import cv2
import numpy as np
import random

def crop_image_fast(original_path, output_original_dir, crop_size_ratio=1.0, num_crops=1):
    """
    對單個原始圖像進行多次隨機正方形裁剪，並將結果儲存在指定目錄中。

    Args:
        original_path (str): 原始圖像檔案路徑。
        output_original_dir (str): 存放裁剪後原始圖像的目錄。
        crop_size_ratio (float, optional): 正方形裁剪尺寸相對於較短邊的比例。預設為 1.0。
        num_crops (int, optional): 對每個圖像進行裁剪的次數。預設為 1。
    """
    try:
        # 使用 cv2 讀取圖像
        original_image = cv2.imread(original_path)
        if original_image is None:
            raise FileNotFoundError(f"無法讀取圖像檔案: {original_path}")

        original_height, original_width = original_image.shape[:2]

        shorter_side = min(original_width, original_height)
        crop_size = int(shorter_side * crop_size_ratio)

        if crop_size > original_width or crop_size > original_height:
            print(f"警告: 裁剪尺寸 ({crop_size}) 大於圖像尺寸，將使用較短邊的長度作為裁剪尺寸。")
            crop_size = shorter_side

        if not os.path.exists(output_original_dir):
            os.makedirs(output_original_dir)

        base_name, ext = os.path.splitext(os.path.basename(original_path))

        for i in range(num_crops):
            max_x = original_width - crop_size
            max_y = original_height - crop_size

            if max_x < 0 or max_y < 0:
                print(f"警告: 圖像尺寸 ({original_width}x{original_height}) 小於裁剪尺寸 ({crop_size})，無法進行裁剪。")
                break

            start_x = random.randint(0, max_x)
            start_y = random.randint(0, max_y)
            end_x = start_x + crop_size
            end_y = start_y + crop_size

            # 使用 numpy 進行裁剪
            cropped_original = original_image[start_y:end_y, start_x:end_x]

            output_original_name = os.path.join(output_original_dir, f"{base_name}_cropped_{i+1}{ext}")

            # 使用 cv2 儲存圖像
            cv2.imwrite(output_original_name, cropped_original)
            print(f"裁剪 #{i+1} 已儲存至: {output_original_name}")

    except FileNotFoundError as e:
        print(f"錯誤: {e}")
    except ValueError as e:
        print(f"錯誤: {e}")
    except Exception as e:
        print(f"發生錯誤: {e}")

def batch_crop_images_fast(input_original_dir, output_original_dir="cropped_originals", num_crops=5):
    """
    批量對指定目錄下的原始圖像進行隨機正方形裁剪，並將結果儲存。

    Args:
        input_original_dir (str): 存放原始圖像的目錄。
        output_original_dir (str, optional): 存放裁剪後原始圖像的目錄。預設為 "cropped_originals"。
        num_crops (int, optional): 對每個圖像進行裁剪的次數。預設為 5。
    """
    if not os.path.exists(output_original_dir):
        os.makedirs(output_original_dir)

    original_files = [f for f in os.listdir(input_original_dir) if os.path.isfile(os.path.join(input_original_dir, f))]

    for original_file in original_files:
        # 過濾掉包含 "_mask" 的檔案，確保只處理原始圖像
        if "_mask" not in original_file:
            original_path = os.path.join(input_original_dir, original_file)
            print(f"正在對 {original_file} 進行裁剪...")
            crop_image_fast(original_path, output_original_dir, num_crops=num_crops)

if __name__ == "__main__":
    expanded_original_path = input("請輸入存放原始圖像的目錄路徑: ")
    num_crop = int(input("請輸入每個樣本需要裁剪的次數 (預設 5): ") or "5")
    output_original = input("請輸入存放裁剪後原圖的目錄路徑 (預設: cropped_originals): ") or "cropped_originals"

    batch_crop_images_fast(expanded_original_path, output_original_dir=output_original, num_crops=num_crop)