import whois
import csv
import time
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread 

# --- Configuration ---
# NOTE: This is now the OUTPUT FOLDER, not a file.
OUTPUT_FOLDER = "output/individual_results/"
REQUEST_DELAY_SECONDS = 2 

FIELDNAMES = [
    "domain", "registrar", "creation_date", "expiration_date", "updated_date", 
    "status", "name_servers", "error_message"
]

class WhoisApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌐 Interactive WHOIS Fetcher GUI")
        self.geometry("800x700")
        self.style = ttk.Style(self)
        self.style.theme_use('clam') 

        # --- Variables ---
        self.status_var = tk.StringVar(value="Ready. Enter domains above and click 'Start Fetching'.")
        self.results_counter = 0 # Counter for successful files saved
        
        # --- Build Layout (Same as before) ---
        self.create_widgets()

    # --- GUI Widget Setup (UNCHANGED) ---
    def create_widgets(self):
        # 1. Main Frame setup
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(fill='both', expand=True)

        # 2. Header and Status
        header_label = ttk.Label(main_frame, text="Bulk WHOIS Domain Lookup", font=('Helvetica', 16, 'bold'))
        header_label.pack(pady=10)

        # 3. Domain Input Area
        ttk.Label(main_frame, text="Enter Domains (One per line):", font=('Helvetica', 10, 'bold')).pack(anchor='w')
        
        self.domain_input_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=8, width=90, font=('Consolas', 10))
        self.domain_input_text.pack(fill='x', pady=5)
        self.domain_input_text.insert(tk.END, "google.com\nexample.org\nopenai.com")

        # 4. Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Fetching", command=self.start_whois_thread, style='Accent.TButton')
        self.start_button.pack(side='left', padx=10)
        
        ttk.Button(button_frame, text="Clear Input", command=self.clear_input).pack(side='left', padx=10)
        
        ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder).pack(side='left', padx=10)

        # 5. Status Bar
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground='blue')
        status_label.pack(pady=5)

        # 6. Progress/Results Display Area
        ttk.Label(main_frame, text="--- Results Log ---", font=('Helvetica', 12)).pack(pady=5)
        
        self.result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, width=90, font=('Consolas', 10))
        self.result_text.pack(fill='both', expand=True)
        self.result_text.tag_config('success', foreground='green')
        self.result_text.tag_config('error', foreground='red')
        self.result_text.tag_config('info', foreground='blue')
        
    # --- Helper Functions (UNCHANGED) ---
    def log_message(self, message, tag=None):
        self.result_text.insert(tk.END, message + "\n", tag)
        self.result_text.see(tk.END) 
    
    def clear_input(self):
        self.domain_input_text.delete('1.0', tk.END)
        self.status_var.set("Input cleared.")

    def get_domains_from_input(self):
        input_text = self.domain_input_text.get("1.0", tk.END).strip()
        domains = [line.strip() for line in input_text.splitlines() if line.strip()]
        return domains

    def get_whois_info(self, domain):
        """Fetches WHOIS information for a single domain (UNCHANGED)."""
        result = {"domain": domain, "error_message": ""}
        for field in FIELDNAMES:
            if field not in result:
                result[field] = "N/A"

        try:
            w = whois.whois(domain)

            if isinstance(w.domain_name, list) and not w.domain_name:
                 result["status"] = "NOT FOUND / RESERVED"
                 return result

            result["registrar"] = str(w.registrar) if w.registrar else "N/A"
            result["creation_date"] = str(w.creation_date)
            result["expiration_date"] = str(w.expiration_date)
            result["updated_date"] = str(w.updated_date)
            
            if w.status:
                status_list = w.status if isinstance(w.status, list) else [w.status]
                result["status"] = " | ".join(status_list)
            else:
                result["status"] = "REGISTERED"
                
            name_servers = w.name_servers if isinstance(w.name_servers, list) else [w.name_servers]
            result["name_servers"] = ", ".join([ns for ns in name_servers if ns]) if name_servers else "N/A"

            return result

        except whois.parser.PywhoisError as e:
            result["status"] = "NOT FOUND"
            result["error_message"] = str(e).split('\n')[0]
            return result
        except Exception as e:
            result["status"] = "ERROR"
            result["error_message"] = f"Unexpected Error: {e}"
            return result

    # --- MODIFIED: Save a single dictionary (one domain) to a CSV file ---
    def save_single_result(self, data_dict):
        """Writes a single domain's WHOIS data dictionary to its own CSV file."""
        # Sanitize domain name to be file-system friendly (replace dots with underscores)
        domain_name_safe = data_dict['domain'].replace('.', '_')
        filename = os.path.join(OUTPUT_FOLDER, f"{domain_name_safe}.csv")
        
        try:
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                writer.writeheader()
                # Writerow expects a single dictionary
                writer.writerow(data_dict) 
                
            self.results_counter += 1
            return True

        except Exception as e:
            self.log_message(f"❌ Error saving {data_dict['domain']} to CSV: {e}", 'error')
            return False

    # --- Threading and Main Process (MODIFIED) ---

    def start_whois_thread(self):
        """Starts the main fetching logic in a separate thread."""
        domains = self.get_domains_from_input()
        if not domains:
            messagebox.showwarning("No Input", "Please enter at least one domain name into the input box.")
            return

        self.start_button.config(state=tk.DISABLED, text="Fetching...")
        self.status_var.set("Processing domains... Please wait.")
        self.results_counter = 0 # Reset counter
        self.result_text.delete('1.0', tk.END) 

        # Start a background thread to prevent GUI freeze
        thread = Thread(target=self.run_fetcher_process, args=(domains,))
        thread.start()

    def run_fetcher_process(self, domains):
        """Core fetching loop run in the background thread."""
        
        total_domains = len(domains)
        self.log_message(f"Starting lookup for {total_domains} domains. Output folder: {OUTPUT_FOLDER}", 'info')

        for i, domain in enumerate(domains):
            self.status_var.set(f"Processing: {domain} ({i + 1}/{total_domains})")
            
            info = self.get_whois_info(domain)
            
            # --- MODIFIED LOGIC: Save immediately ---
            self.save_single_result(info)
            # ---------------------------------------

            status = info.get("status", "N/A")
            log_tag = 'error' if "NOT FOUND" in status.upper() or "ERROR" in status.upper() else 'success'
            
            self.log_message(f"[{i + 1}/{total_domains}] {info['domain']:<30} -> Status: {status}", log_tag)
            
            time.sleep(REQUEST_DELAY_SECONDS)
            
        # 3. Finalization
        self.status_var.set(f"Process Complete! Saved {self.results_counter} files to {OUTPUT_FOLDER}")

        # Re-enable the button once done
        self.start_button.config(state=tk.NORMAL, text="Start Fetching")
        
    # --- Open Output Folder (MODIFIED to use the new folder path) ---
    def open_output_folder(self):
        """Opens the new individual results folder in the native file explorer."""
        # NOTE: The path is now OUTPUT_FOLDER
        folder_path = os.path.abspath(OUTPUT_FOLDER) 
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            messagebox.showinfo("Folder Created", f"The output folder was created at: {folder_path}")

        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.uname().sysname == 'Darwin':  # macOS
                os.system(f'open "{folder_path}"')
            else:  # Linux/Other (Robust command list)
                commands_to_try = [
                    f'nautilus "{folder_path}"', 
                    f'gio open "{folder_path}"',  
                    f'xdg-open "{folder_path}"', 
                    f'dolphin "{folder_path}"', 
                    f'thunar "{folder_path}"'    
                ]
                
                opened = False
                for command in commands_to_try:
                    if os.system(command) == 0:
                        opened = True
                        break
                
                if not opened:
                    messagebox.showwarning("Manual Open Required", 
                        f"Could not automatically open the folder. Please navigate manually to:\n\n{folder_path}")
                        
        except Exception as e:
            messagebox.showerror("Error", 
                f"An unexpected error occurred while trying to open the folder.\nError: {e}")

if __name__ == "__main__":
    app = WhoisApp()
    app.mainloop()
