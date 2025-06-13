import os
import shutil

def _process_file(source_path_str, output_path_str, old_filepath, new_filename_only, original_filename):
    """
    Helper function to process a single file: copy or move based on paths.
    """
    # Normalize paths for reliable comparison
    # os.path.realpath resolves symlinks and normalizes the path
    norm_source_path = os.path.realpath(source_path_str)
    norm_output_path = os.path.realpath(output_path_str)

    # Construct the full new filepath in the output directory
    new_filepath_in_output = os.path.join(output_path_str, new_filename_only)

    try:
        if norm_source_path == norm_output_path:
            # Paths are the same, rename/move in place
            # old_filepath is already in the source_path_str (which is also output_path_str)
            # new_filepath_in_output is also in the same directory
            shutil.move(old_filepath, new_filepath_in_output)
            print(f"  √ 已在原位置重命名: '{original_filename}' -> '{new_filename_only}'")
        else:
            # Paths are different, copy the file to the output directory with the new name
            shutil.copy2(old_filepath, new_filepath_in_output)
            print(f"  √ 已复制并以新名称保存: '{original_filename}' -> '{new_filename_only}' (于: {output_path_str})")
        return True
    except OSError as e:
        print(f"  × 操作失败 (OSError): '{original_filename}' -> '{new_filename_only}'. 错误: {e}")
    except shutil.Error as e:
        print(f"  × 操作失败 (shutil.Error): '{original_filename}' -> '{new_filename_only}'. 错误: {e}")
    return False

def batch_replace_in_filenames(source_directory_path, output_directory_path, old_string, new_string):
    """
    批量替换文件名中的指定字符串。
    如果输出路径与源路径不同，则复制并重命名到输出路径，原文件不变。
    如果输出路径与源路径相同，则在原位置重命名。
    """
    if not os.path.isdir(source_directory_path):
        print(f"错误: 源路径 '{source_directory_path}' 不是一个有效的文件夹。")
        return

    if not os.path.isdir(output_directory_path):
        try:
            os.makedirs(output_directory_path, exist_ok=True)
            print(f"已创建输出文件夹: '{output_directory_path}'")
        except OSError as e:
            print(f"错误: 创建输出文件夹 '{output_directory_path}' 失败。错误: {e}")
            return

    print(f"\n--- 开始替换文件名中的字符串 ---")
    print(f"源文件夹: {source_directory_path}")
    print(f"输出文件夹: {output_directory_path}")
    print(f"要替换的字符串: '{old_string}'")
    print(f"替换为: '{new_string}'")

    processed_count = 0
    total_files = 0

    for filename in os.listdir(source_directory_path):
        old_filepath = os.path.join(source_directory_path, filename)

        if os.path.isfile(old_filepath):
            base_name, extension = os.path.splitext(filename)
            if old_string in base_name:
                total_files += 1
                new_base_name = base_name.replace(old_string, new_string)
                new_filename_only = new_base_name + extension
                if _process_file(source_directory_path, output_directory_path, old_filepath, new_filename_only, filename):
                    processed_count += 1
            else:
                print(f"  跳过文件 (未找到要替换的字符串): '{filename}'")
        else:
            print(f"  跳过子目录: {filename}")

    print(f"\n--- 替换文件名中的字符串完成 ---")
    print(f"共扫描 {total_files} 个文件，成功处理 {processed_count} 个。")

