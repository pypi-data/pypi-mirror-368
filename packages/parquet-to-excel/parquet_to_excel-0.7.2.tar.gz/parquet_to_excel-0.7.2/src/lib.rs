use serde::Deserialize;
use std::collections::{HashMap, HashSet};
use pyo3::{exceptions::PyException, prelude::{pyclass, pyfunction, pymodule, wrap_pyfunction, Bound, PyModule, PyModuleMethods as _, PyResult}, pymethods};

use ::parquet_to_excel::feishu::{AppConfig, BitTableInfo, download_feishu_file, upload_parquet_folder_to_bittable};
use ::parquet_to_excel::{parq_file_to_csv, parq_folder_to_csv, parq_file_to_xlsx, parq_folder_to_xlsx, utils::load_toml, xlsx::{XlsxMaps, folder_to_parquet}};


#[pyfunction]
#[pyo3(signature = (source, destination, header_labels=HashMap::new(), select_columns=HashSet::new()))]
fn parquet_file_to_csv(source: String, destination: String, header_labels: HashMap<String, String>, select_columns: HashSet<String>) -> PyResult<()> {
    match parq_file_to_csv(source, destination, &header_labels, &select_columns) {
        Ok(_) => {
            Ok(())
        },
        Err(e) => {
            Err(PyException::new_err(e.to_string()))
        }
    }
}


#[pyfunction]
#[pyo3(signature = (source, destination, header_labels=HashMap::new(), select_columns=HashSet::new()))]
fn parquet_files_to_csv(source: String, destination: String, header_labels: HashMap<String, String>, select_columns: HashSet<String>) -> PyResult<()> {
    match parq_folder_to_csv(source, destination, &header_labels, &select_columns) {
        Ok(_) => {
            Ok(())
        },
        Err(e) => {
            Err(PyException::new_err(e.to_string()))
        }
    }
}


#[pyfunction]
#[pyo3(signature = (source, destination, sheet_name=None, sheet_column=None, header_labels=HashMap::new(), select_columns=HashSet::new()))]
fn parquet_file_to_xlsx(source: String, destination: String, sheet_name: Option<String>, sheet_column: Option<String>, header_labels: HashMap<String, String>, select_columns: HashSet<String>) -> PyResult<()> {
    match parq_file_to_xlsx(source, destination, sheet_name, sheet_column, &header_labels, &select_columns) {
        Ok(_) => {
            Ok(())
        },
        Err(e) => {
            Err(PyException::new_err(e.to_string()))
        }
    }
}


#[pyfunction]
#[pyo3(signature = (source, destination, sheet_name=None, sheet_column=None, header_labels=HashMap::new(), select_columns=HashSet::new()))]
fn parquet_files_to_xlsx(source: String, destination: String, sheet_name: Option<String>, sheet_column: Option<String>, header_labels: HashMap<String, String>, select_columns: HashSet<String>) -> PyResult<()> {
    match parq_folder_to_xlsx(source, destination, sheet_name, sheet_column, &header_labels, &select_columns) {
        Ok(_) => {
            Ok(())
        },
        Err(e) => {
            Err(PyException::new_err(e.to_string()))
        }
    }
}

#[derive(Deserialize)]
struct XlsxMapSetting{
    xlsx_maps: Vec<XlsxMaps>,
}

// 写一个python函数调用parquet_to_excel库的，folder_to_parquet函数
// folder_to_parquet(mps: Vec<XlsxMaps>, datadir: &str) -> Result<(), Box<dyn std::error::Error>>
#[pyfunction]
fn xlsx_folder_to_parquet(toml_path: String, datadir: String) -> PyResult<Vec<HashMap<String, Vec<(String, String, String, String)>>>> {
    match load_toml::<&String, XlsxMapSetting>(&toml_path) {
        Ok(setting) => {
            match folder_to_parquet(setting.xlsx_maps, datadir.as_str()) {
                Ok(msg) => {
                    Ok(msg)
                },
                Err(e) => {
                    Err(PyException::new_err(e.to_string()))
                }
            }
        },
        Err(e) => {
            Err(PyException::new_err(e.to_string()))
        }
    }
}

/// 上传多维表格任务
#[derive(Deserialize, Debug, Clone)]
pub struct BtUploadMission {
    pub label: String,
    pub local: String,           //  本地数据文件
    #[serde(default)]
    pub clear: bool,             //  上传数据前是否先清空，默认为false
    pub bittable: BitTableInfo
}

