import { test, expect } from '@playwright/test';

test.use({
  locale: 'python'
});

test('test', async ({ page }) => {
  await page.goto('http://localhost:7862/?__theme=dark');
  await page.getByRole('button', { name: '图片信息' }).click();
  await page.locator('#pnginfo_image').getByText('拖拽图像到此处 -或- 点击上传').click();
  await page.locator('body').setInputFiles('00558-913820330.png');
  await page.getByRole('button', { name: '>> 文生图' }).click();
  page.once('dialog', dialog => {
    console.log(`Dialog message: ${dialog.message()}`);
    dialog.dismiss().catch(() => {});
  });
  await page.locator('#uuid-0d3ce5bf-7c2b-4961-ace6-1f8c81dd17fe').first().click();
});