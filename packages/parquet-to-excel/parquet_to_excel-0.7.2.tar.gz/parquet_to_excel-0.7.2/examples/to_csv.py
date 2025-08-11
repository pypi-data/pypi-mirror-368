from parquet_to_excel import parquet_file_to_csv, parquet_files_to_csv

parquet_file_to_csv(
    r"D:\Projects\RustTool\data\.duck\yo_dxzh\source=合并报表公司主体及内部客商编码（管理责任人：刘露）.xlsx\data.parquet", 
    r"D:\Felix\Desktop\out1.csv", 
    header_labels={"ddbm": "地点编码"},
    select_columns=set(["sheet", "yjkm", "yjkmsm"]))

parquet_files_to_csv(
    r"D:\Projects\RustTool\data\.duck\yo_dxzh", 
    r"D:\Felix\Desktop\out2.csv", 
    header_labels={"ddbm": "地点编码"},
    select_columns=set(["sheet", "yjkm", "yjkmsm"]))

