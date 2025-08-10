#define PY_SSIZE_T_CLEAN
#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <limits.h>

// Global reference to Transcript class
static PyObject *Transcript = NULL;

// Reusable buffers to avoid malloc per line
static int block_sizes_buffer[1000];
static int block_starts_buffer[1000];

static int convert_strand_to_int(char strand_char) {
    switch (strand_char) {
        case '+': return 1;
        case '-': return -1;
        default: return 0;  // unknown
    }
}

// Fast direct buffer parsing - no malloc, no string copying
static PyObject* parse_bed12_line_fast(const char *line_start, const char *line_end) {
    Py_ssize_t line_len = line_end - line_start;
    
    // Skip empty lines and comments
    if (line_len == 0 || line_start[0] == '#' || line_start[0] == '\n') {
        Py_RETURN_NONE;
    }

    if (line_len > 100000) {  // Reasonable maximum
        PyErr_SetString(PyExc_ValueError, "BED12 line too long (>100KB)");
        return NULL;
    }

    // Find all 11 tab positions using direct pointer scanning
    const char *tabs[11];
    int tab_count = 0;
    const char *ptr = line_start;
    
    while (ptr < line_end && tab_count < 11) {
        const char *tab_pos = memchr(ptr, '\t', line_end - ptr);
        if (!tab_pos) break;
        tabs[tab_count++] = tab_pos;
        ptr = tab_pos + 1;
    }
    
    if (tab_count < 11) {
        PyErr_Format(PyExc_ValueError, "BED12 line has only %d tabs, expected 11", tab_count);
        return NULL;
    }

    // Parse numeric fields directly with strtol
    char *endptr;
    const char *field_start;
    
    // chromStart (field 1)
    field_start = tabs[0] + 1;
    long chrom_start = strtol(field_start, &endptr, 10);
    if (endptr == field_start || chrom_start < 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid chromStart");
        return NULL;
    }
    
    // thickStart (field 6)
    field_start = tabs[5] + 1;
    long thick_start = strtol(field_start, &endptr, 10);
    if (endptr == field_start || thick_start < 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid thickStart");
        return NULL;
    }
    
    // thickEnd (field 7)
    field_start = tabs[6] + 1;
    long thick_end = strtol(field_start, &endptr, 10);
    if (endptr == field_start || thick_end < 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid thickEnd");
        return NULL;
    }
    
    // blockCount (field 9)
    field_start = tabs[8] + 1;
    long block_count_long = strtol(field_start, &endptr, 10);
    if (endptr == field_start || block_count_long <= 0 || block_count_long > 1000) {
        PyErr_Format(PyExc_ValueError, "Invalid block count: %ld", block_count_long);
        return NULL;
    }
    
    int block_count = (int)block_count_long;
    
    // Extract string fields with stack buffers
    char chrom[256], name[256];
    Py_ssize_t chrom_len = tabs[0] - line_start;
    Py_ssize_t name_len = tabs[3] - tabs[2] - 1;
    
    if (chrom_len >= 256 || name_len >= 256 || chrom_len == 0 || name_len == 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid chromosome or name field");
        return NULL;
    }
    
    memcpy(chrom, line_start, chrom_len);
    chrom[chrom_len] = '\0';
    memcpy(name, tabs[2] + 1, name_len);
    name[name_len] = '\0';
    
    // Get strand
    char strand_char = (tabs[4] + 1 < tabs[5]) ? tabs[4][1] : '.';
    
    // Parse block sizes directly from buffer
    const char *sizes_start = tabs[9] + 1;
    const char *sizes_end = tabs[10];
    const char *parse_ptr = sizes_start;
    
    for (int i = 0; i < block_count && i < 1000; i++) {
        if (parse_ptr >= sizes_end) {
            PyErr_Format(PyExc_ValueError, "Not enough block sizes (expected %d)", block_count);
            return NULL;
        }
        
        long size = strtol(parse_ptr, &endptr, 10);
        if (endptr == parse_ptr || size <= 0) {
            PyErr_SetString(PyExc_ValueError, "Invalid block size");
            return NULL;
        }
        
        block_sizes_buffer[i] = (int)size;
        
        // Skip to next comma or end
        parse_ptr = endptr;
        if (parse_ptr < sizes_end && *parse_ptr == ',') {
            parse_ptr++;
        }
    }
    
    // Parse block starts directly from buffer
    const char *starts_start = tabs[10] + 1;
    parse_ptr = starts_start;
    
    for (int i = 0; i < block_count && i < 1000; i++) {
        if (parse_ptr >= line_end) {
            PyErr_Format(PyExc_ValueError, "Not enough block starts (expected %d)", block_count);
            return NULL;
        }
        
        long start = strtol(parse_ptr, &endptr, 10);
        if (endptr == parse_ptr || start < 0) {
            PyErr_SetString(PyExc_ValueError, "Invalid block start");
            return NULL;
        }
        
        block_starts_buffer[i] = (int)start;
        
        // Skip to next comma or end
        parse_ptr = endptr;
        if (parse_ptr < line_end && *parse_ptr == ',') {
            parse_ptr++;
        }
    }

    // Quick validation of block ordering
    for (int i = 1; i < block_count; i++) {
        if (block_starts_buffer[i] <= block_starts_buffer[i-1]) {
            PyErr_Format(PyExc_ValueError, "Block starts not in ascending order at block %d", i);
            return NULL;
        }
    }

    // Create numpy array for blocks (N, 2) with absolute coordinates
    npy_intp dims[2] = {block_count, 2};
    PyObject *blocks_array = PyArray_SimpleNew(2, dims, NPY_UINT32);
    if (!blocks_array) {
        return NULL;
    }

    // Fill the blocks array with absolute coordinates
    uint32_t *blocks_data = (uint32_t*)PyArray_DATA((PyArrayObject*)blocks_array);
    for (int i = 0; i < block_count; i++) {
        uint32_t abs_start = (uint32_t)(chrom_start + block_starts_buffer[i]);
        uint32_t abs_end = abs_start + (uint32_t)block_sizes_buffer[i];
        blocks_data[i * 2] = abs_start;      // start
        blocks_data[i * 2 + 1] = abs_end;    // end
    }

    // Convert strand
    int strand_int = convert_strand_to_int(strand_char);

    // Create CDS start/end (None if thick_start == thick_end)
    PyObject *cds_start_obj = Py_None;
    PyObject *cds_end_obj = Py_None;
    if (thick_start < thick_end) {
        cds_start_obj = PyLong_FromLong(thick_start);
        cds_end_obj = PyLong_FromLong(thick_end);
        if (!cds_start_obj || !cds_end_obj) {
            Py_DECREF(blocks_array);
            Py_XDECREF(cds_start_obj);
            Py_XDECREF(cds_end_obj);
            return NULL;
        }
    } else {
        Py_INCREF(Py_None);
        Py_INCREF(Py_None);
    }

    // Create Python objects for chromosome and name (both as strings for consistency)
    PyObject *chrom_str = PyUnicode_FromString(chrom);
    PyObject *name_str = PyUnicode_FromString(name);
    if (!chrom_str || !name_str) {
        Py_DECREF(blocks_array);
        Py_DECREF(cds_start_obj);
        Py_DECREF(cds_end_obj);
        Py_XDECREF(chrom_str);
        Py_XDECREF(name_str);
        return NULL;
    }

    // Check if Transcript class is available
    if (!Transcript) {
        Py_DECREF(blocks_array);
        Py_DECREF(cds_start_obj);
        Py_DECREF(cds_end_obj);
        Py_DECREF(chrom_str);
        Py_DECREF(name_str);
        PyErr_SetString(PyExc_RuntimeError, "Transcript class not available");
        return NULL;
    }

    // Create Transcript object
    PyObject *args_tuple = PyTuple_New(6);
    if (!args_tuple) {
        Py_DECREF(blocks_array);
        Py_DECREF(cds_start_obj);
        Py_DECREF(cds_end_obj);
        Py_DECREF(chrom_str);
        Py_DECREF(name_str);
        return NULL;
    }

    PyTuple_SetItem(args_tuple, 0, blocks_array);  // blocks
    PyTuple_SetItem(args_tuple, 1, PyLong_FromLong(strand_int));  // strand
    PyTuple_SetItem(args_tuple, 2, chrom_str);  // chrom
    PyTuple_SetItem(args_tuple, 3, name_str);  // id
    PyTuple_SetItem(args_tuple, 4, cds_start_obj);  // cds_start
    PyTuple_SetItem(args_tuple, 5, cds_end_obj);    // cds_end

    PyObject *transcript = PyObject_CallObject(Transcript, args_tuple);
    Py_DECREF(args_tuple);

    return transcript;
}