def batch_replace_file_extensions(source_directory_path, output_directory_path, old_extension, new_extension):
    """
    批量替换指定目录下文件的后缀名。
    如果输出路径与源路径不同，则复制并重命名到输出路径，原文件不变。
    如果输出路径与源路径相同，则在原位置重命名。
    """
    if not os.path.isdir(source_directory_path):
        print(f"错误: 源路径 '{source_directory_path}' 不是一个有效的文件夹。")
        return

    if not os.path.isdir(output_directory_path):
        try:
            os.makedirs(output_directory_path, exist_ok=True)
            print(f"已创建输出文件夹: '{output_directory_path}'")
        except OSError as e:
            print(f"错误: 创建输出文件夹 '{output_directory_path}' 失败。错误: {e}")
            return

    print(f"\n--- 开始替换文件后缀 ---")
    print(f"源文件夹: {source_directory_path}")
    print(f"输出文件夹: {output_directory_path}")
    print(f"要替换的旧后缀名: '{old_extension}'")
    print(f"新的后缀名: '{new_extension}'")

    processed_count = 0
    total_files = 0

    for filename in os.listdir(source_directory_path):
        old_filepath = os.path.join(source_directory_path, filename)

        if os.path.isfile(old_filepath):
            if filename.lower().endswith(old_extension.lower()):
                total_files += 1
                base_name = filename[:-len(old_extension)]
                new_filename_only = base_name + new_extension
                if _process_file(source_directory_path, output_directory_path, old_filepath, new_filename_only, filename):
                    processed_count += 1
            elif old_extension == '' and '.' not in filename: # Handle files with no extension when old_extension is specified as ''
                total_files += 1
                new_filename_only = filename + new_extension
                if _process_file(source_directory_path, output_directory_path, old_filepath, new_filename_only, filename):
                    processed_count += 1
            elif old_extension != '' and not filename.lower().endswith(old_extension.lower()):
                print(f"  跳过文件 (旧后缀名不匹配): '{filename}'")
            elif old_extension == '' and '.' in filename:
                print(f"  跳过文件 (文件有扩展名，但旧后缀名为空): '{filename}'")

        else:
            print(f"  跳过子目录: {filename}")

    print(f"\n--- 替换文件后缀完成 ---")
    print(f"共扫描 {total_files} 个文件，成功处理 {processed_count} 个。")

def batch_add_prefix_to_filenames(source_directory_path, output_directory_path, prefix):
    """
    批量给文件名增加前缀。
    如果输出路径与源路径不同，则复制并重命名到输出路径，原文件不变。
    如果输出路径与源路径相同，则在原位置重命名。
    """
    if not os.path.isdir(source_directory_path):
        print(f"错误: 源路径 '{source_directory_path}' 不是一个有效的文件夹。")
        return

    if not os.path.isdir(output_directory_path):
        try:
            os.makedirs(output_directory_path, exist_ok=True)
            print(f"已创建输出文件夹: '{output_directory_path}'")
        except OSError as e:
            print(f"错误: 创建输出文件夹 '{output_directory_path}' 失败。错误: {e}")
            return

    print(f"\n--- 开始添加前缀 ---")
    print(f"源文件夹: {source_directory_path}")
    print(f"输出文件夹: {output_directory_path}")
    print(f"要添加的前缀: '{prefix}'")

    processed_count = 0
    total_files = 0

    for filename in os.listdir(source_directory_path):
        old_filepath = os.path.join(source_directory_path, filename)

        if os.path.isfile(old_filepath):
            total_files += 1
            new_filename_only = f"{prefix}{filename}"
            if _process_file(source_directory_path, output_directory_path, old_filepath, new_filename_only, filename):
                processed_count += 1
        else:
            print(f"  跳过子目录: {filename}")

    print(f"\n--- 添加前缀完成 ---")
    print(f"共扫描 {total_files} 个文件，成功处理 {processed_count} 个。")

def batch_add_suffix_to_filenames(source_directory_path, output_directory_path, suffix):
    """
    批量给文件名增加后缀 (在主文件名和扩展名之间)。
    如果输出路径与源路径不同，则复制并重命名到输出路径，原文件不变。
    如果输出路径与源路径相同，则在原位置重命名。
    """
    if not os.path.isdir(source_directory_path):
        print(f"错误: 源路径 '{source_directory_path}' 不是一个有效的文件夹。")
        return

    if not os.path.isdir(output_directory_path):
        try:
            os.makedirs(output_directory_path, exist_ok=True)
            print(f"已创建输出文件夹: '{output_directory_path}'")
        except OSError as e:
            print(f"错误: 创建输出文件夹 '{output_directory_path}' 失败。错误: {e}")
            return

    print(f"\n--- 开始添加后缀 ---")
    print(f"源文件夹: {source_directory_path}")
    print(f"输出文件夹: {output_directory_path}")
    print(f"要添加的后缀: '{suffix}'")

    processed_count = 0
    total_files = 0

    for filename in os.listdir(source_directory_path):
        old_filepath = os.path.join(source_directory_path, filename)

        if os.path.isfile(old_filepath):
            total_files += 1
            base_name, extension = os.path.splitext(filename)
            new_filename_only = f"{base_name}{suffix}{extension}"
            if _process_file(source_directory_path, output_directory_path, old_filepath, new_filename_only, filename):
                processed_count += 1
        else:
            print(f"  跳过子目录: {filename}")

    print(f"\n--- 添加后缀完成 ---")
    print(f"共扫描 {total_files} 个文件，成功处理 {processed_count} 个。")

