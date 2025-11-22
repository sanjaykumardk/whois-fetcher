# 🌐 Interactive WHOIS Fetcher GUI

This is a Python application with a graphical user interface (GUI) built using **Tkinter** and **python-whois**. It allows users to input multiple domain names, fetch their WHOIS registration data (creation date, expiration date, registrar, status), and save the results into individual CSV files for easy review.

The application uses **threading** to ensure the GUI remains responsive while the network-intensive WHOIS lookups are performed.

## ✨ Features

* **Interactive Input:** Enter domains directly into a multi-line text box.
* **Non-Blocking GUI:** Runs network fetches in a separate thread to prevent the application from freezing.
* **Structured Output:** Saves each domain's WHOIS data to a separate CSV file (e.g., `google_com.csv`).
* **Rate Limiting:** Includes a 2-second delay between requests to avoid being blocked by WHOIS servers.
* **Cross-Platform:** Designed to work across Windows, macOS, and Linux.

---
## 📂 Project Structure
```
whois-fetcher/
├── whois_interactive_gui.py  # The main Python script (GUI)
├── requirements.txt           # Required Python packages
├── output/
│   └── individual_results/    # Folder containing all individual domain CSV files
└── README.md
```
## ⚙️ Installation

### 1. Prerequisites

You must have **Python 3** installed on your system.

### 2. Install Python Dependencies

Navigate to the project directory and install the required Python libraries using the `requirements.txt` file:

```bash
cd whois-fetcher/
pip install -r requirements.txt
# If using GNOME (Common on Fedora/Ubuntu):
sudo dnf install nautilus  # Or apt install nautilus on Debian/Ubuntu
```
## 💻 Run Command
```
python3 whois_gui.py
```
