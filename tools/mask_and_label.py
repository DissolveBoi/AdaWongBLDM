import os
import cv2
import numpy as np
import sys
import shutil # 新增：用於檔案複製

def safe_path_join(*paths):
    """
    安全的路径拼接，处理中文路径编码问题。
    
    Args:
        *paths: 路径组件
        
    Returns:
        str: 拼接后的路径
    """
    result = os.path.join(*paths)
    # 确保路径使用正确的编码
    if isinstance(result, bytes):
        result = result.decode('utf-8', errors='ignore')
    return os.path.normpath(result)

def safe_listdir(path):
    """
    安全的目录列表获取，处理中文文件名编码问题。
    
    Args:
        path (str): 目录路径
        
    Returns:
        list: 文件名列表
    """
    try:
        files = os.listdir(path)
        # 确保文件名使用正确的编码
        result = []
        for f in files:
            if isinstance(f, bytes):
                f = f.decode('utf-8', errors='ignore')
            result.append(f)
        return result
    except UnicodeDecodeError:
        # 如果出现编码错误，尝试使用系统默认编码
        try:
            files = os.listdir(path.encode('gbk'))
            return [f.decode('gbk', errors='ignore') for f in files]
        except:
            print(f"警告: 无法正确读取目录 {path} 中的文件名")
            return []

def find_matching_files(mask_dir, label_dir):
    """
    找到mask和label文件夹中对应的文件组合。
    
    Args:
        mask_dir (str): 掩码文件夹路径  
        label_dir (str): 标签文件夹路径
        
    Returns:
        list: 包含匹配文件信息的列表
    """
    matching_sets = []
    
    if not os.path.exists(mask_dir):
        print(f"错误: 掩码文件夹 '{mask_dir}' 不存在")
        return matching_sets
    
    try:
        all_files = safe_listdir(mask_dir)
        mask_files = [f for f in all_files 
                      if os.path.isfile(safe_path_join(mask_dir, f)) and 
                      ('_mask.' in f.lower())]
    except Exception as e:
        print(f"错误: 无法读取掩码文件夹: {e}")
        return matching_sets
    
    for mask_file in mask_files:
        try:
            mask_suffix_identifier = '_mask.'
            if mask_suffix_identifier in mask_file.lower():
                mask_pos = mask_file.lower().find(mask_suffix_identifier)
                base_name = mask_file[:mask_pos]
                
                # 提取副檔名 (例如：.png, .jpg)
                file_extension_part = mask_file[mask_pos + len(mask_suffix_identifier):]
                image_ext = '.' + file_extension_part # 例如：".png"
                
                label_file = base_name + "_label" + image_ext
                
                mask_path = safe_path_join(mask_dir, mask_file)
                label_path = safe_path_join(label_dir, label_file)
                
                if os.path.exists(label_path):
                    matching_sets.append({
                        'base_name': base_name,
                        'mask_file': mask_file,
                        'label_file': label_file,
                        'mask_path': mask_path,
                        'label_path': label_path,
                        'ext': image_ext  # 新增：儲存副檔名
                    })
                else:
                    print(f"警告: {base_name} 的对应label文件不存在，跳过")
                    print(f"   缺少: {label_file}")
            else:
                continue
        except Exception as e:
            print(f"警告: 处理文件 {mask_file} 时出错: {e}")
            continue
    
    return matching_sets

