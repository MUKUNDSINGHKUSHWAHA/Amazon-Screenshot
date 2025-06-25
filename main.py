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

def read_keywords(filepath):
    ext = os.path.splitext(filepath)[-1].lower()
    if ext == ".csv":
        df = pd.read_csv(filepath, header=None)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(filepath, header=None)
    else:
        raise ValueError("Unsupported file type")
    return df.iloc[:, 0].dropna().astype(str).tolist()

def setup_mobile_driver():
    mobile_emulation = {
        "deviceMetrics": { "width": 412, "height": 915, "pixelRatio": 2.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    }
    options = Options()
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=412,1600")
    return webdriver.Chrome(options=options)

def capture_long_screenshot(driver, keyword, save_path):
    try:
        search_url = f"https://www.amazon.in/s?k={keyword.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(1)

        temp_files = []

        # 1️⃣  Grab three viewport-sized screenshots
        for i in range(5):
            
            if i == 1:                                            # for shots 1 and 2 scroll first
                driver.execute_script("window.scrollBy(0, window.innerHeight-100);")
                time.sleep(2)
            elif i > 1 :
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                time.sleep(2)
            filename = f"temp{i+1}.png"
            driver.save_screenshot(filename)
            temp_files.append(filename)

        # 2️⃣  Load images, crop 10 % off the second one, and stash in a list
        images = []
        for idx, path in enumerate(temp_files):
            img = Image.open(path)
            if idx == 1:                                     # second screenshot (0-based index)
                h = img.height
                crop_px = int(h * 0.11)                      # 10 % of its height
                img = img.crop((0, crop_px, img.width, h))
            # elif idx == 3:                                   # fifth screenshot (0-based index)
            #     h = img.height
            #     crop_px = int(h * 0.10)                      # 10 % from bottom
            #     img = img.crop((0, 0, img.width, h - crop_px))

            images.append(img)


        # 3️⃣  Stitch
        total_height = sum(img.height for img in images)
        stitched_img = Image.new('RGB', (images[0].width, total_height))
        y_offset = 0
        for img in images:
            stitched_img.paste(img, (0, y_offset))
            y_offset += img.height

        # 4️⃣  Save & clean up
        filename = sanitize_filename(keyword) + ".png"
        screenshot_path = os.path.join(save_path, filename)
        stitched_img.save(screenshot_path)

        for f in temp_files:
            os.remove(f)

        return "Success", filename, ""
    except Exception as e:
        return "Failed", "", str(e)


def run_process(file_path):
    keywords = read_keywords(file_path)
    output_folder = create_output_folder()
    summary = []
    failed = []

    for keyword in keywords:
        for attempt in range(2):
            try:
                driver = setup_mobile_driver()
                status, filename, notes = capture_long_screenshot(driver, keyword, output_folder)
                driver.quit()
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



