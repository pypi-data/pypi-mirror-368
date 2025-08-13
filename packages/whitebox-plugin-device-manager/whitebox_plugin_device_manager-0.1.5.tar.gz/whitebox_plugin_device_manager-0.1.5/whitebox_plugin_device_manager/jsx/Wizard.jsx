import { useEffect } from "react";
import useDeviceWizardStore from "./stores/device_wizard";
import useDevicesStore from "./stores/devices";
import WizardPageDeviceList from "./WizardPageDeviceList";
import WizardPageDeviceSelection from "./WizardPageDeviceSelection";
import WizardPageDeviceConnection from "./WizardPageDeviceConnection";
import "./common/dynamic_elements/FieldElements";
import "./common/dynamic_elements/WizardElements";

const WizardContainer = () => {
  const renderTarget = useDeviceWizardStore((state) => state.getRenderTarget());

  if (renderTarget === "device-selection") return <WizardPageDeviceSelection />;

  if (renderTarget === "device-connection")
    return <WizardPageDeviceConnection />;

  return <WizardPageDeviceList />;
};

const Wizard = () => {
  const fetchDevices = useDevicesStore((state) => state.fetchDevices);
  const fetchSupportedDevices = useDeviceWizardStore(
    (state) => state.fetchSupportedDevices
  );

  useEffect(() => {
    fetchSupportedDevices();
    fetchDevices();
  }, []);

  return <WizardContainer />;
};

export { Wizard };
export default Wizard;
