"""
Debug script to test core scanner functionality
Run this to diagnose issues: python debug_tests.py
"""

from secretsentry import SecretSentry
import tempfile
import os

def debug_scanner():
    """Debug the scanner with simple test cases"""
    scanner = SecretSentry()
    
    print("🔍 Testing basic scanner functionality...")
    print(f"📋 Loaded {len(scanner.patterns)} patterns")
    
    # Test 1: Simple in-memory test
    print("\n1. Testing AWS key pattern...")
    test_cases = [
        ('AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"', 'aws_access_key'),
        ('password = "secretpass123"', 'password'),
        ('github_token = "ghp_1234567890abcdef1234567890abcdef12345678"', 'github_token'),
        ('email = "test@example.com"', 'email'),
    ]
    
    for test_content, expected_pattern in test_cases:
        print(f"\n   Testing: {test_content}")
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            findings = scanner.scan_file(temp_file)
            print(f"   Found {len(findings)} findings:")
            for finding in findings:
                print(f"     - {finding.pattern_type}: {finding.matched_text}")
            
            # Check if expected pattern was found
            expected_found = any(expected_pattern in f.pattern_type for f in findings)
            print(f"   Expected '{expected_pattern}': {'✅ FOUND' if expected_found else '❌ NOT FOUND'}")
            
        finally:
            os.unlink(temp_file)
    
    # Test 2: Sanitization
    print(f"\n2. Testing sanitization...")
    test_content = 'API_KEY = "sk_live_testkey123456789"'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        findings = scanner.scan_file(temp_file)
        print(f"   Found {len(findings)} findings before sanitization")
        
        if findings:
            stats = scanner.sanitize_files(backup=True, dry_run=True)
            print(f"   Dry run stats: {stats}")
            
            # Check file unchanged
            with open(temp_file, 'r') as f:
                content_after_dry = f.read()
            print(f"   Content unchanged after dry run: {'✅' if content_after_dry == test_content else '❌'}")
            
            # Actual sanitization
            stats = scanner.sanitize_files(backup=True, dry_run=False)
            print(f"   Actual sanitization stats: {stats}")
            
            with open(temp_file, 'r') as f:
                content_after_real = f.read()
            print(f"   Content changed after sanitization: {'✅' if content_after_real != test_content else '❌'}")
            print(f"   New content: {content_after_real}")
            
    finally:
        os.unlink(temp_file)
        backup_file = temp_file + '.backup'
        if os.path.exists(backup_file):
            os.unlink(backup_file)

if __name__ == '__main__':
    debug_scanner()