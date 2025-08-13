import { useState } from "react";

const { importWhiteboxComponent, utils } = Whitebox;
const IconEye = importWhiteboxComponent("icons.eye");
const InputContentArea = importWhiteboxComponent("ui.input-content-area");

const DEInputText = ({
  config,
  getter,
  setter,
  errorGetter = null,
  ...props
}) => {
  const classes = utils.getGenericClassNames({ config, props });

  if (errorGetter) {
    props.borderClass = "border-warning";
  }

  const placeholder = config.placeholder;

  const fieldLabel = getter && (
    <div
      className="flex items-start px-2 py-1 bg-white
                      absolute left-3 top-[-0.625rem]"
    >
      <p className="text-high-emphasis text-xs">{placeholder}</p>
    </div>
  );

  const messages = errorGetter && (
    <div className="px-4">
      <p className="c_field_error text-warning">{errorGetter}</p>
    </div>
  );

  return (
    <div className="c_input_field flex flex-col items-start gap-1 relative">
      <div className="flex flex-col items-start self-stretch">
        <InputContentArea
          className={utils.getClasses(...classes)}
          name={config.name}
          placeholder={placeholder}
          value={getter}
          onChange={(e) => setter(e.currentTarget.value)}
          required={config.required}
          {...props}
        />
        {fieldLabel}
      </div>
      {messages}
    </div>
  );
};

const DEInputPassword = ({ config, ...props }) => {
  const [showPassword, setShowPassword] = useState(false);

  const iconClassName = utils.getClasses(
    "w-6 h-6 cursor-pointer",
    showPassword ? "fill-high-emphasis" : "fill-medium-emphasis"
  );

  props.type = showPassword ? "text" : "password";
  props.rightIcon = (
    <IconEye
      className={iconClassName}
      onClick={() => setShowPassword((value) => !value)}
    />
  );

  return <DEInputText config={config} {...props} />;
};

utils.registerComponentMap({
  field_text: DEInputText,
  field_password: DEInputPassword,
});

export { DEInputText, DEInputPassword };
