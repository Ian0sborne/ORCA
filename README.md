# ORCA - Optical Readout and Camera Analysis
ORCA is a Python-based data acquisition and analysis tool for optical imaging systems.

## OS compatibility
So far, the software used is that provided by ThorLabs for their scientific cameras. This is designed for Windows systems, but is also compatible with Linux.

## Requirements
Scripts rely on the ThorCam software package, which can be found [here](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ThorCam). The Linux compatible software can be downloaded [here](https://media.thorlabs.com/contentassets/f779a6211aa441418ab4122c9ac0ba02/scientific_camera_interfaces_linux-2.1.zip?v=0325124043).

## Installation

Once you have downloaded the software, it will contain the Python SDK in a zip folder found within `/Scientific_Camera_Interfaces/SDK/Python_Toolkit`. To install it, use a package manager such as pip as following:

```
python -m pip install thorlabs_tsi_camera_python_sdk_package.zip
```

This will install the `thorlabs_tsi_sdk` package into your current environment. 

Finally, you will need to export the path to the shared libraries that the scripts need to run with:

```
export LD_LIBRARY_PATH="/Scientific_Camera_Interfaces/SDK/Native_Toolkit/bin/Native_64_lib:$LD_LIBRARY_PATH"
```

## Running the camera scripts

The camera scripts are designed to be run in the terminal using `python3`.

To run the scripts you will need the `opencv` package. To install it run:

```
pip install opencv-python
```

## Troubleshooting

A common error you will encounter when trying to run the scripts is `Segmantation fault (core dumped)`.

This occurs when the camera doesn't have the right USB permissions.

To check what permissions the camera has, first run `lsusb` to find the "Bus" and "Device" your camera is on. Once you have these, you can check your camera permissions with:

```
ls -la /dev/bus/usb/<BUS_NUM>/<DEVICE_NUM>
```

If you see `crw-rw-r--` it means that you only have read access, and this is what is causing the previous error.

To setup write access:

1. `sudo nano /etc/udev/rules.d/99-thorlabs.rules`
2. Add this to the file: `SUBSYSTEM=="usb", ATTR{idVendor}=="1313", MODE="0666", GROUP="plugdev"`
3. `sudo udevadm control --reload-rules`
4. `sudo udevadm trigger`

Unplug and replug the camera and this should fix the error.
