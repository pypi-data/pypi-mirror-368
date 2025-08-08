# UltraQuery

UltraQuery is a fast and lightweight Python module + CLI tool for:

- 📂 Reading `.csv`, `.txt`, and `.sqlite` files  
- 👁️ Viewing data or building DataFrame-like structures  
- 📈 Plotting directly from terminal using CLI flags  
- ⚙️ Powered by a custom **C++ engine** for high performance  

---

## 🔖 Version

- **v0.1.0**
- Released: **08-08-2025**
- Authors: Mayank Chaudhary, Krishna Agarwal, Abhedhya Faujdar

---

## 📦 Installation

```bash
pip install UltraQuery
```

- [GitHub Repository](https://github.com/krishna-agarwal44546/UltraQuery)  
- [PyPI Page](https://pypi.org/project/UltraQuery/)

---

## 🐍 Python Usage

```python
from ultraquery import UltraQuery 

uq = UltraQuery.UltraQuery() 

data={
    "name" : ["adam","james","sofia"],
    "age" : [23,63,87]
}

uq.viewdata("cars.csv", "year") 
uq.df("cars.csv", limit=100) 
uq.plot("cars.csv", xcol="year", ycol="price", graph_type="line")
uq.read_dict(data)
```

---

## 💻 CLI Usage

```bash
ultraquery -f cars.csv -l 50 -df
ultraquery -f cars.csv -l 100 -plt -x year -y price -typ line
```

---

## 🚩 CLI Flags

| Flag          | Description                       |
|---------------|-----------------------------------|
| `-f`          | Path to CSV/SQL file              |
| `-df`         | Show data as a table              |
| `-l`          | Limit number of rows to load      |
| `-plt`        | Enable graph plotting             |
| `-x`          | Set X-axis column                 |
| `-y`          | Set Y-axis column                 |
| `-typ`        | Type of plot (`bar`, `pie`, etc.) |
| `-sql`        | Enable SQLite mode                |
| `table`       | Specify SQLite table              |
| `column_list` | View column list                  |
| `vc`          | View raw column data              |
| `dict`        | Get Dataframe from Dictionary     |
| `col`         | Enter Column                      |

---

## 🧠 Available Functions

```python
viewcolumn(file)             # List columns from a CSV  
viewdata(file, col)          # Display elements of column col 
df(file, n)                  # Load data into custom frame  
viewsql(file, table, n)      # Load rows from SQLite  
plot(file, x, y, typ)        # Plot selected columns
read_dict(dictionary)        # Give dataframe directly from a dictionary
```

### ✅ Supported Plot Types
- bar
- line
- scatter
- pie
- histogram

---

## 📊 Example

```bash
ultraquery -f sales.csv -l 100 -plt -x month -y revenue -typ bar
```

---

## 🚀 Features

- ⚡ Fast CSV reading via C++ engine  
- 🧪 Native Python class interface  
- 🧭 CLI for quick data exploration  
- 🎨 Easy plotting with matplotlib  
- 🗄️ SQLite table reading support  

---

## 🔍 Engine Details

- Uses native shared library (`engine.dll` / `engine.so`)  
- Loaded via `ctypes`  
- Core C++ functions: `readcsv`, `columnsget`, `getdata`, `dataframe`,`read_dict`

---

## 👥 Contributors

- [Contributors.txt](https://github.com/krishna-agarwal44546/UltraQuery/blob/main/Contributors.txt)

## 📄 License

- [LICENSE.txt](https://github.com/krishna-agarwal44546/UltraQuery/blob/main/LICENSE.txt)

---
