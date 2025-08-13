const { importWhiteboxComponent } = Whitebox;
const PrimaryButton = importWhiteboxComponent("ui.button-primary");
const SecondaryButton = importWhiteboxComponent("ui.button-secondary");

const ModalFooterButtons = ({
  fwdBtn = null,
  bckBtn = null,
  fullWidth = false,
}) => {
  const additionalClassNames = fullWidth ? "flex-1" : "";

  return (
    <div
      className="c_modal_footer_buttons
                      flex p-4 gap-4 self-stretch justify-between
                      border-t border-solid border-borders-default"
    >
      {bckBtn && (
        <SecondaryButton
          key="bckBtn"
          {...bckBtn}
          className={additionalClassNames}
        />
      )}

      {fwdBtn && (
        <PrimaryButton
          key="fwdBtn"
          {...fwdBtn}
          className={additionalClassNames}
        />
      )}
    </div>
  );
};

export default ModalFooterButtons;
