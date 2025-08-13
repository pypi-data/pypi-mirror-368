import { act, screen, render, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import moxios from "moxios";
import WizardPageDeviceSelection from "./WizardPageDeviceSelection";
import useDeviceWizardStore from "./stores/device_wizard";
import {
  fixtureSupportedDevices,
  fixtureSupportedDeviceName1,
  fixtureSupportedDeviceName2,
  fixtureSupportedDeviceCodename1,
} from "./__fixtures__/devices";

const { api } = Whitebox;

afterEach(cleanup);

describe("WizardPageDeviceSelection", () => {
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

    // This one immediately uses the prepared response mock from above,
    // so that test runs are not influenced
    const getDeviceWizardState = useDeviceWizardStore.getState;
    await act(async () => {
      await getDeviceWizardState().setPageNumber(1);
      await getDeviceWizardState().fetchSupportedDevices();
    });
  });

  afterEach(() => {
    moxios.uninstall(api.client);
  });

  describe("always", () => {
    it("should display supported devices", async () => {
      render(<WizardPageDeviceSelection />);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const device1 = screen.getByText(fixtureSupportedDeviceName1);
      expect(device1).toBeInTheDocument();

      const device2 = screen.queryByText(fixtureSupportedDeviceName2);
      expect(device2).toBeInTheDocument();
    });

    it("should allow selecting a device", async () => {
      const user = userEvent.setup();

      render(<WizardPageDeviceSelection />);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const deviceElement = screen.getByText(fixtureSupportedDeviceName1);
      expect(deviceElement).toBeInTheDocument();

      await user.click(deviceElement);

      const selectedDeviceCodename =
        getWizardStoreState().getSelectedDeviceCodename();

      expect(selectedDeviceCodename).toEqual(fixtureSupportedDeviceCodename1);
    });
  });

  describe("search", () => {
    it("should filter devices when search query is given", async () => {
      const user = userEvent.setup();

      render(<WizardPageDeviceSelection />);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const searchInput = screen.getByPlaceholderText("Search for devices...");

      const searchQuery = fixtureSupportedDeviceName1.slice(-2);
      await user.type(searchInput, searchQuery);
      await user.tab();

      const device1 = screen.getByText(fixtureSupportedDeviceName1);
      expect(device1).toBeInTheDocument();

      const device2 = screen.queryByText(fixtureSupportedDeviceName2);
      expect(device2).not.toBeInTheDocument();
    });
  });
});
