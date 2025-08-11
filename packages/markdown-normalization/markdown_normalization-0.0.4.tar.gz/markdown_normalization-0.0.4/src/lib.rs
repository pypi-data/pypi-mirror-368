use memchr::{memchr, memmem::Finder};
use pyo3::prelude::*;
use std::collections::HashSet;

#[pyfunction]
pub fn extract_codeblocks(text: &str) -> String {
    let bytes = text.as_bytes();
    let mut output = Vec::with_capacity(bytes.len() >> 1);
    let mut pos = 0;
    let finder = Finder::new(b"```");

    while let Some(open_pos) = finder.find(&bytes[pos..]) {
        let open = pos + open_pos + 3;

        let code_start = match memchr(b'\n', &bytes[open..]) {
            Some(offset) => open + offset + 1,
            None => break,
        };

        let close = match finder.find(&bytes[code_start..]) {
            Some(rel) => code_start + rel,
            None => break,
        };

        if !output.is_empty() {
            output.push(b'\n');
        }

        let mut slice = &bytes[code_start..close];
        while let Some(&last) = slice.last() {
            if matches!(last, b'\n' | b'\r' | b' ' | b'\t') {
                slice = &slice[..slice.len() - 1];
            } else {
                break;
            }
        }

        output.extend_from_slice(slice);
        pos = close + 3;
    }

    unsafe { String::from_utf8_unchecked(output) }
}

#[pyfunction]
pub fn omit_codeblocks(text: &str) -> String {
    let bytes = text.as_bytes();
    let mut output = Vec::with_capacity(bytes.len());
    let mut pos = 0;
    let finder = Finder::new(b"```");
    const PLACEHOLDER: &[u8] = b"[code omitted]";

    while let Some(open_pos) = finder.find(&bytes[pos..]) {
        let open = pos + open_pos;
        output.extend_from_slice(&bytes[pos..open]);

        let code_start = open + 3;
        let lang_end = match memchr(b'\n', &bytes[code_start..]) {
            Some(offset) => code_start + offset + 1,
            None => {
                output.extend_from_slice(&bytes[pos..]);
                break;
            }
        };

        let close = match finder.find(&bytes[lang_end..]) {
            Some(rel) => lang_end + rel + 3,
            None => {
                output.extend_from_slice(&bytes[pos..]);
                break;
            }
        };

        output.extend_from_slice(PLACEHOLDER);
        pos = close;
    }

    output.extend_from_slice(&bytes[pos..]);
    unsafe { String::from_utf8_unchecked(output) }
}

#[pyfunction]
pub fn strip_markdown_formatting(text: &str) -> String {
    let bytes = text.as_bytes();
    let mut output = String::with_capacity(bytes.len());
    let mut pos = 0;
    let finder = Finder::new(b"```");

    while let Some(open_pos) = finder.find(&bytes[pos..]) {
        let code_start = pos + open_pos;

        // Process non-code section
        let non_code = &bytes[pos..code_start];
        remove_inline_markers_to_string(non_code, &mut output);

        // Find end of code block
        let lang_end = match memchr(b'\n', &bytes[code_start + 3..]) {
            Some(offset) => code_start + 3 + offset + 1,
            None => {
                // Unterminated code block
                output.push_str(unsafe { std::str::from_utf8_unchecked(&bytes[code_start..]) });
                return output;
            }
        };

        let close = match finder.find(&bytes[lang_end..]) {
            Some(offset) => lang_end + offset + 3,
            None => {
                output.push_str(unsafe { std::str::from_utf8_unchecked(&bytes[code_start..]) });
                return output;
            }
        };

        // Add code block as-is
        output.push_str(unsafe { std::str::from_utf8_unchecked(&bytes[code_start..close]) });
        pos = close;
    }

    // Process any trailing content after last code block
    if pos < bytes.len() {
        remove_inline_markers_to_string(&bytes[pos..], &mut output);
    }

    output
}

#[inline]
fn remove_inline_markers_to_string(bytes: &[u8], output: &mut String) {
    let mut i = 0;

    while i < bytes.len() {
        match bytes[i] {
            b'*' | b'_' | b'#' => {
                let marker = bytes[i];
                if i + 1 < bytes.len() && bytes[i + 1] == marker {
                    i += 2;
                } else {
                    i += 1;
                }
            }
            b @ 0x00..=0x7F => {
                output.push(b as char);
                i += 1;
            }
            _ => {
                let ch_len = utf8_char_width(bytes[i]);
                if i + ch_len <= bytes.len() {
                    output.push_str(unsafe { std::str::from_utf8_unchecked(&bytes[i..i + ch_len]) });
                    i += ch_len;
                } else {
                    break;
                }
            }
        }
    }
}

#[inline]
const fn utf8_char_width(byte: u8) -> usize {
    match byte {
        0x00..=0x7F => 1,
        0xC0..=0xDF => 2,
        0xE0..=0xEF => 3,
        0xF0..=0xF7 => 4,
        _ => 1,
    }
}

