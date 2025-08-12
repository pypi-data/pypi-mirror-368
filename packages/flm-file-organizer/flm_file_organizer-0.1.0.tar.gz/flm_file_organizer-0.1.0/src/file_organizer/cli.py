#Reference: https://docs.python.org/3/library/os.path.html
import os

#Reference: https://docs.python.org/3/library/shutil.html
import shutil

#Reference: https://questionary.readthedocs.io/en/stable/
import questionary # type: ignore

#Reference: https://docs.python.org/3/library/tkinter.html
import tkinter as tk
from tkinter import filedialog

import argparse

def main() -> None:
    """
    Organizes files in a selected directory into categorized subfolders based on file type.
    
    It separates files into predetermined folders, such as 'Images', ''Videos' and 'Documents'
    
    It will request which folder to organize, and if the select folder does not have files, it will try to "unOrganize" the folder for ease of testing
    """
    parser = argparse.ArgumentParser(
        description="Organize files in a directory based on file types."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed output"
    )
    args = parser.parse_args()
    
    transfers = {}
    current_folder = os.path.dirname(os.path.abspath(__file__))
    value = questionary.confirm(f"Organize this folder: '{current_folder}'? ").ask()
    if(value):
        target_directory = current_folder
    else: 
        target_directory = ask_folder()
        
    # If the user doesn't select any folders
    if not target_directory: 
        print(f"Operation canceled by User.")
        return
    
    # If the user somehow manages to select a non valid directory
    # Should not occur, but better safe than sorry
    if not os.path.isdir(target_directory):
        print(f"{target_directory} is not a valid directory.")
        return

    #Checks to see if there are any files, if not, offers to undo/"unorganize" the folder
    if not has_files(target_directory): 
        print(f"There are no files in the selected folder.")
        check = questionary.confirm(f"Would you like to try and move files to the root?").ask()
        if(check): 
            rollback(target_directory)
            return
        else: 
            print(f"No changes were made.")
            return
    
    #Itirate each file
    for file in os.listdir(target_directory):
        
        #Get Full Path to make sure it exists
        full_path = os.path.join(target_directory, file)
        if os.path.isfile(full_path):
            #Get the corrent folder to transfer to
            destination_folder = get_folder(file)
            
            #Actually Transfer the file to the correct folder
            fileTranfered = transfer_file(full_path, target_directory, destination_folder)
            
            #If the transfer is successful, adds to the counter to be printed after
            if(fileTranfered):
                transfers = counterTransfer(transfers, destination_folder)
    
    #Organize the dictionary to make it in alphabetical order
    #Sorted returns a list of tuples so we convert back to dictionary 
    if args.verbose:
        transfers = dict(sorted(transfers.items()))
        for type, count in  transfers.items():
            print(f"Transfered {count} item(s) to folder '{type}'.")
    else: 
        print(f"Finished.")
                
                
def get_folder(file: str) -> str: 
    """
    Returns the destination folder based on the extension of the file.
    """
    
    destination_folder = "Others"
    
    file_types = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx'],
        'Videos': ['.mp4', '.mov', '.avi', '.mkv'],
        'Audio': ['.mp3', '.wav', '.flac'],
        'Compressed Archives': ['.zip', '.rar', '.7z'],
        'Fonts' : ['.otf', '.ttf', '.woff', '.woff2'],
        'Applications' : ['.exe', '.bat'],
        'JSON' : ['.json'],
        'Models' : ['.obj', '.blend', '.fbx', '.dwg'],
    }
    
    # Get the extention
    # os.path.splitext returns a list: ['filename', '.extention']
    # Could also use file.split('.'), but would have to add the . again or change the dictionary
    extension = os.path.splitext(file)[1].lower()
    for category, extensions in file_types.items():
        if extension in extensions:
            destination_folder = category
            break
    
    return destination_folder

def transfer_file(full_path: str, target_directory: str, destination_folder: str) -> bool:
    """
    Transfer the file to the destination folder, according to the item sent.
    """
     
    # os.path.join(target_directory, destination_folder) creates the path for the folder
    # i.e. C:/path + /destination_folder
    destination_folder = os.path.join(target_directory, destination_folder)

    # os.path.isdir() checks if the directory exists
    # if it doesn't exist, creates a new folder with the name
    if(not os.path.isdir(destination_folder)):
        os.makedirs(destination_folder, exist_ok = True)
        
    #Move the File to the new folder
    if(shutil.move(full_path, destination_folder)):
        return True
    else:
        return False

def counterTransfer(transfers: dict, destination_folder: str) -> dict: 
    """
    Counts the transfered items to be displayed at the end
    """
    if(destination_folder in transfers): 
        transfers[destination_folder] += 1
    else: 
        transfers[destination_folder] = 1
    
    return transfers

def ask_folder() -> str:
    """
    Prompts the user to select the folder they wish to organize.
    """
    # Reference: https://docs.python.org/3/library/dialog.html#module-tkinter.filedialog
    
    # Create a hidden root window
    root = tk.Tk()
    root.withdraw()           
    
    # Brings dialog to the front
    root.attributes('-topmost', True)  
    
    # Request the folder from the user 
    folder_path = filedialog.askdirectory(title="Select a folder to be organized")
    
    root.destroy()            # Close the root window
    return folder_path

def has_files(folder_path: str) -> bool:
    # Check if there's actually files in the path
    for item in os.listdir(folder_path):
        full_path = os.path.join(folder_path, item)
        if os.path.isfile(full_path):  # Checks if it's a file
            return True
    return False

def rollback(root_path: str) -> None:
    if not os.path.isdir(root_path):
        print(f"Error: {root_path} is not a valid directory.")
        return

    for foldername, subfolders, filenames in os.walk(root_path):
        # Skip the root itself
        if foldername == root_path:
            continue

        for filename in filenames:
            source_path = os.path.join(foldername, filename)
            dest_path = os.path.join(root_path, filename)

            # Avoid overwriting by renaming if needed
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_path):
                    dest_path = os.path.join(root_path, f"{base}_{counter}{ext}")
                    counter += 1

            shutil.move(source_path, dest_path)

    print("All files moved to root folder.")

if __name__ == "__main__":
    main()