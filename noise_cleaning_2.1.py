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

def process_file(input_file, output_directory, chunk_duration, update_callback):
    try:
        fs, data = wavfile.read(input_file, mmap=True)
        
        lowcut_1 = 32400
        highcut_1 = 33300
        lowcut_2 = 1
        highcut_2 = 21000
        chunk_size = int(chunk_duration * 60 * fs)
        processed_chunks = []

        for start in np.arange(0, len(data), chunk_size):
            end = start + chunk_size
            current_chunk = data[start:end] if end <= len(data) else data[start:]
            filtered_chunk_1 = apply_bandstop_filter(current_chunk, fs, lowcut_1, highcut_1, order=5)
            filtered_chunk_2 = apply_bandstop_filter(filtered_chunk_1, fs, lowcut_2, highcut_2, order=3)
            processed_chunks.append(filtered_chunk_2)

        processed_data = np.concatenate(processed_chunks)
        output_file = os.path.join(output_directory, os.path.basename(input_file).split('.')[0] + '_processed.wav')
        wavfile.write(output_file, fs, processed_data.astype(np.int16))

        update_callback("Processing complete. The output file is saved as: " + output_file)
    except Exception as e:
        update_callback("Error occurred: " + str(e))

def show_progress_window(root, input_file, output_directory, chunk_duration):
    progress_window = Toplevel(root)
    progress_window.title("Processing")
    progress_label = Label(progress_window, text="Processing, please wait...")
    progress_label.pack()

    def update_status(message):
        progress_label.config(text=message)
        if "complete" in message or "Error" in message:
            progress_window.destroy()

    threading.Thread(target=process_file, args=(input_file, output_directory, chunk_duration, update_status)).start()

def main():
    root = tk.Tk()
    root.withdraw()
    input_file = select_input_file()

    if input_file:
        output_directory = select_output_directory()
        if output_directory:
            chunk_duration = simpledialog.askinteger("Input", "Chunk Duration (in minutes, default 16):", initialvalue=16, parent=root)
            if chunk_duration:
                show_progress_window(root, input_file, output_directory, chunk_duration)
                root.mainloop()
            else:
                print("No chunk duration entered.")
        else:
            print("No output directory selected.")
    else:
        print("No input file selected.")

    root.destroy()

if __name__ == "__main__":
    main()
