#define PY_SSIZE_T_CLEAN
#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <ctype.h>

#ifdef _GNU_SOURCE
#define HAS_GETLINE 1
#else
#define HAS_GETLINE 0
#endif

// Sequence type constants
#define SEQUENCE_TYPE_DNA 0
#define SEQUENCE_TYPE_RNA 1
#define SEQUENCE_TYPE_PROTEIN 2

// Multiplicative nucleotide encoding constants
// Unmasked (uppercase)
#define ADENINE 1             // A = +1
#define GUANINE 2             // G = +2  
#define THYMINE -1            // T = -1
#define URACIL -1             // U = -1 (same as T)
#define CYTOSINE -2           // C = -2
#define UNKNOWN 3             // N = +3 (self-complementary)
#define UNKNOWN_COMP -3       // N = -3 (complement form)

// Masked (lowercase) - multiply by 5
#define ADENINE_MASKED 5      // a = +5 (1 × 5)
#define GUANINE_MASKED 10     // g = +10 (2 × 5)
#define THYMINE_MASKED -5     // t = -5 (-1 × 5)
#define URACIL_MASKED -5      // u = -5 (-1 × 5)
#define CYTOSINE_MASKED -10   // c = -10 (-2 × 5)
#define UNKNOWN_MASKED 15     // n = +15 (3 × 5)
#define UNKNOWN_MASKED_COMP -15  // n = -15 (-3 × 5)

// Gaps (neutral under multiplication)
#define GAP 0

// Frameshifts (self-complementary, different numbers but same semantics)
#define FRAMESHIFT_1 13
#define FRAMESHIFT_1_COMP -13
#define FRAMESHIFT_1_MASKED 65
#define FRAMESHIFT_1_MASKED_COMP -65

// Invalid character (same as GAP in new system)
#define INVALID_CHARACTER 0

// Prime-based amino acid encoding constants
#define STOP_AMINO_ACID 1
#define ALANINE_AA 2
#define ARGININE_AA 3
#define ASPARAGINE_AA 5
#define ASPARTIC_ACID_AA 7
#define CYSTEINE_AA 11
#define GLUTAMIC_ACID_AA 13
#define GLUTAMINE_AA 17
#define GLYCINE_AA 19
#define HISTIDINE_AA 23
#define ISOLEUCINE_AA 29
#define LEUCINE_AA 31
#define LYSINE_AA 37
#define METHIONINE_AA 41
#define PHENYLALANINE_AA 43
#define PROLINE_AA 47
#define SERINE_AA 53
#define THREONINE_AA 59
#define TRYPTOPHAN_AA 61
#define TYROSINE_AA 67
#define VALINE_AA 71
#define ASPARAGINE_OR_ASPARTIC_AA 73
#define GLUTAMINE_OR_GLUTAMIC_AA 79
#define LEUCINE_OR_ISOLEUCINE_AA 83
#define SELENOCYSTEINE_AA 89
#define PYRROLYSINE_AA 97
#define UNKNOWN_AMINO_ACID 101

// Fast nucleotide lookup table (256 entries for all possible bytes)
static int8_t nucleotide_lookup[256];
static int8_t amino_acid_lookup[256];  // Changed to int8_t for prime-based encoding
static int lookup_initialized = 0;