// Optimized file parsing - batch processing like chain parser
static PyObject* parse_bed12_file_fast(PyObject* self, PyObject* args) {
    const char *content;
    Py_ssize_t content_len;

    if (!PyArg_ParseTuple(args, "s#", &content, &content_len)) {
        return NULL;
    }

    if (content_len < 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid content length");
        return NULL;
    }

    // Create list to hold transcripts
    PyObject *transcripts_list = PyList_New(0);
    if (!transcripts_list) {
        return NULL;
    }

    // Fast line processing with memchr
    const char *line_start = content;
    const char *content_end = content + content_len;
    Py_ssize_t line_count = 0;
    
    while (line_start < content_end) {
        // Find end of current line using memchr
        const char *line_end = memchr(line_start, '\n', content_end - line_start);
        if (!line_end) {
            line_end = content_end;  // Last line without newline
        }
        
        // Skip empty lines
        if (line_end > line_start) {
            line_count++;
            
            // Reasonable limit to prevent memory exhaustion
            if (line_count > 1000000) {
                Py_DECREF(transcripts_list);
                PyErr_SetString(PyExc_ValueError, "Too many lines in BED file (>1M)");
                return NULL;
            }
            
            // Parse this line directly
            PyObject *transcript = parse_bed12_line_fast(line_start, line_end);
            if (!transcript) {
                Py_DECREF(transcripts_list);
                return NULL;
            }
            
            // Add to list if not None (skip empty lines)
            if (transcript != Py_None) {
                if (PyList_Append(transcripts_list, transcript) < 0) {
                    Py_DECREF(transcript);
                    Py_DECREF(transcripts_list);
                    return NULL;
                }
            }
            Py_DECREF(transcript);
        }
        
        // Move to next line
        line_start = line_end + 1;
    }

    return transcripts_list;
}

