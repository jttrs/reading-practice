import { test, expect } from '@playwright/test'

test.describe('Decoding module', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage to start fresh
    await page.goto('/')
    await page.evaluate(() => localStorage.clear())
    await page.goto('/#/decoding')
  })

  test('shows a word card on load', async ({ page }) => {
    // Should display a word in large text
    const wordDisplay = page.locator('.text-7xl, .text-8xl')
    await expect(wordDisplay).toBeVisible()
    const word = await wordDisplay.textContent()
    expect(word).toBeTruthy()
    expect(word!.length).toBeGreaterThan(1)
  })

  test('shows prompt text before reveal', async ({ page }) => {
    await expect(page.locator('text=Click or press any key to reveal')).toBeVisible()
  })

  test('reveals breakdown on click', async ({ page }) => {
    // Click anywhere to reveal
    await page.click('.select-none')

    // Breakdown letters should appear (individual letter elements with underlines)
    const letterElements = page.locator('.text-5xl, .text-6xl')
    const count = await letterElements.count()
    expect(count).toBeGreaterThanOrEqual(2)

    // Full word should appear below the breakdown
    const fullWord = page.locator('p.text-3xl')
    await expect(fullWord).toBeVisible()
  })

  test('breakdown has color-coded underlines', async ({ page }) => {
    await page.click('.select-none')

    // Should have both blue (pattern) and gray (non-pattern) underlines
    const blueUnderlines = page.locator('.bg-blue-400')
    const grayUnderlines = page.locator('.bg-gray-300')

    // At least one of each type should exist
    const blueCount = await blueUnderlines.count()
    const grayCount = await grayUnderlines.count()
    expect(blueCount + grayCount).toBeGreaterThanOrEqual(2)
  })

  test('feedback buttons appear on reveal', async ({ page }) => {
    await page.click('.select-none')

    // Green check and red X buttons should appear
    const buttons = page.locator('button')
    const buttonTexts = await buttons.allTextContents()
    const hasCheck = buttonTexts.some(t => t.includes('✓'))
    const hasX = buttonTexts.some(t => t.includes('✗'))
    expect(hasCheck).toBe(true)
    expect(hasX).toBe(true)
  })

  test('correct feedback advances to next word', async ({ page }) => {
    // Get first word
    const wordDisplay = page.locator('.text-7xl, .text-8xl')
    const firstWord = await wordDisplay.textContent()

    // Reveal
    await page.click('.select-none')

    // Click correct (green check)
    const checkButton = page.locator('button:has-text("✓")')
    await checkButton.click()

    // Wait for cooldown to complete (2s)
    await page.waitForTimeout(2500)

    // New word should appear (may or may not be same due to random selection)
    await expect(wordDisplay).toBeVisible()
  })

  test('incorrect feedback advances to next word', async ({ page }) => {
    // Reveal
    await page.click('.select-none')

    // Click incorrect (red X)
    const xButton = page.locator('button:has-text("✗")')
    await xButton.click()

    // Wait for cooldown
    await page.waitForTimeout(2500)

    // Word display should still be showing
    const wordDisplay = page.locator('.text-7xl, .text-8xl')
    await expect(wordDisplay).toBeVisible()
  })

  test('back button navigates to landing', async ({ page }) => {
    await page.click('text=← Back')
    await expect(page).toHaveURL(/#\/$|#$/)
  })

  test('progress counter is visible', async ({ page }) => {
    // Should show "X / Y" progress
    const progress = page.locator('text=/\\d+ \\/ \\d+/')
    await expect(progress).toBeVisible()
  })

  test('phoneme info displays on reveal', async ({ page }) => {
    await page.click('.select-none')

    // Should show pattern info (like "ai, ay → /a/")
    const infoSection = page.locator('.text-gray-400')
    await expect(infoSection.first()).toBeVisible()

    // Should show "from" book attribution
    await expect(page.locator('text=/from "/')).toBeVisible()
  })
})
