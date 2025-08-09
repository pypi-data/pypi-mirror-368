#define PY_SSIZE_T_CLEAN
#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <limits.h>

// Global reference to GenomeAlignment class
static PyObject *GenomeAlignment = NULL;

static int convert_strand_to_int(char strand_char) {
    switch (strand_char) {
        case '+': return 1;
        case '-': return -1;
        default: return 0;  // unknown
    }
}

// Safe integer parsing with range validation
static int safe_parse_int(const char *str, int *result, const char *field_name, int min_val, int max_val) {
    if (!str || *str == '\0') {
        PyErr_Format(PyExc_ValueError, "Empty or NULL value for %s", field_name);
        return -1;
    }
    
    char *endptr;
    errno = 0;
    long val = strtol(str, &endptr, 10);
    
    if (errno == ERANGE || val < INT_MIN || val > INT_MAX) {
        PyErr_Format(PyExc_ValueError, "Value out of integer range for %s: %s", field_name, str);
        return -1;
    }
    
    if (endptr == str || *endptr != '\0') {
        PyErr_Format(PyExc_ValueError, "Invalid integer value for %s: %s", field_name, str);
        return -1;
    }
    
    if (val < min_val || val > max_val) {
        PyErr_Format(PyExc_ValueError, "Value %ld out of range [%d, %d] for %s", val, min_val, max_val, field_name);
        return -1;
    }
    
    *result = (int)val;
    return 0;
}

// Safe string copying with bounds checking
static int safe_strcpy(char *dest, const char *src, size_t dest_size, const char *field_name) {
    if (!src || !dest || dest_size == 0) {
        PyErr_Format(PyExc_ValueError, "Invalid parameters for %s", field_name);
        return -1;
    }
    
    size_t src_len = strlen(src);
    if (src_len >= dest_size) {
        PyErr_Format(PyExc_ValueError, "String too long for %s (max %zu chars): %s", field_name, dest_size - 1, src);
        return -1;
    }
    
    strcpy(dest, src);
    return 0;
}

