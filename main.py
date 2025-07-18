import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time
from utils import sanitize_filename, create_output_folder
from PIL import Image
from Input_reader import read_keywords
from screenshot import capture_long_screenshot
from driver_setup import setup_mobile_driver

def run_process(file_path):
    keywords = read_keywords(file_path)
    output_folder = create_output_folder()
    summary = []
    failed = []

    driver = setup_mobile_driver()  # Create driver ONCE
    for keyword in keywords:
        for attempt in range(2):
            try:
                status, filename, notes = capture_long_screenshot(driver, keyword, output_folder)
                if status == "Success":
                    summary.append([keyword, status, filename, ""])
                    break
                else:
                    if attempt == 1:
                        summary.append([keyword, "Failed", "", notes])
                        failed.append(keyword)
            except Exception as e:
                if attempt == 1:
                    summary.append([keyword, "Failed", "", str(e)])
                    failed.append(keyword)
    driver.quit()  # Quit driver ONCE

    summary_df = pd.DataFrame(summary, columns=["Keyword", "Status", "FileName", "Notes"])
    summary_df.to_csv(os.path.join(output_folder, "summary.csv"), index=False)

    if failed:
        failed_df = pd.DataFrame(failed, columns=["Failed Keywords"])
        failed_df.to_excel(os.path.join(output_folder, "failed_keywords.xlsx"), index=False)

    return output_folder

def choose_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel or CSV", "*.xlsx *.xls *.csv")])
    if file_path:
        entry_var.set(file_path)

def start_job():
    file_path = entry_var.get()
    if not file_path:
        messagebox.showerror("Error", "Please select a file first.")
        return
    try:
        folder = run_process(file_path)
        messagebox.showinfo("Done", f"Screenshots and summary saved in:\n{folder}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Amazon Screenshot Bot")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

entry_var = tk.StringVar()
tk.Label(frame, text="Choose .csv or .xlsx file with search terms:").pack(anchor="w")
tk.Entry(frame, textvariable=entry_var, width=50).pack(pady=5)
tk.Button(frame, text="Browse", command=choose_file).pack()
tk.Button(frame, text="Start", command=start_job, bg="green", fg="white").pack(pady=20)

root.mainloop()