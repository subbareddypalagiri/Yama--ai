"""
YAMA AI — Data Quality Integration Guide
How to use the validators and cleaners in your ingestion pipeline
"""

# ============ STEP-BY-STEP INTEGRATION ============

# STEP 1: Update your ingestion scripts
# Example: backend/add_stage1_acts.py

from app.services.data_validator import LawSectionValidator, BatchValidator
from app.services.data_cleaner import LawDataCleaner, DataQualityReport
from app.db.database import SessionLocal
from app.db.models import LawSection
import json


def ingest_laws_with_quality_checks(raw_data: list, verbose=True):
    """
    Ingest laws with data quality validation
    
    Args:
        raw_data: List of law records from your data source
        verbose: Print progress to console
    
    Returns:
        (ingested_count, failed_count, report)
    """
    
    print("\n" + "="*60)
    print("🔄 Starting data ingestion with quality checks...")
    print("="*60)
    
    # Step 1: Clean the data
    print("\n📝 Step 1: Cleaning raw data...")
    cleaned_laws, skipped = LawDataCleaner.clean_batch(raw_data, verbose=verbose)
    print(f"   ✅ Cleaned: {len(cleaned_laws)}")
    print(f"   ⏭️  Skipped: {len(skipped)}")
    
    if skipped and verbose:
        print("\n   Skipped records:")
        for record in skipped[:5]:  # Show first 5
            print(f"     - Index {record['index']}: {record['reason']}")
    
    # Step 2: Validate the cleaned data
    print("\n✅ Step 2: Validating cleaned data...")
    validator = BatchValidator(verbose=verbose)
    valid_records, invalid_records = validator.validate_batch(cleaned_laws)
    print(f"   ✅ Valid: {len(valid_records)}")
    print(f"   ❌ Invalid: {len(invalid_records)}")
    
    if invalid_records and verbose:
        print("\n   First 3 validation errors:")
        for record in invalid_records[:3]:
            print(f"     - Record {record['index']}:")
            for err in record['errors'][:2]:
                print(f"       {err['loc'][0]}: {err['msg']}")
    
    # Step 3: Check for duplicates
    print("\n🔍 Step 3: Checking for duplicates...")
    duplicates = validator.check_duplicates()
    print(f"   ⚠️  Duplicates found: {len(duplicates)}")
    
    if duplicates and verbose:
        print("\n   Duplicate pairs:")
        for idx1, idx2, similarity in duplicates[:3]:
            r1 = valid_records[idx1]
            r2 = valid_records[idx2]
            print(f"     - {r1['act_name']} {r1['section_number']} ↔ "
                  f"{r2['act_name']} {r2['section_number']} ({similarity:.2%})")
    
    # Step 4: Ingest valid records
    print("\n💾 Step 4: Ingesting into database...")
    db = SessionLocal()
    ingested = 0
    failed = 0
    
    try:
        for record in valid_records:
            try:
                existing = db.query(LawSection).filter(
                    LawSection.act_name == record['act_name'],
                    LawSection.section_number == record['section_number']
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in record.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    db.commit()
                    ingested += 1
                else:
                    # Create new record
                    law = LawSection(**record)
                    db.add(law)
                    db.commit()
                    ingested += 1
                
                if verbose and ingested % 50 == 0:
                    print(f"   ✅ Ingested {ingested} records...")
                    
            except Exception as e:
                db.rollback()
                failed += 1
                if verbose:
                    print(f"   ❌ Failed to ingest: {record.get('act_name')} - {str(e)}")
    
    finally:
        db.close()
    
    # Step 5: Generate report
    print("\n📊 Step 5: Generating report...")
    report = DataQualityReport.generate_summary(
        total_records=len(raw_data),
        valid_records=len(valid_records),
        invalid_records=len(invalid_records),
        duplicates=len(duplicates),
        cleaned_records=len(cleaned_laws),
        skipped_records=len(skipped)
    )
    
    print(report)
    
    # Save error details
    if invalid_records:
        error_file = f"ingestion_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        DataQualityReport.save_errors_to_csv(invalid_records, error_file)
    
    print("="*60)
    print(f"✅ Ingestion complete: {ingested} successful, {failed} failed")
    print("="*60 + "\n")
    
    return ingested, failed, report


# ============ USAGE EXAMPLE ============

def example_usage():
    """
    Example: How to use in your existing ingestion scripts
    """
    
    # Your raw data (from CSV, JSON, API, etc.)
    raw_laws = [
        {
            'act_name': 'Indian Penal Code',
            'section_number': '138',
            'title': 'Dishonor of Cheque',
            'description': 'If cheque is dishonored the person can be prosecuted...',
            'category': 'criminal',
            'keywords': 'cheque, dishonor, bank, offense',
            'punishment': 'Imprisonment up to 2 years and/or fine up to Rs. 1,00,000',
        },
        {
            'act_name': 'Indian Penal Code',
            'section_number': '139',
            'title': 'Return of Cheque for Insufficient Funds',
            'description': 'Cheque is returned for insufficient funds...',
            'category': 'criminal',
            'keywords': 'cheque, funds, bank',
        },
        # ... more records
    ]
    
    # Ingest with quality checks
    ingested, failed, report = ingest_laws_with_quality_checks(raw_laws, verbose=True)
    
    print(f"\nFinal Results:")
    print(f"  Ingested: {ingested}")
    print(f"  Failed: {failed}")


# ============ API ENDPOINT FOR VALIDATION ============

from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/validate-laws")
async def validate_laws(file: UploadFile = File(...)):
    """
    API endpoint to validate law data before ingestion
    Upload CSV/Excel with law data
    """
    
    try:
        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file.file)
        else:
            raise HTTPException(400, "Only CSV and Excel files are supported")
        
        # Convert to list of dicts
        records = df.to_dict(orient='records')
        
        # Validate
        validator = BatchValidator(verbose=False)
        valid, invalid = validator.validate_batch(records)
        duplicates = validator.check_duplicates()
        
        # Return results
        return {
            'total_records': len(records),
            'valid_count': len(valid),
            'invalid_count': len(invalid),
            'duplicate_count': len(duplicates),
            'success_rate': f"{len(valid)/len(records)*100:.1f}%",
            'issues': {
                'invalid_records': invalid[:5],  # First 5 errors
                'duplicate_pairs': duplicates[:5],
            },
            'summary': validator.generate_report()
        }
        
    except Exception as e:
        raise HTTPException(500, f"Validation failed: {str(e)}")


