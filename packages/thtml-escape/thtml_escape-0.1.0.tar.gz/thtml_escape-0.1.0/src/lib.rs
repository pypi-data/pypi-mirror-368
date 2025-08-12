use std::borrow::Cow;

use pyo3::prelude::*;

#[pyfunction]
fn encode(s: &str) -> Cow<'_, str> {
    html_escape::encode_safe(s)
}

#[pyfunction]
fn decode(s: &str) -> Cow<'_, str> {
    html_escape::decode_html_entities(s)
}

#[pymodule]
fn thtml_escape(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encode, m)?)?;
    m.add_function(wrap_pyfunction!(decode, m)?)?;
    Ok(())
}