static PyObject* parse_chain_chunk(PyObject* self, PyObject* args) {
    const char *input;
    Py_ssize_t input_len;
    int min_score = INT_MIN;  // Default: no filtering

    if (!PyArg_ParseTuple(args, "s#|i", &input, &input_len, &min_score)) {
        return NULL;
    }

    // Validate input length
    if (input_len <= 0) {
        PyErr_SetString(PyExc_ValueError, "Empty input");
        return NULL;
    }
    
    // Increase upper bound to accommodate extremely large chains (1GB)
    if (input_len > 1073741824) {  // 1GB limit (safety guard)
        PyErr_SetString(PyExc_ValueError, "Input too large (>1GB)");
        return NULL;
    }

    // 1. Find header line directly in buffer
    const char *header_start = input;
    const char *header_end = memchr(input, '\n', input_len);
    if (!header_end) {
        PyErr_SetString(PyExc_ValueError, "No header line found (missing newline)");
        return NULL;
    }
    
    Py_ssize_t hdr_len = header_end - header_start;
    if (hdr_len <= 0 || hdr_len > 10000) {  // Reasonable header length limit
        PyErr_SetString(PyExc_ValueError, "Invalid or too long header line");
        return NULL;
    }

    // Count blocks by counting remaining newlines
    Py_ssize_t n_blocks = 0;
    const char *scan = header_end + 1;
    while (scan < input + input_len) {
        const char *next_newline = memchr(scan, '\n', input + input_len - scan);
        if (next_newline) {
            n_blocks++;
            scan = next_newline + 1;
        } else {
            // Last line without newline
            if (scan < input + input_len) {
                n_blocks++;
            }
            break;
        }
    }
    
    if (n_blocks < 1) {
        PyErr_SetString(PyExc_ValueError, "Chain chunk too short (need header + at least 1 block)");
        return NULL;
    }
    
    // Remove strict 1M block cap; allow very large chains. Numpy allocation may fail if too large.

    // 2. Parse header line (create temporary null-terminated copy on stack)
    char hdr_buf[10001];  // Stack allocated buffer
    memcpy(hdr_buf, header_start, hdr_len);
    hdr_buf[hdr_len] = '\0';
    const char *hdr = hdr_buf;

    // Parse header with safer approach
    int chain_id, t_size, t_start, t_end, q_size, q_start, q_end, score;
    char t_chrom[256], q_chrom[256], t_strand[8], q_strand[8];  // Larger buffers
    
    int parsed = sscanf(hdr, "chain %d %255s %d %7s %d %d %255s %d %7s %d %d %d",
                        &score, t_chrom, &t_size, t_strand, &t_start, &t_end,
                        q_chrom, &q_size, q_strand, &q_start, &q_end, &chain_id);
    
    if (parsed != 12) {
        PyErr_Format(PyExc_ValueError, "Failed to parse header line. Got %d fields, expected 12. Header: %.100s", parsed, hdr);
        return NULL;
    }

    // Validate header values
    if (score < -INT_MAX || score > INT_MAX) {
        PyErr_Format(PyExc_ValueError, "Invalid score: %d", score);
        return NULL;
    }
    
    if (t_size <= 0 || q_size <= 0) {
        PyErr_Format(PyExc_ValueError, "Invalid chromosome sizes: t_size=%d, q_size=%d", t_size, q_size);
        return NULL;
    }
    
    if (t_start < 0 || t_end < 0 || q_start < 0 || q_end < 0) {
        PyErr_SetString(PyExc_ValueError, "Negative coordinates not allowed");
        return NULL;
    }
    
    if (t_start >= t_end || q_start >= q_end) {
        PyErr_Format(PyExc_ValueError, "Invalid coordinate ranges: t=[%d,%d], q=[%d,%d]", t_start, t_end, q_start, q_end);
        return NULL;
    }
    
    if (t_end > t_size || q_end > q_size) {
        PyErr_Format(PyExc_ValueError, "Coordinates exceed chromosome sizes: t_end=%d>t_size=%d or q_end=%d>q_size=%d", 
                     t_end, t_size, q_end, q_size);
        return NULL;
    }
    
    // Validate strand characters
    if (strlen(t_strand) != 1 || strlen(q_strand) != 1) {
        PyErr_Format(PyExc_ValueError, "Invalid strand values: '%s', '%s'", t_strand, q_strand);
        return NULL;
    }
    
    if (t_strand[0] != '+' && t_strand[0] != '-' && t_strand[0] != '.' &&
        q_strand[0] != '+' && q_strand[0] != '-' && q_strand[0] != '.') {
        PyErr_Format(PyExc_ValueError, "Invalid strand characters: '%c', '%c'", t_strand[0], q_strand[0]);
        return NULL;
    }

    // Apply score filter - return None if score is below threshold
    if (score < min_score) {
        Py_RETURN_NONE;
    }

    // 3. Create output numpy array for blocks (N, 4) format
    npy_intp dims[2] = {n_blocks, 4};
    PyObject *blocks = PyArray_SimpleNew(2, dims, NPY_UINT32);
    if (!blocks) {
        PyErr_SetString(PyExc_MemoryError, "Failed to create numpy array");
        return NULL;
    }
    uint32_t (*arr)[4] = (uint32_t (*)[4]) PyArray_DATA((PyArrayObject *)blocks);

    uint32_t cur_q = (uint32_t)q_start;
    uint32_t cur_t = (uint32_t)t_start;

    // Parse blocks directly from buffer without temporary objects
    const char *line_start = header_end + 1;  // Start after header
    Py_ssize_t block_idx = 0;
    
    while (line_start < input + input_len && block_idx < n_blocks) {
        // Find end of current line
        const char *line_end = memchr(line_start, '\n', input + input_len - line_start);
        if (!line_end) {
            line_end = input + input_len;  // Last line without newline
        }
        
        Py_ssize_t line_len = line_end - line_start;
        if (line_len > 1000) {  // Reasonable line length
            Py_DECREF(blocks);
            PyErr_Format(PyExc_ValueError, "Block line too long at line %ld", (long)(block_idx + 2));
            return NULL;
        }
        
        // Parse integers directly from buffer using strtol
        char *endptr;
        const char *parse_ptr = line_start;
        
        // Parse size
        int size = (int)strtol(parse_ptr, &endptr, 10);
        if (endptr == parse_ptr || size <= 0) {
            Py_DECREF(blocks);
            PyErr_Format(PyExc_ValueError, "Invalid block size at line %ld", (long)(block_idx + 2));
            return NULL;
        }
        
        // Skip whitespace/tabs
        parse_ptr = endptr;
        while (parse_ptr < line_end && (*parse_ptr == ' ' || *parse_ptr == '\t')) {
            parse_ptr++;
        }
        
        // Parse dt (optional)
        int dt = 0;
        if (parse_ptr < line_end && *parse_ptr >= '0' && *parse_ptr <= '9') {
            dt = (int)strtol(parse_ptr, &endptr, 10);
            if (dt < 0) {
                Py_DECREF(blocks);
                PyErr_Format(PyExc_ValueError, "Negative dt at line %ld", (long)(block_idx + 2));
                return NULL;
            }
            
            // Skip whitespace/tabs
            parse_ptr = endptr;
            while (parse_ptr < line_end && (*parse_ptr == ' ' || *parse_ptr == '\t')) {
                parse_ptr++;
            }
        }
        
        // Parse dq (optional)
        int dq = 0;
        if (parse_ptr < line_end && *parse_ptr >= '0' && *parse_ptr <= '9') {
            dq = (int)strtol(parse_ptr, &endptr, 10);
            if (dq < 0) {
                Py_DECREF(blocks);
                PyErr_Format(PyExc_ValueError, "Negative dq at line %ld", (long)(block_idx + 2));
                return NULL;
            }
        }

        // Check for integer overflow
        if (cur_q > UINT32_MAX - size || cur_t > UINT32_MAX - size) {
            Py_DECREF(blocks);
            PyErr_Format(PyExc_ValueError, "Integer overflow in block coordinates at line %ld", (long)(block_idx + 2));
            return NULL;
        }

        uint32_t q_end_block = cur_q + (uint32_t)size;
        uint32_t t_end_block = cur_t + (uint32_t)size;

        // Validate that coordinates don't exceed original ranges
        if (t_end_block > (uint32_t)t_end || q_end_block > (uint32_t)q_end) {
            Py_DECREF(blocks);
            PyErr_Format(PyExc_ValueError, "Block coordinates exceed chain bounds at line %ld", (long)(block_idx + 2));
            return NULL;
        }

        // Convert strands to integers for early use
        int q_strand_int = convert_strand_to_int(q_strand[0]);
        
        // Store block coordinates, reversing query coordinates for negative strand
        uint32_t final_q_start, final_q_end;
        if (q_strand_int == -1) {
            // For negative strand, reverse the query coordinates
            final_q_start = (uint32_t)q_size - q_end_block;
            final_q_end = (uint32_t)q_size - cur_q;
        } else {
            // For positive strand, use coordinates as-is
            final_q_start = cur_q;
            final_q_end = q_end_block;
        }
        
        arr[block_idx][0] = cur_t;           // t_start
        arr[block_idx][1] = t_end_block;     // t_end
        arr[block_idx][2] = final_q_start;   // q_start (strand-corrected)
        arr[block_idx][3] = final_q_end;     // q_end (strand-corrected)

        // Update positions with gaps (checking overflow)
        if (cur_t > UINT32_MAX - size - dt || cur_q > UINT32_MAX - size - dq) {
            Py_DECREF(blocks);
            PyErr_Format(PyExc_ValueError, "Integer overflow with gaps at line %ld", (long)(block_idx + 2));
            return NULL;
        }
        
        cur_t = t_end_block + (uint32_t)dt;
        cur_q = q_end_block + (uint32_t)dq;
        
        // Move to next line
        line_start = line_end + 1;
        block_idx++;
    }

    // Check if GenomeAlignment class is available
    if (!GenomeAlignment) {
        Py_DECREF(blocks);
        PyErr_SetString(PyExc_RuntimeError, "GenomeAlignment class not available");
        return NULL;
    }

    // Create string objects for chromosomes (for consistency with transcripts)
    PyObject *t_chrom_str = PyUnicode_FromString(t_chrom);
    PyObject *q_chrom_str = PyUnicode_FromString(q_chrom);
    if (!t_chrom_str || !q_chrom_str) {
        Py_XDECREF(t_chrom_str);
        Py_XDECREF(q_chrom_str);
        Py_DECREF(blocks);
        return NULL;
    }

    // Convert strands to integers
    int t_strand_int = convert_strand_to_int(t_strand[0]);
    int q_strand_int = convert_strand_to_int(q_strand[0]);

    // Create GenomeAlignment object
    PyObject *genome_alignment = PyObject_CallFunction(
        GenomeAlignment, "iiOiiOiiO",
        chain_id,           // chain_id
        score,              // score
        t_chrom_str,        // t_chrom
        t_strand_int,       // t_strand
        t_size,             // t_size
        q_chrom_str,        // q_chrom
        q_strand_int,       // q_strand
        q_size,             // q_size
        blocks              // blocks
    );

    // Clean up
    Py_DECREF(t_chrom_str);
    Py_DECREF(q_chrom_str);
    Py_DECREF(blocks);

    if (!genome_alignment) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create GenomeAlignment object");
        return NULL;
    }

    return genome_alignment;
}

