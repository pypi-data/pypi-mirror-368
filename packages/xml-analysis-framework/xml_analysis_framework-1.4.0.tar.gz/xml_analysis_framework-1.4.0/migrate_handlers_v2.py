#!/usr/bin/env python3
"""
Migrate all handlers to use the new SpecializedAnalysis structure
"""

import os
import re
from pathlib import Path

def migrate_handler(file_path):
    """Migrate a single handler file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Skip if no SpecializedAnalysis
    if 'SpecializedAnalysis(' not in content:
        return False, "No SpecializedAnalysis found"
    
    # Find all SpecializedAnalysis creations
    pattern = r'return SpecializedAnalysis\(\s*document_type="[^"]+",([^)]+)\)'
    
    def replace_specialized_analysis(match):
        # Get the parameters after document_type
        params = match.group(1)
        
        # Build replacement
        replacement = '''# Get document type info  
        doc_type = self.detect_type(file_path, root=root, namespaces={})
        
        return SpecializedAnalysis(
            # From DocumentTypeInfo
            type_name=doc_type.type_name,
            confidence=doc_type.confidence,
            version=doc_type.version,
            schema_uri=doc_type.schema_uri,
            metadata=doc_type.metadata,
            # Analysis fields''' + params + ')'
        
        return replacement
    
    # Replace all occurrences
    original = content
    content = re.sub(pattern, replace_specialized_analysis, content, flags=re.DOTALL)
    
    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True, "Migrated successfully"
    
    return False, "No changes made"

def main():
    """Migrate all handlers"""
    handlers_dir = Path("src/handlers")
    handler_files = sorted(handlers_dir.glob("*_handler.py"))
    
    print(f"Migrating {len(handler_files)} handlers...\n")
    
    success = 0
    for handler_file in handler_files:
        migrated, msg = migrate_handler(handler_file)
        status = "✅" if migrated else "⏭️"
        print(f"{status} {handler_file.name}: {msg}")
        if migrated:
            success += 1
    
    print(f"\n✅ Migrated {success}/{len(handler_files)} handlers")

if __name__ == "__main__":
    main()