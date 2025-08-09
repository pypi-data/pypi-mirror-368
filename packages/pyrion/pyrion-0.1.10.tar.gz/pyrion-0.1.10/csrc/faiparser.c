#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <ctype.h>

#ifdef _GNU_SOURCE
#define HAS_STRNDUP 1
#else
#define HAS_STRNDUP 0
#endif

// Configuration constants for performance tuning
#define INITIAL_FAI_CAPACITY 1024
#define NAME_BUFFER_SIZE 256
#define LINE_BUFFER_SIZE 65536

// Structure to hold FAI entry data
typedef struct {
    char *name;         // Sequence name
    long length;        // Sequence length in bases
    long offset;        // Byte offset where sequence starts
    int line_bases;     // Bases per line
    int line_bytes;     // Bytes per line (including newline)
} FaiEntry;

// Dynamic array for FAI entries
typedef struct {
    FaiEntry *entries;
    size_t count;
    size_t capacity;
} FaiArray;

// Custom strndup if not available
#if !HAS_STRNDUP
static char* strndup(const char *s, size_t n) {
    size_t len = strnlen(s, n);
    char *dup = malloc(len + 1);
    if (dup) {
        memcpy(dup, s, len);
        dup[len] = '\0';
    }
    return dup;
}
#endif

// Initialize FAI array with larger initial capacity
static FaiArray* fai_array_new(void) {
    FaiArray *arr = malloc(sizeof(FaiArray));
    if (!arr) return NULL;
    
    arr->entries = malloc(sizeof(FaiEntry) * INITIAL_FAI_CAPACITY);
    if (!arr->entries) {
        free(arr);
        return NULL;
    }
    
    arr->count = 0;
    arr->capacity = INITIAL_FAI_CAPACITY;
    return arr;
}

// Resize FAI array if needed - grow by 1.5x for better memory efficiency
static int fai_array_resize(FaiArray *arr) {
    if (arr->count < arr->capacity) return 0;
    
    size_t new_capacity = arr->capacity + (arr->capacity >> 1);  // 1.5x growth
    FaiEntry *new_entries = realloc(arr->entries, sizeof(FaiEntry) * new_capacity);
    if (!new_entries) return -1;
    
    arr->entries = new_entries;
    arr->capacity = new_capacity;
    return 0;
}

// Add FAI entry to array - uses strndup for efficient name copying
static int fai_array_add(FaiArray *arr, const char *name, size_t name_len, 
                        long length, long offset, int line_bases, int line_bytes) {
    if (fai_array_resize(arr) < 0) return -1;
    
    FaiEntry *entry = &arr->entries[arr->count];
    
    // Use strndup for efficient name copying
    entry->name = strndup(name, name_len);
    if (!entry->name) return -1;
    
    entry->length = length;
    entry->offset = offset;
    entry->line_bases = line_bases;
    entry->line_bytes = line_bytes;
    
    arr->count++;
    return 0;
}

// Free FAI array
static void fai_array_free(FaiArray *arr) {
    if (!arr) return;
    
    for (size_t i = 0; i < arr->count; i++) {
        free(arr->entries[i].name);
    }
    free(arr->entries);
    free(arr);
}

// Check if line is a FASTA header
static inline int is_fasta_header(const char *line) {
    return line[0] == '>';
}

// Extract sequence name length from header - returns pointer and sets length
static const char* extract_sequence_name_info(const char *header, size_t *name_len) {
    if (header[0] != '>') {
        *name_len = 0;
        return NULL;
    }
    
    const char *start = header + 1;  // Skip '>'
    const char *end = start;
    
    // Find end of sequence name (first whitespace or end of string)
    while (*end && !isspace(*end)) {
        end++;
    }
    
    *name_len = end - start;
    return (*name_len > 0) ? start : NULL;
}

