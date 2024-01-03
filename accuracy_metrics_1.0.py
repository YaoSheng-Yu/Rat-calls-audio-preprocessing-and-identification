import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import traceback
from openpyxl import Workbook


def select_file(message):
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title=message)
    root.destroy()
    return filepath

def compare_files(file_path_1, file_path_2):
    data_1 = pd.read_excel(file_path_1)
    data_2 = pd.read_excel(file_path_2)

    # Extract and rename the relevant columns
    columns = ['ID', 'Accepted', 'Score', 'Begin Time (s)', 'End Time (s)', 'Call Length (s)', 'Principal Frequency (kHz)', 'Low Freq (kHz)', 'High Freq (kHz)']
    new_names = ['id', 'accepted', 'score', 'begin', 'end', 'length', 'pfreq', 'lfreq', 'hfreq']
    data_1 = data_1[columns]
    data_1.columns = new_names
    data_2 = data_2[columns]
    data_2.columns = new_names

    # Sort data by begin time
    data_1 = data_1.sort_values(by='begin')
    data_2 = data_2.sort_values(by='begin')

    # Assume data_1 is sorted by 'begin' time
    matched_calls = set()
    missed_calls = set()
    matched_indices_data_1 = set()
    
    
    for index_2, row_2 in data_2.iterrows():
        middle_2 = (row_2['begin'] + row_2['end']) / 2
        match_found = False
    
        # Only loop through calls in data_1 that start before the end of the call in data_2
        for index_1, row_1 in data_1[data_1['begin'] <= row_2['end']].iterrows():
            if index_1 in matched_indices_data_1:
                continue  # Skip already matched calls
    
            # No need to check calls in data_1 that end before the start of the call in data_2
            if row_1['end'] < row_2['begin']:
                continue
    
            # Check for overlap
            overlap = min(row_2['end'], row_1['end']) - max(row_2['begin'], row_1['begin'])
            duration_1 = row_1['end'] - row_1['begin']
            duration_2 = row_2['end'] - row_2['begin']
            overlap_percentage_1 = overlap / duration_1
            overlap_percentage_2 = overlap / duration_2
    
            # Check if overlap is valid according to your condition
            overlap_threshold = 0.333
            if overlap_percentage_1 >= overlap_threshold and overlap_percentage_2 >= overlap_threshold:
                matched_calls.add((index_2, index_1))
                matched_indices_data_1.add(index_1)
                match_found = True
                break  # Stop searching once a match is found
    
        if not match_found:
            missed_calls.add(index_2)
    
    
    #Correctly matched calls
    TP = len(matched_calls)
    #Calls in Data1 that have no match in Data2
    FN = len(data_1) - len(matched_indices_data_1)
    #Calls in Data2 that have no match in Data1
    FP = len(data_2) - TP

    # Now we calculate Precision, Recall, and F1 Score
    precision = TP / (TP + FP) if TP + FP > 0 else 0
    recall = TP / (TP + FN) if TP + FN > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # Prepare the result message
    result_message = f'Precision: {precision * 100:.2f}%\n'
    result_message += f'Recall: {recall * 100:.2f}%\n'
    result_message += f'F1 Score: {f1_score * 100:.2f}%\n'
    result_message += f'TP: {TP}, FN: {FN}, FP: {FP}'
    return result_message

def main():
    try:
        file_path_1 = select_file("Select the reference file (Data 1)")
        file_path_2 = select_file("Select the comparison file (Data 2)")

        if file_path_1 and file_path_2:
            result_message = compare_files(file_path_1, file_path_2)
            messagebox.showinfo("Comparison Results", result_message)
            print(result_message)
        else:
            print("File selection cancelled.")
    except Exception as e:
        error_info = traceback.format_exc()
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", error_info)
        root.destroy()

        

if __name__ == "__main__":
    main()
