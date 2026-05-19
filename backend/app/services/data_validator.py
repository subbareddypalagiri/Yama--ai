"""
YAMA AI — Data Validation Service
Validates legal data quality before ingestion
"""

import re
from typing import Optional, List, Tuple, Dict
from pydantic import BaseModel, field_validator, ValidationError
import hashlib


class LawSectionValidator(BaseModel):
    """Validates individual law section records"""
    
    act_name: str
    section_number: str
    title: str
    description: str
    category: str
    keywords: Optional[str] = None
    punishment: Optional[str] = None
    old_law_reference: Optional[str] = None
    jurisdiction: Optional[str] = "central"
    law_type: Optional[str] = "act"
    
    @field_validator('act_name')
    @classmethod
    def validate_act_name(cls, v: str) -> str:
        """Act name should be meaningful and properly formatted"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Act name too short (minimum 3 characters)")
        
        if len(v) > 500:
            raise ValueError("Act name too long (max 500 characters)")
        
        # Check for common Indian law patterns
        # Should contain keywords like: Act, Code, Rules, Regulations, etc.
        valid_patterns = [
            r'Act', r'Code', r'Rules', r'Regulations', 
            r'Ordinance', r'Schedule', r'Amendment'
        ]
        
        if not any(re.search(pattern, v, re.IGNORECASE) for pattern in valid_patterns):
            # Log warning but don't fail - user might have custom naming
            print(f"⚠️  Warning: Act name '{v}' doesn't match standard law naming pattern")
        
        return v.strip()
    
    @field_validator('section_number')
    @classmethod
    def validate_section_number(cls, v: str) -> str:
        """Section numbers must follow Indian law format"""
        if not v or not v.strip():
            raise ValueError("Section number cannot be empty")
        
        v = v.strip()
        
        # Valid formats: "138", "336-A", "7(1)", "230A(1)", etc.
        if not re.match(r'^[\d]+[A-Z]?(\([0-9a-zA-Z]+\))?(-[A-Z]+)?$', v):
            raise ValueError(
                f"Invalid section format: '{v}'. "
                f"Expected formats: '138', '336-A', '7(1)', '230A(1)'"
            )
        
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Title should be descriptive"""
        if not v or len(v.strip()) < 5:
            raise ValueError("Title too short (minimum 5 characters)")
        
        if len(v) > 1000:
            raise ValueError("Title too long (max 1000 characters)")
        
        # Remove excessive whitespace
        v = ' '.join(v.split())
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Description should have meaningful content"""
        if not v or len(v.strip()) < 20:
            raise ValueError("Description too short (minimum 20 characters)")
        
        if len(v) > 10000:
            raise ValueError("Description too long (max 10000 characters)")
        
        # Remove excessive whitespace and clean up
        v = ' '.join(v.split())
        
        # Check for common OCR/corruption patterns
        if bool(re.search(r'[^\x20-\x7E\u0900-\u097F]', v)):
            print(f"⚠️  Warning: Description contains unusual characters")
        
        return v
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Category must be valid legal domain"""
        if not v:
            raise ValueError("Category cannot be empty")
        
        valid_categories = {
            'criminal', 'civil', 'constitutional', 'consumer',
            'cyber', 'motor_vehicle', 'family', 'property',
            'labour', 'tax', 'constitutional', 'administrative',
            'environmental', 'intellectual_property', 'commercial',
            'corporate', 'bankruptcy', 'maritime'
        }
        
        v_lower = v.lower().strip()
        if v_lower not in valid_categories:
            raise ValueError(
                f"Invalid category: '{v}'. "
                f"Must be one of: {', '.join(sorted(valid_categories))}"
            )
        
        return v_lower
    
    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v: Optional[str]) -> Optional[str]:
        """Keywords should be meaningful"""
        if not v:
            return v
        
        if len(v) > 500:
            raise ValueError("Keywords too long (max 500 characters)")
        
        # Split and check each keyword
        keywords = [k.strip() for k in v.split(',')]
        
        for kw in keywords:
            if len(kw) < 2:
                raise ValueError(f"Keyword too short: '{kw}' (minimum 2 characters)")
            if len(kw) > 50:
                raise ValueError(f"Keyword too long: '{kw}' (max 50 characters)")
        
        return v.lower()
    
    @field_validator('jurisdiction')
    @classmethod
    def validate_jurisdiction(cls, v: Optional[str]) -> Optional[str]:
        """Jurisdiction must be valid"""
        if not v:
            return "central"
        
        valid = ['central', 'state', 'union_territory', 'local']
        if v.lower() not in valid:
            raise ValueError(f"Invalid jurisdiction: '{v}'. Must be one of: {valid}")
        
        return v.lower()
    
    @field_validator('law_type')
    @classmethod
    def validate_law_type(cls, v: Optional[str]) -> Optional[str]:
        """Law type classification"""
        if not v:
            return "act"
        
        valid = ['act', 'code', 'rule', 'amendment', 'article', 'notification', 'judgment', 'ordinance']
        if v.lower() not in valid:
            raise ValueError(f"Invalid law type: '{v}'. Must be one of: {valid}")
        
        return v.lower()


