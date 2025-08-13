import ModalPage from "./common/ModalPage";
import ModalFooterButtons from "./common/ModalFooterButtons";
import ModalTopNav from "./common/scaffolding/ModalTopNav";
import useDeviceWizardStore from "./stores/device_wizard";
import useDevicesStore from "./stores/devices";

const { importWhiteboxComponent, utils, toasts, DynamicContentRenderer } =
  Whitebox;

const Button = importWhiteboxComponent("ui.button");

// region assets
const IconEclipse = importWhiteboxComponent("icons.eclipse");
const IconArrowLeft = importWhiteboxComponent("icons.arrow-back");
const IconClose = importWhiteboxComponent("icons.close");
// endregion assets

const StepContent = () => {
  const stepHtmlTemplate = useDeviceWizardStore((state) =>
    state.getDeviceStepTemplate()
  );

  return (
    <DynamicContentRenderer
      className="flex flex-col self-stretch items-center gap-4 text-center"
      html={stepHtmlTemplate}
      includeSlots
    />
  );
};

const ScreenTopNav = () => {
  const isIdle = useDeviceWizardStore((state) => state.isIdle());

  const goBackToDeviceSelection = useDeviceWizardStore(
    (state) => state.goBackToDeviceSelection
  );
  const goBackToDeviceList = useDeviceWizardStore(
    (state) => state.goBackToDeviceList
  );

  const backButton = (
    <Button
      leftIcon={<IconArrowLeft />}
      disabled={!isIdle}
      onClick={goBackToDeviceSelection}
      key="backButton"
    />
  );
  const closeButton = (
    <Button
      leftIcon={<IconClose />}
      disabled={!isIdle}
      onClick={goBackToDeviceList}
      key="closeButton"
    />
  );

  const leadingButtons = [backButton];
  const trailingButtons = [closeButton];

  return (
    <ModalTopNav
      text="Device connection checklist"
      leadingButtons={leadingButtons}
      trailingButtons={trailingButtons}
    />
  );
};

const FooterElement = ({ element }) => {
  // Fetch state to ensure component is re-rendered when state changes
  useDeviceWizardStore((state) => state.getDeviceSetupStep());

  const fetchDevices = useDevicesStore((state) => state.fetchDevices);

  const isIdle = useDeviceWizardStore((state) => state.isIdle());
  const addDevice = useDeviceWizardStore((state) => state.addDevice);

  const goBackToDeviceList = useDeviceWizardStore(
    (state) => state.goBackToDeviceList
  );

  const nextStep = useDeviceWizardStore((state) => state.nextPage);
  const setDeviceSetupStep = useDeviceWizardStore(
    (state) => state.setDeviceSetupStep
  );

  const actionSkipToEnd = () => setDeviceSetupStep(4);
  const actionGoBack = () => setDeviceSetupStep(0);
  const actionNext = () => nextStep();

  const action2OnClickMap = {
    WIZARD_ADD_DEVICE: async () => {
      if (!isIdle) return;

      const success = await addDevice({ syncTimeOnErrorMs: 500 });

      if (!success) return;

      toasts.success({
        message: `Device added successfully`,
      });
      fetchDevices(); // Ensure the device list is up-to-date
      goBackToDeviceList();
    },
    WIZARD_STEP_INITIAL: actionGoBack,
    WIZARD_STEP_NEXT: actionNext,
    WIZARD_STEP_LAST: actionSkipToEnd,
  };

  const action2PropsMap = {
    WIZARD_ADD_DEVICE: {
      isLoading: !isIdle,
    },
    WIZARD_STEP_INITIAL: {
      disabled: !isIdle,
    },
  };

  return {
    text: element.config.text,
    onClick: action2OnClickMap[element.config.action],
    ...action2PropsMap[element.config.action],
  };
};

const Footer = () => {
  const stepConfig = useDeviceWizardStore((state) =>
    state.getWizardStepConfig()
  );

  const leftButton =
    stepConfig.actions?.left &&
    FooterElement({ element: stepConfig.actions.left });

  const rightButton =
    stepConfig.actions?.right &&
    FooterElement({ element: stepConfig.actions.right });

  return (
    <div className="mt-auto self-stretch">
      <ModalFooterButtons bckBtn={leftButton} fwdBtn={rightButton} />
    </div>
  );
};

const WizardStepIndicator = () => {
  const deviceConfig = useDeviceWizardStore((state) =>
    state.getSelectedDeviceConfig()
  );
  const wizardSteps = deviceConfig?.wizard_steps;

  const totalSteps = wizardSteps?.length;
  const stepNumber = useDeviceWizardStore((state) =>
    state.getDeviceSetupStep()
  );
  const setStepNumber = useDeviceWizardStore(
    (state) => state.setDeviceSetupStep
  );

  return (
    <div className="c_wizard_step_indicator flex items-center gap-3">
      {Array.from({ length: totalSteps }, (_, index) => {
        const isActive = index === stepNumber;
        const className = utils.getClasses(
          "c_wizard_step_indicator_item",
          "w-2",
          isActive
            ? "fill-surface-primary"
            : "fill-borders-default cursor-pointer"
        );

        return (
          <IconEclipse
            key={index}
            onClick={() => setStepNumber(index)}
            className={className}
          />
        );
      })}
    </div>
  );
};

const Screen = () => {
  return (
    <div className="flex flex-col h-full overflow-y-scroll-hidden">
      <div
        className="flex flex-col flex-1 self-stretch items-center
                        px-6 gap-4 overflow-y-scroll-hidden"
      >
        <div className="text-high-emphasis">
          <p>Complete the checklist</p>
        </div>

        <StepContent />
        <WizardStepIndicator />
      </div>

      <Footer />
    </div>
  );
};

const WizardPageDeviceConnection = () => {
  const topNav = <ScreenTopNav />;

  return (
    <ModalPage topNav={topNav}>
      <Screen />
    </ModalPage>
  );
};

export default WizardPageDeviceConnection;
