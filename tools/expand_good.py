import os
import cv2
import numpy as np
import random

def expand_image_no_mask_cv2(original_path, num_expansions, output_original_dir):
    """
    使用 cv2 和 numpy 對單個原始圖像進行多次擴充，並將結果儲存。

    Args:
        original_path (str): 原始圖像的完整檔案路徑。
        num_expansions (int): 擴充的次數。
        output_original_dir (str): 存放擴充後原始圖像的目錄。
    """
    try:
        original_image = cv2.imread(original_path)
        if original_image is None:
            print(f"警告: 無法讀取圖像 {original_path}")
            return

        h, w, channels = original_image.shape

        # 計算目標邊長 l，取寬度和高度的平均值
        l = 256

        padding_color = [127, 127, 127]  # cv2 使用 BGR 格式，但由於填充色是灰度，所以順序不影響

        for i in range(num_expansions):
            new_width, new_height = w, h
            expanded_original = None

            if h < w:
                # 在高度方向上擴充，使其成為 l x w 的圖像
                padding_h = l - h
                # 隨機決定上下填充的量
                padding_top = random.randint(0, padding_h)
                padding_bottom = padding_h - padding_top

                new_height = l
                expanded_original = cv2.copyMakeBorder(original_image, padding_top, padding_bottom, 0, 0, cv2.BORDER_CONSTANT, value=padding_color)

            elif w < h:
                # 在寬度方向上擴充，使其成為 h x l 的圖像
                padding_w = l - w
                # 隨機決定左右填充的量
                padding_left = random.randint(0, padding_w)
                padding_right = padding_w - padding_left

                new_width = l
                expanded_original = cv2.copyMakeBorder(original_image, 0, 0, padding_left, padding_right, cv2.BORDER_CONSTANT, value=padding_color)
            else:
                # 如果寬度和高度相等 (正方形)，則不進行擴充
                expanded_original = original_image

            # 組合輸出檔案名稱並儲存
            base_name, ext = os.path.splitext(os.path.basename(original_path))
            output_original_name = os.path.join(output_original_dir, f"{base_name}_expanded_cv2_{i+1}{ext}")

            cv2.imwrite(output_original_name, expanded_original)
            print(f"已擴充並儲存 (cv2): {output_original_name}")

    except FileNotFoundError:
        print(f"錯誤: 找不到檔案 {original_path}")
    except Exception as e:
        print(f"處理 {original_path} 時發生未預期的錯誤: {e}")

def batch_expand_images_no_mask_cv2(original_dir, num_expansions=1, output_original_dir="expanded_originals_cv2"):
    """
    使用 cv2 和 numpy 批量擴充指定目錄下的原始圖像，並將結果儲存。

    Args:
        original_dir (str): 存放原始圖像的目錄。
        num_expansions (int, optional): 每個圖像需要擴充的次數。預設為 1。
        output_original_dir (str, optional): 存放擴充後原始圖像的目錄。預設為 "expanded_originals_cv2"。
    """
    if not os.path.exists(output_original_dir):
        os.makedirs(output_original_dir)

    original_files = [f for f in os.listdir(original_dir) if os.path.isfile(os.path.join(original_dir, f))]

    for original_file in original_files:
        name, ext = os.path.splitext(original_file)
        # 根據原始邏輯，可選擇只處理檔名為數字的檔案
        if not name.isdigit():
            # 如果您想處理所有圖片，而不只是檔名為數字的圖片，可以移除或註解掉下面這行
            continue

        original_path = os.path.join(original_dir, original_file)

        print(f"正在處理 (cv2): {original_file}")
        # 呼叫更新後的擴充函式
        expand_image_no_mask_cv2(original_path, num_expansions, output_original_dir)

if __name__ == "__main__":
    original_images_path = input("請輸入存放原始圖像的目錄路徑: ")
    num_expand = int(input("請輸入每個圖像需要擴充的次數: "))
    output_original = input("請輸入存放擴充後圖像的目錄路徑 (預設: expanded_originals_cv2): ") or "expanded_originals_cv2"

    batch_expand_images_no_mask_cv2(original_images_path, num_expansions=num_expand, output_original_dir=output_original)