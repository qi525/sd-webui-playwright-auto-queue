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

    page.get_by_role("button", name="图片信息").wait_for(state="visible", timeout=10000)
    page.get_by_role("button", name="图片信息").click()

    file_input_locator = page.locator("#pnginfo_image input[type='file']")
    file_input_locator.wait_for(state="attached", timeout=10000)
    file_input_locator.set_input_files("00558-913820330.png")

    # 在文件上传后，等待页面处理完成，例如等待某个加载指示器消失或关键元素出现
    # 这里可以根据你的页面实际情况进行调整，例如等待图片预览加载完成
    # time.sleep(2) # 临时等待2秒，观察效果，如果页面有特定元素表示加载完成，最好等待该元素

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

    # --- 增加等待时间 ---
    print("等待 10 秒后关闭浏览器...")
    time.sleep(10) # 暂停 10 秒

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)