// Legacy wrapper for compatibility
static PyObject* parse_bed12_line(PyObject* self, PyObject* args) {
    const char *line;
    Py_ssize_t line_len;

    if (!PyArg_ParseTuple(args, "s#", &line, &line_len)) {
        return NULL;
    }

    return parse_bed12_line_fast(line, line + line_len);
}

// Use the fast version for file parsing
static PyObject* parse_bed12_file(PyObject* self, PyObject* args) {
    return parse_bed12_file_fast(self, args);
}

// Method table
static PyMethodDef Bed12parserMethods[] = {
    {"parse_bed12_line", parse_bed12_line, METH_VARARGS, "Parse single BED12 line to Transcript"},
    {"parse_bed12_file", parse_bed12_file, METH_VARARGS, "Parse BED12 file content to Transcript list"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef bed12parsermodule = {
    PyModuleDef_HEAD_INIT,
    "_bed12parser",
    NULL,
    -1,
    Bed12parserMethods
};

PyMODINIT_FUNC PyInit__bed12parser(void) {
    import_array();  // required for NumPy C API
    
    PyObject *module = PyModule_Create(&bed12parsermodule);
    if (!module) {
        return NULL;
    }
    
    // Import Transcript class
    PyObject *genes_module = PyImport_ImportModule("pyrion.core.genes");
    if (!genes_module) {
        Py_DECREF(module);
        return NULL;
    }
    
    Transcript = PyObject_GetAttrString(genes_module, "Transcript");
    Py_DECREF(genes_module);
    
    if (!Transcript) {
        Py_DECREF(module);
        return NULL;
    }
    
    return module;
}