// Initialize lookup tables for fast encoding
static void init_lookup_tables(void) {
    if (lookup_initialized) return;
    
    // Initialize all to invalid (0)
    for (int i = 0; i < 256; i++) {
        nucleotide_lookup[i] = INVALID_CHARACTER;
        amino_acid_lookup[i] = UNKNOWN_AMINO_ACID;
    }
    
    // Multiplicative nucleotide encoding scheme - Unmasked (uppercase)
    nucleotide_lookup['A'] = ADENINE;
    nucleotide_lookup['G'] = GUANINE;
    nucleotide_lookup['T'] = THYMINE;
    nucleotide_lookup['U'] = URACIL;
    nucleotide_lookup['C'] = CYTOSINE;
    nucleotide_lookup['N'] = UNKNOWN;
    nucleotide_lookup['-'] = GAP;
    
    // Masked (lowercase) - multiply by 5
    nucleotide_lookup['a'] = ADENINE_MASKED;
    nucleotide_lookup['g'] = GUANINE_MASKED;
    nucleotide_lookup['t'] = THYMINE_MASKED;
    nucleotide_lookup['u'] = URACIL_MASKED;
    nucleotide_lookup['c'] = CYTOSINE_MASKED;
    nucleotide_lookup['n'] = UNKNOWN_MASKED;
    // Note: gaps remain neutral (0) regardless of case
    
    // Prime-based amino acid encoding
    amino_acid_lookup['*'] = STOP_AMINO_ACID;                  // Stop = 1
    amino_acid_lookup['A'] = ALANINE_AA;                       // Alanine = 2
    amino_acid_lookup['R'] = ARGININE_AA;                      // Arginine = 3
    amino_acid_lookup['N'] = ASPARAGINE_AA;                    // Asparagine = 5
    amino_acid_lookup['D'] = ASPARTIC_ACID_AA;                 // Aspartic acid = 7
    amino_acid_lookup['C'] = CYSTEINE_AA;                      // Cysteine = 11
    amino_acid_lookup['E'] = GLUTAMIC_ACID_AA;                 // Glutamic acid = 13
    amino_acid_lookup['Q'] = GLUTAMINE_AA;                     // Glutamine = 17
    amino_acid_lookup['G'] = GLYCINE_AA;                       // Glycine = 19
    amino_acid_lookup['H'] = HISTIDINE_AA;                     // Histidine = 23
    amino_acid_lookup['I'] = ISOLEUCINE_AA;                    // Isoleucine = 29
    amino_acid_lookup['L'] = LEUCINE_AA;                       // Leucine = 31
    amino_acid_lookup['K'] = LYSINE_AA;                        // Lysine = 37
    amino_acid_lookup['M'] = METHIONINE_AA;                    // Methionine = 41
    amino_acid_lookup['F'] = PHENYLALANINE_AA;                 // Phenylalanine = 43
    amino_acid_lookup['P'] = PROLINE_AA;                       // Proline = 47
    amino_acid_lookup['S'] = SERINE_AA;                        // Serine = 53
    amino_acid_lookup['T'] = THREONINE_AA;                     // Threonine = 59
    amino_acid_lookup['W'] = TRYPTOPHAN_AA;                    // Tryptophan = 61
    amino_acid_lookup['Y'] = TYROSINE_AA;                      // Tyrosine = 67
    amino_acid_lookup['V'] = VALINE_AA;                        // Valine = 71
    amino_acid_lookup['B'] = ASPARAGINE_OR_ASPARTIC_AA;        // Asparagine or Aspartic acid = 73
    amino_acid_lookup['Z'] = GLUTAMINE_OR_GLUTAMIC_AA;         // Glutamine or Glutamic acid = 79
    amino_acid_lookup['J'] = LEUCINE_OR_ISOLEUCINE_AA;         // Leucine or Isoleucine = 83
    amino_acid_lookup['U'] = SELENOCYSTEINE_AA;                // Selenocysteine = 89
    amino_acid_lookup['O'] = PYRROLYSINE_AA;                   // Pyrrolysine = 97
    amino_acid_lookup['X'] = UNKNOWN_AMINO_ACID;               // Unknown = 101
    
    // Masked amino acids (lowercase) - multiply by -1
    amino_acid_lookup['a'] = -ALANINE_AA;                      // a = -2
    amino_acid_lookup['r'] = -ARGININE_AA;                     // r = -3
    amino_acid_lookup['n'] = -ASPARAGINE_AA;                   // n = -5
    amino_acid_lookup['d'] = -ASPARTIC_ACID_AA;                // d = -7
    amino_acid_lookup['c'] = -CYSTEINE_AA;                     // c = -11
    amino_acid_lookup['e'] = -GLUTAMIC_ACID_AA;                // e = -13
    amino_acid_lookup['q'] = -GLUTAMINE_AA;                    // q = -17
    amino_acid_lookup['g'] = -GLYCINE_AA;                      // g = -19
    amino_acid_lookup['h'] = -HISTIDINE_AA;                    // h = -23
    amino_acid_lookup['i'] = -ISOLEUCINE_AA;                   // i = -29
    amino_acid_lookup['l'] = -LEUCINE_AA;                      // l = -31
    amino_acid_lookup['k'] = -LYSINE_AA;                       // k = -37
    amino_acid_lookup['m'] = -METHIONINE_AA;                   // m = -41
    amino_acid_lookup['f'] = -PHENYLALANINE_AA;                // f = -43
    amino_acid_lookup['p'] = -PROLINE_AA;                      // p = -47
    amino_acid_lookup['s'] = -SERINE_AA;                       // s = -53
    amino_acid_lookup['t'] = -THREONINE_AA;                    // t = -59
    amino_acid_lookup['w'] = -TRYPTOPHAN_AA;                   // w = -61
    amino_acid_lookup['y'] = -TYROSINE_AA;                     // y = -67
    amino_acid_lookup['v'] = -VALINE_AA;                       // v = -71
    amino_acid_lookup['b'] = -ASPARAGINE_OR_ASPARTIC_AA;       // b = -73
    amino_acid_lookup['z'] = -GLUTAMINE_OR_GLUTAMIC_AA;        // z = -79
    amino_acid_lookup['j'] = -LEUCINE_OR_ISOLEUCINE_AA;        // j = -83
    amino_acid_lookup['u'] = -SELENOCYSTEINE_AA;               // u = -89
    amino_acid_lookup['o'] = -PYRROLYSINE_AA;                  // o = -97
    amino_acid_lookup['x'] = -UNKNOWN_AMINO_ACID;              // x = -101
    
    lookup_initialized = 1;
}