static PyObject* parse_many_chain_chunks(PyObject* self, PyObject* args) {
    PyObject *chunks_list;
    int min_score = INT_MIN;  // Default: no filtering
    
    if (!PyArg_ParseTuple(args, "O!|i", &PyList_Type, &chunks_list, &min_score)) {
        return NULL;
    }
    
    Py_ssize_t n_chunks = PyList_Size(chunks_list);
    if (n_chunks < 0) {
        return NULL;
    }
    
    if (n_chunks > 10000000) {  // Reasonable limit
        PyErr_Format(PyExc_ValueError, "Too many chunks: %ld (max 1M)", (long)n_chunks);
        return NULL;
    }
    
    // Create output list of GenomeAlignment objects (will be compacted later)
    PyObject *alignments_list = PyList_New(0);
    if (!alignments_list) {
        return NULL;
    }
    
    // Process each chunk
    for (Py_ssize_t i = 0; i < n_chunks; i++) {
        PyObject *chunk = PyList_GetItem(chunks_list, i);
        if (!chunk) {
            Py_DECREF(alignments_list);
            return NULL;
        }
        
        // Parse this chunk using the existing function with score filter
        PyObject *args_tuple = PyTuple_Pack(2, chunk, PyLong_FromLong(min_score));
        if (!args_tuple) {
            Py_DECREF(alignments_list);
            return NULL;
        }
        
        PyObject *alignment = parse_chain_chunk(self, args_tuple);
        Py_DECREF(args_tuple);
        
        if (!alignment) {
            // If parsing failed, clean up and return error
            Py_DECREF(alignments_list);
            return NULL;
        }
        
        // Only add to output list if not None (not filtered out)
        if (alignment != Py_None) {
            if (PyList_Append(alignments_list, alignment) < 0) {
                Py_DECREF(alignment);
                Py_DECREF(alignments_list);
                return NULL;
            }
        }
        Py_DECREF(alignment);
    }
    
    return alignments_list;
}