def batch_rename_files_sequentially(source_directory_path, output_directory_path):
    """
    批量将文件按顺序重命名为数字格式。
    如果输出路径与源路径不同，则复制并重命名到输出路径，原文件不变。
    如果输出路径与源路径相同，则在原位置重命名 (通过两阶段操作避免冲突)。
    """
    if not os.path.isdir(source_directory_path):
        print(f"错误: 源路径 '{source_directory_path}' 不是一个有效的文件夹。")
        return

    # Normalize paths for reliable comparison
    norm_source_path = os.path.realpath(source_directory_path)
    norm_output_path = os.path.realpath(output_directory_path)

    if not os.path.isdir(output_directory_path):
        try:
            os.makedirs(output_directory_path, exist_ok=True)
            print(f"已创建输出文件夹: '{output_directory_path}'")
        except OSError as e:
            print(f"错误: 创建输出文件夹 '{output_directory_path}' 失败。错误: {e}")
            return

    print(f"\n--- 开始顺序重命名 ---")
    print(f"源文件夹: {source_directory_path}")
    print(f"输出文件夹: {output_directory_path}")
    print("将按原名称顺序重命名为数字格式 (1, 2, 3...)")

    files_to_process = []
    for filename in os.listdir(source_directory_path):
        filepath = os.path.join(source_directory_path, filename)
        if os.path.isfile(filepath):
            files_to_process.append(filename)

    files_to_process.sort() # 确保按原始文件名排序

    processed_count = 0
    total_files = len(files_to_process)

    print(f"找到 {total_files} 个文件，开始处理...")

    if norm_source_path == norm_output_path:
        # 在原地重命名，需要两阶段操作以避免冲突
        temp_renames = [] # 存储 (old_filepath, temp_filepath, original_filename, new_filename_only)

        # 阶段1: 重命名为临时名称
        print("  阶段1: 临时重命名...")
        for index, original_filename in enumerate(files_to_process, start=1):
            old_filepath = os.path.join(source_directory_path, original_filename)
            _, extension = os.path.splitext(original_filename)
            # 使用一个不太可能与现有文件冲突的临时名称
            temp_filename_only = f"__temp_rename_{index}{extension}" # 加上独特前缀
            temp_filepath = os.path.join(source_directory_path, temp_filename_only)

            try:
                shutil.move(old_filepath, temp_filepath)
                temp_renames.append((temp_filepath, f"{index}{extension}", original_filename))
                print(f"  √ 已临时重命名: '{original_filename}' -> '{temp_filename_only}'")
            except OSError as e:
                print(f"  × 临时重命名失败 (OSError): '{original_filename}'. 错误: {e}")
                # 如果临时重命名失败，为了避免后续错误，我们直接跳过这个文件
                continue
        
        # 阶段2: 重命名为最终名称
        print("  阶段2: 最终重命名...")
        for temp_filepath, final_filename_only, original_filename in temp_renames:
            final_filepath = os.path.join(source_directory_path, final_filename_only)
            try:
                shutil.move(temp_filepath, final_filepath)
                print(f"  √ 已最终重命名: '{original_filename}' -> '{final_filename_only}'")
                processed_count += 1
            except OSError as e:
                print(f"  × 最终重命名失败 (OSError): '{original_filename}' -> '{final_filename_only}'. 错误: {e}")
                # 记录失败，如果需要，可以考虑将文件恢复到临时名称
    else:
        # 源和输出目录不同，直接复制并重命名
        for index, original_filename in enumerate(files_to_process, start=1):
            old_filepath = os.path.join(source_directory_path, original_filename)
            _, extension = os.path.splitext(original_filename)
            new_filename_only = f"{index}{extension}"
            
            # _process_file 已经处理了复制逻辑
            if _process_file(source_directory_path, output_directory_path, old_filepath, new_filename_only, original_filename):
                processed_count += 1

    print(f"\n--- 顺序重命名完成 ---")
    print(f"共扫描 {total_files} 个文件，成功处理 {processed_count} 个。")

