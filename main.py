# filename: main.py
import os
import datetime
from loguru import logger
import time
from playwright.sync_api import Playwright, sync_playwright, expect
from pathlib import Path
import asyncio
from my_tools import setup_logger, open_output_files_automatically, open_completed_logs

# --- 文件拆分功能 ---
def split_txt_file_by_lines(file_path: Path) -> list[Path]:
    """
    将指定的TXT文件按行数进行拆分。
    拆分后的文件将锁定在Python运行文件的同一个目录里面。
    默认按照每份100行进行拆分，并等待用户确认后继续。

    Args:
        file_path (Path): 要拆分的TXT文件路径。

    Returns:
        list[Path]: 成功生成的拆分文件路径列表。
    """
    script_dir = Path(__file__).resolve().parent # 获取当前脚本的目录
    logger.info(f"开始处理文件拆分任务：'{file_path}'")

    # 1. 检查文件是否存在，不存在则创建
    if not file_path.exists(): # 检查文件是否存在，使用 Path.exists()
        logger.info(f"文件 '{file_path}' 不存在，已创建空文件作为初始化。")
        try:
            with open(str(file_path), 'w', encoding='utf-8') as f: # 将 Path 对象转换为字符串以便 open() 函数使用
                pass  # 创建一个空文件
            logger.success(f"成功创建空文件 '{file_path}'。")
        except IOError as e:
            logger.error(f"创建文件 '{file_path}' 失败: {e}")
            return []

    # 2. 读取文件并统计总行数
    total_lines = 0
    try:
        with open(str(file_path), 'r', encoding='utf-8') as f: # 将 Path 对象转换为字符串以便 open() 函数使用
            for _ in f:
                total_lines += 1
        logger.info(f"文件 '{file_path}' 总行数：{total_lines}")
    except Exception as e:
        logger.error(f"读取文件 '{file_path}' 统计行数失败: {e}")
        return []

    # 3. 处理空文件情况
    if total_lines == 0:
        logger.info(f"文件 '{file_path}' 为空。由于没有内容可供拆分，Playwright 自动化将跳过运行。请填充文件后再次运行以进行处理。")
        return []

    # 4. 默认按照一次输入一百行进行拆分，并等待用户确认
    lines_per_output_file = 100
    num_parts = (total_lines + lines_per_output_file - 1) // lines_per_output_file # 向上取整计算份数

    logger.info(f"文件 '{file_path}' 共有 {total_lines} 行。将按每份 {lines_per_output_file} 行进行拆分。")
    logger.info(f"计划拆分为 {num_parts} 份。")
    if total_lines % lines_per_output_file != 0:
        logger.info(f"其中，最后一份将包含 {total_lines % lines_per_output_file} 行。")

    # 自动打开文件供用户检查，并等待用户确认
    logger.info(f"即将自动打开文件 '{file_path}' 供您检查。")
    # 使用 my_tools 中的函数打开文件
    open_output_files_automatically([file_path], logger)
    input("请检查文件内容，确认无误后按 Enter 键继续文件处理...") # 等待用户输入

    # 初始化计数器和已生成文件路径列表
    processed_lines = 0
    success_files = 0
    failed_files = 0
    generated_file_paths = []

    # 5. 读取文件并写入拆分文件
    try:
        with open(str(file_path), 'r', encoding='utf-8') as infile: # 将 Path 对象转换为字符串以便 open() 函数使用
            current_part_num = 1
            current_line_count = 0
            current_output_file = None
            current_writer = None

            for line in infile:
                # 确定当前文件应包含的行数
                if current_part_num < num_parts:
                    target_lines_for_this_part = lines_per_output_file
                else: # 这是最后一部分
                    target_lines_for_this_part = total_lines % lines_per_output_file
                    if target_lines_for_this_part == 0 and total_lines > 0: # 如果 total_lines 是 100 的倍数，则最后一部分也是 100 行
                        target_lines_for_this_part = lines_per_output_file

                # 如果没有输出文件打开，或者当前文件已达到行数限制，则创建新的输出文件
                if current_output_file is None or current_line_count >= target_lines_for_this_part:
                    # 关闭之前的文件（如果存在）
                    if current_writer:
                        current_writer.close()
                        logger.success(f"文件 '{current_output_file}' 写入完成。")
                        success_files += 1

                    # 生成新的文件名并保存到 'cache' 目录
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    cache_dir = script_dir / "cache" # 使用 Path 对象创建目录
                    cache_dir.mkdir(parents=True, exist_ok=True) # 创建 cache 目录（如果不存在）
                    output_filename = cache_dir / f"拆分{current_part_num}_{timestamp}.txt" # 使用 Path 对象创建文件名
                    generated_file_paths.append(output_filename) # 存储生成的文件路径
                    current_output_file = output_filename
                    current_line_count = 0 # 重置行计数器

                    try:
                        current_writer = open(str(output_filename), 'w', encoding='utf-8') # 将 Path 对象转换为字符串以便 open() 函数使用
                        logger.info(f"开始写入文件：'{output_filename}'")
                    except IOError as e:
                        logger.error(f"打开文件 '{output_filename}' 失败: {e}")
                        failed_files += 1
                        current_part_num += 1 # 尝试创建下一个文件
                        continue # 继续主循环，跳过当前行

                # 写入当前行
                if current_writer:
                    current_writer.write(line)
                    current_line_count += 1
                    processed_lines += 1

                # 如果当前份的行数达到预定值，则关闭当前文件，准备下一个文件
                if current_line_count == target_lines_for_this_part:
                    if current_writer:
                        current_writer.close()
                        logger.success(f"文件 '{current_output_file}' 写入完成。")
                        success_files += 1
                        current_writer = None # 确保在下一轮循环中创建新文件
                    current_part_num += 1

            # 确保最后一个文件被关闭（处理最后一部分行数不足 100 的情况）
            if current_writer:
                current_writer.close()
                logger.success(f"文件 '{current_output_file}' 写入完成。")
                success_files += 1

    except Exception as e:
        logger.error(f"文件拆分过程中发生错误: {e}")
        logger.critical(f"【异常警报】文件拆分失败！")
    finally:
        logger.info(f"--- 文件拆分任务总结 ---")
        logger.info(f"总行数：{total_lines}")
        logger.info(f"已处理行数：{processed_lines}")
        logger.info(f"成功拆分文件数：{success_files}")
        logger.info(f"失败拆分文件数：{failed_files}")
        logger.info(f"任务完成。")
        return generated_file_paths

