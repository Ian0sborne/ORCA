# ORCA - Optical Readout and Camera Analysis
ORCA is a Python-based data acquisition and analysis tool for optical imaging systems.

## OS compatibility
So far, the software used is that provided by ThorLabs for their scientific cameras. This is designed for Windows systems, but is also compatible with Linux.

## Requirements
Scripts rely on the ThorCam software package, which can be found [here](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ThorCam). The Linux compatible software can be downloaded [here](https://media.thorlabs.com/contentassets/f779a6211aa441418ab4122c9ac0ba02/scientific_camera_interfaces_linux-2.1.zip?v=0325124043).

## Installation

Once you have downloaded the software, it will contain the Python SDK in a zip folder found within `/Scientific_Camera_Interfaces/SDK/Python_Toolkit`. To install it, use a package manager such as pip as following:

```
python.exe -m pip install thorlabs_tsi_camera_python_sdk_package.zip
```

This will install the `thorlabs_tsi_sdk` package into your current environment. 

Additional examples and requirements can be installed as:

```
pip install -r /Scientific_Camera_Interfaces/SDK/Python_Toolkit/examples/Requirements.txt  
```

Finally, in the directory where you run your scripts, you will need to export the path to the shared libraries that the scripts need to run with:

```
`export LD_LIBRARY_PATH="/Scientific_Camera_Interfaces/SDK/Native_To_Toolkit/bin/Native_64_lib:$LD_LIBRARY_PATH"`
```