// Fast sequence encoding functions
static void encode_nucleotides_fast(const char *sequence, size_t length, int8_t *output) {
    for (size_t i = 0; i < length; i++) {
        output[i] = nucleotide_lookup[(unsigned char)sequence[i]];
    }
}

static void encode_amino_acids_fast(const char *sequence, size_t length, int8_t *output) {
    for (size_t i = 0; i < length; i++) {
        output[i] = amino_acid_lookup[(unsigned char)sequence[i]];
    }
}

// Optimized buffer for reading large sequences efficiently
typedef struct {
    char *data;
    size_t capacity;
    size_t length;
} SequenceBuffer;

static int buffer_init(SequenceBuffer *buffer, size_t initial_capacity) {
    buffer->data = malloc(initial_capacity);
    if (!buffer->data) {
        return -1;
    }
    buffer->capacity = initial_capacity;
    buffer->length = 0;
    return 0;
}

static int buffer_ensure_capacity(SequenceBuffer *buffer, size_t needed) {
    if (buffer->capacity >= needed) {
        return 0;
    }
    
    // Double capacity until we have enough space
    size_t new_capacity = buffer->capacity;
    while (new_capacity < needed) {
        new_capacity <<= 1;  // Equivalent to *= 2 but faster
    }
    
    char *new_data = realloc(buffer->data, new_capacity);
    if (!new_data) {
        return -1;
    }
    
    buffer->data = new_data;
    buffer->capacity = new_capacity;
    return 0;
}

