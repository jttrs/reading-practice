import { test, expect } from '@playwright/test'

test.describe('Landing page', () => {
  test('renders module cards', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('heading', { name: 'Decoding' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Sight Words' })).toBeVisible()
  })

  test('navigates to decoding module', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Decoding')
    await expect(page).toHaveURL(/#\/decoding/)
  })

  test('navigates to sight words module', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Sight Words')
    await expect(page).toHaveURL(/#\/sight-words/)
  })
})
