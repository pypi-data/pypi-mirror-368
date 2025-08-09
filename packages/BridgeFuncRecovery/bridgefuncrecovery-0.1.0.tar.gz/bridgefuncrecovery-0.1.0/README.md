# BridgeFuncRecovery
This project aims to probabilistically model the post-earthquake functional recovery of bridges. The source codes are programmed in Python.

### Reference
[1] Wu, C., Burton, H., Zsarnóczay, A., Chen. S., Xie. Y., Terzić, V., Günay, S., Padgett, J., Mieler, and M., Almufti, I. (2025). Modeling Post-earthquake Functional Recovery of Bridges. Earthquake Spectra. 

### Prerequisites
Python: version 3.6 or above.

Necessary Python packages: copy, numpy, pandas, os, scipy, sys, shutil, pathlib, re, time, pickle

### What is each file used for
*main.py* inputs user-specified parameters, and performs the entire analysis. 

*utils.py* provides necessary auxiliary functions that is called from the main script *main.py*. 

After running all cells in *main.py*, a pickle file *Results.pkl* is stored that records model output data. 

*result_anlaysis.py* helps visualize the output data stored in *Results.pkl*. 


### User-specified inputs
Users must specify the following inputs:
- *IM_fixed
- *num_span*
- *CompQty*
- *WorkerAllo_percrew*
- *Worker_Replace*

The main function can be called using:
```python
from BridgeFuncRecovery import run

# Example usage:
results = run(IM_fixed=..., num_span=..., CompQty=..., WorkerAllo_percrew=..., Worker_Replace=...)
```
This will return the result dictionary and save it to a *Results.pkl*


### Analyzing the Results
The functions in *result_analysis.py* are used to interpret and visualize output data from the main analysis. Available functions include:
- *plot_fs_initial(data)*
- *plot_fs_reopening(data)*
- *plot_total_impeding_ccdf(data)*
- *plot_total_repair_ccdf(data)*
- *print_impeding_medians(data)*
- *print_repair_durations(data)*
- *plot_repair_class_distribution_single(data, comp_name)*
- *plot_all_repair_class_distributions(data)*
- *plot_closed_lane_initial(data)*
- *show_all_results(data)*

These functions can be called using:
```python
from BridgeFuncRecovery import run, plot_repair_class_distribution_single
# Example usage:
# Run the analysis
results = run(IM_fixed=..., num_span=..., CompQty=..., WorkerAllo_percrew=..., Worker_Replace=...)

# Plot the Repair Class distribution for columns
plot_repair_class_distribution_single(results, 'Col')
```

This will save the results to *Results.pkl* and display a figure visualizing Repair Class (RC) distribution for columns.