// Count bases inline during line processing - optimized version
static inline int count_bases_and_get_line_info(const char *line, size_t line_len, int *total_bytes) {
    int base_count = 0;
    const char *ptr = line;
    const char *end = line + line_len;
    
    // Optimized counting loop - processes 4 chars at a time when possible
    while (ptr + 4 <= end) {
        // Unroll loop for better performance
        if (!isspace(ptr[0])) base_count++;
        if (!isspace(ptr[1])) base_count++;
        if (!isspace(ptr[2])) base_count++;
        if (!isspace(ptr[3])) base_count++;
        ptr += 4;
    }
    
    // Handle remaining characters
    while (ptr < end) {
        if (!isspace(*ptr)) base_count++;
        ptr++;
    }
    
    // Calculate total bytes including newline
    *total_bytes = (int)line_len;
    return base_count;
}

// Main function to parse FASTA and generate FAI entries - heavily optimized
static FaiArray* parse_fasta_to_fai(const char *filename) {
    FILE *file = fopen(filename, "rb");  // Use binary mode for consistent byte counting
    if (!file) {
        PyErr_SetFromErrnoWithFilename(PyExc_IOError, filename);
        return NULL;
    }
    
    FaiArray *fai_array = fai_array_new();
    if (!fai_array) {
        fclose(file);
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate FAI array");
        return NULL;
    }
    
    // Use larger buffer for better I/O performance
    char *line_buffer = malloc(LINE_BUFFER_SIZE);
    if (!line_buffer) {
        fclose(file);
        fai_array_free(fai_array);
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate line buffer");
        return NULL;
    }
    
    // Current sequence tracking
    char *current_name = NULL;
    size_t current_name_len = 0;
    long current_length = 0;
    long current_offset = 0;
    int line_bases = 0;
    int line_bytes = 0;
    int first_seq_line = 1;
    int consistent_line_format = 1;
    
    char *line;
    while ((line = fgets(line_buffer, LINE_BUFFER_SIZE, file)) != NULL) {
        // Get accurate file position BEFORE processing the line
        long line_start_offset = ftell(file) - strlen(line);
        
        // Remove trailing newline and get line info
        size_t line_len = strlen(line);
        int has_newline = 0;
        if (line_len > 0 && line[line_len-1] == '\n') {
            line[line_len-1] = '\0';
            line_len--;
            has_newline = 1;
        }
        
        if (is_fasta_header(line)) {
            // Save previous sequence if exists
            if (current_name) {
                if (fai_array_add(fai_array, current_name, current_name_len, 
                                 current_length, current_offset, line_bases, line_bytes) < 0) {
                    free(current_name);
                    free(line_buffer);
                    fclose(file);
                    fai_array_free(fai_array);
                    PyErr_SetString(PyExc_MemoryError, "Failed to add FAI entry");
                    return NULL;
                }
                free(current_name);  // Free previous name
                current_name = NULL;
            }
            
            // Extract new sequence name info and make a copy
            const char *name_ptr = extract_sequence_name_info(line, &current_name_len);
            if (!name_ptr || current_name_len == 0) {
                free(line_buffer);
                fclose(file);
                fai_array_free(fai_array);
                PyErr_SetString(PyExc_ValueError, "Invalid FASTA header");
                return NULL;
            }
            
            // Make a copy of the name to avoid buffer reuse issues
            current_name = strndup(name_ptr, current_name_len);
            if (!current_name) {
                free(line_buffer);
                fclose(file);
                fai_array_free(fai_array);
                PyErr_SetString(PyExc_MemoryError, "Failed to allocate sequence name");
                return NULL;
            }
            
            // Reset sequence tracking
            current_length = 0;
            current_offset = ftell(file);  // Next line will be start of sequence
            line_bases = 0;
            line_bytes = 0;
            first_seq_line = 1;
            consistent_line_format = 1;
            
        } else if (current_name) {
            // Sequence line - count bases inline
            int total_line_bytes;
            int bases_in_line = count_bases_and_get_line_info(line, line_len, &total_line_bytes);
            
            current_length += bases_in_line;
            
            // Handle line format detection and validation
            if (first_seq_line) {
                line_bases = bases_in_line;
                line_bytes = total_line_bytes + (has_newline ? 1 : 0);
                first_seq_line = 0;
            } else {
                // Check if line format is consistent (except possibly last line)
                if (bases_in_line != line_bases && consistent_line_format) {
                    // This might be the last line or single-line sequence
                    // Keep the original line_bases for consistent formatting
                    consistent_line_format = 0;
                }
            }
        }
    }
    
    // Check for file read errors
    if (ferror(file)) {
        if (current_name) free(current_name);
        free(line_buffer);
        fclose(file);
        fai_array_free(fai_array);
        PyErr_SetFromErrnoWithFilename(PyExc_IOError, filename);
        return NULL;
    }
    
    // Save last sequence if exists
    if (current_name) {
        if (fai_array_add(fai_array, current_name, current_name_len, 
                         current_length, current_offset, line_bases, line_bytes) < 0) {
            free(current_name);
            free(line_buffer);
            fclose(file);
            fai_array_free(fai_array);
            PyErr_SetString(PyExc_MemoryError, "Failed to add final FAI entry");
            return NULL;
        }
        free(current_name);  // Free final name
    }
    
    free(line_buffer);
    fclose(file);
    
    return fai_array;
}

