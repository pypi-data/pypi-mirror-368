# Scripts

Utility and development scripts for the XML Analysis Framework.

## Utility Scripts

### collect_test_files.py
Downloads and organizes XML test files from various sources for testing the framework.

```bash
python scripts/collect_test_files.py
```

## Debug Scripts

Located in `debug/` subdirectory for troubleshooting and development.

### debug_handlers.py
Debug script for testing individual handler functionality and troubleshooting handler issues.

### debug_kml.py
Specialized debugging for KML (Google Earth) document processing.

### debug_soap_namespaces.py
Namespace handling troubleshooting for SOAP envelope processing.

## Usage

```bash
# Run utility scripts from project root
python scripts/collect_test_files.py

# Run debug scripts from project root
python scripts/debug/debug_handlers.py
python scripts/debug/debug_kml.py
python scripts/debug/debug_soap_namespaces.py
```