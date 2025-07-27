# my_test.py
from playwright.sync_api import Playwright, sync_playwright, expect
import time # 导入 time 模块

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("http://localhost:7862/?__theme=dark")

    # 显式等待 "图片信息" 按钮可见并点击
    page.get_by_role("button", name="图片信息").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="图片信息").click()

    # 显式等待 "拖拽图像到此处 -或- 点击上传" 文本可见并点击
    # 原始选择器可能不够精确，我们尝试等待文本出现
    # 或者直接点击上传区域（如果它是可点击的）
    # 这里我们等待文本出现，并确保其父元素可点击
    upload_area_locator = page.locator("#pnginfo_image").get_by_text("拖拽图像到此处 -或- 点击上传")
    upload_area_locator.wait_for(state="visible", timeout=10000)
    upload_area_locator.click()

    # 确保文件输入框可见并设置文件
    # 对于 set_input_files，Playwright 通常会自动等待文件输入框出现
    # 但如果之前点击操作没有成功激活文件输入，这里可能会有问题
    page.locator("body").set_input_files("00558-913820330.png")

    # 显式等待 "文生图" 按钮可见并点击
    page.get_by_role("button", name="文生图", exact=True).wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="文生图", exact=True).click()

    # 以下操作可能也需要类似的等待，根据实际情况添加
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