// Python wrapper function
static PyObject* py_parse_fasta_to_fai(PyObject *self, PyObject *args) {
    const char *filename;
    
    if (!PyArg_ParseTuple(args, "s", &filename)) {
        return NULL;
    }
    
    FaiArray *fai_array = parse_fasta_to_fai(filename);
    if (!fai_array) {
        return NULL;  // Error already set
    }
    
    // Convert to Python list of tuples
    PyObject *result = PyList_New(fai_array->count);
    if (!result) {
        fai_array_free(fai_array);
        return NULL;
    }
    
    for (size_t i = 0; i < fai_array->count; i++) {
        FaiEntry *entry = &fai_array->entries[i];
        
        PyObject *tuple = PyTuple_New(5);
        if (!tuple) {
            Py_DECREF(result);
            fai_array_free(fai_array);
            return NULL;
        }
        
        // Create tuple elements
        PyObject *name_obj = PyUnicode_FromString(entry->name);
        PyObject *length_obj = PyLong_FromLong(entry->length);
        PyObject *offset_obj = PyLong_FromLong(entry->offset);
        PyObject *line_bases_obj = PyLong_FromLong(entry->line_bases);
        PyObject *line_bytes_obj = PyLong_FromLong(entry->line_bytes);
        
        if (!name_obj || !length_obj || !offset_obj || !line_bases_obj || !line_bytes_obj) {
            Py_XDECREF(name_obj);
            Py_XDECREF(length_obj);
            Py_XDECREF(offset_obj);
            Py_XDECREF(line_bases_obj);
            Py_XDECREF(line_bytes_obj);
            Py_DECREF(tuple);
            Py_DECREF(result);
            fai_array_free(fai_array);
            return NULL;
        }
        
        PyTuple_SET_ITEM(tuple, 0, name_obj);
        PyTuple_SET_ITEM(tuple, 1, length_obj);
        PyTuple_SET_ITEM(tuple, 2, offset_obj);
        PyTuple_SET_ITEM(tuple, 3, line_bases_obj);
        PyTuple_SET_ITEM(tuple, 4, line_bytes_obj);
        
        PyList_SET_ITEM(result, i, tuple);
    }
    
    fai_array_free(fai_array);
    return result;
}

// Method definitions
static PyMethodDef FaiParserMethods[] = {
    {"parse_fasta_to_fai", py_parse_fasta_to_fai, METH_VARARGS, 
     "Parse FASTA file and return FAI entries as list of tuples"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef faiparsermodule = {
    PyModuleDef_HEAD_INIT,
    "_faiparser",
    "Fast FASTA indexer for generating FAI entries - Production optimized",
    -1,
    FaiParserMethods
};

// Module initialization
PyMODINIT_FUNC PyInit__faiparser(void) {
    return PyModule_Create(&faiparsermodule);
} 