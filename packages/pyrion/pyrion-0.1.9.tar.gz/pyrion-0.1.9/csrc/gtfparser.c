#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

// GTF line structure for parsing
typedef struct {
    char *seqname;
    char *source;
    char *feature;
    int start;       // 0-based
    int end;         // 0-based exclusive
    char *score;
    char strand;
    char *frame;
    char *attributes;
} GTFLine;

// Transcript building structure
typedef struct {
    char *transcript_id;
    char *gene_id;
    char *chrom;
    char strand;
    int *exon_starts;
    int *exon_ends;
    int exon_count;
    int exon_capacity;
    int cds_start;
    int cds_end;
    int has_cds;
} TranscriptBuilder;

// Gene chunk structure
typedef struct {
    char *gene_id;
    TranscriptBuilder **transcripts;
    int transcript_count;
    int transcript_capacity;
} GeneChunk;

// Extract gene_id from attributes string
static char* extract_gene_id(const char* attributes) {
    const char* gene_id_start = strstr(attributes, "gene_id \"");
    if (!gene_id_start) return NULL;
    
    gene_id_start += 9; // Skip "gene_id \""
    const char* gene_id_end = strchr(gene_id_start, '"');
    if (!gene_id_end) return NULL;
    
    size_t len = gene_id_end - gene_id_start;
    char* gene_id = malloc(len + 1);
    if (!gene_id) return NULL;
    
    strncpy(gene_id, gene_id_start, len);
    gene_id[len] = '\0';
    return gene_id;
}

// Extract transcript_id from attributes string
static char* extract_transcript_id(const char* attributes) {
    const char* transcript_id_start = strstr(attributes, "transcript_id \"");
    if (!transcript_id_start) return NULL;
    
    transcript_id_start += 15; // Skip "transcript_id \""
    const char* transcript_id_end = strchr(transcript_id_start, '"');
    if (!transcript_id_end) return NULL;
    
    size_t len = transcript_id_end - transcript_id_start;
    char* transcript_id = malloc(len + 1);
    if (!transcript_id) return NULL;
    
    strncpy(transcript_id, transcript_id_start, len);
    transcript_id[len] = '\0';
    return transcript_id;
}

// Parse a single GTF line
static int parse_gtf_line(const char* line, GTFLine* gtf_line) {
    if (!line || !gtf_line) return 0;
    
    // Skip comments and empty lines
    if (line[0] == '#' || line[0] == '\0' || line[0] == '\n') return 0;
    
    // Make a copy of the line for tokenization
    char* line_copy = strdup(line);
    if (!line_copy) return 0;
    
    char* tokens[9];
    int token_count = 0;
    
    // Split by tabs
    char* token = strtok(line_copy, "\t");
    while (token && token_count < 9) {
        tokens[token_count++] = strdup(token);
        token = strtok(NULL, "\t");
    }
    
    free(line_copy);
    
    if (token_count != 9) {
        // Free allocated tokens
        for (int i = 0; i < token_count; i++) {
            free(tokens[i]);
        }
        return 0;
    }
    
    // Parse coordinates (convert from 1-based to 0-based)
    gtf_line->start = atoi(tokens[3]) - 1;
    gtf_line->end = atoi(tokens[4]);
    
    // Store fields
    gtf_line->seqname = tokens[0];
    gtf_line->source = tokens[1];
    gtf_line->feature = tokens[2];
    gtf_line->score = tokens[5];
    gtf_line->strand = tokens[6][0];
    gtf_line->frame = tokens[7];
    gtf_line->attributes = tokens[8];
    
    // Clean up attributes (remove trailing newline)
    char* newline = strchr(gtf_line->attributes, '\n');
    if (newline) *newline = '\0';
    
    return 1;
}

// Free GTF line
static void free_gtf_line(GTFLine* gtf_line) {
    if (!gtf_line) return;
    free(gtf_line->seqname);
    free(gtf_line->source);
    free(gtf_line->feature);
    free(gtf_line->score);
    free(gtf_line->frame);
    free(gtf_line->attributes);
}

// Create new transcript builder
static TranscriptBuilder* create_transcript_builder(const char* transcript_id, const char* gene_id, 
                                                   const char* chrom, char strand) {
    TranscriptBuilder* builder = malloc(sizeof(TranscriptBuilder));
    if (!builder) return NULL;
    
    builder->transcript_id = strdup(transcript_id);
    builder->gene_id = strdup(gene_id);
    builder->chrom = strdup(chrom);
    builder->strand = strand;
    builder->exon_capacity = 16;
    builder->exon_starts = malloc(builder->exon_capacity * sizeof(int));
    builder->exon_ends = malloc(builder->exon_capacity * sizeof(int));
    builder->exon_count = 0;
    builder->cds_start = -1;
    builder->cds_end = -1;
    builder->has_cds = 0;
    
    return builder;
}

