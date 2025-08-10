"""The visualization module was quickly prototyped in Cursor without thorough design.

A cleaner architecture and improved visuals are planned for a future release."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Optional
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from .core.intervals import GenomicInterval
from .core.genome_alignment import GenomeAlignment
from .core.genes import Transcript


class TrackType(Enum):
    INTERVALS = "intervals"
    ALIGNMENTS = "alignments" 
    TRANSCRIPTS = "transcripts"


class GenomicFeature(ABC):
    """Abstract base class for genomic features with start/end coordinates."""
    
    @property
    @abstractmethod
    def start(self) -> int:
        pass
    
    @property
    @abstractmethod
    def end(self) -> int:
        pass
    
    @property
    def length(self) -> int:
        return self.end - self.start


class Band:
    """Holds non-overlapping features placed in same vertical band."""
    
    def __init__(self, index: int):
        self.features: List[GenomicFeature] = []
        self.index = index
    
    def can_add_feature(self, feature: GenomicFeature) -> bool:
        """Check if feature can be added without overlap."""
        for existing in self.features:
            if not (feature.end <= existing.start or feature.start >= existing.end):
                return False
        return True
    
    def add_feature(self, feature: GenomicFeature):
        """Add feature to this band."""
        self.features.append(feature)


class Level:
    """Contains features of one type, produces non-overlapping bands."""
    
    def __init__(self):
        self.features: List[GenomicFeature] = []
        self.bands: List[Band] = []
    
    def add_features(self, features: List[GenomicFeature]):
        """Add features to this level."""
        self.features.extend(features)
    
    def compute_bands(self):
        """Greedy algorithm to assign features to non-overlapping bands."""
        self.bands = []
        
        # Sort features by start position for efficient packing
        sorted_features = sorted(self.features, key=lambda f: f.start)
        
        for feature in sorted_features:
            # Try to place in existing band
            placed = False
            for band in self.bands:
                if band.can_add_feature(feature):
                    band.add_feature(feature)
                    placed = True
                    break
            
            # Create new band if needed
            if not placed:
                new_band = Band(len(self.bands))
                new_band.add_feature(feature)
                self.bands.append(new_band)


class LayoutManager:
    """Assigns tracks to levels and produces packed band layout."""
    
    def __init__(self):
        self.levels: Dict[TrackType, Level] = {
            TrackType.INTERVALS: Level(),
            TrackType.ALIGNMENTS: Level(), 
            TrackType.TRANSCRIPTS: Level()
        }
    
    def add_track(self, track: 'Track'):
        """Assign track to correct level based on type."""
        level = self.levels[track.type]
        level.add_features(track.features)
    
    def compute_layout(self):
        """Run layout logic for all levels."""
        for level in self.levels.values():
            level.compute_bands()
    
    def get_total_bands(self) -> int:
        """Get total number of bands across all levels."""
        return sum(len(level.bands) for level in self.levels.values())


class Track:
    """Logical unit of data belonging to one category."""
    
    def __init__(self, name: str, features: List[GenomicFeature], track_type: TrackType):
        self.name = name
        self.features = features
        self.type = track_type


class GenomicRuler:
    """Renders genomic coordinate ruler with fixed height."""
    
    def __init__(self, interval: GenomicInterval, tick_count: int = 10, 
                 inverted: bool = False, height: float = 0.15):
        self.interval = interval
        self.tick_count = tick_count
        self.inverted = inverted
        self.height = height
    
    def draw(self, ax, y: float = 0.0):
        """Draw ruler at specified y position."""
        # Main ruler line
        ax.hlines(y, self.interval.start, self.interval.end, 
                 color="black", linewidth=2)
        
        # Calculate tick positions
        ticks = np.linspace(self.interval.start, self.interval.end, 
                           self.tick_count + 1, dtype=int)
        
        # Use fixed visual tick length that doesn't scale with coordinate space
        # Get the total coordinate range to normalize tick size
        ylim = ax.get_ylim()
        coord_range = ylim[1] - ylim[0]
        # Fixed visual tick length as a small fraction of coordinate space
        tick_len = coord_range * 0.02  # Always 2% of coordinate space
        
        for x in ticks:
            if self.inverted:
                # Tick goes down, label above
                ax.add_line(mlines.Line2D([x, x], [y, y - tick_len], 
                                        color="black", linewidth=1))
                ax.text(x, y + tick_len * 0.5, f"{x:,}", 
                       ha="center", va="bottom", fontsize=8, rotation=45)
            else:
                # Tick goes up, label below
                ax.add_line(mlines.Line2D([x, x], [y, y + tick_len], 
                                        color="black", linewidth=1))
                ax.text(x, y - tick_len * 1.5, f"{x:,}", 
                       ha="center", va="top", fontsize=8, rotation=45)


class VisualizationWindow:
    """Entry point for rendering genomic data visualization."""
    
    def __init__(self, interval: GenomicInterval, height: Optional[float] = None, 
                 band_height: float = 0.35, band_spacing: float = 0.05, 
                 level_spacing: float = 0.2, ruler_height: float = 0.4, 
                 label_height: float = 0.15, show_labels: bool = True,
                 left_padding_width: int = 15000, show_feature_labels: bool = True):
        self.interval = interval
        self.tracks: List[Track] = []
        self.layout_manager = LayoutManager()
        self.height = height
        self.band_height = band_height  # Fixed absolute height per band
        self.band_spacing = band_spacing  # Small gap between bands in same level
        self.level_spacing = level_spacing  # Larger gap between different levels
        self.ruler_height = ruler_height  # Fixed ruler height
        self.ruler_to_content_spacing = 0.3  # Gap between ruler and first band
        self.label_height = label_height  # Height reserved for track labels
        self.show_labels = show_labels  # Whether to show track labels
        self.left_padding_width = left_padding_width  # Fixed width for feature labels (in genomic coordinates)
        self.show_feature_labels = show_feature_labels  # Whether to show individual feature labels
    
    def add_track(self, track: Track):
        """Add a track to the window."""
        self.tracks.append(track)
        self.layout_manager.add_track(track)
    
    def _get_level_track_names(self, track_type: TrackType) -> str:
        """Get combined track names for a given level."""
        track_names = [track.name for track in self.tracks if track.type == track_type]
        if len(track_names) == 0:
            return ""
        elif len(track_names) == 1:
            return track_names[0]
        else:
            return " + ".join(track_names)  # Combine multiple track names
    
    def _get_feature_id(self, feature: GenomicFeature) -> Optional[str]:
        """Extract a display ID from a genomic feature."""
        if hasattr(feature, '_transcript'):
            # Transcript feature - the ID is stored in .id attribute
            transcript = feature._transcript
            if hasattr(transcript, 'id') and transcript.id:
                transcript_id = transcript.id
                
                # Add directional prefix based on strand
                if hasattr(transcript, 'strand'):
                    strand = transcript.strand
                    # Handle different strand representations
                    if hasattr(strand, 'value'):  # Strand enum
                        is_negative = strand.value == -1
                    elif isinstance(strand, int):  # Integer strand
                        is_negative = strand == -1
                    elif isinstance(strand, str):  # String strand
                        is_negative = strand == "-"
                    else:
                        is_negative = None
                    
                    if is_negative is True:
                        return f"<{transcript_id}"  # Negative strand
                    elif is_negative is False:
                        return f">{transcript_id}"  # Positive strand
                    else:
                        return transcript_id  # Unknown strand, no prefix
                else:
                    return transcript_id  # No strand info, no prefix
            return None
        elif hasattr(feature, '_alignment'):
            # Alignment feature - show chain_id + direction + query_chrom
            alignment = feature._alignment
            if hasattr(alignment, 'chain_id') and alignment.chain_id:
                chain_id = str(alignment.chain_id)
                
                # Get query chromosome name
                q_chrom = getattr(alignment, 'q_chrom', 'unknown')
                
                # Get query strand and choose direction arrow
                q_strand = getattr(alignment, 'q_strand', 1)
                if q_strand == -1:
                    direction = "<<<"  # Negative strand
                else:
                    direction = ">>>"  # Positive strand (default)
                
                return f"{chain_id}{direction}{q_chrom}"
            return None
        elif hasattr(feature, '_interval'):
            # Interval feature - only show real names
            interval = feature._interval
            if hasattr(interval, 'name') and interval.name:
                return interval.name
            return None
        return None
    
    def _compute_height(self) -> float:
        """Compute total height needed for visualization using absolute sizing."""
        if self.height is not None:
            return self.height
        
        # Calculate height for each level separately
        content_height = 0
        non_empty_levels = []
        
        for level in self.layout_manager.levels.values():
            if level.bands:
                non_empty_levels.append(level)
                # Height for this level: label + num_bands * band_height + gaps between bands
                level_height = (len(level.bands) * self.band_height + 
                               (len(level.bands) - 1) * self.band_spacing)
                # Add label height if labels are enabled
                if self.show_labels:
                    level_height += self.label_height
                content_height += level_height
        
        # Add gaps between levels
        if len(non_empty_levels) > 1:
            content_height += (len(non_empty_levels) - 1) * self.level_spacing
        
        # Total: minimal ruler space + conditional content/spacing
        # Use fixed minimal ruler space (enough for ticks and labels)
        minimal_ruler_space = 0.15  # Small fixed space for ruler, ticks, and labels
        
        if content_height > 0:
            # Has content: ruler + gap + content + top padding
            total_height = (minimal_ruler_space + 
                           self.ruler_to_content_spacing + 
                           content_height + 
                           0.1)  # Small top padding
        else:
            # No content: ruler + small space for grid lines
            total_height = minimal_ruler_space + 0.1  # Ruler + space for grid lines
        
        return total_height
    
    def show(self, figsize: tuple = (12, 6)):
        """Trigger layout and rendering."""
        # Compute layout
        self.layout_manager.compute_layout()
        
        # Create figure with computed height
        total_height = self._compute_height()
        # Use proportional scaling so bands always have same visual height
        # Target: each band (0.35 units) should be ~0.4 inches visually
        inches_per_coordinate_unit = 1.2  # This gives reasonable visual band heights
        
        if total_height <= 0.3:  # Empty or minimal plot
            fig_height = 2  # Small figure for empty plots
        else:
            # Pure linear scaling - no minimum constraint to ensure consistent visual heights
            fig_height = min(15, total_height * inches_per_coordinate_unit)  # Max 15" to avoid huge plots
        fig, ax = plt.subplots(figsize=(figsize[0], fig_height))
        
        # Set up coordinate system with left padding for feature labels
        right_padding = (self.interval.end - self.interval.start) * 0.01
        left_boundary = self.interval.start - self.left_padding_width
        ax.set_xlim(left_boundary, self.interval.end + right_padding)
        ax.set_ylim(0, total_height)
        
        # Render ruler at bottom with minimal space for labels
        ruler = GenomicRuler(self.interval, height=self.ruler_height)
        # Use fixed positioning to avoid circular dependencies
        ruler_line_y = 0.05  # Fixed small space for labels below
        ruler.draw(ax, y=ruler_line_y)
        
        # Start rendering content above ruler area  
        ruler_area_height = 0.15  # Match the minimal_ruler_space calculation
        
        # Check if there's any content to render
        has_content = any(len(level.bands) > 0 for level in self.layout_manager.levels.values())
        current_y = ruler_area_height + (self.ruler_to_content_spacing if has_content else 0)
        
        # Render tracks by level with absolute positioning
        for track_type in [TrackType.INTERVALS, TrackType.ALIGNMENTS, TrackType.TRANSCRIPTS]:
            level = self.layout_manager.levels[track_type]
            if not level.bands:
                continue
            
            # Render each band in this level with fixed band height
            for i, band in enumerate(level.bands):
                band_center_y = current_y + self.band_height / 2
                self._render_band(ax, band, band_center_y, track_type)
                current_y += self.band_height
                
                # Add small gap between bands (except after last band)
                if i < len(level.bands) - 1:
                    current_y += self.band_spacing
            
            # Render track label above the tracks if enabled
            if self.show_labels:
                track_names = self._get_level_track_names(track_type)
                if track_names:
                    # Position label above the track area
                    self._render_track_label(ax, track_names, current_y)
                    current_y += self.label_height
            
            # Add larger gap between levels
            current_y += self.level_spacing
        
        # Grid lines
        self._draw_grid_lines(ax)
        
        # Clean up axes - hide all matplotlib default elements
        ax.set_title(f"{self.interval.chrom}", fontsize=12, pad=10, loc="left")
        ax.set_xticks([])  # Remove x-axis ticks
        ax.set_yticks([])  # Remove y-axis ticks
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)  # Remove bottom spine too
        
        plt.tight_layout()
        plt.show()
    
    def _render_track_label(self, ax, label_text: str, y: float):
        """Render track label centered with padding above."""
        xlim = ax.get_xlim()
        # Position label at the center of the plot area
        label_x = (xlim[0] + xlim[1]) / 2  # Center horizontally
        # Add small padding above the label text
        vertical_padding = self.label_height * 0.2  # 20% of label height as padding
        label_y = y + vertical_padding + (self.label_height - vertical_padding) / 2
        
        ax.text(label_x, label_y, label_text, 
               ha="center", va="center", fontsize=10, fontweight="bold",
               color="black", transform=ax.transData)
    
    def _render_feature_label(self, ax, feature: GenomicFeature, y: float):
        """Render individual feature label - next to feature or in left area for clipped features."""
        if not self.show_feature_labels:
            return
        
        feature_id = self._get_feature_id(feature)
        if not feature_id:
            return  # Skip if no real ID
        
        # Use original feature coordinates for space calculation (before clipping)
        original_start = self._get_original_feature_start(feature)
        available_space = original_start - self.interval.start
        
        if available_space >= 2000:
            # Feature starts with enough space in window - label next to feature
            gap_width = (self.interval.end - self.interval.start) * 0.003
            visible_start = max(original_start, self.interval.start)
            label_x = visible_start - gap_width
            
            ax.text(label_x, y, feature_id, 
                   ha="right", va="center", fontsize=8, fontfamily="monospace",
                   color="black", transform=ax.transData)
                   
        else:
            # Clipped feature - put label in safe left area, one per band
            xlim = ax.get_xlim()
            # Position safely in left padding area - further from the interval boundary
            label_x = self.interval.start - self.left_padding_width * 0.7  # 70% into padding area
            
            ax.text(label_x, y, feature_id, 
                   ha="right", va="center", fontsize=8, fontfamily="monospace",
                   color="black", transform=ax.transData)  # Black for visibility, right-aligned
    
    def _get_original_feature_start(self, feature: GenomicFeature) -> int:
        """Get the original (unclipped) start coordinate of a feature."""
        if hasattr(feature, '_alignment'):
            # For alignments, get the original start from the first block
            alignment = feature._alignment
            if hasattr(alignment, 'blocks') and len(alignment.blocks) > 0:
                return int(alignment.blocks[0][0])  # First block t_start
        elif hasattr(feature, '_transcript'):
            # For transcripts, get start from first block
            transcript = feature._transcript
            if hasattr(transcript, 'blocks') and len(transcript.blocks) > 0:
                return int(transcript.blocks[0][0])
        
        # Fallback to current feature.start
        return feature.start
    
    def _render_band(self, ax, band: Band, y: float, track_type: TrackType):
        """Render features in a band."""
        for feature in band.features:
            if track_type == TrackType.INTERVALS:
                self._render_interval(ax, feature, y)
            elif track_type == TrackType.ALIGNMENTS:
                self._render_alignment(ax, feature, y)
            elif track_type == TrackType.TRANSCRIPTS:
                self._render_transcript(ax, feature, y)
    
    def _render_interval(self, ax, feature: GenomicFeature, y: float):
        """Render a genomic interval with fixed absolute height."""
        # Clip feature to not extend into padding area
        clipped_start = max(feature.start, self.interval.start)
        clipped_end = feature.end
        
        if clipped_end <= clipped_start:
            return  # Nothing to render
        
        width = clipped_end - clipped_start
        # Use 80% of band height, centered at y
        rect_height = self.band_height * 0.8
        rect = plt.Rectangle((clipped_start, y - rect_height/2), 
                           width, rect_height, 
                           facecolor='lightblue', edgecolor='navy', linewidth=1)
        ax.add_patch(rect)
        
        # Render feature label on the left if there's space
        self._render_feature_label(ax, feature, y)
    
    def _render_alignment(self, ax, feature: GenomicFeature, y: float):
        """Render a genome alignment showing blocks and sophisticated gap representation."""
        # Get the original alignment from the feature wrapper
        alignment = feature._alignment
        rect_height = self.band_height * 0.8
        
        # Get current window bounds for clipping - respect padding boundary
        xlim = ax.get_xlim()
        window_start = max(xlim[0], self.interval.start)  # Don't extend into padding
        window_end = xlim[1]
        
        # Draw each aligned block individually
        visible_blocks = []
        for i, block in enumerate(alignment.blocks):
            t_start, t_end, q_start, q_end = block[0], block[1], block[2], block[3]
            
            # Skip blocks completely outside the window
            if t_end <= window_start or t_start >= window_end:
                continue
                
            # Clip block to window bounds
            clipped_start = max(int(t_start), window_start)
            clipped_end = min(int(t_end), window_end)
            clipped_width = clipped_end - clipped_start
            
            if clipped_width > 0:
                # Draw the aligned block
                rect = plt.Rectangle((clipped_start, y - rect_height/2), 
                                   clipped_width, rect_height, 
                                   facecolor='lightcoral', edgecolor='darkred', linewidth=1)
                ax.add_patch(rect)
                visible_blocks.append((i, clipped_start, clipped_end, t_start, t_end, q_start, q_end))
        
        # Draw sophisticated gap representation between consecutive blocks
        for i in range(len(visible_blocks) - 1):
            curr_idx, curr_vis_start, curr_vis_end, curr_t_start, curr_t_end, curr_q_start, curr_q_end = visible_blocks[i]
            next_idx, next_vis_start, next_vis_end, next_t_start, next_t_end, next_q_start, next_q_end = visible_blocks[i + 1]
            
            # Only draw gap if blocks are consecutive in the original alignment
            if next_idx == curr_idx + 1:
                gap_start = curr_vis_end
                gap_end = next_vis_start
                
                if gap_end > gap_start:
                    # Analyze query coordinates to determine gap type
                    if alignment.q_strand == -1:
                        # For negative strand, coordinates are reversed
                        q_gap_exists = curr_q_start > next_q_end  # Gap in query if there's space
                    else:
                        # For positive strand
                        q_gap_exists = next_q_start > curr_q_end  # Gap in query if there's space
                    
                    if q_gap_exists:
                        # Gap in both T and Q: doubled line
                        offset = rect_height * 0.15
                        ax.plot([gap_start, gap_end], [y + offset, y + offset], 
                               color='darkred', linewidth=2, alpha=0.7, solid_capstyle='butt')
                        ax.plot([gap_start, gap_end], [y - offset, y - offset], 
                               color='darkred', linewidth=2, alpha=0.7, solid_capstyle='butt')
                    else:
                        # No gap in Q (deletion in Q): single thicker line
                        ax.plot([gap_start, gap_end], [y, y], 
                               color='darkred', linewidth=3, alpha=0.8, solid_capstyle='butt')
        
        # Render feature label on the left if there's space
        self._render_feature_label(ax, feature, y)
    
    def _render_transcript(self, ax, feature: GenomicFeature, y: float):
        """Render a transcript with CDS at full height and UTRs at 50% height."""
        # Get the original transcript from the feature wrapper
        transcript = feature._transcript
        
        # Draw intron line spanning the transcript, clipped to window
        transcript_start = int(transcript.blocks[0, 0])
        transcript_end = int(transcript.blocks[-1, 1])
        
        # Clip to window bounds - respect padding boundary
        xlim = ax.get_xlim()
        window_start = max(xlim[0], self.interval.start)  # Don't extend into padding
        window_end = xlim[1]
        clipped_start = max(transcript_start, window_start)
        clipped_end = min(transcript_end, window_end)
        
        if clipped_end > clipped_start:
            ax.plot([clipped_start, clipped_end], [y, y], 
                   color='navy', linewidth=2, solid_capstyle='butt')
            

        
        # Define heights for different regions
        cds_height = self.band_height * 0.8
        utr_height = cds_height * 0.5  # 50% of CDS height
        
        if transcript.is_coding:
            # Get CDS and UTR blocks separately
            cds_blocks = transcript.cds_blocks
            utr5_blocks = transcript.utr5_blocks  
            utr3_blocks = transcript.utr3_blocks
            
            # Draw CDS blocks at full height
            for cds_start, cds_end in cds_blocks:
                # Clip block to not extend into padding
                clipped_cds_start = max(cds_start, self.interval.start)
                clipped_cds_end = cds_end
                if clipped_cds_end > clipped_cds_start:
                    width = clipped_cds_end - clipped_cds_start
                    rect = plt.Rectangle((clipped_cds_start, y - cds_height/2), 
                                       width, cds_height, 
                                       facecolor='navy', edgecolor='darkblue', linewidth=1)
                    ax.add_patch(rect)
            
            # Draw 5' UTR blocks at 50% height (centered)
            for utr_start, utr_end in utr5_blocks:
                # Clip block to not extend into padding
                clipped_utr_start = max(utr_start, self.interval.start)
                clipped_utr_end = utr_end
                if clipped_utr_end > clipped_utr_start:
                    width = clipped_utr_end - clipped_utr_start
                    rect = plt.Rectangle((clipped_utr_start, y - utr_height/2), 
                                       width, utr_height, 
                                       facecolor='lightblue', edgecolor='navy', linewidth=1)
                    ax.add_patch(rect)
            
            # Draw 3' UTR blocks at 50% height (centered)
            for utr_start, utr_end in utr3_blocks:
                # Clip block to not extend into padding
                clipped_utr_start = max(utr_start, self.interval.start)
                clipped_utr_end = utr_end
                if clipped_utr_end > clipped_utr_start:
                    width = clipped_utr_end - clipped_utr_start
                    rect = plt.Rectangle((clipped_utr_start, y - utr_height/2), 
                                       width, utr_height, 
                                       facecolor='lightblue', edgecolor='navy', linewidth=1)
                    ax.add_patch(rect)
        else:
            # Non-coding transcript: draw all exons as UTR-style (50% height)
            for exon_start, exon_end in transcript.blocks:
                # Clip block to not extend into padding
                clipped_exon_start = max(exon_start, self.interval.start)
                clipped_exon_end = exon_end
                if clipped_exon_end > clipped_exon_start:
                    width = clipped_exon_end - clipped_exon_start
                    rect = plt.Rectangle((clipped_exon_start, y - utr_height/2), 
                                       width, utr_height, 
                                       facecolor='lightblue', edgecolor='navy', linewidth=1)
                    ax.add_patch(rect)
        
        # Render feature label on the left if there's space
        self._render_feature_label(ax, feature, y)
    
    def _draw_grid_lines(self, ax):
        """Draw vertical grid lines above the ruler area only."""
        tick_step = (self.interval.end - self.interval.start) // 10
        ymin, ymax = ax.get_ylim()
        
        # Use fixed ruler area height (matching the show() method)
        ruler_area_height = 0.15
        
        for i in range(11):
            x = self.interval.start + i * tick_step
            # Draw grid lines above the ruler area (now height includes space for them)
            ax.vlines(x, ruler_area_height, ymax, color="lightgrey", 
                     linestyle="--", linewidth=0.5, alpha=0.7)


# Wrapper functions to adapt existing pyrion classes to GenomicFeature interface
class IntervalFeature(GenomicFeature):
    """Wrapper for GenomicInterval."""
    
    def __init__(self, interval: GenomicInterval):
        self._interval = interval
    
    @property
    def start(self) -> int:
        return self._interval.start
    
    @property  
    def end(self) -> int:
        return self._interval.end


class AlignmentFeature(GenomicFeature):
    """Wrapper for GenomeAlignment."""
    
    def __init__(self, alignment: GenomeAlignment):
        self._alignment = alignment
    
    @property
    def start(self) -> int:
        return int(self._alignment.t_span[0])
    
    @property
    def end(self) -> int:
        return int(self._alignment.t_span[1])


class TranscriptFeature(GenomicFeature):
    """Wrapper for Transcript."""
    
    def __init__(self, transcript: Transcript):
        self._transcript = transcript
    
    @property
    def start(self) -> int:
        return int(self._transcript.blocks[0, 0])
    
    @property
    def end(self) -> int:
        return int(self._transcript.blocks[-1, 1]) 


# Convenience functions for creating tracks from pyrion data
def create_interval_track(name: str, intervals: List[GenomicInterval]) -> Track:
    """Create an interval track from a list of GenomicInterval objects."""
    features = [IntervalFeature(interval) for interval in intervals]
    return Track(name, features, TrackType.INTERVALS)


def create_alignment_track(name: str, alignments: List[GenomeAlignment]) -> Track:
    """Create an alignment track from a list of GenomeAlignment objects.""" 
    features = [AlignmentFeature(alignment) for alignment in alignments]
    return Track(name, features, TrackType.ALIGNMENTS)


def create_transcript_track(name: str, transcripts: List[Transcript]) -> Track:
    """Create a transcript track from a list of Transcript objects."""
    features = [TranscriptFeature(transcript) for transcript in transcripts]
    return Track(name, features, TrackType.TRANSCRIPTS)


def create_window_for_region(chrom: str, start: int, end: int, **kwargs) -> VisualizationWindow:
    """Create a VisualizationWindow for a specific genomic region."""
    interval = GenomicInterval(chrom, start, end)
    return VisualizationWindow(interval, **kwargs)


# Quick visualization functions
def visualize_intervals(intervals: List[GenomicInterval], window_interval: GenomicInterval = None, 
                       track_name: str = "Intervals", band_height: float = 0.35, **kwargs):
    """Quick function to visualize a list of intervals."""
    if window_interval is None:
        # Auto-determine window from intervals
        if not intervals:
            raise ValueError("No intervals provided and no window_interval specified")
        min_start = min(interval.start for interval in intervals)
        max_end = max(interval.end for interval in intervals)
        chrom = intervals[0].chrom
        padding = (max_end - min_start) * 0.1
        window_interval = GenomicInterval(chrom, 
                                        max(0, int(min_start - padding)),
                                        int(max_end + padding))
    
    window = VisualizationWindow(window_interval, band_height=band_height, **kwargs)
    track = create_interval_track(track_name, intervals)
    window.add_track(track)
    window.show()


def visualize_transcripts(transcripts: List[Transcript], window_interval: GenomicInterval = None,
                         track_name: str = "Transcripts", band_height: float = 0.35, **kwargs):
    """Quick function to visualize a list of transcripts."""
    if window_interval is None:
        # Auto-determine window from transcripts
        if not transcripts:
            raise ValueError("No transcripts provided and no window_interval specified")
        min_start = min(int(transcript.blocks[0, 0]) for transcript in transcripts)
        max_end = max(int(transcript.blocks[-1, 1]) for transcript in transcripts)
        chrom = transcripts[0].chrom
        padding = (max_end - min_start) * 0.1
        window_interval = GenomicInterval(chrom,
                                        max(0, int(min_start - padding)),
                                        int(max_end + padding))
    
    window = VisualizationWindow(window_interval, band_height=band_height, **kwargs)
    track = create_transcript_track(track_name, transcripts)
    window.add_track(track)
    window.show()


def visualize_alignments(alignments: List[GenomeAlignment], window_interval: GenomicInterval = None,
                        track_name: str = "Alignments", band_height: float = 0.35, **kwargs):
    """Quick function to visualize a list of alignments.""" 
    if window_interval is None:
        # Auto-determine window from alignments
        if not alignments:
            raise ValueError("No alignments provided and no window_interval specified")
        min_start = min(int(alignment.t_span[0]) for alignment in alignments)
        max_end = max(int(alignment.t_span[1]) for alignment in alignments)
        chrom = alignments[0].t_chrom
        padding = (max_end - min_start) * 0.1
        window_interval = GenomicInterval(chrom,
                                        max(0, int(min_start - padding)),
                                        int(max_end + padding))
    
    window = VisualizationWindow(window_interval, band_height=band_height, **kwargs)
    track = create_alignment_track(track_name, alignments)
    window.add_track(track)
    window.show() 