static int buffer_append_clean(SequenceBuffer *buffer, const char *data, size_t length) {
    // Pre-calculate needed space for non-whitespace characters
    size_t clean_chars = 0;
    for (size_t i = 0; i < length; i++) {
        if (!isspace(data[i])) {
            clean_chars++;
        }
    }
    
    if (clean_chars == 0) return 0;
    
    if (buffer_ensure_capacity(buffer, buffer->length + clean_chars) != 0) {
        return -1;
    }
    
    // Copy only non-whitespace characters
    char *dest = buffer->data + buffer->length;
    for (size_t i = 0; i < length; i++) {
        if (!isspace(data[i])) {
            *dest++ = data[i];
        }
    }
    
    buffer->length += clean_chars;
    return 0;
}

static void buffer_clear(SequenceBuffer *buffer) {
    buffer->length = 0;
}

static void buffer_free(SequenceBuffer *buffer) {
    free(buffer->data);
    buffer->data = NULL;
    buffer->capacity = 0;
    buffer->length = 0;
}

// Custom getline implementation for systems without getline()
#if !HAS_GETLINE
static ssize_t custom_getline(char **lineptr, size_t *n, FILE *stream) {
    if (!lineptr || !n || !stream) {
        return -1;
    }
    
    if (*lineptr == NULL || *n == 0) {
        *n = 128;
        *lineptr = malloc(*n);
        if (!*lineptr) {
            return -1;
        }
    }
    
    size_t pos = 0;
    int c;
    
    while ((c = fgetc(stream)) != EOF) {
        if (pos + 1 >= *n) {
            size_t new_size = *n * 2;
            char *new_ptr = realloc(*lineptr, new_size);
            if (!new_ptr) {
                return -1;
            }
            *lineptr = new_ptr;
            *n = new_size;
        }
        
        (*lineptr)[pos++] = c;
        
        if (c == '\n') {
            break;
        }
    }
    
    if (pos == 0 && c == EOF) {
        return -1;
    }
    
    (*lineptr)[pos] = '\0';
    return pos;
}
#endif

// Helper function to process a complete sequence
static PyObject* create_sequence_tuple(const char *header, SequenceBuffer *seq_buffer, int sequence_type) {
    if (!header || !seq_buffer || seq_buffer->length == 0) {
        return NULL;
    }
    
    PyObject *array = NULL;
    PyObject *seq_tuple = NULL;
    
    if (sequence_type == SEQUENCE_TYPE_PROTEIN) {
        // Create amino acid sequence
        npy_intp dims[] = {(npy_intp)seq_buffer->length};
        array = PyArray_SimpleNew(1, dims, NPY_INT8);
        if (!array) {
            return NULL;
        }
        
        int8_t *array_data = (int8_t*)PyArray_DATA((PyArrayObject*)array);
        encode_amino_acids_fast(seq_buffer->data, seq_buffer->length, array_data);
    } else {
        // Create nucleotide sequence (DNA or RNA)
        npy_intp dims[] = {(npy_intp)seq_buffer->length};
        array = PyArray_SimpleNew(1, dims, NPY_INT8);
        if (!array) {
            return NULL;
        }
        
        int8_t *array_data = (int8_t*)PyArray_DATA((PyArrayObject*)array);
        encode_nucleotides_fast(seq_buffer->data, seq_buffer->length, array_data);
    }
    
    seq_tuple = Py_BuildValue("(sOi)", header, array, sequence_type);
    Py_DECREF(array);  // Py_BuildValue increments reference, so we decref here
    
    return seq_tuple;
}