def get_user_choice():
    """
    获取用户选择的重命名模式。
    """
    while True:
        print("\n请选择操作模式:")
        print("1. 添加后缀 (在主文件名和扩展名之间)")
        print("2. 按顺序重命名为数字 (例如: 1.jpg, 2.png ...)")
        print("3. 添加前缀 (在完整文件名前)")
        print("4. 替换文件后缀 (例如: .jpg -> .png)")
        print("5. 替换文件名中的一部分 (例如: _mask -> _triple)")

        choice = input("请输入您的选择 (1, 2, 3, 4 或 5): ").strip()

        if choice in ['1', '2', '3', '4', '5']:
            return choice
        else:
            print("无效输入，请输入 1, 2, 3, 4 或 5。")

if __name__ == "__main__":
    print("欢迎使用文件批量处理工具！")
    source_directory = input("请输入源文件夹路径: ").strip()

    if not os.path.isdir(source_directory):
        print(f"错误: 源路径 '{source_directory}' 不是一个有效的文件夹。程序将退出。")
        exit()

    output_directory = input("请输入输出文件夹路径 (若与源文件夹相同，请再次输入源文件夹路径): ").strip()

    if not output_directory:
        print("错误: 输出文件夹路径不能为空。程序将退出。")
        exit()

    # 预先创建输出目录（如果不存在）
    if not os.path.isdir(output_directory):
        try:
            os.makedirs(output_directory, exist_ok=True)
            print(f"提示: 输出文件夹 '{output_directory}' 不存在，已自动创建。")
        except OSError as e:
            print(f"错误: 创建输出文件夹 '{output_directory}' 失败。错误: {e} 程序将退出。")
            exit()

    user_choice = get_user_choice()

    norm_source_path = os.path.realpath(source_directory)
    norm_output_path = os.path.realpath(output_directory)

    if norm_source_path != norm_output_path:
        print(f"\n提示: 源文件夹和输出文件夹不同。")
        print(f"原始文件将保留在 '{source_directory}' 中。")
        print(f"处理后的文件副本将保存到 '{output_directory}'。")
    else:
        print(f"\n提示: 源文件夹和输出文件夹相同。")
        print(f"文件将在 '{source_directory}' 中直接重命名。")

    if user_choice == '1':
        suffix_to_add = input("请输入要添加的后缀内容 (例如: _backup, -v2): ").strip()
        if not suffix_to_add:
            print("后缀内容不能为空，操作已取消。")
        else:
            batch_add_suffix_to_filenames(source_directory, output_directory, suffix_to_add)

    elif user_choice == '2':
        print(f"\n警告: 此操作会将 '{source_directory}' 中的文件")
        if norm_source_path == norm_output_path:
            print(f"直接重命名为数字格式 (原文件名将丢失)！此操作使用两阶段重命名以避免冲突。")
        else:
            print(f"复制到 '{output_directory}' 并重命名为数字格式 (源文件保留，但输出文件名将为数字格式)！")

        confirm = input("确认继续吗？(y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            batch_rename_files_sequentially(source_directory, output_directory)
        else:
            print("操作已取消。")

    elif user_choice == '3':
        prefix_to_add = input("请输入要添加的前缀内容 (例如: new_, draft_): ").strip()
        if not prefix_to_add:
            print("前缀内容不能为空，操作已取消。")
        else:
            batch_add_prefix_to_filenames(source_directory, output_directory, prefix_to_add)

    elif user_choice == '4':
        old_extension = input("请输入要替换的旧后缀名 (例如: .jpg): ").strip()
        new_extension = input("请输入新的后缀名 (例如: .png): ").strip()
        if not old_extension or not new_extension:
            print("旧后缀名和新后缀名不能为空，操作已取消。")
        else:
            if not old_extension.startswith('.'):
                old_extension = '.' + old_extension
            if not new_extension.startswith('.'):
                new_extension = '.' + new_extension
            batch_replace_file_extensions(source_directory, output_directory, old_extension, new_extension)

    elif user_choice == '5':
        old_string = input("请输入要替换的旧字符串 (例如: _mask): ").strip()
        new_string = input("请输入新的字符串 (例如: _triple): ").strip()
        if not old_string:
            print("要替换的旧字符串不能为空，操作已取消。")
        else:
            batch_replace_in_filenames(source_directory, output_directory, old_string, new_string)

    print("\n所有操作已完成！")