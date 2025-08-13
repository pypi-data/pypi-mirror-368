import { create } from "zustand";

const { api, toasts } = Whitebox;

const deviceWizardStore = (set, get) => ({
  // region wizard rendering

  pageNumber: 0,

  nextPage: () => set((state) => ({ pageNumber: state.pageNumber + 1 })),
  setPageNumber: (pageNumber) => set({ pageNumber }),

  goBackToDeviceList: () => set({ pageNumber: 0 }),
  goBackToDeviceSelection: () => set({ pageNumber: 1 }),

  getRenderTarget: () => {
    const pageNumber = get().pageNumber;

    if (pageNumber === 0) {
      return "device-list";
    }

    if (pageNumber === 1) {
      return "device-selection";
    }

    return "device-connection";
  },

  // endregion wizard rendering

  // region device-specific

  supportedDevices: null,

  selectedDeviceCodename: null,
  selectedConnectionType: null,

  fetchSupportedDevices: async () => {
    let data;

    const url = api.getPluginProvidedPath("device.supported-device-list");

    try {
      const response = await api.client.get(url);
      data = await response.data;
    } catch {
      // FixMe: UX-REVISIT
      //        ERROR-HANDLING
      //        More info: #116
      toasts.error({
        message: `Could not fetch supported devices, try refreshing the page. If
                  that does not succeed, please try turning Whitebox off and on`,
      });
      return false;
    }

    set({ supportedDevices: data.supported_devices });
    return true;
  },

  getDeviceSetupStep: () => get().pageNumber - 2,
  setDeviceSetupStep: (stepNumber) => set({ pageNumber: stepNumber + 2 }),

  getDeviceStepTemplate: () => {
    const stepConfig = get().getWizardStepConfig();
    return stepConfig?.template;
  },

  getSelectedDeviceCodename: () => get().selectedDeviceCodename,
  setSelectedDeviceCodename: (selectedDeviceCodename) =>
    set({ selectedDeviceCodename }),

  getSelectedDeviceConfig: () => {
    const deviceCodename = get().getSelectedDeviceCodename();
    const supportedDevices = get().supportedDevices;
    const device = supportedDevices.find(
      (device) => device.codename === deviceCodename
    );
    return device;
  },

  getConnectionTypes: () => {
    const device = get().getSelectedDeviceConfig();
    return device?.connection_types;
  },

  getSelectedConnectionType: () => {
    let connectionType = get().selectedConnectionType;

    if (!connectionType) {
      connectionType = Object.keys(get().getConnectionTypes())[0];
    }

    return connectionType;
  },

  setSelectedConnectionType: (selectedConnectionType) => {
    // Do not reset or change anything if the selected one is still the same
    if (get().selectedConnectionType === selectedConnectionType) {
      return;
    }

    set({
      selectedConnectionType,
      // Reset it upon change
      connectionDetails: {},
    });
  },

  getWizardSteps: () => {
    const device = get().getSelectedDeviceConfig();
    return device?.wizard_steps;
  },

  getWizardStepConfig: () => {
    const wizardSteps = get().getWizardSteps();
    const stepNumber = get().getDeviceSetupStep();
    return wizardSteps[stepNumber];
  },

  getConnectionParameters: () => {
    const device = get().getSelectedDeviceConfig();
    const selectedConnectionType = get().getSelectedConnectionType();
    return device?.connection_types[selectedConnectionType];
  },
  // endregion device-specific

  // region device connection
  status: "idle",
  connectionDetails: {},
  formErrors: {},

  isIdle: () => get().status === "idle",

  updateConnectionDetails({ ...details }) {
    set((state) => {
      let errors = state.formErrors;

      // When a user changes a field, remove the error message if present
      Object.keys(details).forEach((key) => {
        if (key in errors) {
          // eslint-disable-next-line no-unused-vars
          let { [key]: _, ...strippedErrors } = errors;
          errors = strippedErrors;
        }
      });

      return {
        connectionDetails: { ...state.connectionDetails, ...details },
        formErrors: errors,
      };
    });
  },

  addDevice: async ({ syncTimeOnErrorMs = 0 }) => {
    const { selectedDeviceCodename, connectionDetails } = get();
    const selectedConnectionType = get().getSelectedConnectionType();

    const syncErrorPromise = new Promise((resolve) => {
      setTimeout(resolve, syncTimeOnErrorMs);
    });

    const payload = {
      codename: selectedDeviceCodename,
      connection_type: selectedConnectionType,
      connection_settings: connectionDetails,
    };

    const url = api.getPluginProvidedPath("device.device-connection-management");

    set({ status: "connecting" });

    try {
      await api.client.post(url, payload);
      return true;
    } catch (error) {
      // If timeout was provided, ensure the errors are shown after the timeout
      // to avoid flickering across screens
      await syncErrorPromise;

      // If there is a network error or the server is down, show a generic error
      if (api.isServerError(error)) {
        // FixMe: UX-REVISIT
        //        ERROR-HANDLING
        //        More info: #116
        toasts.error({
          message:
            "An error occurred while adding the device, please try again",
        });
        return false;
      }

      // Otherwise, add the error messages to appropriate fields
      const data = error.response?.data;
      const connectionErrors = data?.connection_settings;

      // DRF returns errors in a list, even if there's one element. We want to
      // display the first error from the list within the forms
      const errors = {};
      Object.entries(connectionErrors).forEach(([fieldName, fieldErrors]) => {
        errors[fieldName] = fieldErrors[0];
      });
      set({ formErrors: errors });

      return false;
    } finally {
      set({ status: "idle" });
    }
  },
  // endregion device connection
});

const useDeviceWizardStore = create(deviceWizardStore);

export default useDeviceWizardStore;