@router.post("/ingest-laws")
async def ingest_laws(file: UploadFile = File(...)):
    """
    API endpoint to ingest validated laws
    """
    
    try:
        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)
        
        records = df.to_dict(orient='records')
        
        # Ingest with quality checks
        ingested, failed, report = ingest_laws_with_quality_checks(
            records, 
            verbose=False
        )
        
        return {
            'status': 'success',
            'ingested': ingested,
            'failed': failed,
            'message': f"Successfully ingested {ingested} laws"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {str(e)}")


# ============ CHECKLIST ============

"""
✅ IMPLEMENTATION CHECKLIST - TIP 1: Data Quality First

Before you start:
- [ ] Copy data_validator.py to backend/app/services/
- [ ] Copy data_cleaner.py to backend/app/services/
- [ ] Install any missing dependencies (if any)

Integration:
- [ ] Update your ingestion scripts (add_stage*.py) to use validators
- [ ] Add the validate_laws API endpoint
- [ ] Add the ingest_laws API endpoint
- [ ] Create test data with intentional errors to test validators

Testing:
- [ ] Test with valid data → should pass
- [ ] Test with invalid section numbers → should fail
- [ ] Test with OCR errors → should be cleaned
- [ ] Test with duplicate records → should be detected
- [ ] Test with missing fields → should be skipped

Monitoring:
- [ ] Set up error logging
- [ ] Generate reports after each ingestion
- [ ] Track data quality metrics over time
- [ ] Review invalid records regularly

Documentation:
- [ ] Document all valid categories and law types
- [ ] Document section number format requirements
- [ ] Create data submission guidelines for contributors
"""
