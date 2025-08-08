# OASIS Board Python Package

Usage:
  oasis-gui
  oasis-tui



                    +-------------------+
                    |     oasis-api     |
                    |  (Python library) |
                    +-------------------+
                             ^
         +-------------------+---------------------+
         |                   |                     |
+----------------+   +----------------+   +----------------+
|   oasis-cli    |   |   oasis-tui    |   |   oasis-gui    |
| (flags & args) |   | (guided menus) |   | (desktop/web)  |
+----------------+   +----------------+   +----------------+

## HDF5 File Format for OASIS Measurements

### **Overview**

Measurement data is stored in [HDF5](https://www.hdfgroup.org/solutions/hdf5/) files in a **tidy data** format, making it easy to analyze, visualize, and share.

### **Structure**

* The main dataset is stored at the root as `/data`.
* The file contains **attributes** describing metadata and the measurement setup.

#### **Data Table: `/data`**

* Shape: `(N, )` where `N = number of channels × number of time points`
* Each row represents a single observation:

  * **channel**: Integer (1–8), channel number
  * **time**: Float (seconds), timestamp of the sample
  * **voltage**: Float (volts), measured voltage value

Example (first few rows):

| channel | time    | voltage |
| ------- | ------- | ------- |
| 1       | 0.00000 | 0.0324  |
| 1       | 0.00100 | 0.0451  |
| ...     | ...     | ...     |
| 8       | 9.99900 | 0.0078  |

* **Units:**

  * The `voltage` column has the attribute `unit = "V"`

#### **File Attributes (Metadata)**

* `duration_s`: Duration of acquisition (in seconds)
* `sampling_frequency_hz`: Sampling frequency (in Hz)
* `voltage_ranges`: Array of voltage ranges for each channel (in volts)
* `voltage_ranges_unit`: `"V"`
* `channels`: Number of channels (typically 8)
* `tidy_format`: Description of the tidy layout

#### **Why Tidy Data?**

* **Each variable forms a column:** channel, time, voltage
* **Each observation forms a row:** one reading from one channel at one time
* **Each type of observational unit forms a table:** all data is in `/data`
* This format makes the data easy to filter, aggregate, and visualize in Python (Pandas), R, MATLAB, etc.

---

### **How to Read the File (Python Example)**

```python
import h5py
import numpy as np

with h5py.File("measurement.h5", "r") as f:
    data = f["data"][:]
    print("Fields:", data.dtype.names)  # ('channel', 'time', 'voltage')
    print("First row:", data[0])
    print("Sampling frequency:", f.attrs["sampling_frequency_hz"])
    print("Voltage ranges:", f.attrs["voltage_ranges"])
```

---

### **Viewing**

* Use [HDFView](https://www.hdfgroup.org/downloads/hdfview/) or Vitables to inspect your data and metadata visually.
