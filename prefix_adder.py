import os
import time
import platform
import subprocess
from loguru import logger
import sys
from typing import Tuple, List

# 配置loguru日志
# 日志文件会根据时间戳生成，防止覆盖，并限制大小为10MB
# 1. 创建日志文件夹
LOG_FOLDER = "prefix_adder_log"
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
# 2. 修改日志文件路径
LOG_FILE_PATH = os.path.join(LOG_FOLDER, "prefix_adder_{time}.txt")
logger.add(LOG_FILE_PATH, rotation="10 MB", level="INFO")

# 默认将日志输出到控制台（stderr）
logger.add(sys.stderr, level="INFO")

# --- 文件系统工具函数 (从 my_tools 引入，用于支持文件打开) ---

def normalize_drive_letter(path_str: str) -> str:
    """
    如果路径以驱动器号开头，将其转换为大写。
    例如: c:\\test -> C:\\test
    """
    if sys.platform.startswith('win') and len(path_str) >= 2 and path_str[1] == ':':
        return path_str[0].upper() + path_str[1:]
    return path_str

def open_output_files_automatically(
    file_paths: List[str], # 注意这里使用 str，因为原始代码中没有 Path 对象
    logger_obj
):
    """
    根据用户设置自动打开生成的输出文件。
    Args:
        file_paths (List[str]): 包含要打开的文件路径的列表。
        logger_obj (logger): Loguru logger 实例。
    """
    # 默认不检查环境变量 DISABLE_AUTO_OPEN，因为此模块更简单

    # 定义延迟时间 (秒)，避免文件刚写入就尝试打开导致权限问题
    OPEN_FILE_DELAY_SECONDS = 0.5 

    for file_path_str in file_paths:
        # 尝试打开前增加延迟
        logger_obj.debug(f"尝试打开文件 '{normalize_drive_letter(file_path_str)}' 前，等待 {OPEN_FILE_DELAY_SECONDS} 秒。")
        time.sleep(OPEN_FILE_DELAY_SECONDS)

        actual_path_to_open = file_path_str
        # 注意: 此简化模块不处理 Loguru 的 .zip 压缩日志文件特殊情况

        if not os.path.exists(actual_path_to_open):
            logger_obj.warning(f"警告: 无法自动打开文件 '{normalize_drive_letter(actual_path_to_open)}'，因为文件不存在。")
            continue

        try:
            normalized_path = normalize_drive_letter(actual_path_to_open)
            logger_obj.info(f"自动打开: {normalized_path}")
            
            if sys.platform == "win32":
                # Windows 系统：使用 Popen + explorer 启动，确保进程在后台运行且不带控制台窗口。
                try:
                    # CREATE_NO_WINDOW (0x08000000) 标志用于隐藏新进程的控制台窗口
                    # 使用 Popen 启动，不阻塞主程序，不捕获输出，实现非阻塞后台打开
                    subprocess.Popen(
                        ['explorer', normalized_path], 
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        start_new_session=True # 确保它是一个独立进程
                    )
                    logger_obj.info(f"已尝试使用 Popen/explorer 启动文件打开进程 (后台非阻塞): {normalized_path}")

                except FileNotFoundError:
                    logger_obj.error(f"错误: explorer 命令未找到。请检查系统 PATH。", exc_info=True)
                except Exception as e:
                    logger_obj.error(f"执行 explorer 时发生未知错误: {e}", exc_info=True)

            elif sys.platform == "darwin": # macOS
                # macOS 系统
                # check=False 避免非零返回码引发异常
                subprocess.run(['open', normalized_path], check=False) 
            else: # Linux 系统 (使用 xdg-open)
                # check=False 避免非零返回码引发异常
                subprocess.run(['xdg-open', normalized_path], check=False) 
            
        except FileNotFoundError:
            # 捕获其他平台或特定错误
            logger_obj.error(f"错误: 无法找到打开文件 '{normalized_path}' 的应用程序。请手动打开。", exc_info=True)
        except Exception as e:
            logger_obj.error(f"自动打开文件 '{normalized_path}' 时发生意外错误: {e}", exc_info=True)


# --- 文件准备工具函数 ---

def prepare_files(prefix_file: str, input_file: str) -> bool:
    """
    检查并创建所需文件，如果文件不存在则写入示例内容。
    自动打开文件供用户检查。
    返回 True 表示文件已准备好，False 表示发生错误。
    
    注意：这里的 prefix_file 和 input_file 现在是 main 函数中计算出的绝对路径。
    """
    files_to_create = {
        prefix_file: "[LOG] ",
        input_file: "系统启动...\n加载配置成功。\n任务完成。"
    }
    
    files_missing = False
    
    for filename, default_content in files_to_create.items():
        if not os.path.exists(filename):
            try:
                # 使用传入的 filename (已经是绝对路径)
                abs_path = filename 
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(default_content)
                # 注意：这里日志中仍然显示 basename，但实际操作的是绝对路径
                logger.warning(f"文件 '{os.path.basename(filename)}' 不存在，已自动创建并填充示例内容。路径：{abs_path}")
                files_missing = True
            except Exception as e:
                # 文件创建失败是严重错误
                logger.error(f"创建文件 '{os.path.basename(filename)}' 失败: {e}")
                return False

    # 无论文件是否缺失，都应该尝试打开文件供用户检查和编辑
    logger.info("-" * 50)
    logger.info(f"重要：文件已准备就绪。尝试自动打开 '{os.path.basename(prefix_file)}' 和 '{os.path.basename(input_file)}' 进行检查。")
    logger.info("-" * 50)
    
    # 自动打开文件供用户检查，使用最健壮的 explorer/open 模式
    open_output_files_automatically([prefix_file, input_file], logger)

    if files_missing:
        return True # 成功准备文件
        
    return True # 文件都已存在