class DataQualityChecker:
    """Check for data quality issues"""
    
    DUPLICATE_THRESHOLD = 0.85  # 85% similarity = potential duplicate
    
    @staticmethod
    def calculate_content_hash(text: str) -> str:
        """Calculate SHA-256 hash of content for change detection"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def check_for_ocr_errors(text: str) -> List[str]:
        """Detect common OCR errors in legal text"""
        errors = []
        
        ocr_patterns = {
            r'\bl\b': 'Possible OCR error: "l" should be "I"',
            r'0f\b': 'Possible OCR error: "0f" should be "of"',
            r'lRS': 'Possible OCR error: "lRS" should be "IRS"',
            r'rn(?=[a-z])': 'Possible OCR error: "rn" might be "m"',
            r'\b\d{1}0O': 'Possible OCR error: "O" mixed with "0"',
            r'§': 'Possible OCR error: "§" instead of "Section"',
        }
        
        for pattern, message in ocr_patterns.items():
            if re.search(pattern, text):
                errors.append(message)
        
        return errors
    
    @staticmethod
    def check_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0-1)"""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def validate_section_reference(section: str, act: str) -> bool:
        """Validate that a section number exists in an act"""
        # This would need a lookup table
        # For now, just check format
        return bool(re.match(r'^[\d]+[A-Z]?(-[A-Z])?(\([0-9]+\))?$', section))
    
    @staticmethod
    def check_data_completeness(record: Dict) -> Dict[str, any]:
        """Check if record has all required fields"""
        results = {
            'is_complete': True,
            'missing_fields': [],
            'warnings': []
        }
        
        required = ['act_name', 'section_number', 'title', 'description', 'category']
        for field in required:
            if not record.get(field):
                results['missing_fields'].append(field)
                results['is_complete'] = False
        
        # Check optional but important fields
        if not record.get('keywords'):
            results['warnings'].append("Missing keywords (recommended for search)")
        
        if not record.get('punishment') and 'criminal' in record.get('category', ''):
            results['warnings'].append("Criminal law missing punishment information")
        
        return results


class BatchValidator:
    """Validates batches of law records"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.valid_records: List[Dict] = []
        self.invalid_records: List[Dict] = []
        self.duplicates: List[Tuple[Dict, Dict, float]] = []
    
    def validate_batch(self, records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate batch of records
        Returns: (valid_records, invalid_records)
        """
        self.valid_records = []
        self.invalid_records = []
        
        for idx, record in enumerate(records):
            try:
                # Validate using Pydantic model
                validated = LawSectionValidator(**record)
                self.valid_records.append(validated.model_dump())
                
                if self.verbose:
                    print(f"✅ Record {idx}: Valid")
                    
            except ValidationError as e:
                error_detail = {
                    'index': idx,
                    'record': record,
                    'errors': e.errors()
                }
                self.invalid_records.append(error_detail)
                
                if self.verbose:
                    print(f"❌ Record {idx}: Invalid")
                    for err in e.errors():
                        print(f"   - {err['loc']}: {err['msg']}")
        
        return self.valid_records, self.invalid_records
    
    def check_duplicates(self) -> List[Tuple[int, int, float]]:
        """
        Check for duplicate or near-duplicate records
        Returns: List of (idx1, idx2, similarity_score)
        """
        duplicates = []
        checker = DataQualityChecker()
        
        for i in range(len(self.valid_records)):
            for j in range(i + 1, len(self.valid_records)):
                r1 = self.valid_records[i]
                r2 = self.valid_records[j]
                
                # Check if same act + section
                if (r1.get('act_name') == r2.get('act_name') and 
                    r1.get('section_number') == r2.get('section_number')):
                    duplicates.append((i, j, 1.0))
                    continue
                
                # Check description similarity
                similarity = checker.check_similarity(
                    r1.get('description', ''),
                    r2.get('description', '')
                )
                
                if similarity >= checker.DUPLICATE_THRESHOLD:
                    duplicates.append((i, j, similarity))
                    if self.verbose:
                        print(f"⚠️  Duplicate detected: Record {i} & {j} ({similarity:.2%} similar)")
        
        self.duplicates = duplicates
        return duplicates
    
    def generate_report(self) -> Dict:
        """Generate validation report"""
        return {
            'total_records': len(self.valid_records) + len(self.invalid_records),
            'valid_count': len(self.valid_records),
            'invalid_count': len(self.invalid_records),
            'duplicate_count': len(self.duplicates),
            'success_rate': len(self.valid_records) / (len(self.valid_records) + len(self.invalid_records)) * 100 if (len(self.valid_records) + len(self.invalid_records)) > 0 else 0,
            'invalid_records': self.invalid_records,
            'duplicates': self.duplicates
        }
