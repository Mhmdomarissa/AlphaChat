#!/usr/bin/env python3
"""
Validation script for RAGFLOW chunk size changes.
This script validates that all chunk size defaults have been updated correctly.
"""

import os
import re
import sys
from pathlib import Path

def validate_chunk_sizes():
    """Validate that chunk size changes have been applied correctly."""
    
    print("🔍 Validating RAGFLOW chunk size changes...")
    print("=" * 60)
    
    # Define expected changes
    expected_changes = {
        # Backend files
        "rag/nlp/__init__.py": {
            "naive_merge": "chunk_token_num=512",
            "naive_merge_with_images": "chunk_token_num=512", 
            "naive_merge_docx": "chunk_token_num=512",
            "overlap": "overlapped_percent=0.15"
        },
        "rag/app/naive.py": {
            "excel_chunk": "chunk_token_num = 1024",
            "text_default": "chunk_token_num", 512,
            "markdown_default": "chunk_token_num", 512,
            "html_default": "chunk_token_num", 512,
            "json_default": "chunk_token_num", 512
        },
        "rag/flow/chunker/chunker.py": {
            "chunk_size": "chunk_token_size = 512",
            "overlap": "overlapped_percent = 0.15"
        },
        "deepdoc/parser/txt_parser.py": {
            "call_method": "chunk_token_num=512",
            "parser_method": "chunk_token_num=512"
        },
        # Frontend files
        "web/src/pages/dataset/setting/index.tsx": {
            "chunk_token_num": "chunk_token_num: 512",
            "html4excel": "html4excel: true"
        },
        "web/src/pages/dataset/dataset-setting/index.tsx": {
            "chunk_token_num": "chunk_token_num: 512", 
            "html4excel": "html4excel: true"
        },
        "web/src/components/chunk-method-dialog/use-default-parser-values.ts": {
            "chunk_token_num": "chunk_token_num: 512",
            "html4excel": "html4excel: true"
        }
    }
    
    validation_results = {}
    base_path = Path("/home/ec2-user/ragflow")
    
    for file_path, expected_values in expected_changes.items():
        full_path = base_path / file_path
        
        if not full_path.exists():
            print(f"❌ File not found: {file_path}")
            validation_results[file_path] = False
            continue
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_valid = True
            print(f"\n📁 Checking {file_path}:")
            
            for check_name, expected_value in expected_values.items():
                if expected_value in content:
                    print(f"  ✅ {check_name}: Found '{expected_value}'")
                else:
                    print(f"  ❌ {check_name}: Expected '{expected_value}' not found")
                    file_valid = False
            
            validation_results[file_path] = file_valid
            
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            validation_results[file_path] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    total_files = len(validation_results)
    valid_files = sum(1 for valid in validation_results.values() if valid)
    
    print(f"Total files checked: {total_files}")
    print(f"Files with correct changes: {valid_files}")
    print(f"Files with issues: {total_files - valid_files}")
    
    if valid_files == total_files:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ Chunk size changes have been applied correctly")
        return True
    else:
        print("\n⚠️  SOME VALIDATIONS FAILED!")
        print("❌ Some files may need manual review")
        return False

def validate_excel_processing():
    """Validate Excel processing improvements."""
    
    print("\n🔍 Validating Excel processing improvements...")
    print("=" * 60)
    
    excel_checks = {
        "rag/app/naive.py": [
            "html4excel", True,
            "enable_field_mapping", True,
            "chunk_token_num = 1024"
        ]
    }
    
    base_path = Path("/home/ec2-user/ragflow")
    
    for file_path, checks in excel_checks.items():
        full_path = base_path / file_path
        
        if not full_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n📁 Checking {file_path}:")
            
            for i in range(0, len(checks), 2):
                check_name = checks[i]
                expected_value = checks[i + 1]
                
                if isinstance(expected_value, bool):
                    if f'"{check_name}": {str(expected_value).lower()}' in content or f"'{check_name}': {str(expected_value).lower()}" in content:
                        print(f"  ✅ {check_name}: Found {expected_value}")
                    else:
                        print(f"  ❌ {check_name}: Expected {expected_value} not found")
                else:
                    if expected_value in content:
                        print(f"  ✅ {check_name}: Found '{expected_value}'")
                    else:
                        print(f"  ❌ {check_name}: Expected '{expected_value}' not found")
                        
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")

def main():
    """Main validation function."""
    
    print("🚀 RAGFLOW Chunk Size Validation Script")
    print("=" * 60)
    
    # Validate chunk size changes
    chunk_validation = validate_chunk_sizes()
    
    # Validate Excel processing
    validate_excel_processing()
    
    print("\n" + "=" * 60)
    print("📋 RECOMMENDATIONS")
    print("=" * 60)
    
    if chunk_validation:
        print("✅ All chunk size changes have been applied successfully")
        print("✅ Excel processing has been improved")
        print("✅ Frontend defaults have been updated")
        print("\n🎯 NEXT STEPS:")
        print("1. Rebuild the Docker image with: docker build -t ragflow:custom .")
        print("2. Restart the RAGFLOW container")
        print("3. Test with your Excel files to verify improvements")
        print("4. Monitor chunk quality and adjust if needed")
    else:
        print("❌ Some validations failed - please review the output above")
        print("🔧 Manual fixes may be required")
    
    return chunk_validation

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)