def extract_defect_mask(label_path, mask_path, defect_id):
    """
    根据指定的缺陷ID从label中提取相应区域，并在mask中保留该区域。
    
    Args:
        label_path (str): 标签文件路径
        mask_path (str): 掩码文件路径
        defect_id (int): 缺陷ID
        
    Returns:
        numpy.ndarray or None: 处理后的掩码，如果没有指定缺陷则返回None
    """
    try:
        def safe_imread(filepath):
            try:
                img = cv2.imread(filepath, cv2.IMREAD_COLOR)
                if img is not None:
                    return img
                
                with open(filepath, 'rb') as f:
                    data = np.frombuffer(f.read(), dtype=np.uint8)
                    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
                    return img
            except Exception as e:
                print(f"     读取文件失败: {e}")
                return None
            
        label_img = safe_imread(label_path)
        if label_img is None:
            print(f"   错误: 无法读取label文件: {os.path.basename(label_path)}")
            return None
            
        mask_img = safe_imread(mask_path)
        if mask_img is None:
            print(f"   错误: 无法读取mask文件: {os.path.basename(mask_path)}")
            return None
        
        if label_img.shape != mask_img.shape:
            print(f"   错误: label和mask图像尺寸不匹配")
            print(f"     label尺寸: {label_img.shape}")
            print(f"     mask尺寸: {mask_img.shape}")
            return None
        
        defect_mask = np.all(label_img == [defect_id, defect_id, defect_id], axis=2)
        
        if not np.any(defect_mask):
            return None 
        
        new_mask = np.zeros_like(mask_img)
        new_mask[defect_mask] = mask_img[defect_mask]
        
        return new_mask
        
    except Exception as e:
        print(f"   错误: 处理文件时发生异常: {e}")
        return None

def convert_to_gray_white(mask_img):
    """
    将掩码图像转换为灰白格式：黑色(0,0,0) -> 灰色(127,127,127)，其他保持不变。
    
    Args:
        mask_img (numpy.ndarray): 输入的掩码图像
        
    Returns:
        numpy.ndarray: 转换后的图像
    """
    output_img = mask_img.copy()
    black_pixels = np.all(mask_img == [0, 0, 0], axis=2)
    output_img[black_pixels] = [127, 127, 127]
    return output_img

