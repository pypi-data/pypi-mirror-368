import { test } from "@tests/setup";
import { expect } from "@playwright/test";
import * as deviceFixtures from "./__fixtures__/devices";
import {
  fixtureSupportedDeviceName2,
  fixtureSupportedDevices,
} from "./__fixtures__/devices";

test.describe("Wizard Device Connection", () => {
  const deviceTarget = fixtureSupportedDevices.supported_devices[0];
  const wizardSteps = deviceTarget.wizard_steps;

  // Helper function to navigate through wizard steps
  const navigateToStep = async (page, stepNumber) => {
    const wizard = page.locator("div.c_modal_page");
    const footer = wizard.locator(".c_modal_footer_buttons");

    for (let i = 0; i < stepNumber; i++) {
      const nextButton = footer.locator("button").nth(1); // Next button is second button
      await nextButton.click();
      await page.waitForTimeout(100); // Small wait for transitions
    }
  };

  // Helper function to click footer button by index
  const clickFooterButton = async (page, buttonIndex) => {
    const wizard = page.locator("div.c_modal_page");
    const footer = wizard.locator(".c_modal_footer_buttons");
    const targetButton = footer.locator("button").nth(buttonIndex);

    await expect(targetButton).toBeVisible();
    await targetButton.click();
    await page.waitForTimeout(100);
  };

  test.beforeEach(async ({ page }) => {
    await deviceFixtures.mockDevicesListMultipleDevices(page);
    await deviceFixtures.mockSupportedDevices(page);

    await page.goto("/");

    const wizard = page.locator("div.c_modal_page");
    await expect(wizard).toBeVisible();

    // Navigate to device selection page
    const addDeviceButton = wizard.getByRole("button", { name: "Add device" });
    await addDeviceButton.click();

    // Search for and select specific device
    const searchInput = wizard.locator("input");
    await searchInput.fill(fixtureSupportedDeviceName2);

    const deviceOption = wizard.locator("div.c_device_option");
    await expect(deviceOption).toHaveCount(1);
    await deviceOption.click();

    // Wait for device connection page to load
    await expect(wizard).toContainText(/Device connection checklist/);
  });

  test("should display device connection checklist page", async ({ page }) => {
    const wizard = page.locator("div.c_modal_page");

    // Verify main heading and description
    const heading = wizard.getByText(/Device connection checklist/);
    const description = wizard.getByText(/Complete the checklist/);

    await expect(heading).toBeVisible();
    await expect(description).toBeVisible();
  });

  test("should display step indicator with correct number of steps", async ({
    page,
  }) => {
    const wizard = page.locator("div.c_modal_page");
    const stepIndicator = wizard.locator(".c_wizard_step_indicator");
    const indicatorItems = stepIndicator.locator(
      ".c_wizard_step_indicator_item"
    );

    await expect(stepIndicator).toBeVisible();
    await expect(indicatorItems).toHaveCount(wizardSteps.length);
  });

  test("should show first step as active initially", async ({ page }) => {
    const wizard = page.locator("div.c_modal_page");
    const stepIndicator = wizard.locator(".c_wizard_step_indicator");
    const indicatorItems = stepIndicator.locator(
      ".c_wizard_step_indicator_item"
    );

    const firstStep = indicatorItems.nth(0);
    await expect(firstStep).toHaveClass(/fill-surface-primary/);
  });

  // Test step navigation by clicking step indicators
  wizardSteps.slice(0, -1).forEach((step, targetStepIndex) => {
    test(`should navigate to step ${
      targetStepIndex + 1
    } when clicking step indicator`, async ({ page }) => {
      const wizard = page.locator("div.c_modal_page");
      const stepIndicator = wizard.locator(".c_wizard_step_indicator");
      const indicatorItems = stepIndicator.locator(
        ".c_wizard_step_indicator_item"
      );

      const targetItem = indicatorItems.nth(targetStepIndex);
      await targetItem.click();

      // Verify the clicked step is now active
      await expect(targetItem).toHaveClass(/fill-surface-primary/);
    });
  });

  test("should display navigation buttons in footer", async ({ page }) => {
    const wizard = page.locator("div.c_modal_page");
    const footer = wizard.locator(".c_modal_footer_buttons");
    const buttons = footer.locator("button");

    await expect(footer).toBeVisible();
    await expect(buttons).toHaveCount(2);

    const backButton = buttons.nth(0);
    const nextButton = buttons.nth(1);

    await expect(backButton).toBeVisible();
    await expect(nextButton).toBeVisible();
  });

  test("should navigate through steps using footer buttons", async ({
    page,
  }) => {
    const wizard = page.locator("div.c_modal_page");

    // Navigate forward through a few steps
    await clickFooterButton(page, 1); // Next button
    await clickFooterButton(page, 1); // Next button

    // Verify we've progressed
    const stepIndicator = wizard.locator(".c_wizard_step_indicator");
    const indicatorItems = stepIndicator.locator(
      ".c_wizard_step_indicator_item"
    );
    const thirdStep = indicatorItems.nth(2);

    await expect(thirdStep).toHaveClass(/fill-surface-primary/);
  });

  test.describe("WiFi Connectivity Form", () => {
    test.beforeEach(async ({ page }) => {
      // Navigate to the WiFi step
      await navigateToStep(page, 4);

      const wizard = page.locator("div.c_modal_page");
      const header = wizard.locator("p.text-2xl.font-semibold");
      await expect(header).toContainText("Wi-Fi: Enter details");
    });

    test("should display WiFi connection form with all required fields", async ({
      page,
    }) => {
      const wizard = page.locator("div.c_modal_page");
      const fieldDescriptors =
        deviceFixtures.fixtureSupportedDevices.supported_devices[0]
          .connection_types.wifi.fields;

      const form = wizard.locator(".connection_form");
      const fields = form.locator("input");

      const expectedFieldCount = Object.keys(fieldDescriptors).length;
      await expect(fields).toHaveCount(expectedFieldCount);
    });

    test("should have correctly configured form fields", async ({ page }) => {
      const wizard = page.locator("div.c_modal_page");
      const fieldDescriptors =
        deviceFixtures.fixtureSupportedDevices.supported_devices[0]
          .connection_types.wifi.fields;

      const form = wizard.locator(".connection_form");
      const fields = form.locator("input");

      const fieldEntries = Object.entries(fieldDescriptors);

      for (let i = 0; i < fieldEntries.length; i++) {
        const field = fields.nth(i);
        const [fieldName, fieldInfo] = fieldEntries[i];

        await expect(field).toHaveAttribute("name", fieldName);
        await expect(field).toHaveAttribute("placeholder", fieldInfo.name);

        // Test additional field properties if available
        if (fieldInfo.type) {
          await expect(field).toHaveAttribute("type", fieldInfo.type);
        }

        if (fieldInfo.required) {
          await expect(field).toHaveAttribute("required");
        }
      }
    });

    test("should allow filling out WiFi connection form", async ({ page }) => {
      const wizard = page.locator("div.c_modal_page");
      const form = wizard.locator(".connection_form");

      // Fill form with valid data
      const ssidField = form.locator('input[name="ssid"]').first();
      const passwordField = form.locator('input[type="password"]').first();

      await expect(ssidField).toBeVisible();
      await ssidField.fill("TestNetwork");

      await expect(passwordField).toBeVisible();
      await passwordField.fill("TestPassword123");

      // Submit form
      const submitButton = wizard.getByRole("button", {
        name: "Connect device",
      });
      await submitButton.isVisible();
      await submitButton.click();
    });
  });
});
