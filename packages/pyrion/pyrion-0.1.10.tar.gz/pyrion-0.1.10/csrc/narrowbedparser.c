#define PY_SSIZE_T_CLEAN
#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <limits.h>

// Global reference to GenomicInterval class
static PyObject *GenomicInterval = NULL;

static int convert_strand_to_int(char strand_char) {
    switch (strand_char) {
        case '+': return 1;
        case '-': return -1;
        default: return 0;  // unknown
    }
}

// Safe string to long conversion with error checking
static int safe_strtol(const char *str, long *result, const char *field_name) {
    if (!str || *str == '\0') {
        PyErr_Format(PyExc_ValueError, "Empty or NULL value for %s", field_name);
        return -1;
    }
    
    char *endptr;
    errno = 0;
    *result = strtol(str, &endptr, 10);
    
    if (errno == ERANGE) {
        PyErr_Format(PyExc_ValueError, "Value out of range for %s: %s", field_name, str);
        return -1;
    }
    
    if (endptr == str || *endptr != '\0') {
        PyErr_Format(PyExc_ValueError, "Invalid numeric value for %s: %s", field_name, str);
        return -1;
    }
    
    return 0;
}



static PyObject* parse_narrow_bed_line(PyObject* self, PyObject* args) {
    const char *line;
    Py_ssize_t line_len;
    int expected_width;

    if (!PyArg_ParseTuple(args, "s#i", &line, &line_len, &expected_width)) {
        return NULL;
    }

    // Skip empty lines and comments
    if (line_len == 0 || line[0] == '#' || line[0] == '\n') {
        Py_RETURN_NONE;
    }

    // Validate line length to prevent buffer overflows
    if (line_len > 100000) {  // Reasonable maximum for BED line
        PyErr_SetString(PyExc_ValueError, "BED line too long (>100KB)");
        return NULL;
    }

    // Validate width range
    if (expected_width < 3 || expected_width > 9) {
        PyErr_Format(PyExc_ValueError, "Invalid BED width: %d (must be 3-9)", expected_width);
        return NULL;
    }

    // Split line by tabs
    char *line_copy = (char*)malloc(line_len + 1);
    if (!line_copy) {
        PyErr_NoMemory();
        return NULL;
    }
    memcpy(line_copy, line, line_len);
    line_copy[line_len] = '\0';

    char *fields[9];  // Maximum 9 fields
    int field_count = 0;
    char *token = strtok(line_copy, "\t");
    while (token && field_count < 9) {
        fields[field_count++] = token;
        token = strtok(NULL, "\t");
    }

    if (field_count != expected_width) {
        free(line_copy);
        PyErr_Format(PyExc_ValueError, "BED line has %d fields, expected %d", field_count, expected_width);
        return NULL;
    }

    // Parse required fields (chrom, start, end)
    char *chrom = fields[0];
    long start, end;
    
    if (safe_strtol(fields[1], &start, "start") < 0 ||
        safe_strtol(fields[2], &end, "end") < 0) {
        free(line_copy);
        return NULL;
    }

    // Validate coordinates
    if (start < 0 || end < 0) {
        free(line_copy);
        PyErr_SetString(PyExc_ValueError, "Negative coordinates not allowed");
        return NULL;
    }

    if (start >= end) {
        free(line_copy);
        PyErr_Format(PyExc_ValueError, "Invalid interval: start %ld >= end %ld", start, end);
        return NULL;
    }

    // Validate chromosome field
    if (strlen(chrom) == 0) {
        free(line_copy);
        PyErr_SetString(PyExc_ValueError, "Empty chromosome field");
        return NULL;
    }

    // Parse optional fields with defaults
    char *name = NULL;
    int strand_int = 0;  // UNKNOWN by default
    
    // Field 3 (index 3): name (if present)
    if (field_count >= 4 && strlen(fields[3]) > 0) {
        name = fields[3];
    }
    
    // Field 5 (index 5): strand (if present) - note: skipping score field at index 4
    if (field_count >= 6 && strlen(fields[5]) > 0) {
        strand_int = convert_strand_to_int(fields[5][0]);
    }

    // Create Python objects
    PyObject *chrom_str = PyUnicode_FromString(chrom);
    PyObject *start_obj = PyLong_FromLong(start);
    PyObject *end_obj = PyLong_FromLong(end);
    PyObject *strand_obj = PyLong_FromLong(strand_int);
    PyObject *id_obj = name ? PyUnicode_FromString(name) : Py_None;
    
    if (!chrom_str || !start_obj || !end_obj || !strand_obj) {
        free(line_copy);
        Py_XDECREF(chrom_str);
        Py_XDECREF(start_obj);
        Py_XDECREF(end_obj);
        Py_XDECREF(strand_obj);
        if (id_obj != Py_None) Py_XDECREF(id_obj);
        return NULL;
    }

    if (id_obj == Py_None) {
        Py_INCREF(Py_None);
    }

    // Check if GenomicInterval class is available
    if (!GenomicInterval) {
        free(line_copy);
        Py_DECREF(chrom_str);
        Py_DECREF(start_obj);
        Py_DECREF(end_obj);
        Py_DECREF(strand_obj);
        Py_DECREF(id_obj);
        PyErr_SetString(PyExc_RuntimeError, "GenomicInterval class not available");
        return NULL;
    }

    // Create GenomicInterval object
    PyObject *args_tuple = PyTuple_New(5);
    if (!args_tuple) {
        free(line_copy);
        Py_DECREF(chrom_str);
        Py_DECREF(start_obj);
        Py_DECREF(end_obj);
        Py_DECREF(strand_obj);
        Py_DECREF(id_obj);
        return NULL;
    }

    PyTuple_SetItem(args_tuple, 0, chrom_str);  // chrom
    PyTuple_SetItem(args_tuple, 1, start_obj);  // start
    PyTuple_SetItem(args_tuple, 2, end_obj);    // end
    PyTuple_SetItem(args_tuple, 3, strand_obj); // strand
    PyTuple_SetItem(args_tuple, 4, id_obj);     // id

    PyObject *interval = PyObject_CallObject(GenomicInterval, args_tuple);
    Py_DECREF(args_tuple);

    // Cleanup
    free(line_copy);

    return interval;
}

