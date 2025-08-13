const { importWhiteboxComponent } = Whitebox;
const Button = importWhiteboxComponent("ui.button");
const IconLink = importWhiteboxComponent("icons.link");
const IconEclipse = importWhiteboxComponent("icons.eclipse");

const DeviceStatus = ({ isConnected }) => {
  const badgeColor = isConnected ? "fill-success" : "fill-error";

  return (
    <span className="inline-flex items-center gap-1">
      <IconEclipse className={"h-1.5 w-1.5 " + badgeColor} />
      {isConnected ? "Connected" : "Disconnected"}
    </span>
  );
};

const DeviceConnection = ({ deviceName, isConnected, icon, action = null }) => {
  const deviceIcon = icon || <IconLink />;

  return (
    <div
      className="c_device_connection
                      flex p-4 items-center gap-4 self-stretch
                      border border-solid border-borders-default rounded-full"
    >
      <div className="">
        <Button
          typeClass="btn-secondary"
          leftIcon={deviceIcon}
          className="bg-x-low-emphasis"
        />
      </div>

      <div className="flex flex-col items-start gap-1 flex-1">
        <span className="text-full-emphasis font-bold leading-tight">
          {deviceName}
        </span>

        <DeviceStatus isConnected={isConnected} />
      </div>

      {action && <div className="">{action}</div>}
    </div>
  );
};

export { DeviceConnection };
export default DeviceConnection;
