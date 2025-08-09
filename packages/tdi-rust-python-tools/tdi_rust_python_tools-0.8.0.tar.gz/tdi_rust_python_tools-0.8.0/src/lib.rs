use csv::ReaderBuilder;
use html_escape::decode_html_entities;
use lazy_static::lazy_static;
use pyo3::exceptions::PyTypeError;
use pyo3::exceptions::{PyFileNotFoundError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use regex::Regex;
use rust_xlsxwriter::Workbook;
use std::collections::HashSet;
use std::path::Path;
use std::str;

lazy_static! {
    static ref LT_GT_PATTERN: Regex = Regex::new(
        r"(?x)
        (?P<start>^|\s|>)
        (?P<symbol>[<>])
        (?P<matched_char>[^\s/>])
        "
    )
    .unwrap();
}
/// Take a list of values, split them by a separator, and combine them into a single string with no duplicates.
#[pyfunction]
fn combine_dedupe_values(values: Vec<String>, separator: &str) -> PyResult<String> {
    let mut output: HashSet<String> = HashSet::new();

    for value in values {
        let terms: HashSet<String> = value.split(separator).map(String::from).collect();
        output.extend(terms);
    }

    let mut sorted_output: Vec<&str> = output.iter().map(String::as_str).collect();
    sorted_output.sort();

    Ok(sorted_output.join(", "))
}

/// Replace "<" and ">" symbols with "< " and " >" respectively.
#[pyfunction]
fn fix_lt_gt(value: &str) -> PyResult<String> {
    Ok(LT_GT_PATTERN
        .replace_all(value, "$start$symbol $matched_char")
        .into_owned())
}

/// Unescape HTML characters in a string.
#[pyfunction]
fn unescape_html_chars(value: &str) -> PyResult<String> {
    Ok(decode_html_entities(value).into_owned())
}

lazy_static! {
    static ref TEMPERATURE_PATTERN: Regex = Regex::new(r"(?i)(-?\d+\.?\d*)(\s*[^°]C)").unwrap();
}

/// Clean up temperature values by adding a degree symbol and removing any extra characters.
#[pyfunction]
fn clean_temperature(value: &str) -> PyResult<String> {
    let value = TEMPERATURE_PATTERN.replace_all(value, "$1°C");
    Ok(value.replace("℃", "°C"))
}

lazy_static! {
    static ref CHINESE_CHARS: Regex = Regex::new(r"[\p{Script=Han}]").unwrap();
}

/// Remove Chinese characters from a string.
#[pyfunction]
fn remove_chinese_chars(value: &str) -> PyResult<String> {
    Ok(CHINESE_CHARS.replace_all(value, "").to_string())
}

lazy_static! {
    static ref HTML_PATTERN: Regex = Regex::new(r"<.*?>").unwrap();
}

/// Remove HTML tags from a string.
#[pyfunction]
fn strip_html_tags(value: &str) -> PyResult<String> {
    let result = HTML_PATTERN.replace_all(value, "");
    Ok(result.to_string())
}

lazy_static! {
    static ref FORMULA_PATTERN: Regex = Regex::new(r"([A-Za-z])(\d+)").unwrap();
}

/// Add subscript tags to chemical formulae.
#[pyfunction]
fn add_chemical_formula_subscript(value: &str) -> PyResult<String> {
    let result = FORMULA_PATTERN.replace_all(value, r"$1<sub>$2</sub>");
    Ok(result.to_string())
}

/// Convert a CSV file to an Excel file.
///
/// # Panics
///
/// Panics if the CSV file does not exist or if the file is not a CSV file.
///
/// # Errors
///
/// This function will return an error if the CSV file does not exist or if the file is not a CSV file.
#[pyfunction]
fn convert_to_xlsx(csv_path: &str) -> PyResult<()> {
    // Convert the str path to a path object
    let csv_path = Path::new(csv_path);

    if !csv_path.exists() {
        // Raise a Python FileNotFoundError exception
        let error_message = format!("File not found: {}", csv_path.display());
        let error = PyFileNotFoundError::new_err(error_message);
        return Err(error);
    }

    if csv_path.extension() != Some("csv".as_ref()) {
        // Raise a Python ValueError exception
        let error_message = format!("File is not a CSV file: {}", csv_path.display());
        let error = PyValueError::new_err(error_message);
        return Err(error);
    }

    // Setting up Excel file
    let xlsx_path = csv_path.with_extension("xlsx");
    let mut workbook = Workbook::new();
    let sheet = workbook.add_worksheet();

    // Reading CSV file and writing to Excel file
    let mut csv_reader = match ReaderBuilder::new()
        .has_headers(false)
        .flexible(true)
        .from_path(csv_path)
    {
        Ok(reader) => reader,
        Err(e) => {
            return Err(PyValueError::new_err(format!(
                "Failed to open CSV file: {}",
                e
            )))
        }
    };
    for (row_number, row) in csv_reader.records().enumerate() {
        let row_data = match row {
            Ok(r) => r,
            Err(e) => {
                return Err(PyValueError::new_err(format!(
                    "Failed to read CSV row: {}",
                    e
                )))
            }
        };
        for (column, cell) in row_data.iter().enumerate() {
            // Try to write the cell to the Excel file
            match sheet.write(row_number as u32, column as u16, cell) {
                Ok(_) => (), // Do nothing as the cell was written successfully
                Err(e) => {
                    // Handle the error by trying to truncate the cell
                    eprintln!("Failed to write to cell: {:?}, value: {}", e, cell);

                    // Truncate the cell to 32766 characters (the maximum allowed by Excel)
                    let truncated_cell = if cell.len() > 32766 {
                        &cell[..32766]
                    } else {
                        cell
                    };

                    // If we still can't write the cell, raise an error for Python
                    if let Err(e) = sheet.write(row_number as u32, column as u16, truncated_cell) {
                        let error_message = format!(
                            "Failed to write truncated cell: {:?}, value: {}",
                            e, truncated_cell
                        );
                        eprintln!("{}", error_message);
                        let python_error = PyValueError::new_err(error_message);
                        return Err(python_error);
                    }
                }
            }
        }
    }

    // Finishing up
    if let Err(e) = workbook.save(&xlsx_path) {
        return Err(PyValueError::new_err(format!(
            "Failed to save XLSX file: {}",
            e
        )));
    }

    Ok(())
}

// DictWriter
// Helper to convert a csv::Error into a Python-compatible error.
fn csv_error_to_py_err(err: csv::Error) -> PyErr {
    PyValueError::new_err(err.to_string())
}

#[pyclass]
struct DictWriter {
    // The Python file-like object (e.g., a file handle, an io.StringIO)
    file_object: Py<PyAny>,
    // The header fields, in order.
    fieldnames: Vec<String>,
    // The internal buffer for CSV data
    buffer: Vec<u8>,
    // Buffer for reusing string vectors to reduce allocations
    string_buffer: Vec<String>,
}

#[pymethods]
impl DictWriter {
    #[new]
    fn __new__(py: Python, f: Py<PyAny>, fieldnames: Vec<String>) -> PyResult<Self> {
        // Ensure the file-like object has a 'write' method.
        let file_obj = f.bind(py);
        if !file_obj.hasattr("write")? {
            return Err(PyTypeError::new_err(
                "Argument 'f' must be a file-like object with a .write() method.",
            ));
        }

        // Create a CSV writer that writes to an internal, growable byte buffer.
        // Use standard LF line endings (\n) which is modern practice on Unix systems
        let buffer = Vec::new();

        Ok(DictWriter {
            file_object: f,
            fieldnames: fieldnames.clone(),
            buffer,
            string_buffer: Vec::with_capacity(fieldnames.len()),
        })
    }

    /// Writes the header row to the file.
    pub fn writeheader(&mut self, py: Python) -> PyResult<()> {
        // Create a temporary writer for this operation
        let mut writer = csv::WriterBuilder::new().from_writer(&mut self.buffer);
        writer
            .write_record(&self.fieldnames)
            .map_err(csv_error_to_py_err)?;
        writer
            .flush()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        drop(writer); // Ensure writer is dropped before we use the buffer

        self.flush_buffer_to_py_file(py)
    }

    /// Writes a single dictionary row to the file.
    pub fn writerow(&mut self, py: Python, row: &Bound<PyDict>) -> PyResult<()> {
        // Reuse the string buffer to avoid allocations
        self.string_buffer.clear();
        self.string_buffer.reserve(self.fieldnames.len());

        for key in &self.fieldnames {
            let value = match row.get_item(key) {
                Ok(Some(val)) => val.str()?.to_str()?.to_string(),
                _ => String::new(), // Key doesn't exist
            };
            self.string_buffer.push(value);
        }

        // Create a temporary writer for this operation
        let mut writer = csv::WriterBuilder::new().from_writer(&mut self.buffer);
        writer
            .write_record(&self.string_buffer)
            .map_err(csv_error_to_py_err)?;
        writer
            .flush()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        drop(writer); // Ensure writer is dropped before we use the buffer

        self.flush_buffer_to_py_file(py)
    }

    /// Writes a list of dictionary rows to the file.
    /// Optimized to batch process rows and reduce Python interop overhead.
    pub fn writerows(&mut self, py: Python, rows: Vec<Bound<PyDict>>) -> PyResult<()> {
        // Create a single writer for all rows to maximize efficiency
        let mut writer = csv::WriterBuilder::new().from_writer(&mut self.buffer);

        // Process all rows first, then flush once at the end
        for row in &rows {
            // Reuse the string buffer to avoid allocations
            self.string_buffer.clear();
            self.string_buffer.reserve(self.fieldnames.len());

            for key in &self.fieldnames {
                let value = match row.get_item(key) {
                    Ok(Some(val)) => val.str()?.to_str()?.to_string(),
                    _ => String::new(), // Key doesn't exist
                };
                self.string_buffer.push(value);
            }

            writer
                .write_record(&self.string_buffer)
                .map_err(csv_error_to_py_err)?;
        }

        // Flush the writer and drop it before using the buffer
        writer
            .flush()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        drop(writer);

        // Single flush at the end for better performance
        self.flush_buffer_to_py_file(py)
    }
}

impl DictWriter {
    /// A helper method to take the contents of the internal buffer,
    /// write them to the Python file object, and clear the buffer.
    /// Optimized to reuse the buffer efficiently.
    fn flush_buffer_to_py_file(&mut self, py: Python) -> PyResult<()> {
        // Only proceed if there's actually data to write
        if !self.buffer.is_empty() {
            // Convert the UTF-8 bytes to a Python string
            let py_string =
                str::from_utf8(&self.buffer).map_err(|e| PyValueError::new_err(e.to_string()))?;

            // Call the write() method on the Python file object
            self.file_object.call_method1(py, "write", (py_string,))?;

            // Clear the buffer for reuse
            self.buffer.clear();
        }

        Ok(())
    }
}

/// A Python module implemented in Rust.
#[pymodule(name = "tdi_rust_python_tools")]
fn string_sum(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(combine_dedupe_values, m)?)?;
    m.add_function(wrap_pyfunction!(fix_lt_gt, m)?)?;
    m.add_function(wrap_pyfunction!(unescape_html_chars, m)?)?;
    m.add_function(wrap_pyfunction!(clean_temperature, m)?)?;
    m.add_function(wrap_pyfunction!(remove_chinese_chars, m)?)?;
    m.add_function(wrap_pyfunction!(strip_html_tags, m)?)?;
    m.add_function(wrap_pyfunction!(add_chemical_formula_subscript, m)?)?;
    m.add_function(wrap_pyfunction!(convert_to_xlsx, m)?)?;
    m.add_class::<DictWriter>()?;
    Ok(())
}