// Optimized FASTA parsing function
static PyObject* parse_fasta_fast(PyObject* self, PyObject* args) {
    const char *filename;
    int sequence_type;  // 0=DNA, 1=RNA, 2=PROTEIN
    
    if (!PyArg_ParseTuple(args, "si", &filename, &sequence_type)) {
        return NULL;
    }
    
    if (sequence_type < 0 || sequence_type > 2) {
        PyErr_SetString(PyExc_ValueError, "sequence_type must be 0 (DNA), 1 (RNA), or 2 (PROTEIN)");
        return NULL;
    }
    
    init_lookup_tables();
    
    FILE *file = fopen(filename, "r");
    if (!file) {
        PyErr_Format(PyExc_IOError, "Cannot open file: %s", filename);
        return NULL;
    }
    
    PyObject *sequences_list = PyList_New(0);
    if (!sequences_list) {
        fclose(file);
        return NULL;
    }
    
    SequenceBuffer seq_buffer;
    if (buffer_init(&seq_buffer, 8192) != 0) {  // Start with 8KB
        fclose(file);
        Py_DECREF(sequences_list);
        PyErr_NoMemory();
        return NULL;
    }
    
    // Use getline for handling very long lines
    char *line = NULL;
    size_t line_capacity = 0;
    ssize_t line_length;
    
    char *current_header = NULL;
    int in_sequence = 0;
    
#if HAS_GETLINE
    while ((line_length = getline(&line, &line_capacity, file)) != -1) {
#else
    while ((line_length = custom_getline(&line, &line_capacity, file)) != -1) {
#endif
        // Remove trailing newline/carriage return efficiently
        if (line_length > 0 && line[line_length-1] == '\n') {
            line[--line_length] = '\0';
        }
        if (line_length > 0 && line[line_length-1] == '\r') {
            line[--line_length] = '\0';
        }
        
        if (line_length > 0 && line[0] == '>') {
            // Process previous sequence if we have one
            if (in_sequence && current_header && seq_buffer.length > 0) {
                PyObject *seq_tuple = create_sequence_tuple(current_header, &seq_buffer, sequence_type);
                if (!seq_tuple) {
                    goto error_cleanup;
                }
                
                if (PyList_Append(sequences_list, seq_tuple) != 0) {
                    Py_DECREF(seq_tuple);
                    goto error_cleanup;
                }
                Py_DECREF(seq_tuple);
            }
            
            // Start new sequence - header is line+1 (skip '>'), not further processed
            free(current_header);
            current_header = strdup(line + 1);
            if (!current_header) {
                PyErr_NoMemory();
                goto error_cleanup;
            }
            
            buffer_clear(&seq_buffer);
            in_sequence = 1;
            
        } else if (in_sequence && line_length > 0) {
            // Append sequence line (remove whitespace efficiently)
            if (buffer_append_clean(&seq_buffer, line, line_length) != 0) {
                PyErr_NoMemory();
                goto error_cleanup;
            }
        }
    }
    
    // Check for file read errors
    if (ferror(file)) {
        PyErr_SetFromErrnoWithFilename(PyExc_IOError, filename);
        goto error_cleanup;
    }
    
    // Process final sequence if we have one
    if (in_sequence && current_header && seq_buffer.length > 0) {
        PyObject *seq_tuple = create_sequence_tuple(current_header, &seq_buffer, sequence_type);
        if (seq_tuple) {
            if (PyList_Append(sequences_list, seq_tuple) == 0) {
                Py_DECREF(seq_tuple);
            } else {
                Py_DECREF(seq_tuple);
                goto error_cleanup;
            }
        }
    }
    
    // Cleanup and return success
    buffer_free(&seq_buffer);
    free(current_header);
    free(line);
    fclose(file);
    
    return sequences_list;

error_cleanup:
    buffer_free(&seq_buffer);
    free(current_header);
    free(line);
    fclose(file);
    Py_DECREF(sequences_list);
    return NULL;
}

// Method definitions
static PyMethodDef FastaParserMethods[] = {
    {"parse_fasta_fast", parse_fasta_fast, METH_VARARGS,
     "Fast FASTA file parser returning encoded sequences"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef fastaparsermodule = {
    PyModuleDef_HEAD_INIT,
    "_fastaparser",
    "Fast FASTA file parser with numpy integration - Production optimized",
    -1,
    FastaParserMethods
};

// Module initialization
PyMODINIT_FUNC PyInit__fastaparser(void) {
    // Import numpy first
    import_array();
    
    PyObject *module = PyModule_Create(&fastaparsermodule);
    if (!module) {
        return NULL;
    }
    
    return module;
} 