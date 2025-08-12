#!/usr/bin/env python3
"""
Migrate the remaining handlers that use different patterns
"""

import os
import re
from pathlib import Path

# List of remaining handlers that need manual migration
remaining_handlers = [
    "docbook_handler.py",
    "enterprise_config_handler.py", 
    "hibernate_handler.py",
    "ivy_handler.py",
    "log4j_config_handler.py",
    "openapi_xml_handler.py",
    "saml_handler.py",
    "sitemap_handler.py",
    "soap_envelope_handler.py",
    "svg_handler.py",
    "test_report_handler.py"
]

def fix_handler(file_path):
    """Fix a specific handler"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Different patterns these handlers might use
    patterns = [
        # Pattern 1: return SpecializedAnalysis(document_type=variable, ...)
        (r'return SpecializedAnalysis\(\s*document_type=([^,]+),([^)]+)\)', 
         r'''# Get document type info
        doc_type = self.detect_type(file_path, root=root, namespaces={})
        
        return SpecializedAnalysis(
            # From DocumentTypeInfo
            type_name=doc_type.type_name,
            confidence=doc_type.confidence,
            version=doc_type.version,
            schema_uri=doc_type.schema_uri,
            metadata=doc_type.metadata,
            # Analysis fields\2)'''),
        
        # Pattern 2: return SpecializedAnalysis(\n    document_type=..., (multiline)
        (r'return SpecializedAnalysis\(\s*\n\s*document_type=([^,]+),([^)]+)\)', 
         r'''# Get document type info
        doc_type = self.detect_type(file_path, root=root, namespaces={})
        
        return SpecializedAnalysis(
            # From DocumentTypeInfo
            type_name=doc_type.type_name,
            confidence=doc_type.confidence,
            version=doc_type.version,
            schema_uri=doc_type.schema_uri,
            metadata=doc_type.metadata,
            # Analysis fields\2)''')
    ]
    
    original = content
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    
    return False

def main():
    handlers_dir = Path("src/handlers")
    
    print("Fixing remaining handlers...\n")
    
    fixed = 0
    for handler_name in remaining_handlers:
        handler_path = handlers_dir / handler_name
        if not handler_path.exists():
            print(f"⚠️  {handler_name}: File not found")
            continue
            
        if fix_handler(handler_path):
            print(f"✅ {handler_name}: Fixed")
            fixed += 1
        else:
            print(f"⏭️  {handler_name}: No changes needed or pattern not found")
    
    print(f"\n✅ Fixed {fixed}/{len(remaining_handlers)} remaining handlers")

if __name__ == "__main__":
    main()