#[pyfunction]
pub fn omit_urls(text: &str) -> String {
    let bytes = text.as_bytes();
    let mut result = String::with_capacity(text.len());
    let mut i = 0;
    const URL_PLACEHOLDER: &str = "[url omitted]";

    while i < bytes.len() {
        if i < bytes.len() && bytes[i] > 127 {
            let ch_len = utf8_char_width(bytes[i]);
            if i + ch_len <= bytes.len() {
                result.push_str(unsafe { std::str::from_utf8_unchecked(&bytes[i..i + ch_len]) });
                i += ch_len;
            } else {
                i += 1;
            }
            continue;
        }

        match bytes[i] {
            b'[' => {
                i += 1;
                let link_start = i;
                while i < bytes.len() && bytes[i] != b']' {
                    i += 1;
                }

                if i < bytes.len() {
                    result.push_str(unsafe {
                        std::str::from_utf8_unchecked(&bytes[link_start..i])
                    });
                    i += 1;

                    if i < bytes.len() && bytes[i] == b'(' {
                        i += 1;
                        while i < bytes.len() && bytes[i] != b')' {
                            i += 1;
                        }
                        if i < bytes.len() {
                            i += 1;
                        }
                    }
                }
            }
            b'h' if i + 7 <= bytes.len() => {
                if &bytes[i..i + 7] == b"http://" {
                    result.push_str(URL_PLACEHOLDER);
                    i += 7;
                    while i < bytes.len() && !bytes[i].is_ascii_whitespace() && bytes[i] != b')' {
                        i += 1;
                    }
                } else if i + 8 <= bytes.len() && &bytes[i..i + 8] == b"https://" {
                    result.push_str(URL_PLACEHOLDER);
                    i += 8;
                    while i < bytes.len() && !bytes[i].is_ascii_whitespace() && bytes[i] != b')' {
                        i += 1;
                    }
                } else {
                    result.push(bytes[i] as char);
                    i += 1;
                }
            }
            b'w' if i + 4 <= bytes.len() && &bytes[i..i + 4] == b"www." => {
                result.push_str(URL_PLACEHOLDER);
                i += 4;
                while i < bytes.len() && !bytes[i].is_ascii_whitespace() && bytes[i] != b')' {
                    i += 1;
                }
            }
            ch => {
                result.push(ch as char);
                i += 1;
            }
        }
    }

    result
}

#[pyfunction]
pub fn extract_urls(text: &str) -> Vec<String> {
    let bytes = text.as_bytes();
    let mut urls = HashSet::new();
    let mut i = 0;

    while i < bytes.len() {
        if bytes[i] > 127 {
            let ch_len = utf8_char_width(bytes[i]);
            i += ch_len.min(bytes.len() - i);
            continue;
        }

        match bytes[i] {
            b'[' => {
                // Handle markdown links [text](url)
                i += 1;
                while i < bytes.len() && bytes[i] != b']' {
                    i += 1;
                }

                if i < bytes.len() {
                    i += 1; // skip ]
                    if i < bytes.len() && bytes[i] == b'(' {
                        i += 1; // skip (
                        let start = i;
                        while i < bytes.len() && bytes[i] != b')' {
                            i += 1;
                        }
                        if let Ok(url) = std::str::from_utf8(&bytes[start..i]) {
                            let url = url.trim();
                            if url.starts_with("http://") || url.starts_with("https://") {
                                urls.insert(url.to_string());
                            } else if url.starts_with("www.") {
                                urls.insert(format!("http://{}", url));
                            }
                        }
                        if i < bytes.len() {
                            i += 1; // skip )
                        }
                    }
                }
            }
            b'h' if i + 7 <= bytes.len() => {
                if &bytes[i..i + 7] == b"http://" {
                    let start = i;
                    i += 7;
                    while i < bytes.len() && !bytes[i].is_ascii_whitespace() 
                        && bytes[i] != b')' && bytes[i] != b',' 
                        && bytes[i] != b'"' && bytes[i] != b'\'' 
                        && bytes[i] != b'<' && bytes[i] != b'>' {
                        i += 1;
                    }
                    if let Ok(url) = std::str::from_utf8(&bytes[start..i]) {
                        urls.insert(url.to_string());
                    }
                } else if i + 8 <= bytes.len() && &bytes[i..i + 8] == b"https://" {
                    let start = i;
                    i += 8;
                    while i < bytes.len() && !bytes[i].is_ascii_whitespace() 
                        && bytes[i] != b')' && bytes[i] != b',' 
                        && bytes[i] != b'"' && bytes[i] != b'\'' 
                        && bytes[i] != b'<' && bytes[i] != b'>' {
                        i += 1;
                    }
                    if let Ok(url) = std::str::from_utf8(&bytes[start..i]) {
                        urls.insert(url.to_string());
                    }
                } else {
                    i += 1;
                }
            }
            b'w' if i + 4 <= bytes.len() && &bytes[i..i + 4] == b"www." => {
                let start = i;
                i += 4;
                while i < bytes.len() && !bytes[i].is_ascii_whitespace() 
                    && bytes[i] != b')' && bytes[i] != b',' 
                    && bytes[i] != b'"' && bytes[i] != b'\'' 
                    && bytes[i] != b'<' && bytes[i] != b'>' {
                    i += 1;
                }
                if let Ok(url) = std::str::from_utf8(&bytes[start..i]) {
                    urls.insert(format!("http://{}", url));
                }
            }
            _ => i += 1,
        }
    }

    urls.into_iter().collect()
}

#[pyfunction]
pub fn normalize_markdown(text: &str) -> String {
    omit_codeblocks(&omit_urls(&strip_markdown_formatting(text)))
}

#[pymodule]
fn markdown_normalization(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_codeblocks, m)?)?;
    m.add_function(wrap_pyfunction!(omit_codeblocks, m)?)?;
    m.add_function(wrap_pyfunction!(strip_markdown_formatting, m)?)?;
    m.add_function(wrap_pyfunction!(omit_urls, m)?)?;
    m.add_function(wrap_pyfunction!(extract_urls, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_markdown, m)?)?;
    Ok(())
}