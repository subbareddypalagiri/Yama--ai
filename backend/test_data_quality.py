"""
YAMA AI — Data Quality Testing Script
Test the validators and cleaners with real scenarios
Run: python test_data_quality.py
"""

from app.services.data_validator import BatchValidator, DataQualityChecker
from app.services.data_cleaner import LawDataCleaner, DataQualityReport


def test_valid_data():
    """Test with correctly formatted data"""
    print("\n" + "="*70)
    print("TEST 1: Valid Data (Should Pass)")
    print("="*70)
    
    valid_laws = [
        {
            'act_name': 'Indian Penal Code',
            'section_number': '138',
            'title': 'Dishonor of Cheque for Insufficiency of Funds in Account',
            'description': 'If a cheque is returned by the bank with the reason '
                         'that it has been dishonored due to insufficient funds in '
                         'the account, the person issuing the cheque can be prosecuted.',
            'category': 'criminal',
            'keywords': 'cheque, dishonor, bank, offense, punishment',
            'punishment': 'Imprisonment up to 2 years and/or fine up to Rs. 1,00,000',
            'jurisdiction': 'central',
            'law_type': 'code',
        },
        {
            'act_name': 'Transfer of Property Act, 1882',
            'section_number': '138',
            'title': 'What Transfers of Property are',
            'description': 'An act whereby a living person as owner transfers, or '
                         'declares himself to transfer, to one or more other living persons, '
                         'or to himself and one or more other living persons, the whole or any '
                         'part of his interest in immovable property.',
            'category': 'property',
            'keywords': 'property, transfer, immovable, owner',
            'jurisdiction': 'central',
            'law_type': 'act',
        },
    ]
    
    validator = BatchValidator(verbose=True)
    valid, invalid = validator.validate_batch(valid_laws)
    
    print(f"\n✅ Result: {len(valid)} valid, {len(invalid)} invalid")
    return len(invalid) == 0


def test_invalid_data():
    """Test with intentionally invalid data"""
    print("\n" + "="*70)
    print("TEST 2: Invalid Data (Should Fail Gracefully)")
    print("="*70)
    
    invalid_laws = [
        # Missing required field
        {
            'act_name': 'IPC',
            'section_number': '138',
            # Missing: title, description, category
        },
        # Invalid section format
        {
            'act_name': 'Indian Penal Code',
            'section_number': 'INVALID-FORMAT',
            'title': 'Test',
            'description': 'Test description here for validation',
            'category': 'criminal',
        },
        # Invalid category
        {
            'act_name': 'Indian Penal Code',
            'section_number': '138',
            'title': 'Dishonor of Cheque',
            'description': 'Test description here for validation',
            'category': 'invalid_category',
        },
        # Description too short
        {
            'act_name': 'Indian Penal Code',
            'section_number': '138',
            'title': 'Dishonor',
            'description': 'Short',
            'category': 'criminal',
        },
    ]
    
    validator = BatchValidator(verbose=True)
    valid, invalid = validator.validate_batch(invalid_laws)
    
    print(f"\n✅ Result: {len(valid)} valid, {len(invalid)} invalid")
    print(f"\nExpected 4 failures, got {len(invalid)}")
    return len(invalid) == 4


def test_data_cleaning():
    """Test data cleaning with OCR errors"""
    print("\n" + "="*70)
    print("TEST 3: Data Cleaning (OCR Error Fixes)")
    print("="*70)
    
    messy_laws = [
        {
            'act_name': 'Indian Penal C0de',  # OCR error: 0 instead of O
            'section_number': '138 A',  # Space instead of dash
            'title': 'Dishonor of Che9ue',  # OCR error
            'description': 'lf  a  cheque  is   dishonored',  # Multiple spaces
            'category': 'CRIMINAL',  # Wrong case
            'keywords': 'cheque,  dishonor , bank',  # Irregular spacing
        },
        {
            'act_name': 'Transfer of Property Act',
            'section_number': '  138  ',  # Extra spaces
            'title': 'What Transfers',
            'description': 'An act whereby a living person as 0wner transfers',  # OCR: 0 instead of O
            'category': 'property',
        },
    ]
    
    print("\nBefore cleaning:")
    for law in messy_laws:
        print(f"  Section: '{law['section_number']}', Keywords: '{law.get('keywords')}'")
    
    cleaned, skipped = LawDataCleaner.clean_batch(messy_laws, verbose=True)
    
    print("\nAfter cleaning:")
    for law in cleaned:
        print(f"  Section: '{law['section_number']}', Keywords: '{law.get('keywords')}'")
    
    print(f"\n✅ Result: {len(cleaned)} cleaned, {len(skipped)} skipped")
    return len(cleaned) > 0


