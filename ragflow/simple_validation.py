#!/usr/bin/env python3
"""
Simple validation script for RAGFLOW chunk size changes.
"""

import os
from pathlib import Path

def check_file_changes():
    """Check if chunk size changes have been applied."""
    
    print("🔍 Checking RAGFLOW chunk size changes...")
    print("=" * 50)
    
    # Key files to check
    files_to_check = [
        "rag/nlp/__init__.py",
        "rag/app/naive.py", 
        "rag/flow/chunker/chunker.py",
        "deepdoc/parser/txt_parser.py"
    ]
    
    base_path = Path("/home/ec2-user/ragflow")
    changes_found = 0
    
    for file_path in files_to_check:
        full_path = base_path / file_path
        
        if not full_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n📁 {file_path}:")
            
            # Check for 512 token changes
            if "chunk_token_num=512" in content or "chunk_token_num = 512" in content:
                print("  ✅ Found 512 token changes")
                changes_found += 1
            else:
                print("  ❌ 512 token changes not found")
                
            # Check for 1024 Excel changes
            if "chunk_token_num = 1024" in content:
                print("  ✅ Found Excel 1024 token changes")
                changes_found += 1
            else:
                print("  ❌ Excel 1024 token changes not found")
                
            # Check for overlap changes
            if "overlapped_percent=0.15" in content or "overlapped_percent = 0.15" in content:
                print("  ✅ Found 15% overlap changes")
                changes_found += 1
            else:
                print("  ❌ 15% overlap changes not found")
                
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
    
    print(f"\n📊 Total changes found: {changes_found}")
    
    if changes_found >= 8:  # Expected minimum changes
        print("✅ Chunk size changes appear to be applied correctly")
        return True
    else:
        print("❌ Some changes may be missing")
        return False

def main():
    """Main function."""
    print("🚀 RAGFLOW Chunk Size Validation")
    print("=" * 50)
    
    success = check_file_changes()
    
    if success:
        print("\n🎉 VALIDATION PASSED!")
        print("✅ Changes have been applied successfully")
        print("\n🎯 NEXT STEPS:")
        print("1. Rebuild Docker image")
        print("2. Test with different file types")
        print("3. Verify Excel processing improvements")
    else:
        print("\n⚠️  VALIDATION FAILED!")
        print("❌ Some changes may need manual review")
    
    return success

if __name__ == "__main__":
    main()

