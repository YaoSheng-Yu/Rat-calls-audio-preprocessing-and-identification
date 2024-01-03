import tkinter as tk
from tkinter import filedialog, simpledialog, Toplevel, Label
import threading
from scipy.io import wavfile
from scipy.signal import butter, lfilter
import numpy as np
import os

def butter_bandstop(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandstop')
    return b, a

def apply_bandstop_filter(data, sr, lowcut, highcut, order=5):
    b, a = butter_bandstop(lowcut, highcut, sr, order)
    y = lfilter(b, a, data)
    return y

def select_input_file():
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename()
    root.destroy()
    return filepath

def select_output_directory():
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory()
    root.destroy()
    return directory

def process_file(input_file, output_directory, time_range, lowcut, highcut, order, update_callback):
    try:
        fs, data = wavfile.read(input_file, mmap=True)
        
        start_time, end_time = time_range
        start_sample = int(start_time * fs)
        end_sample = min(int(end_time * fs), len(data))

        # Apply bandstop filter only within the specified time range
        data_filtered = data.copy()
        data_filtered[start_sample:end_sample] = apply_bandstop_filter(data[start_sample:end_sample], fs, lowcut, highcut, order)

        output_file = os.path.join(output_directory, os.path.basename(input_file).split('.')[0] + '_processed.wav')
        wavfile.write(output_file, fs, data_filtered.astype(np.int16))

        update_callback("Processing complete. The output file is saved as: " + output_file)
    except Exception as e:
        update_callback("Error occurred: " + str(e))



def show_progress_window(root, input_file, output_directory, time_range, lowcut, highcut, order):
    progress_window = Toplevel(root)
    progress_window.title("Processing")
    progress_label = Label(progress_window, text="Processing, please wait...")
    progress_label.pack()

    def update_status(message):
        progress_label.config(text=message)
        if "complete" in message or "Error" in message:
            progress_window.destroy()

    threading.Thread(target=process_file, args=(input_file, output_directory, time_range, lowcut, highcut, order, update_status)).start()

def main():
    root = tk.Tk()
    root.withdraw()
    input_file = select_input_file()

    if input_file:
        output_directory = select_output_directory()
        if output_directory:
            # Get user input for frequency range and order
            lowcut = simpledialog.askfloat("Input", "Enter lower cutoff frequency (Hz):\nExample: For 20kHz, enter 20000", parent=root)
            highcut = simpledialog.askfloat("Input", "Enter higher cutoff frequency (Hz):\nExample: For 22kHz, enter 22000", parent=root)
            order = simpledialog.askinteger("Input", "Enter filter order:\nRecommended range: 3-6 (higher order means sharper cutoff, but more processing)", parent=root, initialvalue=5)
            start_time = simpledialog.askfloat("Input", "Enter start time for filter (seconds):\nExample: For 1 minute, enter 60", parent=root)
            end_time = simpledialog.askfloat("Input", "Enter end time for filter (seconds):\nExample: For 2 minutes, enter 120", parent=root)


            if all([lowcut, highcut, order, start_time, end_time]):
                time_range = (start_time, end_time)
                show_progress_window(root, input_file, output_directory, time_range, lowcut, highcut, order)
                root.mainloop()
            else:
                print("Filter parameters not fully entered.")
        else:
            print("No output directory selected.")
    else:
        print("No input file selected.")

    root.destroy()

if __name__ == "__main__":
    main()
