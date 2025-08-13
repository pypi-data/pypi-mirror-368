// region device list

const fixtureNoDevices = []

const fixtureMultipleDevices = [
  {
    id: 1,
    name: "Device 8999",
    codename: "insta360_x4",
  },
  {
    id: 2,
    name: "Device 9000",
    codename: "insta360_x4"
  },
]

const mockDevicesList = async (page, mock) => {
  await page.route('**/plugin-views/whitebox_plugin_device_manager/devices/', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify(mock)
    });
  })
}

const mockDevicesListNoDevices =
    async (page) => await mockDevicesList(page, fixtureNoDevices)

const mockDevicesListMultipleDevices =
    async (page) => await mockDevicesList(page, fixtureMultipleDevices)

// endregion device list

// region supported devices

const fixtureSupportedDeviceCodename1 = 'insta360_x3'
const fixtureSupportedDeviceName1 = 'Insta360 X3'

const fixtureSupportedDeviceCodename2 = 'insta360_x4'
const fixtureSupportedDeviceName2 = 'Insta360 X4'

const fixtureSupportedDevices = {
  "supported_devices": [
    {
      "codename": fixtureSupportedDeviceCodename1,
      "device_name": fixtureSupportedDeviceName1,
      "device_image_url": "/static/whitebox_plugin_device_insta360/insta360_x3/insta360_x3.webp",
      "connection_types": {
        "wifi": {
          "name": "Wi-Fi",
          "fields": {
            "ssid": {
              "name": "Network Name",
              "type": "text",
              "required": false
            },
            "password": {
              "name": "Network Password",
              "type": "password",
              "required": true
            }
          }
        }
      },
      "wizard_steps": [
        {
          "template": "\n\n<div class=\"wizard-media-container\">\n  <img src=\"%API_URL%/static/\" alt=\"\">\n</div>\n\n\n<p class=\"text-high-emphasis text-lg font-semibold\">Introduction</p>\n\n<p class=\"text-2xl font-semibold\"> setup guide</p>\n\n<p class=\"text-high-emphasis font-medium leading-6\">\n  Welcome to the  setup guide!\n  Follow these simple steps to get your camera ready for action. Let's get started!\n</p>\n",
          "actions": {
            "left": {
              "type": "button",
              "config": {
                "text": "Skip to end",
                "action": "WIZARD_STEP_LAST"
              }
            },
            "right": {
              "type": "button",
              "config": {
                "text": "Start",
                "action": "WIZARD_STEP_NEXT"
              }
            }
          }
        },
        {
          "template": "\n\n\n\n\n<link href=\"%API_URL%/static/videojs/video-js.css\" rel=\"stylesheet\" />\n<script src=\"%API_URL%/static/videojs/video.min.js\"></script>\n\n<div class=\"wizard-media-container\">\n  <video controls muted loop autoplay>\n    <source src=\"%API_URL%/static/whitebox_plugin_device_insta360/insta360_x4/wizard_step_1.mp4\">\n    Your browser does not support the video tag.\n  </video>\n</div>\n\n\n<p class=\"text-high-emphasis text-lg font-semibold\">Step 1 of 4</p>\n\n<p class=\"text-2xl font-semibold\">MicroSD: Insert</p>\n\n<p class=\"text-high-emphasis font-medium leading-6\">\n  Before you begin recording, make sure to insert a compatible MicroSD card\n  into your Insta360 X3. To insert the card, open the side compartment on the\n  camera, remove the battery and gently push the MicroSD card into the slot\n  until it clicks into place, and close the compartment securely.\n</p>\n",
          "actions": {
            "left": {
              "type": "button",
              "config": {
                "text": "Skip to end",
                "action": "WIZARD_STEP_LAST"
              }
            },
            "right": {
              "type": "button",
              "config": {
                "text": "Checked",
                "action": "WIZARD_STEP_NEXT"
              }
            }
          }
        },
        {
          "template": "\n\n\n\n\n<link href=\"%API_URL%/static/videojs/video-js.css\" rel=\"stylesheet\" />\n<script src=\"%API_URL%/static/videojs/video.min.js\"></script>\n\n<div class=\"wizard-media-container\">\n  <video controls muted loop autoplay>\n    <source src=\"%API_URL%/static/whitebox_plugin_device_insta360/insta360_x4/wizard_step_2.mp4\">\n    Your browser does not support the video tag.\n  </video>\n</div>\n\n\n<p class=\"text-high-emphasis text-lg font-semibold\">Step 2 of 4</p>\n\n<p class=\"text-2xl font-semibold\">Camera: Charge</p>\n\n<p class=\"text-high-emphasis font-medium leading-6\">\n  Before heading out to shoot, check that your Insta360 X3 is fully charged.\n  Use the provided USB cable to connect the camera to a power source. The\n  camera’s LED indicator will turn off when the battery is fully charged. It’s a\n  good idea to keep a spare battery or portable charger handy for longer sessions.\n</p>\n",
          "actions": {
            "left": {
              "type": "button",
              "config": {
                "text": "Skip to end",
                "action": "WIZARD_STEP_LAST"
              }
            },
            "right": {
              "type": "button",
              "config": {
                "text": "Checked",
                "action": "WIZARD_STEP_NEXT"
              }
            }
          }
        },
        {
          "template": "\n\n\n\n\n<link href=\"%API_URL%/static/videojs/video-js.css\" rel=\"stylesheet\" />\n<script src=\"%API_URL%/static/videojs/video.min.js\"></script>\n\n<div class=\"wizard-media-container\">\n  <video controls muted loop autoplay>\n    <source src=\"%API_URL%/static/whitebox_plugin_device_insta360/insta360_x4/wizard_step_3.mp4\">\n    Your browser does not support the video tag.\n  </video>\n</div>\n\n\n<p class=\"text-high-emphasis text-lg font-semibold\">Step 3 of 4</p>\n\n<p class=\"text-2xl font-semibold\">Camera: Activate</p>\n\n<p class=\"text-high-emphasis font-medium leading-6\">\n  To activate your camera, power it on and enable Wi-Fi. Download the Insta360\n  app from the App Store or Google Play, then follow the app’s prompts to\n  connect to your camera’s Wi-Fi and complete the pairing process. The app will\n  also guide you through any necessary firmware updates.\n</p>\n",
          "actions": {
            "left": {
              "type": "button",
              "config": {
                "text": "Skip to end",
                "action": "WIZARD_STEP_LAST"
              }
            },
            "right": {
              "type": "button",
              "config": {
                "text": "Checklist complete",
                "action": "WIZARD_STEP_NEXT"
              }
            }
          }
        },
        {
          "template": "\n\n\n\n\n<link href=\"%API_URL%/static/videojs/video-js.css\" rel=\"stylesheet\" />\n<script src=\"%API_URL%/static/videojs/video.min.js\"></script>\n\n<div class=\"wizard-media-container\">\n  <video controls muted loop autoplay>\n    <source src=\"%API_URL%/static/whitebox_plugin_device_insta360/insta360_x4/wizard_step_3.mp4\">\n    Your browser does not support the video tag.\n  </video>\n</div>\n\n\n<p class=\"text-high-emphasis text-lg font-semibold\">Step 4 of 4</p>\n\n<p class=\"text-2xl font-semibold\">Wi-Fi: Enter details</p>\n\n<slot name=\"wizard_field_block\"></slot>\n",
          "actions": {
            "left": {
              "type": "button",
              "config": {
                "text": "Back",
                "action": "WIZARD_STEP_INITIAL"
              }
            },
            "right": {
              "type": "button",
              "config": {
                "text": "Connect device",
                "action": "WIZARD_ADD_DEVICE"
              }
            }
          }
        }
      ]
    },
    {
      "codename": fixtureSupportedDeviceCodename2,
      "device_name": fixtureSupportedDeviceName2,
      "device_image_url": "/static/whitebox_plugin_device_insta360/insta360_x4/insta360_x4.webp",
      "connection_types": {
        "wifi": {
          "name": "Wi-Fi",
          "fields": {
            "ssid": {
              "name": "Network Name",
              "type": "text",
              "required": true
            },
            "password": {
              "name": "Network Password",
              "type": "password",
              "required": true
            }
          }
        }
      },
      "wizard_steps": [
        {
          "template": "\n\n<div class=\"wizard-media-container\">\n  <img src=\"%API_URL%/static/\" alt=\"\">\n</div>\n\n\n<p class=\"text-high-emphasis text-lg font-semibold\">Introduction</p>\n\n<p class=\"text-2xl font-semibold\"> setup guide</p>\n\n<p class=\"text-high-emphasis font-medium leading-6\">\n  Welcome to the  setup guide!\n  Follow these simple steps to get your camera ready for action. Let's get started!\n</p>\n",
          "actions": {
            "left": {
              "type": "button",
              "config": {
                "text": "Skip to end",
                "action": "WIZARD_STEP_LAST"
              }
            },
            "right": {
              "type": "button",
              "config": {
                "text": "Start",
                "action": "WIZARD_STEP_NEXT"
              }
            }
          }
        },
        {
          "template": "\n\n\n\n\n<link href=\"%API_URL%/static/videojs/video-js.css\" rel=\"stylesheet\" />\n<script src=\"%API_URL%/static/videojs/video.min.js\"></script>\n\n<div class=\"wizard-media-container\">\n  <video controls muted loop autoplay>\n    <source src=\"%API_URL%/static/whitebox_plugin_device_insta360/insta360_x4/wizard_step_1.mp4\">\n    Your browser does not support the video tag.\n  </video>\n</div>\n\n\n<p class=\"text-high-emphasis text-lg font-semibold\">Step 1 of 4</p>\n\n<p class=\"text-2xl font-semibold\">MicroSD: Insert</p>\n\n<p class=\"text-high-emphasis font-medium leading-6\">\n  Before you begin recording, make sure to insert a compatible MicroSD card\n  into your Insta360 X3. To insert the card, open the side compartment on the\n  camera, remove the battery and gently push the MicroSD card into the slot\n  until it clicks into place, and close the compartment securely.\n</p>\n",
          "actions": {
            "left": {
              "type": "button",
              "config": {
                "text": "Skip to end",
                "action": "WIZARD_STEP_LAST"
              }
            },
            "right": {
              "type": "button",
              "config": {
                "text": "Checked",
                "action": "WIZARD_STEP_NEXT"
              }
            }
          }
        },
        {
          "template": "\n\n\n\n\n<link href=\"%API_URL%/static/videojs/video-js.css\" rel=\"stylesheet\" />\n<script src=\"%API_URL%/static/videojs/video.min.js\"></script>\n\n<div class=\"wizard-media-container\">\n  <video controls muted loop autoplay>\n    <source src=\"%API_URL%/static/whitebox_plugin_device_insta360/insta360_x4/wizard_step_2.mp4\">\n    Your browser does not support the video tag.\n  </video>\n</div>\n\n\n<p class=\"text-high-emphasis text-lg font-semibold\">Step 2 of 4</p>\n\n<p class=\"text-2xl font-semibold\">Camera: Charge</p>\n\n<p class=\"text-high-emphasis font-medium leading-6\">\n  Before heading out to shoot, check that your Insta360 X3 is fully charged.\n  Use the provided USB cable to connect the camera to a power source. The\n  camera’s LED indicator will turn off when the battery is fully charged. It’s a\n  good idea to keep a spare battery or portable charger handy for longer sessions.\n</p>\n",
          "actions": {
            "left": {
              "type": "button",
              "config": {
                "text": "Skip to end",
                "action": "WIZARD_STEP_LAST"
              }
            },
            "right": {
              "type": "button",
              "config": {
                "text": "Checked",
                "action": "WIZARD_STEP_NEXT"
              }
            }
          }
        },
        {
          "template": "\n\n\n\n\n<link href=\"%API_URL%/static/videojs/video-js.css\" rel=\"stylesheet\" />\n<script src=\"%API_URL%/static/videojs/video.min.js\"></script>\n\n<div class=\"wizard-media-container\">\n  <video controls muted loop autoplay>\n    <source src=\"%API_URL%/static/whitebox_plugin_device_insta360/insta360_x4/wizard_step_3.mp4\">\n    Your browser does not support the video tag.\n  </video>\n</div>\n\n\n<p class=\"text-high-emphasis text-lg font-semibold\">Step 3 of 4</p>\n\n<p class=\"text-2xl font-semibold\">Camera: Activate</p>\n\n<p class=\"text-high-emphasis font-medium leading-6\">\n  To activate your camera, power it on and enable Wi-Fi. Download the Insta360\n  app from the App Store or Google Play, then follow the app’s prompts to\n  connect to your camera’s Wi-Fi and complete the pairing process. The app will\n  also guide you through any necessary firmware updates.\n</p>\n",
          "actions": {
            "left": {
              "type": "button",
              "config": {
                "text": "Skip to end",
                "action": "WIZARD_STEP_LAST"
              }
            },
            "right": {
              "type": "button",
              "config": {
                "text": "Checklist complete",
                "action": "WIZARD_STEP_NEXT"
              }
            }
          }
        },
        {
          "template": "\n\n\n\n\n<link href=\"%API_URL%/static/videojs/video-js.css\" rel=\"stylesheet\" />\n<script src=\"%API_URL%/static/videojs/video.min.js\"></script>\n\n<div class=\"wizard-media-container\">\n  <video controls muted loop autoplay>\n    <source src=\"%API_URL%/static/whitebox_plugin_device_insta360/insta360_x4/wizard_step_3.mp4\">\n    Your browser does not support the video tag.\n  </video>\n</div>\n\n\n<p class=\"text-high-emphasis text-lg font-semibold\">Step 4 of 4</p>\n\n<p class=\"text-2xl font-semibold\">Wi-Fi: Enter details</p>\n\n<slot name=\"wizard_field_block\"></slot>\n",
          "actions": {
            "left": {
              "type": "button",
              "config": {
                "text": "Back",
                "action": "WIZARD_STEP_INITIAL"
              }
            },
            "right": {
              "type": "button",
              "config": {
                "text": "Connect device",
                "action": "WIZARD_ADD_DEVICE"
              }
            }
          }
        }
      ]
    }
  ]
}

const mockSupportedDevices = async (page) => {
  await page.route('**/plugin-views/whitebox_plugin_device_manager/devices/supported-devices/', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify(fixtureSupportedDevices)
    });
  })
}

// endregion supported devices

export {
  // device list
  fixtureSupportedDeviceCodename1,
  fixtureSupportedDeviceName1,
  fixtureSupportedDeviceCodename2,
  fixtureSupportedDeviceName2,

  fixtureNoDevices,
  fixtureMultipleDevices,
  mockDevicesList,
  mockDevicesListNoDevices,
  mockDevicesListMultipleDevices,

  // supported devices
  fixtureSupportedDevices,
  mockSupportedDevices,
}
