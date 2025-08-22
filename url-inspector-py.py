import requests
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import winsound

monitoring = False

def log_message(icon, message, color="white"):
    """Add a message to the log panel."""
    log_text.configure(state="normal")
    log_text.insert("end", f"{icon} {message}\n", color)
    log_text.configure(state="disabled")
    log_text.see("end")

def check_site(url, options, interval, loop):
    global monitoring
    last_status = None
    while monitoring:
        try:
            response = requests.get(url, timeout=5)
            code = response.status_code
            online = (code == 200)

            if online:
                log_message("✅", f"{url} is ONLINE (code {code})", "green")
                if options["notify_online"] and last_status != True:
                    if options["use_popups"]:
                        show_popup("✅", f"{url} is ONLINE")
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
                last_status = True

            elif not online and options["notify_offline"] and last_status != False:
                if options["use_popups"]:
                    show_popup("❌", f"{url} is OFFLINE (code {code})")
                log_message("❌", f"{url} is OFFLINE (code {code})", "red")
                last_status = False

        except requests.exceptions.SSLError:
            if options["notify_ssl"]:
                if options["use_popups"]:
                    show_popup("🔒", f"{url} requires a valid SSL certificate")
                log_message("🔒", f"{url} requires a valid SSL certificate", "yellow")

        except requests.RequestException as e:
            if options["notify_other"]:
                if options["use_popups"]:
                    show_popup("⚠️", f"Error connecting to {url}\n{e}")
                log_message("⚠️", f"Error connecting to {url}: {e}", "orange")

        for _ in range(interval):
            if not monitoring or not loop:
                break
            time.sleep(1)

        if not loop:
            break 
        
    log_message("🛑", f"Stopped monitoring {url}", "cyan")

def fade_in(window):
    for i in range(0, 11):
        window.attributes("-alpha", i/10)
        window.update()
        time.sleep(0.03)

def fade_out(window):
    if not window.winfo_exists():
        return
    for i in range(10, -1, -1):
        if not window.winfo_exists():
            break
        window.attributes("-alpha", i/10)
        window.update()
        time.sleep(0.03)
    if window.winfo_exists():
        window.destroy()

def show_popup(icon, message):
    popup = tk.Toplevel()
    popup.title("Status Checker")
    popup.geometry("320x130+100+100")
    popup.config(bg="#2e2e2e")
    popup.attributes("-topmost", True)
    popup.attributes("-alpha", 0.0)

    lbl_icon = tk.Label(popup, text=icon, font=("Segoe UI Emoji", 30), bg="#2e2e2e", fg="white")
    lbl_icon.pack(pady=5)

    lbl_msg = tk.Label(popup, text=message, font=("Segoe UI", 11), wraplength=260, bg="#2e2e2e", fg="white")
    lbl_msg.pack(pady=5)

    fade_in(popup)

    def auto_close():
        fade_out(popup)

    popup.after(3000, auto_close)

def start_monitoring():
    global monitoring
    monitoring = True

    url = entry_url.get()

    try:
        interval = int(entry_interval.get())
    except ValueError:
        messagebox.showerror("Error", "Interval must be a number!")
        return

    loop = loop_var.get()

    options = {
        "notify_online": var_online.get(),
        "notify_offline": var_offline.get(),
        "notify_ssl": var_ssl.get(),
        "notify_other": var_other.get(),
        "use_popups": var_popups.get()
    }

    threading.Thread(target=check_site, args=(url, options, interval, loop), daemon=True).start()
    log_message("🚀", f"Started monitoring {url} every {interval} sec.", "cyan")
    messagebox.showinfo("Started", f"Monitoring {url} every {interval} sec.")

    btn_start.config(state="disabled")
    btn_stop.config(state="normal")

def stop_monitoring():
    global monitoring
    monitoring = False
    btn_start.config(state="normal")
    btn_stop.config(state="disabled")

def create_modern_entry(parent, placeholder="", width=30):
    container = tk.Frame(parent, bg="#1e1e2f", highlightthickness=2, highlightbackground="#555", highlightcolor="#4CAF50")
    container.pack(side="left", padx=5)

    entry = tk.Entry(container, width=width, font=("Segoe UI", 11), bg="#2e2e3e", fg="white",
                     insertbackground="white", relief="flat", bd=0)
    entry.pack(ipady=6, padx=6)

    entry.insert(0, placeholder)
    entry.config(fg="gray")

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="white")

    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="gray")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    return entry

root = tk.Tk()
root.title("🌐 URL Status Checker")
root.geometry("800x800")
root.config(bg="#1e1e2f")
style = ttk.Style()
style.configure("TCheckbutton", font=("Segoe UI", 11), background="#2e2e3e", foreground="white")
style.map("TButton",
          background=[("active", "#555")],
          foreground=[("active", "white")])
