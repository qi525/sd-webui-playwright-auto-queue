# my_test.py
from playwright.sync_api import Playwright, sync_playwright, expect
import time

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("http://localhost:7862/?__theme=dark")

    # 显式等待 "图片信息" 按钮可见并点击
    # 如果页面加载慢，这个等待是必要的
    page.get_by_role("button", name="图片信息").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="图片信息").click()

    # --- 优化文件上传部分 ---
    # 查找页面上的文件输入元素。通常是一个 input 标签，类型为 file。
    # 我们可以尝试使用更通用的选择器来找到它，例如 'input[type="file"]'。
    # 如果页面上有多个这样的元素，可能需要更具体的选择器。
    # 这里我们假设它是 #pnginfo_image 区域内的某个 input[type="file"]
    # 也可以直接尝试更通用的 page.locator('input[type="file"]')
    
    # 方案一：尝试在 #pnginfo_image 区域内查找 input[type="file"]
    file_input_locator = page.locator("#pnginfo_image input[type='file']")
    
    # 方案二（如果方案一不行，可以尝试这个更通用的）：
    # file_input_locator = page.locator('input[type="file"]')

    # 显式等待文件输入元素出现。
    # Playwright 的 set_input_files 会自动等待元素，但这里增加显式等待可以避免后续操作失败。
    file_input_locator.wait_for(state="attached", timeout=10000) # 只要元素在DOM中即可，不要求可见

    # 直接设置文件，这会模拟用户选择文件。
    # 注意：确保 '00558-913820330.png' 文件存在于脚本运行的目录下，或者使用绝对路径。
    file_input_locator.set_input_files("00558-913820330.png")

    # 在文件上传后，可能需要等待一些时间让页面处理上传操作，例如图片预览显示出来。
    # 这里可以根据实际情况添加一个短暂的暂停，或者等待图片预览元素可见。
    # 比如等待一个代表图片加载完成的元素出现
    # time.sleep(2) # 临时等待2秒，观察效果

    # --- 文件上传优化结束 ---

    # 显式等待 "文生图" 按钮可见并点击
    page.get_by_role("button", name="文生图", exact=True).wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="文生图", exact=True).click()

    page.get_by_role("button", name="图片信息").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="图片信息").click()

    page.get_by_role("button", name=">> 文生图").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name=">> 文生图").click()

    page.get_by_role("textbox", name="提示词", exact=True).wait_for(state="visible", timeout=10000)
    page.get_by_role("textbox", name="提示词", exact=True).click()
    page.get_by_role("textbox", name="提示词", exact=True).press("ControlOrMeta+a")
    page.get_by_role("textbox", name="提示词", exact=True).fill("")

    page.get_by_role("button", name="🎲️").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="🎲️").click()

    page.get_by_role("textbox", name="脚本").wait_for(state="visible", timeout=10000)
    page.get_by_role("textbox", name="脚本").click()

    page.get_by_role("button", name="Prompts from file or textbox").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="Prompts from file or textbox").click()

    page.get_by_role("textbox", name="提示词输入列表").wait_for(state="visible", timeout=10000)
    page.get_by_role("textbox", name="提示词输入列表").click()
    page.get_by_role("textbox", name="提示词输入列表").fill('1girl, absurdres, ahoge, ass_visible_through_thighs, bikini, black_hair, blue_archive, blush, breasts, breasts_apart, closed_mouth, collarbone, dark-skinned_female, dark_skin, halo, highres, jason_kim, karin_\\(blue_archive\\), large_breasts, long_hair, looking_at_viewer, navel, purple_halo, shirt, slingshot_swimsuit, solo, stomach, straight_hair, string_bikini, sweatdrop, swimsuit, very_long_hair, white_bikini, white_shirt, looking_at_viewer, curvy,seductive_smile,glamor,makeup,blush,,')

    page.get_by_role("button", name="Enqueue").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="Enqueue").click()

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)