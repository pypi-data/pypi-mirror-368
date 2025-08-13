import { test } from "@tests/setup";
import { expect } from "@playwright/test";

import * as deviceFixtures from "./__fixtures__/devices";

test.describe("Wizard Device Selection", () => {
  test.beforeEach(async ({ page }) => {
    await deviceFixtures.mockSupportedDevices(page);
    await deviceFixtures.mockDevicesListMultipleDevices(page);

    await page.goto("/");

    const wizard = page.locator("div.c_modal_page");
    await expect(wizard).toBeVisible();

    // Navigate to device selection page
    const addDeviceButton = wizard.getByRole("button", { name: "Add device" });
    await addDeviceButton.click();

    // Wait for device selection page to load
    await expect(wizard).toContainText(/Select a device/);
  });

  test("should display the device selection page with correct content", async ({
    page,
  }) => {
    const wizard = page.locator("div.c_modal_page");

    // Use more specific assertions
    await expect(wizard.getByText(/Select a device/)).toBeVisible();
    await expect(
      wizard.getByText(/Select the type of device you want to connect/)
    ).toBeVisible();
  });

  test("should display all supported devices from backend", async ({
    page,
  }) => {
    const wizard = page.locator("div.c_modal_page");
    const deviceOptions = wizard.locator("div.c_device_option");

    const expectedDeviceCount =
      deviceFixtures.fixtureSupportedDevices.supported_devices.length;

    await expect(deviceOptions).toHaveCount(expectedDeviceCount);

    // Verify each device is displayed with expected content
    const supportedDevices =
      deviceFixtures.fixtureSupportedDevices.supported_devices;
    for (let i = 0; i < supportedDevices.length; i++) {
      const deviceOption = deviceOptions.nth(i);
      await expect(deviceOption).toContainText(supportedDevices[i].device_name);
    }
  });

  test("should filter devices based on search input", async ({ page }) => {
    const wizard = page.locator("div.c_modal_page");
    const searchInput = wizard
      .locator('input[type="search"], input[placeholder*="search" i], input')
      .first();
    const deviceOptions = wizard.locator("div.c_device_option");

    const supportedDevices =
      deviceFixtures.fixtureSupportedDevices.supported_devices;
    const targetDeviceName = supportedDevices[0].device_name.toLowerCase();

    // Test filtering with lowercase input
    await searchInput.fill(targetDeviceName);
    await expect(deviceOptions).toHaveCount(1);
    await expect(deviceOptions.first()).toContainText(
      supportedDevices[0].device_name
    );

    // Test clearing search restores all devices
    await searchInput.clear();
    await expect(deviceOptions).toHaveCount(supportedDevices.length);
  });

  test("should handle case-insensitive search", async ({ page }) => {
    const wizard = page.locator("div.c_modal_page");
    const searchInput = wizard
      .locator('input[type="search"], input[placeholder*="search" i], input')
      .first();
    const deviceOptions = wizard.locator("div.c_device_option");

    const supportedDevices =
      deviceFixtures.fixtureSupportedDevices.supported_devices;
    const targetDevice = supportedDevices[0];

    // Test with different cases
    const testCases = [
      targetDevice.device_name.toLowerCase(),
      targetDevice.device_name.toUpperCase(),
      targetDevice.device_name, // original case
    ];

    for (const searchTerm of testCases) {
      await searchInput.fill(searchTerm);
      await expect(deviceOptions).toHaveCount(1);
      await expect(deviceOptions.first()).toContainText(
        targetDevice.device_name
      );
      await searchInput.clear();
    }
  });

  test("should handle empty search results gracefully", async ({ page }) => {
    const wizard = page.locator("div.c_modal_page");
    const searchInput = wizard
      .locator('input[type="search"], input[placeholder*="search" i], input')
      .first();
    const deviceOptions = wizard.locator("div.c_device_option");

    // Search for non-existent device
    await searchInput.fill("nonexistentdevice123");
    await expect(deviceOptions).toHaveCount(0);
  });

  test("should allow device selection", async ({ page }) => {
    const wizard = page.locator("div.c_modal_page");
    const deviceOptions = wizard.locator("div.c_device_option");

    // Select first device
    const firstDevice = deviceOptions.first();
    await firstDevice.click();
    await expect(wizard).toContainText(/Device connection checklist/);
  });
});
