import { create } from "zustand";

const { api } = Whitebox;

const devicesStore = (set) => ({
  fetchState: "initial",
  devices: null,

  fetchDevices: async () => {
    let data;

    const url = api.getPluginProvidedPath("device.device-connection-management");

    try {
      const response = await api.client.get(url);
      data = await response.data;
    } catch {
      set({ fetchState: "error" });
      return false;
    }

    set({
      devices: data,
      fetchState: "loaded",
    });
    return true;
  },
});

const useDevicesStore = create(devicesStore);

export default useDevicesStore;
