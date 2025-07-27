# my_test.py
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("http://localhost:7862/?__theme=dark")
    page.get_by_role("button", name="图片信息").click()
    page.locator("#pnginfo_image").get_by_text("拖拽图像到此处 -或- 点击上传").click()
    page.locator("body").set_input_files("00558-913820330.png")
    page.get_by_role("button", name=">> 文生图").click()
    page.get_by_role("textbox", name="提示词", exact=True).click()
    page.get_by_role("textbox", name="提示词", exact=True).press("ControlOrMeta+a")
    page.get_by_role("textbox", name="提示词", exact=True).fill("")
    page.get_by_role("button", name="🎲️").click()
    page.get_by_role("textbox", name="脚本").click()
    page.get_by_role("button", name="Prompts from file or textbox").click()
    page.get_by_role("textbox", name="提示词输入列表").click()
    page.get_by_role("textbox", name="提示词输入列表").fill('1girl, absurdres, ahoge, ass_visible_through_thighs, bikini, black_hair, blue_archive, blush, breasts, breasts_apart, closed_mouth, collarbone, dark-skinned_female, dark_skin, halo, highres, jason_kim, karin_\\(blue_archive\\), large_breasts, long_hair, looking_at_viewer, navel, purple_halo, shirt, slingshot_swimsuit, solo, stomach, straight_hair, string_bikini, sweatdrop, swimsuit, very_long_hair, white_bikini, white_shirt, looking_at_viewer, curvy,seductive_smile,glamor,makeup,blush,,')
    page.get_by_role("button", name="Enqueue").click()

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)