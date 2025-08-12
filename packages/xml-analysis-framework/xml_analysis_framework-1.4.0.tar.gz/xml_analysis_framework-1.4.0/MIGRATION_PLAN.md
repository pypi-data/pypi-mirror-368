# Migration Plan: SpecializedAnalysis extends DocumentTypeInfo

## Current State
- `DocumentTypeInfo`: Contains type_name, confidence, version, etc.
- `SpecializedAnalysis`: Contains document_type (string), analysis fields
- `analyze_document()` returns a dictionary combining both
- `chunk_document()` expects dictionary with nested objects

## Problems
1. API inconsistency between analyzer output and chunking input
2. Redundant document_type field in SpecializedAnalysis
3. Need for format conversions

## Proposed Solution
Make `SpecializedAnalysis` extend `DocumentTypeInfo` to create a unified object.

## Migration Steps

### Phase 1: Update Base Classes (DONE)
✅ Modified `SpecializedAnalysis` to extend `DocumentTypeInfo`
✅ Added file_path, handler_used, namespaces to SpecializedAnalysis

### Phase 2: Update Analyzer
1. Change `analyze_document()` to return `SpecializedAnalysis` instead of dict
2. Merge doc_type info into the analysis object

### Phase 3: Update All Handlers (29 files)
Need to change each handler's `analyze()` method from:
```python
return SpecializedAnalysis(
    document_type="SCAP Security Report",  # Remove this
    key_findings=findings,
    ...
)
```

To:
```python
# Get the doc_type info from detect_type()
doc_type = self.detect_type(file_path, root=root, namespaces=namespaces)

return SpecializedAnalysis(
    # From DocumentTypeInfo
    type_name=doc_type.type_name,
    confidence=doc_type.confidence,
    version=doc_type.version,
    schema_uri=doc_type.schema_uri,
    metadata=doc_type.metadata,
    # Analysis fields
    key_findings=findings,
    ...
)
```

### Phase 4: Update Chunking
- Remove format conversion code (already handles both formats)
- Update to work with SpecializedAnalysis objects

### Phase 5: Update Simple API
- Update wrapper functions to handle new return type
- Ensure backward compatibility

## Backward Compatibility Strategy
1. Add `to_dict()` method to SpecializedAnalysis for legacy code
2. Keep accepting dict format in chunk_document (already done)
3. Deprecation warnings for dict access patterns

## Benefits
1. Single object for complete analysis
2. No format conversions needed
3. Type safety with inheritance
4. Cleaner API
5. Maintains all information including confidence scores