// Method table
static PyMethodDef ChainparserMethods[] = {
    {"parse_chain_chunk", parse_chain_chunk, METH_VARARGS, "Parse single chain chunk to GenomeAlignment (optional min_score filter)"},
    {"parse_many_chain_chunks", parse_many_chain_chunks, METH_VARARGS, "Parse multiple chain chunks to GenomeAlignment list (optional min_score filter)"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef chainparsermodule = {
    PyModuleDef_HEAD_INIT,
    "_chainparser",
    NULL,
    -1,
    ChainparserMethods
};

PyMODINIT_FUNC PyInit__chainparser(void) {
    import_array();  // required for NumPy C API
    
    PyObject *module = PyModule_Create(&chainparsermodule);
    if (!module) {
        return NULL;
    }
    
    // Import GenomeAlignment class
    PyObject *genome_alignment_module = PyImport_ImportModule("pyrion.core.genome_alignment");
    if (!genome_alignment_module) {
        Py_DECREF(module);
        return NULL;
    }
    
    GenomeAlignment = PyObject_GetAttrString(genome_alignment_module, "GenomeAlignment");
    Py_DECREF(genome_alignment_module);
    
    if (!GenomeAlignment) {
        Py_DECREF(module);
        return NULL;
    }
    
    return module;
}