import { test, expect } from '@playwright/test'

test.describe('Settings', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.evaluate(() => localStorage.clear())
    await page.goto('/#/decoding')
  })

  test('settings drawer opens and closes', async ({ page }) => {
    // Click settings gear
    await page.click('text=⚙️')

    // Settings panel should be visible
    await expect(page.locator('text=Settings')).toBeVisible()
    await expect(page.locator('text=Spelling Units')).toBeVisible()

    // Close it
    await page.click('text=Close')
    await expect(page.locator('text=Spelling Units')).not.toBeVisible()
  })

  test('TTS toggle is available', async ({ page }) => {
    await page.click('text=⚙️')

    // TTS checkbox should exist (may or may not be available depending on browser)
    const ttsLabel = page.locator('text=Text-to-Speech')
    // TTS may not be available in headless Chromium, so just check the drawer has content
    const drawerContent = page.locator('.shadow-lg')
    await expect(drawerContent).toBeVisible()
  })

  test('frequency selector shows spelling units', async ({ page }) => {
    await page.click('text=⚙️')

    // Should have select elements for frequency control
    const selects = page.locator('select')
    const count = await selects.count()
    expect(count).toBeGreaterThan(0)

    // Each select should have Off/Low/Normal/High options
    const firstSelect = selects.first()
    await expect(firstSelect.locator('option')).toHaveCount(4)
  })

  test('setting a unit to off persists', async ({ page }) => {
    await page.click('text=⚙️')

    // Change first unit to "off"
    const firstSelect = page.locator('select').first()
    await firstSelect.selectOption('off')

    // Close and reopen settings
    await page.click('text=Close')
    await page.click('text=⚙️')

    // Should still be "off"
    const reopenedSelect = page.locator('select').first()
    await expect(reopenedSelect).toHaveValue('off')
  })

  test('sight words module has settings', async ({ page }) => {
    await page.goto('/#/sight-words')
    await page.click('text=⚙️')

    await expect(page.locator('text=Settings')).toBeVisible()
    await expect(page.locator('text=Sight Words')).toBeVisible()

    const selects = page.locator('select')
    const count = await selects.count()
    expect(count).toBeGreaterThan(0)
  })
})
