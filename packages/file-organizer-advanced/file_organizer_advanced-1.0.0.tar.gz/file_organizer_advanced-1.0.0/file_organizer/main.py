import os
import shutil
import sys

# File type categories
FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".m4a"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
    "Apps": [".dmg", ".pkg", ".app"],
    "Others": []
}

def get_category(filename):
    """Return the category name based on file extension."""
    ext = os.path.splitext(filename)[1].lower()
    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category
    return "Others"

def organize_folder(folder_path):
    """Organize files into category folders based on extension."""
    if not os.path.exists(folder_path):
        print(f"❌ Error: '{folder_path}' does not exist.")
        return

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        # Skip all folders except .app bundles
        if os.path.isdir(item_path) and not item.lower().endswith(".app"):
            continue

        # Only process files or .app bundles
        category = get_category(item)
        target_folder = os.path.join(folder_path, category)
        os.makedirs(target_folder, exist_ok=True)

        target_path = os.path.join(target_folder, item)
        shutil.move(item_path, target_path)
        print(f"✅ Moved: {item} → {category}")

    print(f"\n📂 Folder '{folder_path}' organized successfully!")

def main():
    default_path = os.path.expanduser("~/Downloads")

    # Priority: CLI argument > User input > Default path
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        user_path = input(f"Enter folder path to organize (default: {default_path}): ").strip()
        folder_path = user_path if user_path else default_path

    organize_folder(folder_path)

if __name__ == "__main__":
    main()