# --- 核心处理函数 ---

def get_prefix(prefix_file_path: str) -> str | None:
    """
    读取前缀文件，获取前缀。
    """
    try:
        with open(prefix_file_path, 'r', encoding='utf-8') as f:
            # 读取第一行并移除行尾的换行符（\n, \r），但保留末尾的空格
            prefix = f.readline().rstrip('\n')
            logger.info(f"成功读取前缀文件: '{os.path.basename(prefix_file_path)}'")
            logger.info(f"获取到的前缀为: '{prefix}'")
            return prefix
    except FileNotFoundError:
        # 理论上 prepare_files 已经确保文件存在，这里作为安全备份
        logger.error(f"错误：前缀文件未找到: {os.path.basename(prefix_file_path)}")
        return None
    except Exception as e:
        logger.error(f"读取前缀文件时发生未知错误: {e}")
        return None

def process_and_add_prefix(prefix: str, input_file_path: str, output_file_path: str) -> Tuple[int, int, int]:
    """
    给输入文件的每一行加上前缀，并写入输出文件。
    返回 (总行数, 成功处理行数, 失败行数)
    """
    total_lines = 0
    success_lines = 0
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile, \
             open(output_file_path, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                total_lines += 1
                try:
                    # 移除当前行末尾的换行符，然后加上前缀，最后再重新加上换行符
                    processed_line = prefix + line.strip('\n') + '\n'
                    outfile.write(processed_line)
                    success_lines += 1
                except Exception as e:
                    logger.warning(f"处理第 {total_lines} 行时失败: {line.strip()} | 错误: {e}")

    except FileNotFoundError:
        logger.error(f"错误：输入文件未找到: {os.path.basename(input_file_path)}")
    except Exception as e:
        logger.error(f"处理文件时发生未知错误: {e}")
    
    failed_lines = total_lines - success_lines
    return total_lines, success_lines, failed_lines

# --- 主函数 ---

def main():
    logger.info("--- 任务启动 ---")
    
    # 文件路径定义
    PREFIX_FILE_NAME = "前缀.txt"
    INPUT_FILE_NAME = "处理文档.txt"
    OUTPUT_FILE_NAME = "总行数.txt" # 更改: 合并文件的名称改为 '总行数.txt'

    # 计算脚本文件所在目录的绝对路径，用于定位文件
    # **核心改动点**：确保文件在脚本所在的目录中操作
    try:
        # __file__ 只有在作为脚本运行时才可用
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # 如果在交互式环境（如 IPython）中运行，则退回到当前工作目录
        SCRIPT_DIR = os.getcwd()
        logger.warning(f"无法确定脚本路径（可能是交互式环境），文件将使用当前工作目录: {SCRIPT_DIR}")
    
    # 将文件名转换为基于脚本目录的绝对路径
    PREFIX_FILE = os.path.join(SCRIPT_DIR, PREFIX_FILE_NAME)
    INPUT_FILE = os.path.join(SCRIPT_DIR, INPUT_FILE_NAME)
    OUTPUT_FILE = os.path.join(SCRIPT_DIR, OUTPUT_FILE_NAME)

    # 1. 文件检查与准备 (自动创建并尝试打开文件供检查)
    if not prepare_files(PREFIX_FILE, INPUT_FILE):
        logger.error("文件准备失败，任务中止。")
        return
    
    # 2. 暂停等待用户确认，计时从此刻开始
    try:
        print("\n" + "=" * 50)
        # 提示用户文件所在目录，增强用户体验
        print(f"文件已尝试自动打开，请检查并编辑位于目录 '{SCRIPT_DIR}' 下的文件。")
        input("检查完毕，请按回车键（Enter）继续处理...")
        print("=" * 50 + "\n")
    except EOFError:
        logger.warning("在非交互式环境中运行，跳过回车等待。")
    except KeyboardInterrupt:
        logger.warning("用户取消操作。")
        return
    
    start_time = time.time() # **计时开始节点：用户按下回车**
    logger.info(f"任务开始计时时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    
    # 3. 获取前缀
    prefix_str = get_prefix(PREFIX_FILE)
    if prefix_str is None:
        logger.error("无法获取前缀，任务中止。")
        end_time_fail = time.time()
        logger.info(f"总处理时间: {end_time_fail - start_time:.4f} 秒 (失败中止)")
        logger.info(f"任务结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        return

    # 4. 处理文档并添加前缀
    logger.info(f"开始处理文件 '{INPUT_FILE_NAME}'...")
    total, success, failed = process_and_add_prefix(prefix_str, INPUT_FILE, OUTPUT_FILE)

    # 5. 任务结果汇总
    logger.info("--- 任务处理结果 ---")
    logger.info(f"总数量: {total} 行")
    logger.info(f"成功: {success} 行")
    logger.info(f"失败: {failed} 行")
    
    if failed > 0:
        logger.warning("有部分行处理失败，请检查日志文件。")
    else:
        logger.success(f"所有行处理成功！结果已保存到文件: '{OUTPUT_FILE_NAME}'")
        logger.info(f"开始自动打开合并成功文件: '{OUTPUT_FILE_NAME}'")
        open_output_files_automatically([OUTPUT_FILE], logger) # 更改: 合并成功后自动打开文件
        
    # 6. 计时结束
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    logger.info(f"总处理时间: {elapsed_time:.4f} 秒")
    logger.info(f"任务结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    logger.info("--- 任务结束 ---")

if __name__ == "__main__":
    main()