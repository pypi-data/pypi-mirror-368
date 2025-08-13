import { useState } from "react";
import ModalPage from "./common/ModalPage";
import ModalTopNav from "./common/scaffolding/ModalTopNav";
import useDeviceWizardStore from "./stores/device_wizard";

const { importWhiteboxComponent, utils } = Whitebox;
const Button = importWhiteboxComponent("ui.button");
const InputContentArea = importWhiteboxComponent("ui.input-content-area");

// region assets
const IconSearch = importWhiteboxComponent("icons.search");
const IconClose = importWhiteboxComponent("icons.close");
// endregion assets

const DeviceOption = ({ codename, deviceName, deviceImageUrl }) => {
  const nextPage = useDeviceWizardStore((state) => state.nextPage);
  const setSelectedDeviceCodename = useDeviceWizardStore(
    (state) => state.setSelectedDeviceCodename
  );

  const onDeviceClick = () => {
    setSelectedDeviceCodename(codename);
    nextPage();
  };

  return (
    <div className="c_device_option cursor-pointer" onClick={onDeviceClick}>
      <img
        src={deviceImageUrl}
        alt={deviceName}
        className="bg-x-low-emphasis rounded-3xl"
      />

      <p className="self-stretch text-center">{deviceName}</p>
    </div>
  );
};

const Search = () => {
  const supportedDevices = useDeviceWizardStore(
    (state) => state.supportedDevices
  );
  const [searchQuery, setSearchQuery] = useState("");

  let filteredDevices = supportedDevices;
  if (searchQuery) {
    filteredDevices = supportedDevices?.filter((device) => {
      const lookup = searchQuery.toLowerCase().replaceAll(" ", "");
      const against = device.device_name.toLowerCase().replaceAll(" ", "");
      return against.includes(lookup);
    });
  }

  const searchIcon = (
    <div className="w-6 h-6">
      <IconSearch className="fill-medium-emphasis" />
    </div>
  );

  return (
    <div className="flex flex-col items-center gap-6">
      <p className="text-center text-high-emphasis text-opacity-50 leading-snug">
        Select the type of device you want to connect. These are the devices
        currently compatible with Whitebox.
      </p>

      <div
        className="flex flex-col items-start gap-4 self-stretch
                        "
      >
        <div className="flex flex-col self-stretch ">
          <InputContentArea
            leftIcon={searchIcon}
            placeholder="Search for devices..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex flex-col justify-center gap-2 items-center">
          {filteredDevices?.map((device) => (
            <DeviceOption
              key={device.codename}
              codename={device.codename}
              deviceName={device.device_name}
              deviceImageUrl={utils.buildStaticUrl(device.device_image_url)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const Screen = () => {
  return (
    <div
      className="flex flex-col flex-1 self-stretch items-center
                      px-6 py-8 gap-8 h-full overflow-y-scroll-hidden"
    >
      <Search />

      <div className="mt-auto text-high-emphasis">
        <p>More devices coming soon</p>
      </div>
    </div>
  );
};

const ScreenTopNav = () => {
  const goBackToDeviceList = useDeviceWizardStore(
    (state) => state.goBackToDeviceList
  );

  const closeButton = (
    <Button leftIcon={<IconClose />} onClick={goBackToDeviceList} key="close" />
  );
  const trailingButtons = [closeButton];

  return (
    <ModalTopNav text="Select a device" trailingButtons={trailingButtons} />
  );
};

const WizardPageDeviceSelection = () => {
  const topNav = <ScreenTopNav />;
  return (
    <ModalPage topNav={topNav}>
      <Screen />
    </ModalPage>
  );
};

export default WizardPageDeviceSelection;
