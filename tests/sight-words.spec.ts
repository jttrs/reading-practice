import { test, expect } from '@playwright/test'

test.describe('Sight Words module', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.evaluate(() => localStorage.clear())
    await page.goto('/#/sight-words')
  })

  test('shows a sight word on load', async ({ page }) => {
    const wordDisplay = page.locator('.text-7xl, .text-8xl')
    await expect(wordDisplay).toBeVisible()
    const word = await wordDisplay.textContent()
    expect(word).toBeTruthy()
    expect(word!.length).toBeGreaterThan(1)
  })

  test('shows read prompt before reveal', async ({ page }) => {
    await expect(page.locator('text=Read the word')).toBeVisible()
  })

  test('reveal shows book attribution', async ({ page }) => {
    await page.click('.select-none')
    await expect(page.locator('text=/from "/')).toBeVisible()
  })

  test('feedback buttons appear on reveal', async ({ page }) => {
    await page.click('.select-none')

    const buttonTexts = await page.locator('button').allTextContents()
    expect(buttonTexts.some(t => t.includes('✓'))).toBe(true)
    expect(buttonTexts.some(t => t.includes('✗'))).toBe(true)
  })

  test('feedback advances to next word', async ({ page }) => {
    await page.click('.select-none')
    await page.locator('button:has-text("✓")').click()
    await page.waitForTimeout(2500)

    const wordDisplay = page.locator('.text-7xl, .text-8xl')
    await expect(wordDisplay).toBeVisible()
  })

  test('back button navigates to landing', async ({ page }) => {
    await page.click('text=← Back')
    await expect(page).toHaveURL(/#\/$|#$/)
  })

  test('progress counter is visible', async ({ page }) => {
    await expect(page.locator('text=/\\d+ \\/ \\d+/')).toBeVisible()
  })
})
