"""Data consistency checking utilities."""

from typing import List
from ..core.genes import TranscriptsCollection


def check_data_consistency(transcripts_collection: TranscriptsCollection, detailed: bool = False) -> str:
    """Check data consistency in a transcripts collection.
    
    Analyzes the consistency of applied gene data mappings and reports issues:
    - Transcripts without gene IDs (if gene-transcript mapping was applied)
    - Transcripts without biotypes (if biotype mapping was applied)
    - Genes without names (if gene names were applied)
    """
    report_lines = []
    report_lines.append("Data Consistency Report")
    report_lines.append("=" * 50)
    report_lines.append("")
    
    # Check what mappings were applied
    has_gene_mapping = transcripts_collection.has_gene_mapping
    applied_biotypes = transcripts_collection.applied_biotypes  
    applied_gene_names = transcripts_collection.applied_gene_names
    
    if not any([has_gene_mapping, applied_biotypes, applied_gene_names]):
        report_lines.append("No gene data mappings have been applied to this collection.")
        return "\n".join(report_lines)
    
    report_lines.append("Applied mappings:")
    if has_gene_mapping:
        report_lines.append("  ✓ Gene-transcript mapping")
    if applied_biotypes:
        report_lines.append("  ✓ Transcript biotypes")
    if applied_gene_names:
        report_lines.append("  ✓ Gene names")
    report_lines.append("")
    
    transcripts_without_genes: List[str] = []
    transcripts_without_biotypes: List[str] = []
    
    for transcript in transcripts_collection.transcripts:
        if has_gene_mapping:
            try:
                gene = transcripts_collection.get_gene_by_transcript_id(transcript.id)
                if gene is None:
                    transcripts_without_genes.append(transcript.id)
            except:
                transcripts_without_genes.append(transcript.id)
        
        if applied_biotypes and transcript.biotype is None:
            transcripts_without_biotypes.append(transcript.id)
    
    genes_without_names: List[str] = []
    if has_gene_mapping and applied_gene_names:
        try:
            for gene in transcripts_collection.genes:
                if gene.gene_name is None:
                    genes_without_names.append(gene.gene_id)
        except:
            pass
    
    issues_found = False
    
    if transcripts_without_genes:
        issues_found = True
        report_lines.append(f"⚠️  Transcripts without gene mapping: {len(transcripts_without_genes)}")
        if detailed:
            for transcript_id in transcripts_without_genes[:100]:  # Limit to first 100
                report_lines.append(f"   - {transcript_id}")
            if len(transcripts_without_genes) > 100:
                report_lines.append(f"   ... and {len(transcripts_without_genes) - 100} more")
        else:
            report_lines.append("   (Use detailed=True for complete list)")
        report_lines.append("")
    
    if transcripts_without_biotypes:
        issues_found = True
        report_lines.append(f"⚠️  Transcripts without biotype: {len(transcripts_without_biotypes)}")
        if detailed:
            for transcript_id in transcripts_without_biotypes[:100]:  # Limit to first 100
                report_lines.append(f"   - {transcript_id}")
            if len(transcripts_without_biotypes) > 100:
                report_lines.append(f"   ... and {len(transcripts_without_biotypes) - 100} more")
        else:
            report_lines.append("   (Use detailed=True for complete list)")
        report_lines.append("")
    
    if genes_without_names:
        issues_found = True
        report_lines.append(f"⚠️  Genes without names: {len(genes_without_names)}")
        if detailed:
            for gene_id in genes_without_names[:100]:  # Limit to first 100
                report_lines.append(f"   - {gene_id}")
            if len(genes_without_names) > 100:
                report_lines.append(f"   ... and {len(genes_without_names) - 100} more")
        else:
            report_lines.append("   (Use detailed=True for complete list)")
        report_lines.append("")
    
    if not issues_found:
        report_lines.append("✅ No consistency issues found!")
    else:
        report_lines.append("Issues summary:")
        if transcripts_without_genes:
            report_lines.append(f"   - {len(transcripts_without_genes)} transcripts lack gene mapping")
        if transcripts_without_biotypes:
            report_lines.append(f"   - {len(transcripts_without_biotypes)} transcripts lack biotypes")
        if genes_without_names:
            report_lines.append(f"   - {len(genes_without_names)} genes lack names")
    
    return "\n".join(report_lines)