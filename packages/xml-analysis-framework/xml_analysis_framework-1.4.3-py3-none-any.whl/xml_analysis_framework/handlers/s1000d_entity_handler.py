#!/usr/bin/env python3
"""
Safe entity handling for S1000D XML files

S1000D files often contain external entity references for graphics (ICN references).
This module provides safe preprocessing to handle these entities without security risks.
"""

import re
from typing import Tuple, List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# S1000D standard graphic formats
S1000D_GRAPHIC_FORMATS = {
    'cgm', 'CGM',      # Computer Graphics Metafile
    'jpg', 'JPG', 'jpeg', 'JPEG',  # JPEG
    'png', 'PNG',      # Portable Network Graphics
    'tif', 'TIF', 'tiff', 'TIFF',  # Tagged Image File Format
    'svg', 'SVG',      # Scalable Vector Graphics
    'gif', 'GIF',      # Graphics Interchange Format
    'bmp', 'BMP',      # Bitmap
}

# Pattern for S1000D ICN (Information Control Number) entities
ICN_ENTITY_PATTERN = re.compile(
    r'<!ENTITY\s+'
    r'(ICN-[A-Z0-9\-]+)\s+'  # Entity name (ICN format)
    r'SYSTEM\s+'
    r'"([^"]+)"\s+'          # System identifier (file path)
    r'NDATA\s+'
    r'(\w+)\s*>',            # Notation name
    re.IGNORECASE
)

# Pattern for DOCTYPE with entities
DOCTYPE_WITH_ENTITIES_PATTERN = re.compile(
    r'(<!DOCTYPE\s+\w+\s*\[)'  # DOCTYPE declaration start
    r'([^]]*)'                  # Entity declarations
    r'(\]>)',                   # DOCTYPE declaration end
    re.DOTALL
)


def is_safe_s1000d_entity(entity_name: str, system_id: str, notation: str) -> bool:
    """
    Check if an entity declaration is a safe S1000D graphic reference
    
    Args:
        entity_name: The entity name (e.g., "ICN-C0419-S1000D0360-001-01")
        system_id: The system identifier (e.g., "ICN-C0419-S1000D0360-001-01.CGM")
        notation: The notation type (e.g., "cgm")
    
    Returns:
        True if this is a safe S1000D graphic entity
    """
    # Check if entity name follows ICN pattern
    if not entity_name.startswith('ICN-'):
        return False
    
    # Check if system_id references a known graphic format
    file_ext = system_id.split('.')[-1] if '.' in system_id else ''
    if file_ext not in S1000D_GRAPHIC_FORMATS:
        return False
    
    # Check if notation matches expected graphic format
    if notation.lower() not in [fmt.lower() for fmt in S1000D_GRAPHIC_FORMATS]:
        return False
    
    # Additional safety: no path traversal
    if '..' in system_id or '/' in system_id.replace('\\', '/'):
        if not system_id.startswith('http://') and not system_id.startswith('https://'):
            return False
    
    return True


def extract_s1000d_entities(xml_content: str) -> Tuple[List[Dict[str, str]], str]:
    """
    Extract S1000D entity declarations from XML and return clean XML
    
    Args:
        xml_content: The raw XML content with potential entity declarations
    
    Returns:
        Tuple of (list of entity dictionaries, cleaned XML content)
    """
    entities = []
    
    # Find all ICN entity declarations
    for match in ICN_ENTITY_PATTERN.finditer(xml_content):
        entity_name = match.group(1)
        system_id = match.group(2)
        notation = match.group(3)
        
        if is_safe_s1000d_entity(entity_name, system_id, notation):
            entities.append({
                'name': entity_name,
                'system_id': system_id,
                'notation': notation,
                'type': 'graphic'
            })
            logger.debug(f"Found safe S1000D entity: {entity_name} -> {system_id}")
        else:
            logger.warning(f"Skipping potentially unsafe entity: {entity_name}")
    
    # Remove DOCTYPE declaration with entities if present
    def replace_doctype(match):
        doctype_start = match.group(1)
        doctype_end = match.group(3)
        # Return just the DOCTYPE without the entity declarations
        return '<!DOCTYPE dmodule>'
    
    cleaned_xml = DOCTYPE_WITH_ENTITIES_PATTERN.sub(replace_doctype, xml_content)
    
    return entities, cleaned_xml


def preprocess_s1000d_xml(file_path: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Preprocess S1000D XML file to safely handle entity declarations
    
    Args:
        file_path: Path to the S1000D XML file
    
    Returns:
        Tuple of (cleaned XML content, list of extracted entities)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Extract entities and clean the XML
        entities, cleaned_xml = extract_s1000d_entities(xml_content)
        
        if entities:
            logger.info(f"Extracted {len(entities)} S1000D graphic entities from {file_path}")
        
        return cleaned_xml, entities
        
    except Exception as e:
        logger.error(f"Error preprocessing S1000D file {file_path}: {e}")
        raise


def validate_s1000d_doctype(xml_content: str) -> bool:
    """
    Check if XML has S1000D DOCTYPE declaration
    
    Args:
        xml_content: XML content to check
    
    Returns:
        True if this appears to be an S1000D document
    """
    # Check for S1000D DOCTYPE patterns
    s1000d_doctypes = [
        '<!DOCTYPE dmodule',
        '<!DOCTYPE pm',
        '<!DOCTYPE dml',
        '<!DOCTYPE scormContentPackage',
        '<!DOCTYPE comrep',
    ]
    
    xml_lower = xml_content[:500].lower()  # Check first 500 chars
    return any(doctype in xml_lower for doctype in s1000d_doctypes)


if __name__ == "__main__":
    # Test with a sample S1000D file
    test_xml = """<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE dmodule  [
  <!ENTITY ICN-C0419-S1000D0379-001-01 SYSTEM "ICN-C0419-S1000D0379-001-01.CGM" NDATA cgm >
  <!ENTITY ICN-C0419-S1000D0380-001-01 SYSTEM "ICN-C0419-S1000D0380-001-01.JPG" NDATA jpg >
  <!ENTITY dangerous SYSTEM "file:///etc/passwd" NDATA txt >
]>
<dmodule>
  <content>Test content with &ICN-C0419-S1000D0379-001-01; reference</content>
</dmodule>"""
    
    entities, cleaned = extract_s1000d_entities(test_xml)
    print("Extracted entities:")
    for entity in entities:
        print(f"  - {entity['name']}: {entity['system_id']} ({entity['notation']})")
    print("\nCleaned XML:")
    print(cleaned[:200] + "..." if len(cleaned) > 200 else cleaned)