// Add exon to transcript builder
static void add_exon(TranscriptBuilder* builder, int start, int end) {
    if (!builder) return;
    
    // Resize if needed
    if (builder->exon_count >= builder->exon_capacity) {
        builder->exon_capacity *= 2;
        builder->exon_starts = realloc(builder->exon_starts, builder->exon_capacity * sizeof(int));
        builder->exon_ends = realloc(builder->exon_ends, builder->exon_capacity * sizeof(int));
    }
    
    builder->exon_starts[builder->exon_count] = start;
    builder->exon_ends[builder->exon_count] = end;
    builder->exon_count++;
}

// Add CDS to transcript builder
static void add_cds(TranscriptBuilder* builder, int start, int end) {
    if (!builder) return;
    
    if (!builder->has_cds) {
        builder->cds_start = start;
        builder->cds_end = end;
        builder->has_cds = 1;
    } else {
        if (start < builder->cds_start) builder->cds_start = start;
        if (end > builder->cds_end) builder->cds_end = end;
    }
}

// Free transcript builder
static void free_transcript_builder(TranscriptBuilder* builder) {
    if (!builder) return;
    free(builder->transcript_id);
    free(builder->gene_id);
    free(builder->chrom);
    free(builder->exon_starts);
    free(builder->exon_ends);
    free(builder);
}

// Convert transcript builder to Python Transcript object
static PyObject* transcript_builder_to_python(TranscriptBuilder* builder) {
    if (!builder || builder->exon_count == 0) {
        Py_RETURN_NONE;
    }
    
    // Import the Transcript class
    PyObject* pyrion_core_genes = PyImport_ImportModule("pyrion.core.genes");
    if (!pyrion_core_genes) return NULL;
    
    PyObject* transcript_class = PyObject_GetAttrString(pyrion_core_genes, "Transcript");
    Py_DECREF(pyrion_core_genes);
    if (!transcript_class) return NULL;
    
    // Import Strand enum
    PyObject* pyrion_core_strand = PyImport_ImportModule("pyrion.core.strand");
    if (!pyrion_core_strand) {
        Py_DECREF(transcript_class);
        return NULL;
    }
    
    PyObject* strand_class = PyObject_GetAttrString(pyrion_core_strand, "Strand");
    Py_DECREF(pyrion_core_strand);
    if (!strand_class) {
        Py_DECREF(transcript_class);
        return NULL;
    }
    
    // Convert strand
    PyObject* strand_obj;
    if (builder->strand == '+') {
        strand_obj = PyObject_GetAttrString(strand_class, "PLUS");
    } else if (builder->strand == '-') {
        strand_obj = PyObject_GetAttrString(strand_class, "MINUS");
    } else {
        strand_obj = PyObject_GetAttrString(strand_class, "UNKNOWN");
    }
    Py_DECREF(strand_class);
    
    if (!strand_obj) {
        Py_DECREF(transcript_class);
        return NULL;
    }
    
    // Create numpy array for blocks
    PyObject* numpy = PyImport_ImportModule("numpy");
    if (!numpy) {
        Py_DECREF(transcript_class);
        Py_DECREF(strand_obj);
        return NULL;
    }
    
    // Create 2D array: [[start1, end1], [start2, end2], ...]
    npy_intp dims[2] = {builder->exon_count, 2};
    PyObject* blocks_array = PyArray_SimpleNew(2, dims, NPY_INT32);
    if (!blocks_array) {
        Py_DECREF(numpy);
        Py_DECREF(transcript_class);
        Py_DECREF(strand_obj);
        return NULL;
    }
    
    // Fill array with exon coordinates
    int32_t* data = (int32_t*)PyArray_DATA((PyArrayObject*)blocks_array);
    for (int i = 0; i < builder->exon_count; i++) {
        data[i * 2] = builder->exon_starts[i];
        data[i * 2 + 1] = builder->exon_ends[i];
    }
    
    Py_DECREF(numpy);
    
    PyObject* chrom_bytes = PyUnicode_FromString(builder->chrom);
    if (!chrom_bytes) {
        Py_DECREF(transcript_class);
        Py_DECREF(strand_obj);
        Py_DECREF(blocks_array);
        return NULL;
    }
    
    // Create transcript arguments
    PyObject* args = PyTuple_New(0);
    PyObject* kwargs = PyDict_New();
    
    PyDict_SetItemString(kwargs, "blocks", blocks_array);
    PyDict_SetItemString(kwargs, "strand", strand_obj);
    PyDict_SetItemString(kwargs, "chrom", chrom_bytes);
    PyDict_SetItemString(kwargs, "id", PyUnicode_FromString(builder->transcript_id));
    
    // Add CDS info if present
    if (builder->has_cds) {
        PyDict_SetItemString(kwargs, "cds_start", PyLong_FromLong(builder->cds_start));
        PyDict_SetItemString(kwargs, "cds_end", PyLong_FromLong(builder->cds_end));
    }
    
    // Create transcript object
    PyObject* transcript = PyObject_Call(transcript_class, args, kwargs);
    
    // Cleanup
    Py_DECREF(transcript_class);
    Py_DECREF(strand_obj);
    Py_DECREF(blocks_array);
    Py_DECREF(chrom_bytes);
    Py_DECREF(args);
    Py_DECREF(kwargs);
    
    return transcript;
}

