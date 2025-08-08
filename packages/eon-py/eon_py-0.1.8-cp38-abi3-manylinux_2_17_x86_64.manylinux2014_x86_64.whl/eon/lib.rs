use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyFloat, PyLong, PyBool};
use pyo3::exceptions::PyValueError;
use eon::{Value, Map, Number, Variant};
use vec1::Vec1;

/// Convert an eon::Value to a Python object
fn eon_value_to_python(py: Python, value: &Value) -> PyResult<PyObject> {
    match value {
        Value::Null => Ok(py.None()),
        Value::Bool(b) => Ok(b.to_object(py)),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.to_object(py))
            } else if let Some(f) = n.as_f64() {
                Ok(f.to_object(py))
            } else {
                Ok(n.to_string().to_object(py))
            }
        }
        Value::String(s) => Ok(s.to_object(py)),
        Value::List(arr) => {
            let list = PyList::empty_bound(py);
            for item in arr {
                list.append(eon_value_to_python(py, item)?)?;
            }
            Ok(list.to_object(py))
        }
        Value::Map(obj) => {
            let dict = PyDict::new_bound(py);
            for (key, val) in obj {
                let key_str = if let Value::String(s) = key {
                    s.clone()
                } else {
                    key.to_string()
                };
                dict.set_item(key_str, eon_value_to_python(py, val)?)?;
            }
            Ok(dict.to_object(py))
        }
        Value::Variant(variant) => {
            let dict = PyDict::new_bound(py);
            dict.set_item("__variant__", variant.name.clone())?;
            let list = PyList::empty_bound(py);
            for val in &variant.values {
                list.append(eon_value_to_python(py, val)?)?;
            }
            dict.set_item("__values__", list)?;
            Ok(dict.to_object(py))
        }
    }
}

/// Convert a Python object to an eon::Value
fn python_to_eon_value(obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    // Check for None
    if obj.is_none() {
        return Ok(Value::Null);
    }
    
    // Check for bool (must come before int since bool is a subclass of int in Python)
    if let Ok(b) = obj.downcast::<PyBool>() {
        return Ok(Value::Bool(b.is_true()));
    }
    
    // Check for int
    if let Ok(i) = obj.downcast::<PyLong>() {
        if let Ok(val) = i.extract::<i64>() {
            return Ok(Value::Number(Number::from(val)));
        }
    }
    
    // Check for float
    if let Ok(f) = obj.downcast::<PyFloat>() {
        if let Ok(val) = f.extract::<f64>() {
            return Ok(Value::Number(Number::from(val)));
        }
    }
    
    // Check for string
    if let Ok(s) = obj.extract::<String>() {
        return Ok(Value::String(s));
    }
    
    // Check for list
    if let Ok(list) = obj.downcast::<PyList>() {
        let mut arr = Vec::new();
        for item in list.iter() {
            arr.push(python_to_eon_value(&item)?);
        }
        return Ok(Value::List(arr));
    }
    
    // Check for dict
    if let Ok(dict) = obj.downcast::<PyDict>() {
        // Check if this is a special variant representation
        if let Ok(Some(variant_name)) = dict.get_item("__variant__") {
            if let Ok(Some(values)) = dict.get_item("__values__") {
                if let Ok(name) = variant_name.extract::<String>() {
                    if let Ok(values_list) = values.downcast::<PyList>() {
                        let mut variant_values = Vec::new();
                        for item in values_list.iter() {
                            variant_values.push(python_to_eon_value(&item)?);
                        }
                        // Vec1 requires at least one element
                        if let Ok(vec1) = Vec1::try_from_vec(variant_values) {
                            return Ok(Value::Variant(Variant {
                                name,
                                values: vec1,
                            }));
                        } else {
                            return Err(PyValueError::new_err("Variant must have at least one value"));
                        }
                    }
                }
            }
        }
        
        // Regular dict -> Map conversion
        let mut pairs = Vec::new();
        for (key, value) in dict.iter() {
            let key_str = key.extract::<String>()?;
            pairs.push((Value::String(key_str), python_to_eon_value(&value)?));
        }
        return Ok(Value::Map(Map::from_iter(pairs)));
    }
    
    Err(PyValueError::new_err(format!(
        "Cannot convert Python type {} to Eon value",
        obj.get_type().name()?
    )))
}

/// Parse an EON string into a Python object
#[pyfunction]
fn loads(py: Python, text: &str) -> PyResult<PyObject> {
    match eon::from_str::<Value>(text) {
        Ok(value) => eon_value_to_python(py, &value),
        Err(e) => Err(PyValueError::new_err(format!("Failed to parse EON: {}", e))),
    }
}

/// Serialize a Python object to an EON formatted string
#[pyfunction]
#[pyo3(signature = (obj, indent=None, sort_keys=None))]
fn dumps(obj: &Bound<'_, PyAny>, indent: Option<usize>, sort_keys: Option<bool>) -> PyResult<String> {
    let value = python_to_eon_value(obj)?;
    
    // Note: The eon 0.2.0 Value::to_string() doesn't support custom formatting options
    // The indent and sort_keys parameters are kept for API compatibility but not used yet
    // TODO: When eon library supports these options, implement them
    let _ = indent;
    let _ = sort_keys;
    
    Ok(value.to_string())
}

/// Python module definition
#[pymodule]
fn _eon(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(loads, m)?)?;
    m.add_function(wrap_pyfunction!(dumps, m)?)?;
    Ok(())
}