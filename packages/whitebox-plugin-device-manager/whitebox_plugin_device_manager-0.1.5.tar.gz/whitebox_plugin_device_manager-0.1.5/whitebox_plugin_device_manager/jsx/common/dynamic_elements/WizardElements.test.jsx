// Make sure to import these before importing anything specific so that the
// registry gets populated in time
import "./FieldElements.jsx";
import "./WizardElements.jsx";

import moxios from "moxios";
import { act, render, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import useDeviceWizardStore from "../../stores/device_wizard.js";

const { api, utils } = Whitebox;

afterEach(cleanup);

const fixtureSupportedDevicesWithAllFields = {
  supported_devices: [
    {
      codename: "device_1",
      name: "Device 1",
      connection_types: {
        test_type: {
          name: "Test Type",
          fields: {
            text: {
              name: "Text Field",
              type: "text",
              required: false,
            },
            password: {
              name: "Password Field",
              type: "password",
              required: true,
            },
          },
        },
      },
      wizard_steps: [
        {
          type: "wizard_field_block",
          config: {},
        },
      ],
    },
  ],
};

describe("WizardElements", () => {
  const targetDevice =
    fixtureSupportedDevicesWithAllFields.supported_devices[0];
  const deviceConnectionFields = targetDevice.connection_types.test_type.fields;

  describe("DEWizardFieldBlock", () => {
    beforeEach(async () => {
      moxios.install(api.client);

      await moxios.wait(() => {
        const request = moxios.requests.mostRecent();
        request.respondWith({
          status: 200,
          response: fixtureSupportedDevicesWithAllFields,
        });
      });

      const getDeviceWizardState = useDeviceWizardStore.getState;
      await act(async () => {
        await getDeviceWizardState().fetchSupportedDevices();
        await getDeviceWizardState().setSelectedDeviceCodename("device_1");
        await getDeviceWizardState().setDeviceSetupStep(0);
      });
    });

    afterEach(() => {
      moxios.uninstall(api.client);
    });

    describe("rendering", () => {
      it("should render all fields properly", async () => {
        const index = 0;
        const config = targetDevice.wizard_steps[index];
        expect(config.type).toEqual("wizard_field_block");

        const ComponentToRender = utils.generateDynamicElement({
          config: config,
          index: index,
        });

        const { container } = render(ComponentToRender);

        await act(async () => {
          await new Promise((resolve) => setTimeout(resolve, 0));
        });

        const renderedFields = container.querySelectorAll(".c_generic_element");

        // One for parent block, plus fields
        const expectedFieldCount =
          1 + Object.keys(deviceConnectionFields).length;
        expect(renderedFields).toHaveLength(expectedFieldCount);

        // Convert NodeList to Array
        const renderedFieldsList = [...renderedFields];

        const fullFieldConfig = Object.entries(deviceConnectionFields);

        renderedFieldsList.forEach((field, index) => {
          if (index === 0) {
            // Skip the parent block
            return;
          }

          const lookupIndex = index - 1; // Skip the parent block
          const [fieldName, fieldConfig] = fullFieldConfig[lookupIndex];

          switch (fieldConfig.type) {
            case "text":
              expect(field).not.toBeNull();
              expect(field).not.toHaveAttribute("required");
              expect(field).toHaveAttribute("placeholder", fieldConfig.name);
              expect(field).toHaveAttribute("name", fieldName);
              break;
            case "password":
              expect(field).not.toBeNull();
              expect(field).toHaveAttribute("required");
              expect(field).toHaveAttribute("placeholder", fieldConfig.name);
              expect(field).toHaveAttribute("name", fieldName);
              break;
            default:
              throw new Error(`Unknown field type: ${fieldConfig.type}`);
          }
        });
      });
    });

    describe("interaction", () => {
      it("should update connection details on field change", async () => {
        const user = userEvent.setup();

        const index = 0;
        const config = targetDevice.wizard_steps[index];

        const ComponentToRender = utils.generateDynamicElement({
          config: config,
          index: index,
        });

        const { container } = render(ComponentToRender);

        await act(async () => {
          await new Promise((resolve) => setTimeout(resolve, 0));
        });

        const renderedFields = container.querySelectorAll(".c_generic_element");

        // One for parent block, plus fields
        const expectedFieldCount =
          1 + Object.keys(deviceConnectionFields).length;
        expect(renderedFields).toHaveLength(expectedFieldCount);

        // Convert NodeList to Array
        const renderedFieldsList = [...renderedFields];

        const fullFieldConfig = Object.entries(deviceConnectionFields);

        for (let i = 0; i < renderedFieldsList.length; i++) {
          if (index === 0) {
            // Skip the parent block
            return;
          }

          const field = renderedFieldsList[i];

          const lookupIndex = index - 1; // Skip the parent block
          const [fieldName, fieldConfig] = fullFieldConfig[lookupIndex];

          switch (fieldConfig.type) {
            case "text":
            case "password": {
              await act(() => {
                user.type(field, "new-value");
              });

              const setDetails =
                useDeviceWizardStore.getState().connectionDetails[fieldName];

              expect(setDetails).toEqual("new-value");
              break;
            }
            default:
              throw new Error(`Unknown field type: ${fieldConfig.type}`);
          }
        }
      });
    });
  });
});