// Parse GTF chunk (lines for a single gene)
static PyObject* parse_gtf_chunk(PyObject* self, PyObject* args) {
    PyObject* lines_list;
    if (!PyArg_ParseTuple(args, "O", &lines_list)) {
        return NULL;
    }
    
    if (!PyList_Check(lines_list)) {
        PyErr_SetString(PyExc_TypeError, "Expected list of lines");
        return NULL;
    }
    
    Py_ssize_t num_lines = PyList_Size(lines_list);
    if (num_lines == 0) {
        return PyTuple_New(2); // Empty transcript list and empty mapping
    }
    
    // Hash map for transcript builders (transcript_id -> TranscriptBuilder*)
    PyObject* transcript_builders = PyDict_New();
    char* gene_id = NULL;
    
    // Process each line
    for (Py_ssize_t i = 0; i < num_lines; i++) {
        PyObject* line_obj = PyList_GetItem(lines_list, i);
        if (!PyUnicode_Check(line_obj)) continue;
        
        const char* line = PyUnicode_AsUTF8(line_obj);
        if (!line) continue;
        
        GTFLine gtf_line;
        if (!parse_gtf_line(line, &gtf_line)) continue;
        
        // Extract gene_id and transcript_id
        char* current_gene_id = extract_gene_id(gtf_line.attributes);
        char* transcript_id = extract_transcript_id(gtf_line.attributes);
        
        if (!current_gene_id) {
            free_gtf_line(&gtf_line);
            continue;
        }
        
        // Store gene_id for mapping
        if (!gene_id) {
            gene_id = strdup(current_gene_id);
        }
        
        // Process transcript and exon features
        if (transcript_id && (strcmp(gtf_line.feature, "exon") == 0 || strcmp(gtf_line.feature, "CDS") == 0)) {
            // Get or create transcript builder
            PyObject* builder_obj = PyDict_GetItemString(transcript_builders, transcript_id);
            TranscriptBuilder* builder = NULL;
            
            if (!builder_obj) {
                // Create new transcript builder
                builder = create_transcript_builder(transcript_id, current_gene_id, 
                                                  gtf_line.seqname, gtf_line.strand);
                builder_obj = PyCapsule_New(builder, NULL, NULL);
                PyDict_SetItemString(transcript_builders, transcript_id, builder_obj);
                Py_DECREF(builder_obj);
            } else {
                builder = (TranscriptBuilder*)PyCapsule_GetPointer(builder_obj, NULL);
            }
            
            // Add features
            if (strcmp(gtf_line.feature, "exon") == 0) {
                add_exon(builder, gtf_line.start, gtf_line.end);
            } else if (strcmp(gtf_line.feature, "CDS") == 0) {
                add_cds(builder, gtf_line.start, gtf_line.end);
            }
        }
        
        free(current_gene_id);
        free(transcript_id);
        free_gtf_line(&gtf_line);
    }
    
    // Convert transcript builders to Python Transcript objects
    PyObject* transcripts_list = PyList_New(0);
    PyObject* gene_mapping = PyDict_New();
    
    PyObject* key, *value;
    Py_ssize_t pos = 0;
    
    while (PyDict_Next(transcript_builders, &pos, &key, &value)) {
        TranscriptBuilder* builder = (TranscriptBuilder*)PyCapsule_GetPointer(value, NULL);
        if (builder && builder->exon_count > 0) {
            PyObject* transcript = transcript_builder_to_python(builder);
            if (transcript && transcript != Py_None) {
                PyList_Append(transcripts_list, transcript);
                
                // Add to gene mapping
                PyDict_SetItem(gene_mapping, key, PyUnicode_FromString(gene_id ? gene_id : ""));
                Py_DECREF(transcript);
            }
        }
        free_transcript_builder(builder);
    }
    
    Py_DECREF(transcript_builders);
    free(gene_id);
    
    // Return tuple of (transcripts_list, gene_mapping_dict)
    PyObject* result = PyTuple_New(2);
    PyTuple_SetItem(result, 0, transcripts_list);
    PyTuple_SetItem(result, 1, gene_mapping);
    
    return result;
}

// Module method definitions
static PyMethodDef gtfparser_methods[] = {
    {"parse_gtf_chunk", parse_gtf_chunk, METH_VARARGS, "Parse GTF chunk into transcripts and gene mapping"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef gtfparser_module = {
    PyModuleDef_HEAD_INIT,
    "_gtfparser",
    "High-performance GTF parser",
    -1,
    gtfparser_methods
};

// Module initialization
PyMODINIT_FUNC PyInit__gtfparser(void) {
    import_array(); // Initialize numpy
    return PyModule_Create(&gtfparser_module);
} 