# --- Playwright 自动化功能 ---
def run_playwright_automation(playwright: Playwright, input_file_paths: list[Path]) -> None:
    """
    运行 Playwright 自动化脚本，将拆分后的文件内容依次填充到网页输入框。

    Args:
        playwright (Playwright): Playwright 实例。
        input_file_paths (list[Path]): 包含要填充到网页的文本文件路径列表。
    """
    logger.info("开始运行 Playwright 自动化任务。")
    browser = playwright.chromium.launch(
        headless=False,
        args=["--start-maximized"]
    )
    context = browser.new_context(no_viewport=True)
    page = context.new_page()

    page.goto("http://localhost:7862/?__theme=dark")
    time.sleep(2) # 页面加载后等待 2 秒

    page.get_by_role("button", name="图片信息").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="图片信息").click()
    time.sleep(2) # 点击后等待 2 秒

    file_input_locator = page.locator("#pnginfo_image input[type='file']")
    file_input_locator.wait_for(state="attached", timeout=10000)
    file_input_locator.set_input_files("00558-913820330.png")
    time.sleep(2) # 设置文件后等待 2 秒

    page.get_by_role("button", name=">> 文生图").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name=">> 文生图").click()
    time.sleep(2) # 点击后等待 2 秒

    # --- 提示词清空操作（只执行一次） ---
    page.get_by_role("textbox", name="提示词", exact=True).wait_for(state="visible", timeout=10000)
    page.get_by_role("textbox", name="提示词", exact=True).click()
    time.sleep(2) # 点击后等待 2 秒
    page.get_by_role("textbox", name="提示词", exact=True).press("ControlOrMeta+a")
    time.sleep(2) # 选择后等待 2 秒
    page.get_by_role("textbox", name="提示词", exact=True).fill("")
    time.sleep(2) # 填充（清空）后等待 2 秒
    # --- 提示词清空操作结束 ---

    # --- 骰子按钮（只执行一次） ---
    page.get_by_role("button", name="🎲️").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="🎲️").click()
    time.sleep(2) # 点击后等待 2 秒
    # --- 骰子按钮操作结束 ---

    # Playwright 自动点击“脚本”输入框
    page.get_by_role("textbox", name="脚本").wait_for(state="visible", timeout=10000)
    page.get_by_role("textbox", name="脚本").click()
    time.sleep(2) # 点击后等待 2 秒

    page.get_by_role("button", name="Prompts from file or textbox").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="Prompts from file or textbox").click()
    time.sleep(2) # 点击后等待 2 秒

    # 循环读取拆分文件内容并填充到“提示词输入列表”
    for i, file_path_for_input in enumerate(input_file_paths):
        logger.info(f"正在处理第 {i+1}/{len(input_file_paths)} 个拆分文件：'{file_path_for_input}'")
        try:
            with open(str(file_path_for_input), 'r', encoding='utf-8') as f: # 将 Path 对象转换为字符串以便 open() 函数使用
                content_to_fill = f.read()
        except Exception as e:
            logger.error(f"读取拆分文件 '{file_path_for_input}' 失败: {e}")
            continue # 跳过当前文件，继续下一个

        # 提示词输入列表的操作：清空并填充新内容
        page.get_by_role("textbox", name="提示词输入列表").wait_for(state="visible", timeout=10000)
        page.get_by_role("textbox", name="提示词输入列表").click()
        time.sleep(2) # 点击后等待 2 秒
        page.get_by_role("textbox", name="提示词输入列表").press("ControlOrMeta+a")
        time.sleep(2) # 选择后等待 2 秒
        page.get_by_role("textbox", name="提示词输入列表").fill("") # 清空
        time.sleep(2) # 清空后等待 2 秒

        page.get_by_role("textbox", name="提示词输入列表").fill(content_to_fill) # 填充新内容
        time.sleep(2) # 填充后等待 2 秒

        page.get_by_role("button", name="Enqueue").wait_for(state="visible", timeout=10000)
        page.get_by_role("button", name="Enqueue").click()
        time.sleep(2) # 点击后等待 2 秒

        # 每次加入队列后，等待一段时间让网页处理任务，然后进行下一个输入
        logger.info(f"第 {i+1} 个任务已加入队列，等待 5 秒进行下一个任务。")
        time.sleep(5) # 任务处理等待，避免操作过快

    logger.info("所有拆分文件内容已处理完毕。")

    # --- 添加总等待时间 ---
    print("等待 10 秒后关闭浏览器...")
    time.sleep(10) # 暂停 10 秒

    context.close()
    browser.close()
    logger.info("Playwright 自动化任务完成。")

# --- 主程序入口点 ---
async def main(): # 封装为异步主函数
    # 使用 my_tools 配置 Loguru 日志
    error_log_path, main_log_path = setup_logger()

    # 确保输入文件在脚本的同一目录中
    script_dir = Path(__file__).resolve().parent
    input_file_path = script_dir / "总行数.txt" # 使用 Path 对象表示输入文件

    # 运行文件拆分任务
    logger.info("准备进行文件拆分。")
    # split_txt_file_by_lines 返回一个列表，包含所有生成的拆分文件路径
    split_file_paths = split_txt_file_by_lines(input_file_path)

    # 如果文件拆分成功，则运行 Playwright 自动化
    if split_file_paths:
        logger.info(f"文件拆分成功，共生成 {len(split_file_paths)} 个文件。")
        with sync_playwright() as playwright:
            run_playwright_automation(playwright, split_file_paths)
    else:
        logger.info("由于没有文件可供处理，跳过 Playwright 自动化。") # 更改为信息级别，更友好

    # 任务完成后自动打开日志文件
    await open_completed_logs(main_log_path, error_log_path, logger, is_auto_open=True)

if __name__ == "__main__":
    asyncio.run(main()) # 运行异步主函数