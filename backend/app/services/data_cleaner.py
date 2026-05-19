"""
YAMA AI — Data Cleaning Service
Cleans and normalizes legal data before storage
"""

import re
from typing import List, Dict, Tuple
import unicodedata


class LegalTextCleaner:
    """Cleans legal text from common issues"""
    
    # Common OCR/encoding errors in Indian legal texts
    OCR_FIXES = {
        'lRS': 'IRS',
        'O€': 'O€',  # Currency
        'lndia': 'India',
        'Constitlltion': 'Constitution',
        'Gowemment': 'Government',
        'lnterpretatlon': 'Interpretation',
        'Pllnishment': 'Punishment',
        'Willfull': 'Wilful',
        'Injllry': 'Injury',
        'Offellce': 'Offence',
        'lssue': 'Issue',
        '§': 'Section',
    }
    
    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalize Unicode to standard form"""
        # Decompose accented characters
        text = unicodedata.normalize('NFKD', text)
        # Remove control characters
        text = ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C')
        return text
    
    @staticmethod
    def fix_ocr_errors(text: str) -> str:
        """Fix common OCR errors"""
        for wrong, correct in LegalTextCleaner.OCR_FIXES.items():
            text = text.replace(wrong, correct)
        
        # Fix common patterns
        # "Section" vs "Sec" vs "S." - standardize to "Section"
        text = re.sub(r'\bSec\.?\s+(\d)', r'Section \1', text, flags=re.IGNORECASE)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,;:])', r'\1', text)  # No space before punctuation
        text = re.sub(r'([.,;:])\s*', r'\1 ', text)  # One space after
        
        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Remove leading/trailing and excessive internal whitespace"""
        # Remove tabs and newlines
        text = text.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def standardize_section_format(section: str) -> str:
        """Standardize section number format"""
        section = section.strip()
        
        # Remove "Section" prefix if present
        section = re.sub(r'^Section\s*', '', section, flags=re.IGNORECASE)
        
        # Standardize formats
        # "338-A" -> "338-A" (already correct)
        # "338 A" -> "338-A"
        section = re.sub(r'(\d+)\s+([A-Z])\b', r'\1-\2', section)
        
        # "138(1)" stays as is
        # "138 (1)" -> "138(1)"
        section = re.sub(r'(\d+)\s+\(', r'\1(', section)
        
        return section
    
    @staticmethod
    def extract_case_citations(text: str) -> List[str]:
        """Extract case citations from text"""
        citations = []
        
        # Pattern 1: AIR YYYY SC YYY
        pattern1 = r'AIR\s+(\d{4})\s+(SC|HC|DLT|CAT|NCLAT|NGT|SAT)\s+(\d+)'
        matches = re.finditer(pattern1, text)
        citations.extend([m.group(0) for m in matches])
        
        # Pattern 2: (YYYY) X SC 123
        pattern2 = r'\((\d{4})\)\s+(\d+)\s+(SC|HC)\s+(\d+)'
        matches = re.finditer(pattern2, text)
        citations.extend([m.group(0) for m in matches])
        
        # Pattern 3: Case name v Case name, (YYYY) XXXX
        pattern3 = r'(\w+)\s+v\s+(\w+),\s+\((\d{4})\)\s+(\d+)'
        matches = re.finditer(pattern3, text)
        citations.extend([m.group(0) for m in matches])
        
        return list(set(citations))  # Remove duplicates
    
    @staticmethod
    def extract_amendments(text: str) -> List[Tuple[str, str]]:
        """Extract amendment information from text"""
        amendments = []
        
        # Pattern: "as amended by Act XXX of YYYY"
        pattern = r'as\s+amended\s+by\s+(Act|Bill|Ordinance)\s+([\w\s]+)\s+of\s+(\d{4})'
        matches = re.finditer(pattern, text, flags=re.IGNORECASE)
        
        for match in matches:
            amendment = (match.group(2).strip(), match.group(3))
            amendments.append(amendment)
        
        return amendments
    
    @staticmethod
    def clean_law_text(text: str) -> str:
        """Apply all cleaning steps to legal text"""
        # Step 1: Normalize Unicode
        text = LegalTextCleaner.normalize_unicode(text)
        
        # Step 2: Remove extra whitespace
        text = LegalTextCleaner.remove_extra_whitespace(text)
        
        # Step 3: Fix OCR errors
        text = LegalTextCleaner.fix_ocr_errors(text)
        
        # Step 4: Final cleanup
        text = text.strip()
        
        return text