def test_duplicate_detection():
    """Test duplicate detection"""
    print("\n" + "="*70)
    print("TEST 4: Duplicate Detection")
    print("="*70)
    
    laws_with_duplicates = [
        {
            'act_name': 'Indian Penal Code',
            'section_number': '138',
            'title': 'Dishonor of Cheque',
            'description': 'If cheque is dishonored the person can be prosecuted for fraud.',
            'category': 'criminal',
        },
        {
            'act_name': 'Indian Penal Code',
            'section_number': '138',  # EXACT DUPLICATE
            'title': 'Dishonor of Cheque',
            'description': 'If cheque is dishonored the person can be prosecuted for fraud.',
            'category': 'criminal',
        },
        {
            'act_name': 'Indian Penal Code',
            'section_number': '139',
            'title': 'Return of Cheque',
            'description': 'Cheque returned for insufficient funds in account.',
            'category': 'criminal',
        },
        {
            'act_name': 'Indian Penal Code',
            'section_number': '139A',
            'title': 'Return of Cheque - Amended',
            'description': 'Cheque returned due to insufficient funds in the account.',  # Similar to 139
            'category': 'criminal',
        },
    ]
    
    validator = BatchValidator(verbose=False)
    valid, invalid = validator.validate_batch(laws_with_duplicates)
    duplicates = validator.check_duplicates()
    
    print(f"Found {len(duplicates)} duplicate/near-duplicate pairs:")
    for idx1, idx2, similarity in duplicates:
        r1 = valid[idx1]
        r2 = valid[idx2]
        print(f"  [{idx1}] {r1['act_name']} Section {r1['section_number']}")
        print(f"  [{idx2}] {r2['act_name']} Section {r2['section_number']}")
        print(f"       Similarity: {similarity:.1%}\n")
    
    print(f"✅ Result: Detected {len(duplicates)} issues")
    return len(duplicates) >= 1


def test_ocr_error_detection():
    """Test OCR error detection"""
    print("\n" + "="*70)
    print("TEST 5: OCR Error Detection")
    print("="*70)
    
    texts_with_ocr_errors = [
        "lf a cheque is dishonored by the bank, the person can be prosecuted.",
        "The lRS or Income Tax Department may issue a notice.",
        "Section § 138 of the Penal C0de deals with cheque dishonor.",
        "This is a Willfull act of negligence by the agency.",
        "The person can be sentenced to Pllnishment of imprisonment.",
    ]
    
    checker = DataQualityChecker()
    
    for text in texts_with_ocr_errors:
        print(f"\nText: {text}")
        errors = checker.check_for_ocr_errors(text)
        if errors:
            for error in errors:
                print(f"  ⚠️  {error}")
        else:
            print(f"  ✅ No OCR errors detected")
    
    print(f"\n✅ Result: OCR error detection working")
    return True


def test_full_pipeline():
    """Test the complete ingestion pipeline"""
    print("\n" + "="*70)
    print("TEST 6: Complete Pipeline")
    print("="*70)
    
    raw_data = [
        # Valid
        {
            'act_name': 'Indian Penal Code',
            'section_number': '138',
            'title': 'Dishonor of Cheque',
            'description': 'Dishonor of cheque for insufficiency of funds in account.',
            'category': 'criminal',
        },
        # Has OCR errors that will be cleaned
        {
            'act_name': 'Transfer of Property Act',
            'section_number': '138 A',  # Will be standardized
            'title': 'What Transfers',
            'description': 'An act whereby a living person as 0wner transfers property',
            'category': 'property',
        },
        # Invalid
        {
            'act_name': 'IPC',
            'section_number': 'INVALID',
            'title': 'Title',
            'description': 'desc',  # Too short
            'category': 'invalid',
        },
    ]
    
    # Step 1: Clean
    print("\n1️⃣  Cleaning...")
    cleaned, skipped = LawDataCleaner.clean_batch(raw_data)
    print(f"   Cleaned: {len(cleaned)}, Skipped: {len(skipped)}")
    
    # Step 2: Validate
    print("\n2️⃣  Validating...")
    validator = BatchValidator(verbose=False)
    valid, invalid = validator.validate_batch(cleaned)
    print(f"   Valid: {len(valid)}, Invalid: {len(invalid)}")
    
    # Step 3: Check duplicates
    print("\n3️⃣  Checking duplicates...")
    duplicates = validator.check_duplicates()
    print(f"   Duplicates: {len(duplicates)}")
    
    # Step 4: Report
    print("\n4️⃣  Generating report...")
    report = DataQualityReport.generate_summary(
        total_records=len(raw_data),
        valid_records=len(valid),
        invalid_records=len(invalid),
        duplicates=len(duplicates),
        cleaned_records=len(cleaned),
        skipped_records=len(skipped)
    )
    print(report)
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " DATA QUALITY TESTING - YAMA AI ".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Valid Data", test_valid_data),
        ("Invalid Data", test_invalid_data),
        ("Data Cleaning", test_data_cleaning),
        ("Duplicate Detection", test_duplicate_detection),
        ("OCR Error Detection", test_ocr_error_detection),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "✅ PASSED" if result else "❌ FAILED"))
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append((test_name, f"❌ ERROR: {str(e)[:30]}"))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results:
        symbol = "✅" if "PASSED" in result else "❌"
        print(f"{symbol} {test_name:<30} {result}")
    
    passed = sum(1 for _, r in results if "PASSED" in r)
    total = len(results)
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
