import os
import shutil
import argparse

'''
Usage: python copy_midi_files.py /path/to/source/directory /path/to/destination/directory

Finds all midi files in sub directory and copies them to the root of a new directory
'''

def copy_midi_files(source_dir, destination_dir):
    '''
    Finds all midi files in sub directory and copies them to the root of a new directory
    '''
    # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Counter for skipped files
    skipped_files = 0

    # Walk through the source directory
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('.mid', '.midi')):
                source_path = os.path.join(root, file)
                destination_path = os.path.join(destination_dir, file)

                # Check if the file already exists in the destination
                if os.path.exists(destination_path):
                    print(f"Skipping duplicate file: {file}")
                    skipped_files += 1
                else:
                    try:
                        shutil.copy2(source_path, destination_path)
                        print(f"Copied: {file}")
                    except Exception as e:
                        print(f"Error copying {file}: {str(e)}")
                        skipped_files += 1

    return skipped_files

def main():
    parser = argparse.ArgumentParser(description="Copy MIDI files from source to destination directory.")
    parser.add_argument("source", help="Source directory containing MIDI files")
    parser.add_argument("destination", help="Destination directory for copied MIDI files")
    args = parser.parse_args()

    source_dir = args.source
    destination_dir = args.destination

    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    print(f"Copying MIDI files from {source_dir} to {destination_dir}")
    skipped_files = copy_midi_files(source_dir, destination_dir)

    print(f"\nCopy operation completed.")
    print(f"Skipped files due to duplicates or errors: {skipped_files}")

if __name__ == "__main__":
    main()
