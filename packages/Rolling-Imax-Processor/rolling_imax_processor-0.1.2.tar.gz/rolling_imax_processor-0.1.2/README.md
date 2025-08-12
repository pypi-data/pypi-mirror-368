Rolling_Imax_Processor

This script processes raw intensity measurement data stored in a nested Year to Month to Day folder structure. The data is stored in a nested folder structure organized by Year, then Month, and then Day. Inside the day folders are Excel files named using the format dd-mm-yyyy.xlsx. It reads the per minute rainfall breakpoint data in millimeters per minute (mm/min) from Excel files, calculates rolling maximum values for intensity classes, and outputs results in millimeters per minute (mm/min) for intensity classes I1 to I60.

## Installation

```bash
pip install your_package_name
