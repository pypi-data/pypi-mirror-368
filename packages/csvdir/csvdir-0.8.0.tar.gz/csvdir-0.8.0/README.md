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
- 🪶 **Column selection** – Iterate over just one column or a subset of columns  
- 📛 **Flexible naming** – Choose between file stems (`"data"`) or full filenames (`"data.csv"`) in enumerations  

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
    print(row)
```
**Example output**  
```
{'id': '1', 'name': 'Alice', 'age': '30'}
{'id': '2', 'name': 'Bob', 'age': '25'}
{'id': '3', 'name': 'Charlie', 'age': '40'}
```

---

### Enforce matching headers across files  
```python
for row in read_dir("/data/csvs", strict_headers=True, on_mismatch="skip"):
    print(row)
```
**Example output**  
```
{'id': '1', 'name': 'Alice', 'age': '30'}
{'id': '2', 'name': 'Bob', 'age': '25'}
```

---

### Chunked iteration for large files  
```python
for chunk in read_dir("/data/csvs", chunksize=2):
    print(chunk)
```
**Example output**  
```
[{'id': '1', 'name': 'Alice'}, {'id': '2', 'name': 'Bob'}]
[{'id': '3', 'name': 'Charlie'}]
```

---

### Enumerating rows with names or paths  
```python
r = read_dir("/data/csvs")

for name, row in r.with_names():
    print(name, row)
```
**Example output**  
```
data1 {'id': '1', 'name': 'Alice'}
data1 {'id': '2', 'name': 'Bob'}
```

```python
for path, row in r.with_paths():
    print(path, row)
```
**Example output**  
```
/data/csvs/data1.csv {'id': '1', 'name': 'Alice'}
/data/csvs/data1.csv {'id': '2', 'name': 'Bob'}
```

---

### Selecting a single column  
```python
r = read_dir("/data/csvs")

for value in r.iter_column("name"):
    print(value)
```
**Example output**  
```
Alice
Bob
Charlie
```

```python
for values in read_dir("/data/csvs", chunksize=2).iter_column_chunks("name"):
    print(values)
```
**Example output**  
```
['Alice', 'Bob']
['Charlie']
```

---

### Selecting multiple columns  
```python
r = read_dir("/data/csvs")

for row in r.select_columns(["name", "age"]):
    print(row)
```
**Example output**  
```
{'name': 'Alice', 'age': '30'}
{'name': 'Bob', 'age': '25'}
```

```python
for chunk in read_dir("/data/csvs", chunksize=2).select_columns_chunks(["name", "age"]):
    print(chunk)
```
**Example output**  
```
[{'name': 'Alice', 'age': '30'}, {'name': 'Bob', 'age': '25'}]
[{'name': 'Charlie', 'age': '40'}]
```

---

## 🆕 Pandas Compatibility — `CsvDirFile`  

```python
import pandas as pd
from csvdir import CsvDirFile

f = CsvDirFile("/data/csvs", strict_headers=True, on_mismatch="skip")
df = pd.read_csv(f)
print(df.head())
```
**Example output**  
```
   id   name  age
0   1  Alice   30
1   2    Bob   25
2   3 Charlie   40
```

---

## 📊 Iterator Quick Reference  

| Method | Returns | Chunked Version | Naming Style |
|--------|---------|-----------------|--------------|
| `.with_names()` | `(stem, row_dict)` | `.enumerate()` → `(stem, list[row_dict])` | File stem (`"data"`) |
| `.with_paths()` | `(full_path, row_dict)` | `.with_paths_chunks()` → `(full_path, list[row_dict])` | Full path |
| `.iter_column(col)` | `(stem, value)` | `.iter_column_chunks(col)` → `(stem, list[value])` | File stem |
| `.select_columns(cols)` | `(stem, dict)` | `.select_columns_chunks(cols)` → `(stem, list[dict])` | File stem |
| Default (`__iter__`) | `row_dict` | Chunked default → `list[row_dict]` | N/A |

---

## 💡 Tips & Edge Cases  

- **Hidden Files:** By default, hidden files are ignored; set `include_hidden=True` to include them  
- **Large Files:** Use `chunksize` to prevent memory overload  
- **Mixed Encodings:** `csvdir` can detect BOMs and handle mixed encodings automatically  
- **Header Order:** `strict_headers=True` compares exact header order  
- **Name vs Path:** `.with_names()` and `.enumerate()` return the **stem** (`file.stem`), while `.with_paths()` returns the full path  

---

## 📜 License  

MIT License © 2025  
