import os
import shutil

def main():
    # Get path to Downloads folder
    downloads_folder = os.path.expanduser("~/Downloads")
    
    # Path to sample.pdf (inside package folder)
    current_dir = os.path.dirname(__file__)
    src_file = os.path.join(current_dir, "sample.pdf")  # FIXED here

    # Destination path
    dest_file = os.path.join(downloads_folder, "sample.pdf")
    
    # Copy file
    shutil.copy(src_file, dest_file)
    print(f"✅ sample.pdf has been copied to: {downloads_folder}")
