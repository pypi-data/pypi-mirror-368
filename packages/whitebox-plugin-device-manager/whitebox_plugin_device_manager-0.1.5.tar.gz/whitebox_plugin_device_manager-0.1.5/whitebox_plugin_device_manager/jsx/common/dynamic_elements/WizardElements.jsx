import useDeviceWizardStore from "../../stores/device_wizard";
import { DEInputText, DEInputPassword } from "./FieldElements";

const { utils } = Whitebox;

const prepareConnectionFields = (connectionParameters) => {
  const fieldConfig = connectionParameters?.fields;
  if (!fieldConfig) {
    return [];
  }

  return Object.entries(fieldConfig).map(([fieldName, fieldInfo]) => {
    return {
      type: `wizard_field_${fieldInfo.type}`,
      config: {
        name: fieldName,
        placeholder: fieldInfo.name,
        required: Boolean(fieldInfo.required),
        value: fieldInfo.default || "",
      },
    };
  });
};

const generateWrappedField = (WrappedComponent) => {
  const DEWizardWrappedField = ({ config, ...props }) => {
    const fieldName = config.name;

    const getter = useDeviceWizardStore(
      (state) => state.connectionDetails[fieldName]
    );

    const errorGetter = useDeviceWizardStore(
      (state) => state.formErrors[fieldName]
    );

    const setter = (value) =>
      useDeviceWizardStore.getState().updateConnectionDetails({
        [fieldName]: value,
      });

    return (
      <WrappedComponent
        config={config}
        getter={getter}
        setter={setter}
        errorGetter={errorGetter}
        {...props}
      />
    );
  };
  return DEWizardWrappedField;
};

const DEWizardFieldBlock = ({ config, ...props }) => {
  const connectionParameters = useDeviceWizardStore((state) =>
    state.getConnectionParameters()
  );

  const preparedFieldConfig = prepareConnectionFields(connectionParameters);
  const preparedFields = preparedFieldConfig.map((field, index) => {
    const dynamicProps = {
      config: field,
      index,
    };

    return utils.generateDynamicElement(dynamicProps);
  });

  const classes = utils.getGenericClassNames({ config, props });

  classes.push("flex flex-col self-stretch gap-6 md:gap-4");

  // Add a class to the form to make it easier to target in tests
  classes.push("connection_form");

  return <div className={utils.getClasses(...classes)}>{preparedFields}</div>;
};

const DEWizardInputText = generateWrappedField(DEInputText);
const DEWizardInputPassword = generateWrappedField(DEInputPassword);

utils.registerComponentMap({
  wizard_field_block: DEWizardFieldBlock,
  wizard_field_text: DEWizardInputText,
  wizard_field_password: DEWizardInputPassword,
});

export { DEWizardInputText, DEWizardInputPassword, DEWizardFieldBlock };
