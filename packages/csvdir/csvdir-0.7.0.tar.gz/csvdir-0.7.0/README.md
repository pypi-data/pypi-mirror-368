# 📂 csvdir  
**A blazing-fast, lightweight toolkit for reading and iterating over entire directories of CSV files.**  

`csvdir` lets you treat a folder full of CSVs as if it were a single dataset — no tedious file loops, no clumsy header mismatches. Whether you’re working with a few files or thousands, `csvdir` is built for speed, simplicity, and flexibility.  

---

## ✨ Features  

- 🔄 **Directory-wide iteration** – Read every CSV in a folder as a single stream of rows  
- 🧩 **Header validation** – Enforce matching headers or skip mismatched files  
- 📏 **Chunked reading** – Stream large datasets without blowing up memory  
- 🎯 **Configurable dialect** – Set `delimiter`, `quotechar`, `encoding`, and more  
- 📂 **Recursive scanning** – Optionally include subdirectories  
- 🐼 **Pandas-ready** – Use `CsvDirFile` directly with `pandas.read_csv`  
- 🚫 **Hidden file handling** – Easily skip or include hidden files  

---

## 📦 Installation  

```bash
pip install csvdir
```

---

## 🔹 Basic Usage  

### Iterate over all rows in a directory  
```python
from csvdir import read_dir

for row in read_dir("/data/csvs"):
    print(row)  # Each row is a dict mapping column names to string values
```

---

### Enforce matching headers across files  
```python
for row in read_dir("/data/csvs", strict_headers=True, on_mismatch="skip"):
    print(row)  
```
- `strict_headers=True` → Uses the first file’s header as the standard  
- `on_mismatch`:
  - `"skip"` → skip files with different headers  
  - `"error"` → raise a `ValueError` if a mismatch is found  

---

### Chunked iteration for large files  
```python
for chunk in read_dir("/data/csvs", chunksize=1000):
    # chunk is a list of up to 1000 rows
    process(chunk)
```

---

## 🆕 Pandas Compatibility — `CsvDirFile`  

`CsvDirFile` behaves like a file object that merges multiple CSVs into one continuous file-like stream — perfect for `pandas.read_csv`.

```python
import pandas as pd
from csvdir import CsvDirFile

f = CsvDirFile("/data/csvs", strict_headers=True, on_mismatch="skip")
df = pd.read_csv(f)
print(df.head())
```

**Advantages:**  
- Pandas reads multiple CSVs as if they were one file  
- Automatically skips duplicate headers between files  
- Honors header validation rules  

---

## 📂 API Overview  

### `read_dir(path, **options)`  
Iterates through rows (or chunks) of CSV files in a directory.  

**Parameters:**  
- `extension`: File extension (default `"csv"`)  
- `delimiter`, `quotechar`, `escapechar`: CSV parsing options  
- `encoding`: File encoding (default `"utf-8"`)  
- `strict_headers`: Enforce header consistency (default `False`)  
- `on_mismatch`: `"skip"` or `"error"`  
- `chunksize`: If set, returns lists of rows instead of single rows  
- `recurse`: Include subdirectories (default `False`)  
- `case_insensitive`: Match extensions case-insensitively (default `True`)  
- `include_hidden`: Include dotfiles (default `False`)  

---

## 💡 Tips & Edge Cases  

- **Hidden Files:** By default, hidden files are ignored; set `include_hidden=True` to include them  
- **Large Files:** Use `chunksize` to prevent memory overload  
- **Mixed Encodings:** `csvdir` can detect BOMs and handle mixed encodings automatically  
- **Header Order:** `strict_headers=True` compares exact header order  

---

## 📜 License  

MIT License © 2025  
