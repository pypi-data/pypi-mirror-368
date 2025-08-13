import { test } from "@tests/setup";
import { expect } from "@playwright/test";

import * as deviceFixtures from "./__fixtures__/devices";

test.describe("Wizard Device List", () => {
  test.describe("Default Device Display", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/");
    });

    test("should display default host devices", async ({ page }) => {
      const wizard = page.locator("div.c_modal_page");
      await expect(wizard).toBeVisible();

      const deviceConnections = wizard.locator("div.c_device_connection");

      // Verify user device (first device)
      const userDevice = deviceConnections.nth(0);
      await expect(userDevice).toContainText("The screen you're looking at");

      // Verify host device (second device)
      const hostDevice = deviceConnections.nth(1);
      await expect(hostDevice).toContainText("Whitebox #");
    });

    test("should display navigation buttons in footer", async ({ page }) => {
      const wizard = page.locator("div.c_modal_page");
      const footer = wizard.locator("div.c_modal_footer_buttons");

      await expect(footer).toBeVisible();

      const skipButton = footer.getByRole("button", { name: "Skip" });
      const addDeviceButton = footer.getByRole("button", {
        name: "Add device",
      });

      await expect(skipButton).toBeVisible();
      await expect(addDeviceButton).toBeVisible();

      // Verify button functionality
      await expect(skipButton).toBeEnabled();
      await expect(addDeviceButton).toBeEnabled();
    });

    test("should allow navigation via footer buttons", async ({ page }) => {
      const wizard = page.locator("div.c_modal_page");
      const footer = wizard.locator("div.c_modal_footer_buttons");

      const addDeviceButton = footer.getByRole("button", {
        name: "Add device",
      });
      await addDeviceButton.click();

      // Verify navigation occurred
      await expect(wizard).toContainText(/Select a device/);
    });
  });

  test.describe("No Devices State", () => {
    test.beforeEach(async ({ page }) => {
      await deviceFixtures.mockDevicesListNoDevices(page);
      await page.goto("/");
    });

    test("should display no devices banner with guidance", async ({ page }) => {
      const wizard = page.locator("div.c_modal_page");
      await expect(wizard).toBeVisible();

      const noDevicesBanner = wizard.getByText(/No installed devices/);
      const guidanceText = wizard.getByText(
        /Bringing devices onboard: What to know/
      );

      await expect(noDevicesBanner).toBeVisible();
      await expect(guidanceText).toBeVisible();
    });

    test("should not display device list when no devices available", async ({
      page,
    }) => {
      const wizard = page.locator("div.c_modal_page");

      // Verify no installed devices count is shown
      await expect(wizard).not.toContainText(/Installed devices \(/);
    });

    test("should still show navigation options when no devices", async ({
      page,
    }) => {
      const wizard = page.locator("div.c_modal_page");
      const footer = wizard.locator("div.c_modal_footer_buttons");

      const addDeviceButton = footer.getByRole("button", {
        name: "Add device",
      });
      await expect(addDeviceButton).toBeVisible();
      await expect(addDeviceButton).toBeEnabled();
    });
  });

  test.describe("With Multiple Devices", () => {
    test.beforeEach(async ({ page }) => {
      await deviceFixtures.mockDevicesListMultipleDevices(page);
      await page.goto("/");
    });

    test("should display all installed devices", async ({ page }) => {
      const wizard = page.locator("div.c_modal_page");
      await expect(wizard).toBeVisible();

      // Verify no devices banner is not shown
      await expect(wizard).not.toContainText(/No installed devices/);
      await expect(wizard).not.toContainText(
        /Bringing devices onboard: What to know/
      );
    });

    test("should display installed devices count", async ({ page }) => {
      const wizard = page.locator("div.c_modal_page");
      const mockDevicesCount = deviceFixtures.fixtureMultipleDevices.length;
      const expectedDeviceCountText = `Installed devices (${mockDevicesCount}/10)`;
      await expect(wizard).toContainText(expectedDeviceCountText);
    });
  });
});
