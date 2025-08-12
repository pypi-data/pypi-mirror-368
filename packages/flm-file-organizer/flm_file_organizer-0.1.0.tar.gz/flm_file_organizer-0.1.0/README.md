# 📂 File Organizer

A simple Python utility that organizes files in a selected folder into categorized subfolders based on their file extensions.  
It can also **reverse the organization** by moving files from subfolders back to the root folder — useful for testing or restoring the original state.

---

## ✨ Features
- Automatically categorizes files into folders like **Images**, **Documents**, **Videos**, **Audio**, **Applications**, and more.
- Lets you choose:
  - The **current script directory**.
  - Or any folder via a **folder selection dialog**.
- Detects if a folder has **no files** and offers to **rollback** (un-organize) the folder.
- Prevents overwriting by automatically renaming duplicate files during rollback.
- Supports multiple file types through a configurable mapping.

---

## 📂 Example Folder Structure

**Before**  

```
project/
├── cat.jpg
├── resume.pdf
├── music.mp3
```

**After**  
```
├── Images/
│ └── cat.jpg
├── Documents/
│ └── resume.pdf
├── Audio/
│ └── music.mp3
```

