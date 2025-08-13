import moxios from "moxios";
import { act, screen, render, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import useDeviceWizardStore from "./stores/device_wizard";
import useDevicesStore from "./stores/devices";
import WizardPageDeviceConnection from "./WizardPageDeviceConnection";
import {
  fixtureSupportedDevices,
  fixtureSupportedDeviceCodename1,
} from "./__fixtures__/devices";

const { api, toasts } = Whitebox;

afterEach(cleanup);

describe("WizardPageDeviceConnection", () => {
  const getWizardStoreState = useDeviceWizardStore.getState;

  beforeEach(async () => {
    moxios.install(api.client);

    await moxios.wait(() => {
      const request = moxios.requests.mostRecent();
      request.respondWith({
        status: 200,
        response: fixtureSupportedDevices,
      });
    });

    const getDeviceWizardState = useDeviceWizardStore.getState;
    await act(async () => {
      await getDeviceWizardState().fetchSupportedDevices();
      await getDeviceWizardState().setSelectedDeviceCodename(
        fixtureSupportedDeviceCodename1
      );
    });
  });

  afterEach(() => {
    moxios.uninstall(api.client);
  });

  describe("rendering", () => {
    const deviceTarget = fixtureSupportedDevices.supported_devices[0];

    const wizardSteps = deviceTarget.wizard_steps;

    beforeEach(async () => {
      // Start all rendering tests from step 0
      await act(async () => {
        await getWizardStoreState().setDeviceSetupStep(0);
      });
    });

    it("should render the step indicator properly", async () => {
      const { container } = render(<WizardPageDeviceConnection />);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const stepIndicator = container.querySelector(".c_wizard_step_indicator");
      expect(stepIndicator).toBeInTheDocument();

      const indicatorItems = stepIndicator.querySelectorAll(
        ".c_wizard_step_indicator_item"
      );

      expect(indicatorItems.length).toEqual(wizardSteps.length);
    });

    // Run for every wizard step index separately
    it.each(Array.from(Array(wizardSteps.length - 1).keys()))(
      "should change steps on step indicator item click",
      async (targetStep) => {
        const beforeClickStep = getWizardStoreState().getDeviceSetupStep();
        if (beforeClickStep === targetStep) {
          // Skip if the target step is the same as the current one
          return;
        }

        const user = userEvent.setup();

        const { container } = render(<WizardPageDeviceConnection />);

        await act(async () => {
          await new Promise((resolve) => setTimeout(resolve, 0));
        });

        const stepIndicator = container.querySelector(
          ".c_wizard_step_indicator"
        );
        const indicatorItems = stepIndicator.querySelectorAll(
          ".c_wizard_step_indicator_item"
        );

        const targetItem = indicatorItems[targetStep];

        await act(async () => {
          await user.click(targetItem);
        });

        const afterClickStep = getWizardStoreState().getDeviceSetupStep();
        expect(afterClickStep).toEqual(targetStep);
      }
    );

    it.each(Array.from(Array(wizardSteps.length - 1).keys()))(
      "should render the step content properly",
      async (stepNo) => {
        act(() => getWizardStoreState().setDeviceSetupStep(stepNo));

        const { container } = render(<WizardPageDeviceConnection />);

        await act(async () => {
          await new Promise((resolve) => setTimeout(resolve, 0));
        });

        const stepContent = container.querySelectorAll(".c_generic_element");
        const stepElements = wizardSteps[stepNo].elements;

        stepContent.forEach((renderedElement, index) => {
          const stepElement = stepElements[index];

          switch (stepElement.type) {
            case "text":
              expect(renderedElement).toHaveTextContent(
                stepElement.config.text
              );
              break;
            case "image": {
              const imgElement = renderedElement.querySelector("img");
              const expectedImgSrc = api.getUrl(stepElement.config.url);
              expect(imgElement).toHaveAttribute("src", expectedImgSrc);
              break;
            }
            case "video": {
              const videoElement =
                renderedElement.querySelector("video > source");
              const expectedVideoSrc = api.getUrl(stepElement.config.url);
              expect(videoElement).toHaveAttribute("src", expectedVideoSrc);
              break;
            }
            case "input":
              expect(renderedElement).toHaveAttribute(
                "placeholder",
                stepElement.placeholder
              );
              expect(renderedElement).toHaveAttribute(
                "type",
                stepElement.input_type
              );
              break;
            default:
              throw new Error(`Unknown element type: ${stepElement.type}`);
          }
        });
      }
    );
  });

  describe("actions", () => {
    beforeEach(async () => {
      // Start all rendering tests from step 0
      await act(async () => {
        const lastStep =
          fixtureSupportedDevices.supported_devices[0].wizard_steps.length - 1;
        await getWizardStoreState().setDeviceSetupStep(lastStep);
      });
    });

    it("should allow connecting to device", async () => {
      const { container } = render(<WizardPageDeviceConnection />);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const testValues = {
        ssid: "test_ssid",
        password: "test_password",
      };

      container.querySelectorAll("input").forEach((input) => {
        const elName = input.getAttribute("name");
        expect(elName).toBeDefined();
        input.value = testValues[elName];
      });

      const connectButton = screen.getByText("Connect device");
      expect(connectButton).toBeInTheDocument();

      const mockAddToast = vi.fn();
      const mockAddDevice = vi.fn().mockReturnValueOnce({
        name: "device_name",
      });
      const mockGoBackToDeviceList = vi.fn();
      const mockFetchDevices = vi.fn();

      await act(async () => {
        await toasts.useToastsStore.setState({
          addToast: mockAddToast,
        });
        await useDeviceWizardStore.setState({
          addDevice: mockAddDevice,
          goBackToDeviceList: mockGoBackToDeviceList,
        });
        await useDevicesStore.setState({
          fetchDevices: mockFetchDevices,
        });
      });

      await act(async () => {
        connectButton.click();
      });

      expect(mockAddDevice).toHaveBeenCalledWith({
        syncTimeOnErrorMs: 500,
      });
      expect(mockAddToast).toHaveBeenCalledWith({
        type: "success",
        message: "Device added successfully",
      });
      expect(mockGoBackToDeviceList).toHaveBeenCalledWith();
      expect(mockFetchDevices).toHaveBeenCalledWith();
    });
  });
});