static PyObject* parse_narrow_bed_file(PyObject* self, PyObject* args) {
    const char *content;
    Py_ssize_t content_len;
    int width;

    if (!PyArg_ParseTuple(args, "s#i", &content, &content_len, &width)) {
        return NULL;
    }

    if (content_len < 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid content length");
        return NULL;
    }

    // Validate width
    if (width < 3 || width > 9) {
        PyErr_Format(PyExc_ValueError, "Invalid BED width: %d (must be 3-9)", width);
        return NULL;
    }

    // Create list to hold intervals
    PyObject *intervals_list = PyList_New(0);
    if (!intervals_list) {
        return NULL;
    }

    // Split content into lines
    Py_ssize_t start = 0;
    Py_ssize_t line_count = 0;
    
    for (Py_ssize_t i = 0; i <= content_len; ++i) {
        if (i == content_len || content[i] == '\n') {
            if (i > start) {
                line_count++;
                
                // Reasonable limit to prevent memory exhaustion
                if (line_count > 1000000) {
                    Py_DECREF(intervals_list);
                    PyErr_SetString(PyExc_ValueError, "Too many lines in BED file (>1M)");
                    return NULL;
                }
                
                // Parse this line
                PyObject *args_tuple = PyTuple_New(2);
                if (!args_tuple) {
                    Py_DECREF(intervals_list);
                    return NULL;
                }
                
                PyObject *line_bytes = PyBytes_FromStringAndSize(content + start, i - start);
                if (!line_bytes) {
                    Py_DECREF(args_tuple);
                    Py_DECREF(intervals_list);
                    return NULL;
                }
                
                PyTuple_SetItem(args_tuple, 0, line_bytes);
                PyTuple_SetItem(args_tuple, 1, PyLong_FromLong(width));
                
                PyObject *interval = parse_narrow_bed_line(self, args_tuple);
                Py_DECREF(args_tuple);
                
                if (!interval) {
                    Py_DECREF(intervals_list);
                    return NULL;
                }
                
                // Add to list if not None (skip empty lines)
                if (interval != Py_None) {
                    if (PyList_Append(intervals_list, interval) < 0) {
                        Py_DECREF(interval);
                        Py_DECREF(intervals_list);
                        return NULL;
                    }
                }
                Py_DECREF(interval);
            }
            start = i + 1;
        }
    }

    return intervals_list;
}

// Method table
static PyMethodDef NarrowbedparserMethods[] = {
    {"parse_narrow_bed_line", parse_narrow_bed_line, METH_VARARGS, "Parse single narrow BED line to GenomicInterval"},
    {"parse_narrow_bed_file", parse_narrow_bed_file, METH_VARARGS, "Parse narrow BED file content to GenomicInterval list"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef narrowbedparsermodule = {
    PyModuleDef_HEAD_INIT,
    "_narrowbedparser",
    NULL,
    -1,
    NarrowbedparserMethods
};

PyMODINIT_FUNC PyInit__narrowbedparser(void) {
    import_array();  // required for NumPy C API
    
    PyObject *module = PyModule_Create(&narrowbedparsermodule);
    if (!module) {
        return NULL;
    }
    
    // Import GenomicInterval class
    PyObject *intervals_module = PyImport_ImportModule("pyrion.core.intervals");
    if (!intervals_module) {
        Py_DECREF(module);
        return NULL;
    }
    
    GenomicInterval = PyObject_GetAttrString(intervals_module, "GenomicInterval");
    Py_DECREF(intervals_module);
    
    if (!GenomicInterval) {
        Py_DECREF(module);
        return NULL;
    }
    
    return module;
} 