def process_defect_masks(mask_dir, label_dir, output_dir, defect_id, 
                         original_image_dir, output_original_image_dir): # 新增参数
    """
    处理缺陷检测数据集，提取指定缺陷的掩码，并复制对应的原图。
    
    Args:
        mask_dir (str): 掩码文件夹路径
        label_dir (str): 标签文件夹路径
        output_dir (str): 输出处理后掩码的文件夹路径
        defect_id (int): 要提取的缺陷ID
        original_image_dir (str): 原始图片文件夹路径
        output_original_image_dir (str): 复制原始图片的目标文件夹路径
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建掩码输出目录: {output_dir}")

    # 新增：创建复制原图的输出目录
    if not os.path.exists(output_original_image_dir):
        os.makedirs(output_original_image_dir)
        print(f"已创建原图输出目录: {output_original_image_dir}")
    
    print("正在扫描文件...")
    matching_files = find_matching_files(mask_dir, label_dir)
    
    if not matching_files:
        print("未找到匹配的文件组合，请检查文件夹路径和文件命名")
        return
    
    print(f"找到 {len(matching_files)} 组匹配文件")
    print(f"开始处理缺陷ID: {defect_id}")
    print("-" * 50)
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    copied_originals_count = 0 # 新增：复制原图计数
    original_not_found_count = 0 # 新增：原图未找到计数
    
    for file_set in matching_files:
        print(f"处理: {file_set['base_name']}")
        
        processed_mask = extract_defect_mask(
            file_set['label_path'], 
            file_set['mask_path'], 
            defect_id
        )
        
        if processed_mask is None:
            print(f"   跳过: 未找到缺陷ID {defect_id} 在 {file_set['base_name']}")
            skipped_count += 1
            continue
        
        # 如果找到缺陷，尝试复制原图
        original_image_name = file_set['base_name'] + file_set['ext']
        source_original_path = safe_path_join(original_image_dir, original_image_name)
        dest_original_path = safe_path_join(output_original_image_dir, original_image_name)

        if os.path.exists(source_original_path):
            try:
                shutil.copy2(source_original_path, dest_original_path)
                print(f"  ✓ 已复制原图: {original_image_name} 到 {output_original_image_dir}")
                copied_originals_count += 1
            except Exception as e_copy:
                print(f"  × 复制原图失败: {original_image_name} - {e_copy}")
        else:
            print(f"  ! 警告: 未找到原图: {source_original_path}")
            original_not_found_count +=1

        # 处理并保存掩码
        try:
            gray_white_mask = convert_to_gray_white(processed_mask)
            output_path = safe_path_join(output_dir, file_set['mask_file'])
            
            def safe_imwrite(filepath, img):
                try:
                    success = cv2.imwrite(filepath, img)
                    if success:
                        return True
                    
                    _, encoded_img = cv2.imencode(file_set['ext'], img) # 使用从文件名中提取的正确副檔名
                    with open(filepath, 'wb') as f:
                        f.write(encoded_img.tobytes())
                    return True
                except Exception as e:
                    print(f"     保存失败: {e}")
                    return False
            
            success = safe_imwrite(output_path, gray_white_mask)
            
            if success:
                print(f"  ✓ 已保存处理后掩码: {file_set['mask_file']}")
                processed_count += 1
            else:
                print(f"  × 保存处理后掩码失败: {file_set['mask_file']}")
                error_count += 1
                
        except Exception as e:
            print(f"   × 处理或保存掩码失败: {e}")
            error_count += 1
    
    print("-" * 50)
    print(f"处理完成!")
    print(f"成功处理掩码: {processed_count} 个文件")
    print(f"跳过文件 (不含指定缺陷): {skipped_count} 个文件")
    print(f"处理掩码错误: {error_count} 个文件")
    print(f"成功复制原图: {copied_originals_count} 个文件") # 新增
    print(f"未找到原图: {original_not_found_count} 个文件") # 新增
    print(f"处理后掩码输出目录: {output_dir}")
    print(f"复制原图输出目录: {output_original_image_dir}") # 新增

def main():
    """
    主函数，处理用户输入并执行处理流程。
    """
    if sys.platform.startswith('win'):
        import locale
        try:
            locale.setlocale(locale.LC_ALL, 'Chinese')
        except:
            pass # 如果设置失败，继续执行
    
    print("=== 缺陷检测数据集掩码处理工具 ===")
    print()
    
    mask_dir = input("请输入掩码文件夹路径 (mask): ").strip().strip('"\'')
    label_dir = input("请输入标签文件夹路径 (label): ").strip().strip('"\'')
    output_dir = input("请输入处理后掩码的输出文件夹路径: ").strip().strip('"\'')
    original_image_dir = input("请输入原始图片文件夹路径 (原图): ").strip().strip('"\'') # 新增
    output_original_image_dir = input("请输入复制原始图片的目标文件夹路径: ").strip().strip('"\'') # 新增
    
    while True:
        try:
            defect_id = int(input("请输入要提取的缺陷ID (整数): ").strip())
            break
        except ValueError:
            print("请输入有效的整数")
    
    paths_to_check = [
        (mask_dir, "掩码文件夹"), 
        (label_dir, "标签文件夹"),
        (original_image_dir, "原始图片文件夹") # 新增检查
    ]

    for path, name in paths_to_check:
        if not os.path.exists(path):
            print(f"错误: {name} '{path}' 不存在")
            return
        if not os.path.isdir(path):
            print(f"错误: '{path}' 不是一个有效的文件夹")
            return
    
    print(f"\n开始处理...")
    print(f"掩码文件夹: {mask_dir}")
    print(f"标签文件夹: {label_dir}")
    print(f"原始图片文件夹: {original_image_dir}") # 新增
    print(f"处理后掩码输出文件夹: {output_dir}")
    print(f"复制原图目标文件夹: {output_original_image_dir}") # 新增
    print(f"目标缺陷ID: {defect_id}")
    print()
    
    process_defect_masks(mask_dir, label_dir, output_dir, defect_id, 
                         original_image_dir, output_original_image_dir) # 传入新参数

if __name__ == "__main__":
    main()