title = tk.Label(root, text="🌐 URL Status Checker", font=("Segoe UI", 22, "bold"), bg="#1e1e2f", fg="white")
title.pack(pady=15)
input_frame = tk.LabelFrame(root, text="🔧 Settings", font=("Segoe UI", 13, "bold"),
                            bg="#2e2e3e", fg="white", labelanchor="n", padx=10, pady=10)
input_frame.pack(pady=15, padx=15, fill="x")
url_frame = tk.Frame(input_frame, bg="#2e2e3e")
url_frame.pack(pady=8, fill="x")
lbl_url = tk.Label(url_frame, text="🔗 URL:", font=("Segoe UI", 12),
                   bg="#2e2e3e", fg="white")
lbl_url.pack(side="left", padx=5)
entry_url = create_modern_entry(url_frame, placeholder="https://www.google.com", width=40)
entry_url.pack(side="left", padx=5, ipady=4)
interval_frame = tk.Frame(input_frame, bg="#2e2e3e")
interval_frame.pack(pady=8, fill="x")
lbl_interval = tk.Label(interval_frame, text="⏱ Interval (sec):",
                        font=("Segoe UI", 12), bg="#2e2e3e", fg="white")
lbl_interval.pack(side="left", padx=5)
entry_interval = create_modern_entry(interval_frame, placeholder="60", width=10)
entry_interval.pack(side="left", padx=5, ipady=4)
if entry_interval.get() == "60":
    entry_interval.delete(0, tk.END)
    entry_interval.insert(0, "60")
    entry_interval.config(fg="white")
options_frame = tk.LabelFrame(root, text="⚙️ Options", font=("Segoe UI", 12, "bold"),
                              bg="#2e2e3e", fg="white", labelanchor="n")
options_frame.pack(pady=15, padx=10, fill="x")
var_online = tk.BooleanVar(value=True)
var_offline = tk.BooleanVar(value=True)
var_ssl = tk.BooleanVar(value=True)
var_other = tk.BooleanVar(value=True)
var_popups = tk.BooleanVar(value=True)
loop_var = tk.BooleanVar(value=True)
left_opt = tk.Frame(options_frame, bg="#2e2e3e")
left_opt.pack(side="left", padx=20, pady=10)
right_opt = tk.Frame(options_frame, bg="#2e2e3e")
right_opt.pack(side="left", padx=20, pady=10)
ttk.Checkbutton(left_opt, text="✅ Notify when online", variable=var_online).pack(anchor="w", pady=5)
ttk.Checkbutton(left_opt, text="❌ Notify when offline", variable=var_offline).pack(anchor="w", pady=5)
ttk.Checkbutton(left_opt, text="🔒 Notify SSL issues", variable=var_ssl).pack(anchor="w", pady=5)
ttk.Checkbutton(right_opt, text="⚠️ Notify other errors", variable=var_other).pack(anchor="w", pady=5)
ttk.Checkbutton(right_opt, text="💬 Show popups", variable=var_popups).pack(anchor="w", pady=5)
ttk.Checkbutton(right_opt, text="🔁 Loop monitoring", variable=loop_var).pack(anchor="w", pady=5)
btn_frame = tk.Frame(root, bg="#1e1e2f")
btn_frame.pack(pady=15)
btn_start = tk.Button(btn_frame, text="🚀 START", font=("Segoe UI", 14, "bold"),
                      bg="#4CAF50", fg="white", activebackground="#45a049",
                      command=start_monitoring, relief="flat", bd=0)
btn_start.pack(side="left", padx=15, ipadx=25, ipady=8)
btn_stop = tk.Button(btn_frame, text="🛑 STOP", font=("Segoe UI", 14, "bold"),
                     bg="#F44336", fg="white", activebackground="#d32f2f",
                     command=stop_monitoring, relief="flat", bd=0, state="disabled")
btn_stop.pack(side="left", padx=15, ipadx=25, ipady=8)
log_frame = tk.LabelFrame(root, text="📜 Live Log", font=("Segoe UI", 12, "bold"),
                          bg="#2e2e3e", fg="white", labelanchor="n")
log_frame.pack(pady=10, padx=10, fill="both", expand=True)
scrollbar = tk.Scrollbar(log_frame)
scrollbar.pack(side="right", fill="y")
log_text = tk.Text(log_frame, height=12, state="disabled", bg="#111", fg="white",
                   font=("Consolas", 11), yscrollcommand=scrollbar.set)
log_text.pack(padx=5, pady=5, fill="both", expand=True)
scrollbar.config(command=log_text.yview)
log_text.tag_config("green", foreground="#4CAF50")
log_text.tag_config("red", foreground="#FF5252")
log_text.tag_config("yellow", foreground="#FFD740")
log_text.tag_config("orange", foreground="#FF9800")
log_text.tag_config("cyan", foreground="#00BCD4")
root.mainloop()