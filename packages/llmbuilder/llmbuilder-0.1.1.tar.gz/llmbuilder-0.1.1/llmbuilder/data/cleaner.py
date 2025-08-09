"""
Text cleaning utilities for LLMBuilder.

This module provides the TextCleaner class for preprocessing and cleaning
text data before tokenization and training.
"""

import re
import unicodedata
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from ..utils import get_logger

logger = get_logger("data.cleaner")


@dataclass
class CleaningStats:
    """Statistics from text cleaning operations."""
    original_length: int
    cleaned_length: int
    lines_removed: int
    chars_removed: int
    duplicates_removed: int
    
    @property
    def compression_ratio(self) -> float:
        """Calculate compression ratio."""
        if self.original_length == 0:
            return 0.0
        return self.cleaned_length / self.original_length


class TextCleaner:
    """
    Comprehensive text cleaning and preprocessing for LLM training data.
    
    Handles various text cleaning operations including normalization,
    deduplication, filtering, and formatting.
    """
    
    def __init__(self,
                 min_line_length: int = 10,
                 max_line_length: int = 1000,
                 remove_duplicates: bool = True,
                 normalize_unicode: bool = True,
                 remove_urls: bool = True,
                 remove_emails: bool = True,
                 remove_phone_numbers: bool = True,
                 fix_encoding: bool = True,
                 preserve_formatting: bool = False):
        """
        Initialize the text cleaner.
        
        Args:
            min_line_length: Minimum line length to keep
            max_line_length: Maximum line length to keep
            remove_duplicates: Whether to remove duplicate lines
            normalize_unicode: Whether to normalize Unicode characters
            remove_urls: Whether to remove URLs
            remove_emails: Whether to remove email addresses
            remove_phone_numbers: Whether to remove phone numbers
            fix_encoding: Whether to fix common encoding issues
            preserve_formatting: Whether to preserve original formatting
        """
        self.min_line_length = min_line_length
        self.max_line_length = max_line_length
        self.remove_duplicates = remove_duplicates
        self.normalize_unicode = normalize_unicode
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        self.remove_phone_numbers = remove_phone_numbers
        self.fix_encoding = fix_encoding
        self.preserve_formatting = preserve_formatting
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for text cleaning."""
        # URL pattern
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone number pattern (basic)
        self.phone_pattern = re.compile(
            r'(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        )
        
        # Multiple whitespace patterns
        self.multiple_spaces = re.compile(r' {2,}')
        self.multiple_newlines = re.compile(r'\n{3,}')
        self.trailing_whitespace = re.compile(r'[ \t]+$', re.MULTILINE)
        
        # Special characters and artifacts
        self.control_chars = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')
        self.replacement_char = re.compile(r'�+')
        
        # Common document artifacts
        self.page_numbers = re.compile(r'^\s*\d+\s*$', re.MULTILINE)
        self.header_footer = re.compile(r'^[-=_]{3,}.*$', re.MULTILINE)
    
    def clean_text(self, text: str) -> tuple[str, CleaningStats]:
        """
        Clean text with comprehensive preprocessing.
        
        Args:
            text: Raw text to clean
            
        Returns:
            tuple[str, CleaningStats]: Cleaned text and cleaning statistics
        """
        if not text:
            return "", CleaningStats(0, 0, 0, 0, 0)
        
        original_length = len(text)
        original_lines = text.count('\n') + 1
        
        # Step 1: Fix encoding issues
        if self.fix_encoding:
            text = self._fix_encoding(text)
        
        # Step 2: Normalize Unicode
        if self.normalize_unicode:
            text = self._normalize_unicode(text)
        
        # Step 3: Remove unwanted content
        text = self._remove_unwanted_content(text)
        
        # Step 4: Clean whitespace and formatting
        text = self._clean_whitespace(text)
        
        # Step 5: Filter lines by length
        lines = text.split('\n')
        filtered_lines = self._filter_lines(lines)
        
        # Step 6: Remove duplicates
        duplicates_removed = 0
        if self.remove_duplicates:
            filtered_lines, duplicates_removed = self._remove_duplicate_lines(filtered_lines)
        
        # Step 7: Final cleanup
        cleaned_text = '\n'.join(filtered_lines)
        cleaned_text = self._final_cleanup(cleaned_text)
        
        # Calculate statistics
        cleaned_length = len(cleaned_text)
        cleaned_lines = cleaned_text.count('\n') + 1
        lines_removed = original_lines - cleaned_lines
        chars_removed = original_length - cleaned_length
        
        stats = CleaningStats(
            original_length=original_length,
            cleaned_length=cleaned_length,
            lines_removed=lines_removed,
            chars_removed=chars_removed,
            duplicates_removed=duplicates_removed
        )
        
        return cleaned_text, stats
    
    def _fix_encoding(self, text: str) -> str:
        """Fix common encoding issues."""
        # Common encoding fixes
        fixes = {
            'â€™': "'",  # Smart apostrophe
            'â€œ': '"',  # Smart quote left
            'â€': '"',   # Smart quote right
            'â€"': '—',  # Em dash
            'â€"': '–',  # En dash
            'â€¦': '...',  # Ellipsis
            'Ã¡': 'á',   # á with encoding issue
            'Ã©': 'é',   # é with encoding issue
            'Ã­': 'í',   # í with encoding issue
            'Ã³': 'ó',   # ó with encoding issue
            'Ãº': 'ú',   # ú with encoding issue
        }
        
        for wrong, right in fixes.items():
            text = text.replace(wrong, right)
        
        return text
    
    def _normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters."""
        # Normalize to NFC form (canonical composition)
        text = unicodedata.normalize('NFC', text)
        
        # Remove or replace problematic Unicode categories
        cleaned_chars = []
        for char in text:
            category = unicodedata.category(char)
            
            # Keep most characters, but filter out some problematic ones
            if category.startswith('C'):  # Control characters
                if char in '\n\r\t':  # Keep essential whitespace
                    cleaned_chars.append(char)
                # Skip other control characters
            else:
                cleaned_chars.append(char)
        
        return ''.join(cleaned_chars)
    
    def _remove_unwanted_content(self, text: str) -> str:
        """Remove unwanted content like URLs, emails, etc."""
        if self.remove_urls:
            text = self.url_pattern.sub('[URL]', text)
        
        if self.remove_emails:
            text = self.email_pattern.sub('[EMAIL]', text)
        
        if self.remove_phone_numbers:
            text = self.phone_pattern.sub('[PHONE]', text)
        
        # Remove control characters and replacement characters
        text = self.control_chars.sub('', text)
        text = self.replacement_char.sub('', text)
        
        # Remove common document artifacts
        text = self.page_numbers.sub('', text)
        text = self.header_footer.sub('', text)
        
        return text
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean up whitespace and formatting."""
        if not self.preserve_formatting:
            # Normalize whitespace
            text = self.multiple_spaces.sub(' ', text)
            text = self.multiple_newlines.sub('\n\n', text)
            text = self.trailing_whitespace.sub('', text)
            
            # Remove leading/trailing whitespace from lines
            lines = text.split('\n')
            lines = [line.strip() for line in lines]
            text = '\n'.join(lines)
        
        return text
    
    def _filter_lines(self, lines: List[str]) -> List[str]:
        """Filter lines by length and content."""
        filtered = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check length constraints
            if len(line) < self.min_line_length:
                continue
            
            if len(line) > self.max_line_length:
                # Optionally truncate instead of removing
                line = line[:self.max_line_length]
            
            # Skip lines that are mostly punctuation or numbers
            if self._is_mostly_junk(line):
                continue
            
            filtered.append(line)
        
        return filtered
    
    def _is_mostly_junk(self, line: str) -> bool:
        """Check if a line is mostly junk (punctuation, numbers, etc.)."""
        if len(line) < 3:
            return True
        
        # Count different character types
        alpha_count = sum(1 for c in line if c.isalpha())
        total_count = len(line)
        
        # If less than 30% alphabetic characters, consider it junk
        if alpha_count / total_count < 0.3:
            return True
        
        # Check for common junk patterns
        junk_patterns = [
            r'^[0-9\s\-\.]+$',  # Only numbers, spaces, dashes, dots
            r'^[^\w\s]+$',      # Only punctuation
            r'^[A-Z\s]+$',      # Only uppercase and spaces (might be headers)
        ]
        
        for pattern in junk_patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _remove_duplicate_lines(self, lines: List[str]) -> tuple[List[str], int]:
        """Remove duplicate lines while preserving order."""
        seen = set()
        unique_lines = []
        duplicates_count = 0
        
        for line in lines:
            # Use a normalized version for duplicate detection
            normalized = line.lower().strip()
            
            if normalized not in seen:
                seen.add(normalized)
                unique_lines.append(line)
            else:
                duplicates_count += 1
        
        return unique_lines, duplicates_count
    
    def _final_cleanup(self, text: str) -> str:
        """Final cleanup pass."""
        # Remove excessive blank lines at start/end
        text = text.strip()
        
        # Ensure text ends with a newline if it's not empty
        if text and not text.endswith('\n'):
            text += '\n'
        
        return text
    
    def clean_batch(self, texts: List[str]) -> List[tuple[str, CleaningStats]]:
        """
        Clean a batch of texts.
        
        Args:
            texts: List of texts to clean
            
        Returns:
            List[tuple[str, CleaningStats]]: List of cleaned texts and their stats
        """
        results = []
        
        for i, text in enumerate(texts):
            try:
                cleaned_text, stats = self.clean_text(text)
                results.append((cleaned_text, stats))
            except Exception as e:
                logger.error(f"Error cleaning text {i}: {e}")
                # Return original text with empty stats on error
                results.append((text, CleaningStats(len(text), len(text), 0, 0, 0)))
        
        return results
    
    def get_cleaning_summary(self, stats_list: List[CleaningStats]) -> Dict[str, Any]:
        """
        Get summary statistics from multiple cleaning operations.
        
        Args:
            stats_list: List of cleaning statistics
            
        Returns:
            Dict[str, Any]: Summary statistics
        """
        if not stats_list:
            return {}
        
        total_original = sum(s.original_length for s in stats_list)
        total_cleaned = sum(s.cleaned_length for s in stats_list)
        total_lines_removed = sum(s.lines_removed for s in stats_list)
        total_chars_removed = sum(s.chars_removed for s in stats_list)
        total_duplicates = sum(s.duplicates_removed for s in stats_list)
        
        return {
            'total_texts': len(stats_list),
            'total_original_chars': total_original,
            'total_cleaned_chars': total_cleaned,
            'total_lines_removed': total_lines_removed,
            'total_chars_removed': total_chars_removed,
            'total_duplicates_removed': total_duplicates,
            'average_compression_ratio': total_cleaned / total_original if total_original > 0 else 0,
            'total_size_reduction_mb': (total_original - total_cleaned) / (1024 * 1024)
        }