import toml
from parquet_to_excel import PyAppConfig
from parquet_to_excel import xlsx_folder_to_parquet, download_feishu_spreadsheet, download_feishu_bitable, parquet_folder_to_bittable

with open(r"D:\Projects\RustTool\data\_feishu.toml", "r", encoding="utf-8") as f:
    data = f.read()
    setting = toml.loads(data)

app_config = PyAppConfig(
    app_id=setting["app_id"],
    app_secret=setting["app_secret"],
    redirect_uri=setting["redirect_uri"]
)

# 下载飞书多维表格数据
download_feishu_bitable(
    app_config,
    "GSFMbDpakaP1ChsDQhwcwI4KnXb",
    r"data/bittable"
)

# 下载飞书表格数据
download_feishu_spreadsheet(
    app_config, 
    "KbPXsEkSGhm2e7t803dcVKtwnCe", 
    r"data/spreadsheet"
)

# 将xlsx文件转换为parquet
# print(xlsx_folder_to_parquet(
#     r"D:\Projects\RustTool\settings\etl_tool_dev.toml", 
#     r"data"
# ))

# 将parquet上传多维表格
# print(parquet_folder_to_bittable(
#     app_config,
#     r"D:\Projects\RustTool\settings\etl_tool_dev.toml",
#     r"data"
# ))