#[derive(Deserialize)]
struct BitTableSetting {
    bt_uploads: Vec<BtUploadMission>
}

#[pyfunction]
fn parquet_folder_to_bittable(app_config: PyAppConfig, toml_path: String, data_dir: String) -> PyResult<HashMap<String, Vec<(String, usize, usize, String)>>> {
    match load_toml::<&String, BitTableSetting>(&toml_path) {
        Ok(setting) => {
            let app_config = app_config.to_rust();
            let mut failds = vec![];
            let mut succeeds = vec![];
            for bt_uploads in &setting.bt_uploads {
                // (fsapp: &AppConfig, bittable: &BitTableInfo, local: &str, clear: bool, log_target: &str)
                match upload_parquet_folder_to_bittable(&app_config, &bt_uploads.bittable, &format!("{data_dir}/{}", bt_uploads.local), bt_uploads.clear, "unused") {
                    Ok((dels, ins)) => {
                        succeeds.push((bt_uploads.label.clone(), dels, ins, String::new()));
                    },
                    Err(e) => {
                        failds.push((bt_uploads.label.clone(), 0, 0, e.to_string()));
                    }
                }
            }

            let mut res = HashMap::new();
            res.insert("succeeds".into(), succeeds);
            res.insert("failds".into(), failds);
            Ok(res)

        },
        Err(e) => {
            Err(PyException::new_err(e.to_string()))
        }
    }
}

// 为BitTableInfo实现pyclass，以支持从python对象转换为rust对象
#[pyclass]
#[derive(Deserialize, Clone)]
struct PyAppConfig {
    pub app_id: String,
    pub app_secret: String,
    pub redirect_uri: String,
}

impl PyAppConfig {
    fn to_rust(self) -> AppConfig {
        AppConfig {
            app_id: self.app_id,
            app_secret: self.app_secret,
            redirect_uri: self.redirect_uri
        }
    }
}

#[pymethods]
impl PyAppConfig {
    #[new]
    fn new(app_id: String, app_secret: String, redirect_uri: String) -> Self {
        Self {
            app_id,
            app_secret,
            redirect_uri
        }
    }
}

#[pyfunction]
fn download_feishu_bitable(app_config: PyAppConfig, doc_token: String, save_to: String) -> PyResult<String> {
    let app_config = app_config.to_rust();
    let log_target = "parquet_to_excel";

    // download_bitable_sync<T: Serialize + ?Sized>(args: &T, app_info: &AppConfig, file_token: &str, save_as: &str, log_target: &str)
    // pub fn download_feishu_file(app_info: &AppConfig, doc_token: &str, doc_type: &str, file_type: &str, save_to: &str, log_target: &str)
    match download_feishu_file(&app_config, &doc_token, "bitable", "xlsx", &save_to, &log_target) {
        Ok(res) => {
            Ok(res.display().to_string())
        },
        Err(e) => {
            Err(PyException::new_err(e.to_string()))
        }
    }
}

#[pyfunction]
fn download_feishu_spreadsheet(app_config: PyAppConfig, doc_token: String, save_to: String) -> PyResult<String> {
    let app_config = app_config.to_rust();
    let log_target = "parquet_to_excel";
    // download_bitable_sync<T: Serialize + ?Sized>(args: &T, app_info: &AppConfig, file_token: &str, save_as: &str, log_target: &str)
    match download_feishu_file(&app_config, &doc_token, "sheet", "xlsx", &save_to, &log_target) {
        Ok(res) => {
            Ok(res.display().to_string())
        },
        Err(e) => {
            Err(PyException::new_err(e.to_string()))
        }
    }
}


/// A Python module implemented in Rust.
#[pymodule]
fn parquet_to_excel(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parquet_file_to_csv, m)?)?;
    m.add_function(wrap_pyfunction!(parquet_files_to_csv, m)?)?;
    m.add_function(wrap_pyfunction!(parquet_file_to_xlsx, m)?)?;
    m.add_function(wrap_pyfunction!(parquet_files_to_xlsx, m)?)?;
    m.add_function(wrap_pyfunction!(xlsx_folder_to_parquet, m)?)?;
    m.add_function(wrap_pyfunction!(download_feishu_bitable, m)?)?;
    m.add_function(wrap_pyfunction!(download_feishu_spreadsheet, m)?)?;
    m.add_function(wrap_pyfunction!(parquet_folder_to_bittable, m)?)?;
    m.add_class::<PyAppConfig>()?;

    Ok(())
}


// development build
// maturin develop --release
// publish to pypi
// maturin publish --username __token__  --release