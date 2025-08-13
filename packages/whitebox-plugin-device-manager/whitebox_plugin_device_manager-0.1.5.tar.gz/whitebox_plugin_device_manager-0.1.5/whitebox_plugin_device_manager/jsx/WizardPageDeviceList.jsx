import ModalPage from "./common/ModalPage";
import ModalFooterButtons from "./common/ModalFooterButtons";
import DeviceConnection from "./common/DeviceConnection";
import useDeviceWizardStore from "./stores/device_wizard";
import useDevicesStore from "./stores/devices";

const { importWhiteboxComponent, SlotLoader, utils, toasts, useNavigate } =
  Whitebox;
const TertiaryButton = importWhiteboxComponent("ui.button-tertiary");

// region assets
const LogoWhiteOnBlack = importWhiteboxComponent("icons.logo-white-on-black");
const IconImportExport = importWhiteboxComponent("icons.import-export");
const IconCameraDevice = importWhiteboxComponent("icons.camera-device");
const IconChevronRight = importWhiteboxComponent("icons.chevron-right");
const IconInfo = importWhiteboxComponent("icons.info");
// endregion assets

const Heading = () => {
  return (
    <div className="flex flex-col items-center gap-4 self-stretch">
      <LogoWhiteOnBlack />

      <div
        className="flex flex-col justify-center items-center gap-2
                        self-stretch text-center"
      >
        <p className="text-2xl font-bold">Let&#39;s get you set up</p>
        <p className="text-full-emphasis text-opacity-50 leading-snug">
          To get the best experience, we recommend setting up at least one
          device. This is necessary for us to have a source to generate data.
        </p>
      </div>
    </div>
  );
};

const HostDevices = () => {
  return (
    <div
      className="flex flex-col items-center justify-center
                      self-stretch gap-2 md:gap-3"
    >
      <DeviceConnection deviceName="The screen you're looking at" isConnected />

      <IconImportExport className="fill-medium-emphasis" />

      <DeviceConnection deviceName="Whitebox #1337" isConnected />

      <SlotLoader name="device-status.gps" />
      <SlotLoader name="device-status.sdr" />
    </div>
  );
};

const NoDevicesBanner = () => {
  const deviceFetchState = useDevicesStore((state) => state.fetchState);

  const infoText =
    deviceFetchState === "initial" ? (
      <p className="text-full-emphasis">Loading devices...</p>
    ) : deviceFetchState === "loaded" ? (
      <>
        <p className="font-semibold text-full-emphasis">No installed devices</p>

        <p className="text-high-emphasis">
          You don’t have any installed devices, try adding one.
        </p>
      </>
    ) : (
      <p className="text-error">
        {/* FixMe: UX-REVISIT
                   ERROR-HANDLING
                   More info: #116 */}
        Error loading devices
      </p>
    );

  return (
    <div className="flex flex-col items-center gap-4 self-stretch">
      <IconCameraDevice />

      <div
        className="flex flex-col gap-0.75 align-middle self-stretch
                        text-center leading-snug"
      >
        {infoText}
      </div>

      <div
        className="flex gap-3 rounded-full px-2 py-1 items-center
                        bg-x-low-emphasis text-high-emphasis
                        self-stretch
                        md:self-auto"
      >
        <IconInfo />

        <p className="leading-snug flex-1">
          Bringing devices onboard: What to know
        </p>
      </div>
    </div>
  );
};

const ConnectedDevices = () => {
  const devices = useDevicesStore((state) => state.devices);

  const isLoading = devices === null;
  if (!devices?.length) return <NoDevicesBanner isLoading={isLoading} />;

  const deviceComponents = devices.map((device, index) => {
    const deviceIsConnected = Boolean(index % 2);

    const action = <TertiaryButton leftIcon={<IconChevronRight />} />;

    const iconUrl = utils.buildStaticUrl(device.device_type_icon_url);
    const icon = <img src={iconUrl} alt={device.name} />;

    return (
      <DeviceConnection
        key={index}
        deviceName={device.name}
        isConnected={deviceIsConnected}
        icon={icon}
        action={action}
      />
    );
  });

  return (
    <div className="flex flex-1 flex-col items-center self-stretch gap-2">
      <IconImportExport className="fill-medium-emphasis" />

      <p className="text-full-emphasis">
        Installed devices ({devices.length}/10)
      </p>

      {deviceComponents}
    </div>
  );
};

const DeviceList = () => {
  return (
    <div className="flex flex-col self-stretch gap-4">
      <HostDevices />
      <ConnectedDevices />
    </div>
  );
};

const Footer = () => {
  const navigate = useNavigate();
  const fwdBtnHandler = useDeviceWizardStore((state) => state.nextPage);

  return (
    <div className="mt-auto">
      <ModalFooterButtons
        fwdBtn={{
          text: "Add device",
          onClick: () => fwdBtnHandler(),
        }}
        bckBtn={{
          text: "Skip",
          onClick: () => {
            toasts.info({
              message: `User decided to skip device setup at ${Date.now()}.
                      This message will expire in 5 seconds.`,
              timeout: 5,
            });
            toasts.success({
              message: "User decided to skip device setup at " + Date.now(),
            });
            toasts.error({
              message: "User decided to skip device setup at " + Date.now(),
            });
            navigate("/dashboard");
          },
        }}
        fullWidth
      />
    </div>
  );
};

const Screen = () => {
  return (
    <div className="flex flex-col h-full overflow-y-scroll-hidden">
      <div
        className="flex flex-col flex-1 self-stretch items-center
                        px-6 py-4 gap-8 overflow-y-scroll-hidden"
      >
        <Heading />
        <DeviceList />
      </div>
      <Footer />
    </div>
  );
};

const WizardPageDeviceList = () => {
  return (
    <ModalPage>
      <Screen />
    </ModalPage>
  );
};

export default WizardPageDeviceList;
