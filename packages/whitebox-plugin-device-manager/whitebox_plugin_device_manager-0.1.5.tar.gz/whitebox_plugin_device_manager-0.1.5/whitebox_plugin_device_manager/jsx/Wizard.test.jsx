import { screen, act, cleanup } from "@testing-library/react";
import moxios from "moxios";
import Wizard from "./Wizard";
import useDeviceWizardStore from "./stores/device_wizard";
import {
  fixtureSupportedDevices,
  fixtureSupportedDeviceCodename1,
} from "./__fixtures__/devices";

const { api } = Whitebox;
const { utils } = WhiteboxTest;

afterEach(cleanup);

describe("Wizard", () => {
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

    await act(async () => await getWizardStoreState().fetchSupportedDevices());
    await act(async () =>
      getWizardStoreState().setSelectedDeviceCodename(
        fixtureSupportedDeviceCodename1
      )
    );
  });

  afterEach(() => {
    moxios.uninstall(api.client);
  });

  it("should render first page upon initial render", async () => {
    utils.renderWithRouter(<Wizard />);

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(screen.getByText("Let's get you set up")).toBeInTheDocument();
  });

  it.each([0, 1, 2, 3, 4, 5])(
    "should render appropriate page per DeviceWizardStore state",
    async (pageNo) => {
      act(() => getWizardStoreState().setPageNumber(pageNo));

      utils.renderWithRouter(<Wizard />);

      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0));
      });

      let lookupText;
      if (pageNo === 0) lookupText = "Let's get you set up";
      else if (pageNo === 1) lookupText = "Select a device";
      else if (pageNo >= 2 && pageNo <= 5)
        lookupText = "Device connection checklist";

      expect(screen.getByText(lookupText)).toBeInTheDocument();
    }
  );
});
