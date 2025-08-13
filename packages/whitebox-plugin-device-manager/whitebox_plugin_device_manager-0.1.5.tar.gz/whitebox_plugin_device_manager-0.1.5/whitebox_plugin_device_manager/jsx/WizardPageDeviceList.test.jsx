import { act, screen, cleanup } from "@testing-library/react";
import WizardPageDeviceList from "./WizardPageDeviceList";
import useDevicesStore from "./stores/devices";
import moxios from "moxios";
import useDeviceWizardStore from "./stores/device_wizard";

const { api } = Whitebox;
const { utils } = WhiteboxTest;

afterEach(cleanup);

describe("WizardPageDeviceList", () => {
  beforeEach(async () => {
    moxios.install(api.client);
  });

  afterEach(() => {
    moxios.uninstall(api.client);
  });

  describe("always", () => {
    it("should render the page, listing the host & client devices", async () => {
      utils.renderWithRouter(<WizardPageDeviceList />);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      // Check if the modal header is rendered
      const modalHeader = screen.getByText("Let's get you set up");
      expect(modalHeader).toBeInTheDocument();

      // Check if the primary devices are rendered
      const hostDevice = screen.getByText("Whitebox #1337");
      const clientDevice = screen.getByText("The screen you're looking at");

      expect(hostDevice).toBeInTheDocument();
      expect(clientDevice).toBeInTheDocument();

      // Check if the buttons are rendered
      const addDeviceButton = screen.getByText("Add device");
      const skipButton = screen.getByText("Skip");

      expect(addDeviceButton).toBeInTheDocument();
      expect(skipButton).toBeInTheDocument();
    });

    it("should allow adding new devices", async () => {
      utils.renderWithRouter(<WizardPageDeviceList />);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const addDeviceButton = screen.getByText("Add device");
      const getState = useDeviceWizardStore.getState;

      const currentPage = getState().pageNumber;
      expect(currentPage).toEqual(0);

      await act(async () => {
        addDeviceButton.click();
      });
      const newPage = getState().pageNumber;
      expect(newPage).toEqual(1);
    });
  });

  describe("no devices", () => {
    beforeEach(async () => {
      await moxios.wait(() => {
        const request = moxios.requests.mostRecent();
        request.respondWith({ status: 200, response: [] });
      });
    });

    it("should render the no devices banner", async () => {
      utils.renderWithRouter(<WizardPageDeviceList />);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      await act(async () => {
        const state = useDevicesStore.getState();
        await state.fetchDevices();
      });

      const addDeviceBanner = screen.getByText(
        "You don’t have any installed devices, try adding one."
      );
      expect(addDeviceBanner).toBeInTheDocument();

      const helpText = screen.getByText(
        "Bringing devices onboard: What to know"
      );
      expect(helpText).toBeInTheDocument();
    });
  });

  describe("with devices", () => {
    beforeEach(async () => {
      await moxios.wait(() => {
        const request = moxios.requests.mostRecent();
        request.respondWith({
          status: 200,
          response: [
            {
              id: 1,
              name: "Device 8999",
              codename: "insta360_x4",
            },
            {
              id: 2,
              name: "Device 9000",
              codename: "insta360_x4",
            },
          ],
        });
      });
    });

    it("should render the connected devices", async () => {
      await act(async () => {
        const state = useDevicesStore.getState();
        await state.fetchDevices();
      });

      utils.renderWithRouter(<WizardPageDeviceList />);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      // const deviceCounter = screen.getByText("Installed devices (2/10)")
      const firstDevice = screen.getByText("Device 8999");
      const secondDevice = screen.getByText("Device 9000");

      // expect(deviceCounter).toBeInTheDocument()
      expect(firstDevice).toBeInTheDocument();
      expect(secondDevice).toBeInTheDocument();
    });
  });

  describe("error handling", () => {
    it("should show an error message when fetching devices fails", async () => {
      await moxios.wait(() => {
        const request = moxios.requests.mostRecent();
        request.respondWith({ status: 500 });
      });

      await act(async () => {
        const state = useDevicesStore.getState();
        await state.fetchDevices();
      });

      utils.renderWithRouter(<WizardPageDeviceList />);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      const errorMessage = screen.getByText("Error loading devices");
      expect(errorMessage).toBeInTheDocument();
    });
  });
});
