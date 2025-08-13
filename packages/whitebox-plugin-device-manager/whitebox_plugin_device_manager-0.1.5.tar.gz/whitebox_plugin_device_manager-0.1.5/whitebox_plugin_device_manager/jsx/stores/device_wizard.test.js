import { act } from "@testing-library/react";
import useDeviceWizardStore from "./device_wizard";

import moxios from "moxios";

const { api, toasts } = Whitebox;

describe("DeviceWizardStore", () => {
  describe("page navigation", () => {
    it("should have a clean default state", () => {
      const state = useDeviceWizardStore.getState();

      expect(state.pageNumber).toBe(0);
      expect(state.supportedDevices).toBe(null);
      expect(state.selectedDeviceCodename).toBe(null);
      expect(state.selectedConnectionType).toBe(null);
    });

    it("should allow navigating with nextPage", () => {
      // GIVEN the default state
      const getState = useDeviceWizardStore.getState;
      expect(getState().pageNumber).toBe(0);

      // WHEN calling nextPage
      act(() => getState().nextPage());

      // THEN the page number should be updated
      expect(getState().pageNumber).toBe(1);

      // even multiple times
      act(() => getState().nextPage());
      expect(getState().pageNumber).toBe(2);
    });

    it("should allow updating the page number with setPageNumber", () => {
      // GIVEN the default state
      const getState = useDeviceWizardStore.getState;
      expect(getState().pageNumber).toBe(0);

      // WHEN calling setPageNumber
      const targetPage = 2;
      act(() => getState().setPageNumber(targetPage));

      // THEN the page number should be updated
      expect(getState().pageNumber).toBe(targetPage);
    });

    it("should allow going back to device list", () => {
      // GIVEN any page state
      const getState = useDeviceWizardStore.getState;
      act(() => getState().setPageNumber(12));

      // WHEN calling goBackToDeviceList
      act(() => getState().goBackToDeviceList());

      // THEN the page number should point to beginning
      expect(getState().pageNumber).toBe(0);
    });

    it("should allow going back to device selection", () => {
      // GIVEN any page state
      const getState = useDeviceWizardStore.getState;
      act(() => getState().setPageNumber(12));

      // WHEN calling goBackToDeviceSelection
      act(() => getState().goBackToDeviceSelection());

      // THEN the page number should point to device selection
      expect(getState().pageNumber).toBe(1);
    });
  });

  describe("device setup", () => {
    beforeEach(async () => {
      // import and pass your custom axios instance to this method
      moxios.install(api.client);

      // set up the supported devices
      await moxios.wait(() => {
        const request = moxios.requests.mostRecent();
        request.respondWith({ status: 200, response: mockDeviceListResponse });
      });

      const getState = useDeviceWizardStore.getState;
      await act(async () => await getState().fetchSupportedDevices());
    });

    afterEach(() => {
      // import and pass your custom axios instance to this method
      moxios.uninstall(api.client);
    });

    it("should fetch supported devices", async () => {
      // GIVEN there are devices that the API will return
      const getState = useDeviceWizardStore.getState;

      const mockResponse = {
        supported_devices: [
          {
            codename: "insta360x4",
            name: "Insta360 X4",
            connection_types: ["wifi"],
          },
        ],
      };

      await moxios.wait(() => {
        const request = moxios.requests.mostRecent();
        request.respondWith({ status: 200, response: mockResponse });
      });

      // WHEN calling fetchSupportedDevices
      await act(async () => getState().fetchSupportedDevices());

      // THEN supported devices should be updated
      expect(getState().supportedDevices).toEqual(
        mockResponse.supported_devices
      );
    });

    it("should allow adding a new device", async () => {
      // GIVEN the pending device information added by user
      const getState = useDeviceWizardStore.getState;

      const deviceCodename = "insta360x4";
      const connectionType = "wifi";
      const connectionDetails = {
        ssid: "ISS airlock node #3",
        password: "such-password-many-security-wow",
      };

      await act(async () => {
        getState().setSelectedDeviceCodename(deviceCodename);
        getState().setSelectedConnectionType(connectionType);
        getState().updateConnectionDetails({ ...connectionDetails });
      });

      // WHEN calling addDevice
      await moxios.wait(() => {
        // Merely mock the response to return 200 so we can evaluate the request
        moxios.requests.mostRecent().respondWith({ status: 200 });
      });
      await act(async () => await getState().addDevice({}));

      // THEN the device creation request should be sent
      const expectedUrl = api.getPluginProvidedPath(
        "device.device-connection-management"
      );

      const request = moxios.requests.mostRecent();
      expect(request.config.url).toEqual(expectedUrl);
      expect(request.config.method).toEqual("post");
      expect(JSON.parse(request.config.data)).toMatchObject({
        codename: deviceCodename,
        connection_type: connectionType,
        connection_settings: connectionDetails,
      });
    });

    it("should not reset connection details when a user selects the same connection type", async () => {
      // GIVEN a selected device, and some connection details
      const getState = useDeviceWizardStore.getState;

      const deviceCodename = "insta360x4";
      const connectionType = "wifi";
      const connectionDetails = {
        ssid: "ISS airlock node #3",
        password: "such-password-many-security-wow",
      };

      await act(async () => {
        getState().setSelectedDeviceCodename(deviceCodename);
        getState().setSelectedConnectionType(connectionType);
        getState().updateConnectionDetails({ ...connectionDetails });
      });

      // WHEN selecting the same device again
      await act(async () =>
        getState().setSelectedConnectionType(connectionType)
      );

      // THEN the connection details should not be reset
      expect(getState().connectionDetails).toEqual(connectionDetails);
    });
  });

  describe("error handling", () => {
    const mockAddToast = vi.fn();

    beforeEach(async () => {
      // import and pass your custom axios instance to this method
      moxios.install(api.client);

      // set up the supported devices
      await moxios.wait(() => {
        const request = moxios.requests.mostRecent();
        request.respondWith({ status: 200, response: mockDeviceListResponse });
      });

      const getState = useDeviceWizardStore.getState;
      await act(async () => {
        await toasts.useToastsStore.setState({
          addToast: mockAddToast,
        });

        await getState().fetchSupportedDevices();
        await getState().setSelectedDeviceCodename("insta360x4");
        await getState().setSelectedConnectionType("wifi");
      });
    });

    it("should emit a toast on failure to fetch supported devices", async () => {
      // GIVEN the API will return an error
      const getState = useDeviceWizardStore.getState;

      await moxios.wait(() => {
        const request = moxios.requests.mostRecent();
        request.respondWith({ status: 500 });
      });

      // WHEN calling fetchSupportedDevices
      await act(async () => getState().fetchSupportedDevices());

      // THEN a toast should be emitted
      expect(mockAddToast).toHaveBeenCalledWith({
        message: `Could not fetch supported devices, try refreshing the page. If
                  that does not succeed, please try turning Whitebox off and on`,
        type: "error",
      });
    });

    it("should emit a toast on server failure while adding a device", async () => {
      // GIVEN the API will return an error
      const getState = useDeviceWizardStore.getState;

      await moxios.wait(() => {
        const request = moxios.requests.mostRecent();
        request.respondWith({ status: 500 });
      });

      // WHEN calling addDevice
      await act(async () => getState().addDevice({}));

      // THEN a toast should be emitted
      expect(mockAddToast).toHaveBeenCalledWith({
        message: "An error occurred while adding the device, please try again",
        type: "error",
      });
    });

    it("should store form errors on validation failure while adding a device", async () => {
      // GIVEN the API will return an error
      const getState = useDeviceWizardStore.getState;

      const mockResponse = {
        connection_settings: {
          ssid: ["SSID is required"],
          password: ["Password is required"],
        },
      };

      await moxios.wait(() => {
        const request = moxios.requests.mostRecent();
        request.respondWith({ status: 400, response: mockResponse });
      });

      // WHEN calling addDevice
      await act(async () => getState().addDevice({}));

      // THEN form errors should be updated
      expect(getState().formErrors).toEqual({
        ssid: "SSID is required",
        password: "Password is required",
      });
    });

    it("should remove an existing error on a field when field value gets changed", async () => {
      // GIVEN there is an existing error on a field
      const fieldName = "ssid";

      const getState = useDeviceWizardStore.getState;
      await act(async () => {
        await useDeviceWizardStore.setState({
          formErrors: {
            [fieldName]: "SSID is required",
          },
        });
      });

      // WHEN changing the value of the field
      await act(async () =>
        getState().updateConnectionDetails({ [fieldName]: "new value" })
      );

      // THEN form errors should be updated
      expect(getState().formErrors).toEqual({});
    });
  });
});

const mockDeviceList = [
  {
    codename: "insta360x4",
    name: "Insta360 X4",
    connection_types: ["wifi"],
  },
];

const mockDeviceListResponse = {
  supported_devices: mockDeviceList,
};
