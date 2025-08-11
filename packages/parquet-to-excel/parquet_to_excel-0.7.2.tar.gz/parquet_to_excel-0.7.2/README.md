# parquet_to_excel
A tool to convert parquet file to an/a excel/csv file in rust with constant memory, both a single parquet file and a folder of parquet files are supported.
You can also use python or rust to call it. The python package name is parquet_to_excel too. you can install it by `pip install parquet_to_excel`. If you could not install this package correctly, you can try to install rust and maturin (`pip install maturin`) first. Then you can try again.

# Functions
1. parquet_file_to_csv: convert a single parquet file to a csv file
2. parquet_files_to_csv: convert a folder of parquet files to a csv file
1. parquet_file_to_xlsx: convert a single parquet file to an excel file
2. parquet_files_to_xlsx: convert a folder of parquet files to an excel file

# Python Examples
1. parquet to csv
```python
from parquet_to_excel import parquet_file_to_csv, parquet_files_to_csv

parquet_file_to_csv(
    r"D:\Projects\RustTool\data\.duck\yo_dxzh\source=zzz.xlsx\data.parquet", 
    r"D:\Felix\Desktop\out1.csv", 
    header_labels={"ddbm": "地点编码"},
    select_columns=set(["sheet", "yjkm", "yjkmsm"]))

parquet_files_to_csv(
    r"D:\Projects\RustTool\data\.duck\yo_dxzh", 
    r"D:\Felix\Desktop\out2.csv", 
    header_labels={"ddbm": "地点编码"},
    select_columns=set(["sheet", "yjkm", "yjkmsm"]))
```

2. parquet to xlsx
```python
from parquet_to_excel import parquet_file_to_xlsx, parquet_files_to_xlsx

# write all data into one sheet
parquet_file_to_xlsx(
    r"D:\Projects\RustTool\data\.duck\yo_dxzh\source=合并报表公司主体及内部客商编码（管理责任人：刘露）.xlsx\data.parquet", 
    r"D:\Felix\Desktop\out1.xlsx", 
    sheet_name="data", 
    header_labels={"ddbm": "地点编码"},
    select_columns=set(["sheet", "yjkm", "yjkmsm"]))

# write all data into different sheets by the value of column "sheet"
parquet_files_to_xlsx(
    r"D:\Projects\RustTool\data\.duck\yo_dxzh", 
    r"D:\Felix\Desktop\out2.xlsx", 
    sheet_column = "sheet", 
    header_labels={"ddbm": "地点编码"},
    select_columns=set(["sheet", "yjkm", "yjkmsm"]))
```
