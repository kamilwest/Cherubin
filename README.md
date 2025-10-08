# Cherubin

Cherubin is a real-time network monitoring tool written in Python. It displays data transfer, speeds, packet counts, and top remote IPs in colorful console tables using the Rich library.

## Features
- **Data Transfer:** Real-time upload and download displayed in clear bars and numbers.  
- **Speed & Packets:** Shows Mbps for sending/receiving and number of packets.  
- **Top Remote IPs:** Displays the most active external connections (configurable with `--top`).  
- **Alerts:** Color-coded highlights based on thresholds (green, yellow, red) with configurable alert Mbps.  
- **Lightweight and Portable:** Console-based, only requires Python and Rich library.  

## Installation
git clone https://github.com/kamilwest/cherubin.git
cd cherubin
pip install -r requirements.txt
# or just
pip install rich

# Usage

python cherubin.py [--top 5] [--alert_mbps 50.0] [--refresh 1.0]

*--top : Number of top remote IPs to display (default: 5)*
*--alert_mbps : Threshold for highlighting high-speed interfaces (default: 50 Mbps)*
*--refresh : Refresh interval in seconds (default: 1.0)*

# Building Cherubin

To build the executable from source, use the following command (requires Python 3.13+):
(in venv) pyinstaller --onefile --noconsole --icon=cherubin.ico --hidden-import=psutil --hidden-import=rich cherubin.py
--onefile — package everything into a single executable
--noconsole — hide the console window (optional for GUI apps)
--icon=cherubin.ico — use the provided icon
--hidden-import — include dependencies not automatically detected

After running this, you’ll find the executable in the dist folder.

# Notes & Recommendations

-Best viewed in a console window; avoid full-screen terminal for optimal visual effect.
-Colors indicate network load:
    Green: Low usage
    Yellow: Moderate usage
    Red: High usage
-The program logs exceptions to Cherubin_error.log.
-Lightweight and does not require admin privileges.

# Future Enhancements

-Integrate optional logging for historical network trends.
-Add customizable color themes.
-Package as standalone executable with PyInstaller for Windows/Linux.
-Possible integration with other monitoring tools for automated alerts.

#License

MIT License – free to use, modify, and distribute.