class LawDataCleaner:
    """Clean batch law data"""
    
    @staticmethod
    def clean_law_record(law: Dict) -> Dict:
        """Clean and standardize a single law record"""
        cleaner = LegalTextCleaner()
        
        cleaned = {
            'act_name': law.get('act_name', '').strip(),
            'section_number': cleaner.standardize_section_format(
                law.get('section_number', '')
            ),
            'title': cleaner.clean_law_text(law.get('title', '')),
            'description': cleaner.clean_law_text(law.get('description', '')),
            'category': law.get('category', '').lower().strip(),
            'keywords': law.get('keywords', ''),
            'punishment': cleaner.clean_law_text(law.get('punishment', '')) if law.get('punishment') else None,
            'old_law_reference': law.get('old_law_reference', ''),
            'jurisdiction': law.get('jurisdiction', 'central').lower(),
            'law_type': law.get('law_type', 'act').lower(),
            'source_url': law.get('source_url', ''),
        }
        
        # Clean keywords
        if cleaned['keywords']:
            keywords = [k.strip() for k in cleaned['keywords'].split(',')]
            keywords = [k for k in keywords if k]  # Remove empty
            cleaned['keywords'] = ', '.join(keywords).lower()
        
        return cleaned
    
    @staticmethod
    def clean_batch(laws: List[Dict], verbose: bool = False) -> Tuple[List[Dict], List[Dict]]:
        """
        Clean batch of law records
        Returns: (cleaned_records, skipped_records)
        """
        cleaned = []
        skipped = []
        
        for idx, law in enumerate(laws):
            try:
                if not law.get('description') or not law.get('act_name'):
                    skipped.append({
                        'index': idx,
                        'reason': 'Missing required fields',
                        'record': law
                    })
                    if verbose:
                        print(f"⏭️  Skipped record {idx}: Missing required fields")
                    continue
                
                cleaned_law = LawDataCleaner.clean_law_record(law)
                cleaned.append(cleaned_law)
                
                if verbose:
                    print(f"✅ Cleaned record {idx}: {cleaned_law['act_name']} - {cleaned_law['section_number']}")
                    
            except Exception as e:
                skipped.append({
                    'index': idx,
                    'reason': str(e),
                    'record': law
                })
                if verbose:
                    print(f"❌ Error cleaning record {idx}: {str(e)}")
        
        return cleaned, skipped


class DataQualityReport:
    """Generate data quality reports"""
    
    @staticmethod
    def generate_summary(
        total_records: int,
        valid_records: int,
        invalid_records: int,
        duplicates: int,
        cleaned_records: int,
        skipped_records: int
    ) -> str:
        """Generate a summary report"""
        
        report = f"""
╔════════════════════════════════════════╗
║   DATA QUALITY REPORT - YAMA AI         ║
╚════════════════════════════════════════╝

📊 STATISTICS
─────────────────────────────────────────
Total Records:        {total_records:>6}
Valid Records:        {valid_records:>6} ({valid_records/total_records*100:.1f}%)
Invalid Records:      {invalid_records:>6} ({invalid_records/total_records*100:.1f}%)
Duplicate Issues:     {duplicates:>6}
Successfully Cleaned: {cleaned_records:>6}
Skipped Records:      {skipped_records:>6}

✅ RECOMMENDATIONS
─────────────────────────────────────────
1. Review {invalid_records} invalid records for formatting issues
2. Investigate {duplicates} potential duplicates
3. Check {skipped_records} skipped records for missing data
4. Success rate: {valid_records/total_records*100:.1f}% - {'GOOD' if valid_records/total_records > 0.95 else 'NEEDS IMPROVEMENT'}

🔍 NEXT STEPS
─────────────────────────────────────────
1. Fix OCR errors in invalid records
2. Remove or merge duplicates
3. Ensure all records have complete data
4. Re-run validation before ingestion
"""
        
        return report
    
    @staticmethod
    def save_errors_to_csv(invalid_records: List[Dict], filepath: str):
        """Save invalid records to CSV for review"""
        import csv
        
        if not invalid_records:
            print(f"No errors to save")
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['index', 'act_name', 'section_number', 'error', 'details']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for record in invalid_records:
                    row = {
                        'index': record.get('index', ''),
                        'act_name': record.get('record', {}).get('act_name', ''),
                        'section_number': record.get('record', {}).get('section_number', ''),
                        'error': record['errors'][0].get('type', '') if record['errors'] else '',
                        'details': str(record['errors'][0]) if record['errors'] else '',
                    }
                    writer.writerow(row)
            
            print(f"✅ Error report saved to: {filepath}")
        except Exception as e:
            print(f"❌ Failed to save error report: {e}")
