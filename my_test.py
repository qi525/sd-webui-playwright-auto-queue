# my_test.py
from playwright.sync_api import Playwright, sync_playwright, expect
import time

def run(playwright: Playwright) -> None:
    # 设置浏览器启动参数
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            "--start-maximized" # 尝试最大化窗口，有时比设置固定分辨率更灵活
        ]
    )
    context = browser.new_context(
        no_viewport=True, # 忽略默认视口大小，使用浏览器窗口大小
        # 或者如果你想要固定2K分辨率，可以使用以下配置，但注意这可能不会立即生效为全屏
        # viewport={'width': 2560, 'height': 1440}
    )
    page = context.new_page()

    # 如果没有使用 --start-maximized，并且需要固定分辨率，可以在这里设置
    # page.set_viewport_size({'width': 2560, 'height': 1440}) # 2K分辨率

    page.goto("http://localhost:7862/?__theme=dark")
    time.sleep(2) # 页面加载后等待 2 秒

    page.get_by_role("button", name="图片信息").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="图片信息").click()
    time.sleep(2) # 点击后等待 2 秒

    file_input_locator = page.locator("#pnginfo_image input[type='file']")
    file_input_locator.wait_for(state="attached", timeout=10000)
    file_input_locator.set_input_files("00558-913820330.png")
    time.sleep(2) # 设置文件后等待 2 秒

    page.get_by_role("button", name="文生图", exact=True).wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="文生图", exact=True).click()
    time.sleep(2) # 点击后等待 2 秒

    page.get_by_role("button", name="图片信息").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="图片信息").click()
    time.sleep(2) # 点击后等待 2 秒

    page.get_by_role("button", name=">> 文生图").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name=">> 文生图").click()
    time.sleep(2) # 点击后等待 2 秒

    # --- 以下是注释掉的原始提示词清空操作，由新的对话框处理和点击替代 ---
    # page.get_by_role("textbox", name="提示词", exact=True).wait_for(state="visible", timeout=10000)
    # page.get_by_role("textbox", name="提示词", exact=True).click()
    # page.get_by_role("textbox", name="提示词", exact=True).press("ControlOrMeta+a")
    # page.get_by_role("textbox", name="提示词", exact=True).fill("")
    # --- 替代代码开始 ---

    def handle_dialog(dialog):
        print(f"Dialog message: {dialog.message}")
        dialog.dismiss()
    page.once("dialog", handle_dialog)

    page.locator('#uuid-0d3ce5bf-7c2b-4961-ace6-1f8c81dd17fe').first.click()
    time.sleep(2) # 点击后等待 2 秒

    # --- 替代代码结束 ---

    page.get_by_role("button", name="🎲️").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="🎲️").click()
    time.sleep(2) # 点击后等待 2 秒

    page.get_by_role("textbox", name="脚本").wait_for(state="visible", timeout=10000)
    page.get_by_role("textbox", name="脚本").click()
    time.sleep(2) # 点击后等待 2 秒

    page.get_by_role("button", name="Prompts from file or textbox").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="Prompts from file or textbox").click()
    time.sleep(2) # 点击后等待 2 秒

    page.get_by_role("textbox", name="提示词输入列表").wait_for(state="visible", timeout=10000)
    page.get_by_role("textbox", name="提示词输入列表").click()
    time.sleep(2) # 点击后等待 2 秒

    page.get_by_role("textbox", name="提示词输入列表").fill('1girl, absurdres, ahoge, ass_visible_through_thighs, bikini, black_hair, blue_archive, blush, breasts, breasts_apart, closed_mouth, collarbone, dark-skinned_female, dark_skin, halo, highres, jason_kim, karin_\\(blue_archive\\), large_breasts, long_hair, looking_at_viewer, navel, purple_halo, shirt, slingshot_swimsuit, solo, stomach, straight_hair, string_bikini, sweatdrop, swimsuit, very_long_hair, white_bikini, white_shirt, looking_at_viewer, curvy,seductive_smile,glamor,makeup,blush,,')
    time.sleep(2) # 填充后等待 2 秒

    page.get_by_role("button", name="Enqueue").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="Enqueue").click()
    time.sleep(2) # 点击后等待 2 秒

    # --- 增加总等待时间 ---
    print("等待 10 秒后关闭浏览器...")
    time.sleep(10) # 暂停 10 秒

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)