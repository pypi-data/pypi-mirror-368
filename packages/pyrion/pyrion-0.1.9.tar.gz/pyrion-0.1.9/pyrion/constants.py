# Constants for exon naming
from .core_types import ExonType

EXON_PREFIXES = {
    ExonType.ALL: "exon",
    ExonType.CDS: "cds_exon",
    ExonType.UTR5: "utr5_exon",
    ExonType.UTR3: "utr3_exon"
}

# Constants for numbering
EXON_NUMBER_START = 1
EXON_ID_SEPARATOR = ":"
