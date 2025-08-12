#!/usr/bin/env python3
"""
XML Chunking Strategy and Integration Module

This module provides intelligent chunking strategies for XML documents
to prepare them for LLM processing while preserving context and structure.
"""

import defusedxml.ElementTree as ET
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any


@dataclass
class ChunkingConfig:
    """Configuration for chunking strategy"""

    max_chunk_size: int = 3000  # tokens (approximate)
    min_chunk_size: int = 500
    overlap_size: int = 200
    preserve_hierarchy: bool = True
    include_parent_context: bool = True
    semantic_boundaries: List[str] = None  # Element names that are natural boundaries


@dataclass
class XMLChunk:
    """Represents a chunk of XML content"""

    chunk_id: str
    content: str
    element_path: str
    start_line: int
    end_line: int
    parent_context: Optional[str]
    metadata: Dict[str, Any]
    token_estimate: int
    elements_included: List[str]


class XMLChunkingStrategy:
    """Base class for different chunking strategies"""

    def __init__(
        self, config: ChunkingConfig = None, max_file_size_mb: Optional[float] = None
    ):
        """
        Initialize the chunking strategy

        Args:
            config: Chunking configuration
            max_file_size_mb: Maximum allowed file size in megabytes
        """
        self.config = config or ChunkingConfig()
        self.max_file_size_mb = max_file_size_mb

    def estimate_tokens(self, text: str) -> int:
        """Rough estimation of tokens (words * 1.3)"""
        return int(len(text.split()) * 1.3)

    def generate_chunk_id(self, content: str, index: int) -> str:
        """Generate unique chunk ID"""
        hash_content = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"chunk_{index}_{hash_content}"

    def chunk_document(
        self, file_path: str, specialized_analysis: Dict[str, Any] = None
    ) -> List[XMLChunk]:
        """Chunk an XML document based on the strategy"""
        # Check file size limits if specified
        if self.max_file_size_mb is not None:
            try:
                file_size_bytes = Path(file_path).stat().st_size
                file_size_mb = file_size_bytes / (1024 * 1024)

                if file_size_mb > self.max_file_size_mb:
                    raise ValueError(
                        f"File too large: {file_size_mb:.2f}MB exceeds "
                        f"limit of {self.max_file_size_mb}MB"
                    )
            except OSError as e:
                raise OSError(f"Failed to check file size: {e}")

        # Base method only does validation - subclasses implement actual chunking
        return []


class HierarchicalChunking(XMLChunkingStrategy):
    """Chunks based on XML hierarchy, respecting element boundaries"""

    def chunk_document(
        self, file_path: str, specialized_analysis: Dict[str, Any] = None
    ) -> List[XMLChunk]:
        # Check file size limits (calls parent method)
        super().chunk_document(file_path, specialized_analysis)

        chunks = []
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Determine semantic boundaries based on document type
        if specialized_analysis:
            # Handle SpecializedAnalysis objects, DocumentTypeInfo objects, and dict formats
            if hasattr(specialized_analysis, 'type_name'):
                # SpecializedAnalysis object (has type_name directly)
                type_name = specialized_analysis.type_name
            elif hasattr(specialized_analysis, 'get'):
                # Dictionary format
                document_type = specialized_analysis.get("document_type", {})
                if hasattr(document_type, 'type_name'):
                    # DocumentTypeInfo object from analyze_document
                    type_name = document_type.type_name
                else:
                    # Dictionary format (legacy)
                    type_name = document_type.get("type_name", "")
            else:
                type_name = ""
            
            self.config.semantic_boundaries = self._get_semantic_boundaries(type_name)

        # Start chunking from root
        chunk_index = 0
        for chunk in self._chunk_element(root, "", chunk_index):
            chunks.append(chunk)
            chunk_index += 1

        return chunks

    def _chunk_element(
        self, element: Element, path: str, start_index: int
    ) -> Generator[XMLChunk, None, None]:
        """Recursively chunk an element and its children"""
        current_path = f"{path}/{element.tag}" if path else element.tag

        # Check if this element is a semantic boundary
        if self._is_semantic_boundary(element):
            # For hierarchical chunking, always look for smaller boundaries first
            child_boundaries = []
            for child in element:
                if self._is_semantic_boundary(child):
                    child_boundaries.append(child)

            # If we have semantic boundary children, chunk them individually
            if child_boundaries and element.tag.split("}")[-1] not in [
                "Rule"
            ]:  # Don't subdivide Rules
                yield from self._process_children(element, current_path, start_index)
            else:
                # No boundary children or this is a leaf boundary - create chunk
                content = ET.tostring(element, encoding="unicode")
                tokens = self.estimate_tokens(content)

                if tokens <= self.config.max_chunk_size:
                    # Element fits in one chunk
                    yield self._create_chunk(
                        element, current_path, start_index, content
                    )
                else:
                    # Element too large, need to split children
                    yield from self._split_large_element(
                        element, current_path, start_index
                    )
        else:
            # Not a boundary, continue processing children
            yield from self._process_children(element, current_path, start_index)

    def _is_semantic_boundary(self, element: Element) -> bool:
        """Check if element is a natural chunking boundary"""
        if not self.config.semantic_boundaries:
            return False

        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag
        return tag in self.config.semantic_boundaries

    def _create_chunk(
        self, element: Element, path: str, index: int, content: str = None
    ) -> XMLChunk:
        """Create a chunk from an element"""
        if content is None:
            content = ET.tostring(element, encoding="unicode")

        # Get parent context if configured
        parent_context = None
        if self.config.include_parent_context:
            parent_context = self._get_parent_context(element)

        # Extract metadata
        metadata = {
            "tag": element.tag,
            "attributes": dict(element.attrib),
            "namespace": element.tag.split("}")[0][1:] if "}" in element.tag else None,
        }

        # Get included elements
        elements_included = list(
            set(e.tag.split("}")[-1] if "}" in e.tag else e.tag for e in element.iter())
        )

        return XMLChunk(
            chunk_id=self.generate_chunk_id(content, index),
            content=content,
            element_path=path,
            start_line=0,  # Would need line tracking for accurate values
            end_line=0,
            parent_context=parent_context,
            metadata=metadata,
            token_estimate=self.estimate_tokens(content),
            elements_included=elements_included,
        )

    def _split_large_element(
        self, element: Element, path: str, start_index: int
    ) -> Generator[XMLChunk, None, None]:
        """Split a large element into multiple chunks"""
        # Strategy: Group children until size limit reached
        current_chunk_elements = []
        current_size = 0
        chunk_index = start_index

        for child in element:
            child_content = ET.tostring(child, encoding="unicode")
            child_size = self.estimate_tokens(child_content)

            if (
                current_size + child_size > self.config.max_chunk_size
                and current_chunk_elements
            ):
                # Create chunk from accumulated elements
                yield self._create_chunk_from_elements(
                    current_chunk_elements, element, path, chunk_index
                )
                chunk_index += 1
                current_chunk_elements = [child]
                current_size = child_size
            else:
                current_chunk_elements.append(child)
                current_size += child_size

        # Don't forget the last chunk
        if current_chunk_elements:
            yield self._create_chunk_from_elements(
                current_chunk_elements, element, path, chunk_index
            )

    def _create_chunk_from_elements(
        self, elements: List[Element], parent: Element, path: str, index: int
    ) -> XMLChunk:
        """Create a chunk from a list of elements"""
        # Create a wrapper element
        wrapper = Element(parent.tag, parent.attrib)
        for elem in elements:
            wrapper.append(elem)

        return self._create_chunk(wrapper, path, index)

    def _process_children(
        self, element: Element, path: str, start_index: int
    ) -> Generator[XMLChunk, None, None]:
        """Process children of a non-boundary element"""
        chunk_index = start_index
        for child in element:
            for chunk in self._chunk_element(child, path, chunk_index):
                yield chunk
                chunk_index += 1

    def _get_parent_context(self, element: Element) -> str:
        """Get context from parent elements"""
        # This would need access to parent in real implementation
        return f"Parent: {element.tag}"

    def _get_semantic_boundaries(self, doc_type: str) -> List[str]:
        """Get semantic boundaries based on document type"""
        boundaries = {
            "SCAP Security Report": ["Rule", "Group", "Benchmark"],
            "SCAP/XSD Schema": [
                "complexType",
                "element",
                "simpleType",
                "group",
                "attributeGroup",
            ],
            "SCAP/XCCDF Document": ["Rule", "Group", "Benchmark", "Profile"],
            "ServiceNow Export": ["incident", "sys_journal_field", "sys_attachment"],
            "RSS/Atom Feed": ["item", "entry"],
            "Maven POM": ["dependency", "plugin", "profile"],
            "Spring Configuration": ["bean", "component-scan"],
            "DocBook Documentation": ["chapter", "section", "article"],
            "Log4j Configuration": ["appender", "logger"],
        }

        # Fallback with more common XML elements
        default_boundaries = [
            "section",
            "record",
            "item",
            "entry",
            "rule",
            "group",
            "element",
            "component",
        ]
        return boundaries.get(doc_type, default_boundaries)


class SlidingWindowChunking(XMLChunkingStrategy):
    """Chunks using a sliding window approach with overlap"""

    def chunk_document(
        self, file_path: str, specialized_analysis: Dict[str, Any] = None
    ) -> List[XMLChunk]:
        # Check file size limits (calls parent method)
        super().chunk_document(file_path, specialized_analysis)

        chunks = []

        # Parse the document
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Convert to a list of elements with their content
        elements = self._flatten_elements(root)

        # Create chunks with sliding window
        chunk_index = 0
        i = 0

        while i < len(elements):
            chunk_elements = []
            chunk_size = 0

            # Build chunk up to max size
            j = i
            while j < len(elements) and chunk_size < self.config.max_chunk_size:
                elem_content = elements[j]["content"]
                elem_size = self.estimate_tokens(elem_content)

                if chunk_size + elem_size <= self.config.max_chunk_size:
                    chunk_elements.append(elements[j])
                    chunk_size += elem_size
                    j += 1
                else:
                    break

            # Create chunk if we have content
            if chunk_elements:
                chunk = self._create_chunk_from_flattened(chunk_elements, chunk_index)
                chunks.append(chunk)
                chunk_index += 1

                # Move window (with overlap)
                overlap_size = 0
                overlap_count = 0

                # Count backwards to find overlap point
                for k in range(len(chunk_elements) - 1, -1, -1):
                    overlap_size += self.estimate_tokens(chunk_elements[k]["content"])
                    overlap_count += 1
                    if overlap_size >= self.config.overlap_size:
                        break

                i = j - overlap_count + 1
            else:
                i += 1

        return chunks

    def _flatten_elements(self, root: Element) -> List[Dict[str, Any]]:
        """Flatten XML tree into a list of elements with metadata"""
        flattened = []

        def traverse(elem, path=""):
            current_path = f"{path}/{elem.tag}" if path else elem.tag

            # Add element info
            flattened.append(
                {
                    "element": elem,
                    "path": current_path,
                    "content": ET.tostring(elem, encoding="unicode"),
                    "tag": elem.tag,
                    "depth": current_path.count("/"),
                }
            )

            # Process children
            for child in elem:
                traverse(child, current_path)

        traverse(root)
        return flattened

    def _create_chunk_from_flattened(
        self, elements: List[Dict[str, Any]], index: int
    ) -> XMLChunk:
        """Create chunk from flattened elements"""
        # Combine content
        content_parts = []
        paths = []
        tags = set()

        for elem_info in elements:
            content_parts.append(elem_info["content"])
            paths.append(elem_info["path"])
            tags.add(
                elem_info["tag"].split("}")[-1]
                if "}" in elem_info["tag"]
                else elem_info["tag"]
            )

        content = "\n".join(content_parts)

        return XMLChunk(
            chunk_id=self.generate_chunk_id(content, index),
            content=content,
            element_path="; ".join(set(paths[:3])),  # First 3 unique paths
            start_line=0,
            end_line=0,
            parent_context=None,
            metadata={
                "elements_count": len(elements),
                "depth_range": (
                    min(e["depth"] for e in elements),
                    max(e["depth"] for e in elements),
                ),
            },
            token_estimate=self.estimate_tokens(content),
            elements_included=list(tags),
        )


class ContentAwareChunking(XMLChunkingStrategy):
    """Chunks based on content type and meaning"""

    def __init__(
        self, config: ChunkingConfig = None, max_file_size_mb: Optional[float] = None
    ):
        super().__init__(config, max_file_size_mb)
        self.content_patterns = {
            "narrative": ["para", "p", "description", "abstract", "summary"],
            "structured": ["table", "list", "itemizedlist", "orderedlist"],
            "code": ["code", "programlisting", "screen", "computeroutput"],
            "metadata": ["info", "meta", "metadata", "properties"],
        }

    def chunk_document(
        self, file_path: str, specialized_analysis: Dict[str, Any] = None
    ) -> List[XMLChunk]:
        # Check file size limits (calls parent method)
        super().chunk_document(file_path, specialized_analysis)

        chunks = []
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Group elements by content type
        content_groups = self._group_by_content_type(root)

        # Create chunks for each content group
        chunk_index = 0
        for content_type, elements in content_groups.items():
            for chunk in self._chunk_content_group(content_type, elements, chunk_index):
                chunks.append(chunk)
                chunk_index += 1

        return chunks

    def _group_by_content_type(self, root: Element) -> Dict[str, List[Element]]:
        """Group elements by their content type"""
        groups = {
            "narrative": [],
            "structured": [],
            "code": [],
            "metadata": [],
            "other": [],
        }

        for elem in root.iter():
            content_type = self._determine_content_type(elem)
            groups[content_type].append(elem)

        return {k: v for k, v in groups.items() if v}  # Remove empty groups

    def _determine_content_type(self, element: Element) -> str:
        """Determine the content type of an element"""
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

        for content_type, patterns in self.content_patterns.items():
            if tag.lower() in patterns:
                return content_type

        # Check children for hints
        child_tags = [
            child.tag.split("}")[-1] if "}" in child.tag else child.tag
            for child in element
        ]

        for content_type, patterns in self.content_patterns.items():
            if any(ct.lower() in patterns for ct in child_tags):
                return content_type

        return "other"

    def _chunk_content_group(
        self, content_type: str, elements: List[Element], start_index: int
    ) -> Generator[XMLChunk, None, None]:
        """Create chunks for a group of similar content"""
        # Use different strategies based on content type
        if content_type == "narrative":
            yield from self._chunk_narrative(elements, start_index)
        elif content_type == "code":
            yield from self._chunk_code(elements, start_index)
        elif content_type == "structured":
            yield from self._chunk_structured(elements, start_index)
        else:
            yield from self._chunk_generic(elements, start_index)

    def _chunk_narrative(
        self, elements: List[Element], start_index: int
    ) -> Generator[XMLChunk, None, None]:
        """Chunk narrative content, trying to keep paragraphs together"""
        current_content = []
        current_size = 0
        chunk_index = start_index

        for elem in elements:
            elem_text = ET.tostring(elem, encoding="unicode")
            elem_size = self.estimate_tokens(elem_text)

            if (
                current_size + elem_size > self.config.max_chunk_size
                and current_content
            ):
                # Create chunk
                yield self._create_narrative_chunk(current_content, chunk_index)
                chunk_index += 1

                # Start new chunk with overlap
                overlap_elements = self._get_overlap_elements(current_content)
                current_content = overlap_elements + [elem_text]
                current_size = sum(self.estimate_tokens(e) for e in current_content)
            else:
                current_content.append(elem_text)
                current_size += elem_size

        if current_content:
            yield self._create_narrative_chunk(current_content, chunk_index)

    def _chunk_code(
        self, elements: List[Element], start_index: int
    ) -> Generator[XMLChunk, None, None]:
        """Chunk code content, trying to keep code blocks intact"""
        for i, elem in enumerate(elements):
            content = ET.tostring(elem, encoding="unicode")
            tokens = self.estimate_tokens(content)

            if tokens <= self.config.max_chunk_size:
                # Single code block fits
                yield XMLChunk(
                    chunk_id=self.generate_chunk_id(content, start_index + i),
                    content=content,
                    element_path=self._get_element_path(elem),
                    start_line=0,
                    end_line=0,
                    parent_context=None,
                    metadata={
                        "content_type": "code",
                        "language": elem.get("language", "unknown"),
                    },
                    token_estimate=tokens,
                    elements_included=["code"],
                )
            else:
                # Split large code block
                yield from self._split_large_code_block(elem, start_index + i)

    def _chunk_structured(
        self, elements: List[Element], start_index: int
    ) -> Generator[XMLChunk, None, None]:
        """Chunk structured content like tables and lists"""
        for i, elem in enumerate(elements):
            content = ET.tostring(elem, encoding="unicode")

            yield XMLChunk(
                chunk_id=self.generate_chunk_id(content, start_index + i),
                content=content,
                element_path=self._get_element_path(elem),
                start_line=0,
                end_line=0,
                parent_context=None,
                metadata={"content_type": "structured", "structure_type": elem.tag},
                token_estimate=self.estimate_tokens(content),
                elements_included=[elem.tag],
            )

    def _chunk_generic(
        self, elements: List[Element], start_index: int
    ) -> Generator[XMLChunk, None, None]:
        """Generic chunking for other content"""
        for i, elem in enumerate(elements):
            content = ET.tostring(elem, encoding="unicode")

            yield XMLChunk(
                chunk_id=self.generate_chunk_id(content, start_index + i),
                content=content,
                element_path=self._get_element_path(elem),
                start_line=0,
                end_line=0,
                parent_context=None,
                metadata={"content_type": "other"},
                token_estimate=self.estimate_tokens(content),
                elements_included=[elem.tag],
            )

    def _create_narrative_chunk(self, content_list: List[str], index: int) -> XMLChunk:
        """Create a chunk from narrative content"""
        content = "\n".join(content_list)

        return XMLChunk(
            chunk_id=self.generate_chunk_id(content, index),
            content=content,
            element_path="narrative_section",
            start_line=0,
            end_line=0,
            parent_context=None,
            metadata={
                "content_type": "narrative",
                "paragraph_count": len(content_list),
            },
            token_estimate=self.estimate_tokens(content),
            elements_included=["para", "p", "description"],
        )

    def _get_overlap_elements(self, content_list: List[str]) -> List[str]:
        """Get elements for overlap from the end of content list"""
        overlap_elements = []
        overlap_size = 0

        for content in reversed(content_list):
            overlap_size += self.estimate_tokens(content)
            overlap_elements.insert(0, content)

            if overlap_size >= self.config.overlap_size:
                break

        return overlap_elements

    def _split_large_code_block(
        self, elem: Element, index: int
    ) -> Generator[XMLChunk, None, None]:
        """Split a large code block into smaller chunks"""
        # This is a simplified version - real implementation would be smarter
        text = elem.text or ""
        lines = text.split("\n")

        current_chunk = []
        current_size = 0
        chunk_num = 0

        for line in lines:
            line_size = self.estimate_tokens(line)

            if current_size + line_size > self.config.max_chunk_size and current_chunk:
                # Create chunk
                content = "\n".join(current_chunk)
                yield XMLChunk(
                    chunk_id=self.generate_chunk_id(content, index + chunk_num),
                    content=f"<code>{content}</code>",
                    element_path=self._get_element_path(elem),
                    start_line=0,
                    end_line=0,
                    parent_context=None,
                    metadata={
                        "content_type": "code",
                        "language": elem.get("language", "unknown"),
                        "part": chunk_num + 1,
                    },
                    token_estimate=current_size,
                    elements_included=["code"],
                )

                chunk_num += 1
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size

        # Last chunk
        if current_chunk:
            content = "\n".join(current_chunk)
            yield XMLChunk(
                chunk_id=self.generate_chunk_id(content, index + chunk_num),
                content=f"<code>{content}</code>",
                element_path=self._get_element_path(elem),
                start_line=0,
                end_line=0,
                parent_context=None,
                metadata={
                    "content_type": "code",
                    "language": elem.get("language", "unknown"),
                    "part": chunk_num + 1,
                },
                token_estimate=current_size,
                elements_included=["code"],
            )

    def _get_element_path(self, elem: Element) -> str:
        """Get a simple path representation for an element"""
        # In real implementation, would track actual path
        return elem.tag


class ChunkingOrchestrator:
    """Orchestrates the chunking process using appropriate strategies"""

    def __init__(self, max_file_size_mb: Optional[float] = None):
        """
        Initialize the chunking orchestrator

        Args:
            max_file_size_mb: Maximum allowed file size in megabytes.
                            If None, no size limit is enforced.
                            Recommended: 100MB for production use.
        """
        self.max_file_size_mb = max_file_size_mb
        self.strategies = {
            "hierarchical": HierarchicalChunking,
            "sliding_window": SlidingWindowChunking,
            "content_aware": ContentAwareChunking,
        }

    def chunk_document(
        self,
        file_path: str,
        specialized_analysis: Dict[str, Any],
        strategy: str = "auto",
        config: ChunkingConfig = None,
    ) -> List[XMLChunk]:
        """
        Chunk a document using the appropriate strategy
        
        Args:
            file_path: Path to the XML file to chunk
            specialized_analysis: Analysis result from XMLDocumentAnalyzer.analyze_document()
                                or dictionary with 'document_type' and 'analysis' keys
            strategy: Chunking strategy ("auto", "hierarchical", "sliding_window", "content_aware")
            config: Optional ChunkingConfig for custom chunk sizes and behavior
            
        Returns:
            List of XMLChunk objects
            
        Note:
            This method accepts analysis results directly from analyze_document(),
            no format conversion needed.
        """

        # Check file size limits
        if self.max_file_size_mb is not None:
            try:
                file_size_bytes = Path(file_path).stat().st_size
                file_size_mb = file_size_bytes / (1024 * 1024)

                if file_size_mb > self.max_file_size_mb:
                    raise ValueError(
                        f"File too large: {file_size_mb:.2f}MB exceeds "
                        f"limit of {self.max_file_size_mb}MB"
                    )
            except OSError as e:
                raise OSError(f"Failed to check file size: {e}")

        if strategy == "auto":
            strategy = self._select_strategy(specialized_analysis)

        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")

        # Create strategy instance
        strategy_class = self.strategies[strategy]
        chunker = strategy_class(config, self.max_file_size_mb)

        # Apply document-specific configuration
        if config is None:
            config = self._create_config_for_document(specialized_analysis)
            chunker.config = config

        # Perform chunking
        chunks = chunker.chunk_document(file_path, specialized_analysis)

        # Post-process chunks
        chunks = self._post_process_chunks(chunks, specialized_analysis)

        return chunks

    def _select_strategy(self, analysis) -> str:
        """Select the best chunking strategy based on document analysis"""
        # Handle both SpecializedAnalysis objects and legacy dict formats
        if hasattr(analysis, 'type_name'):
            # SpecializedAnalysis object (new format)
            doc_type = analysis.type_name
        elif isinstance(analysis, dict):
            # Legacy dictionary format
            document_type = analysis.get("document_type", {})
            if hasattr(document_type, 'type_name'):
                # DocumentTypeInfo object from analyze_document
                doc_type = document_type.type_name
            else:
                # Dictionary format (legacy)
                doc_type = document_type.get("type_name", "")
        else:
            doc_type = ""

        # Strategy selection based on document type
        strategy_map = {
            "SCAP Security Report": "hierarchical",
            "SCAP/XSD Schema": "hierarchical",
            "SCAP/XCCDF Document": "hierarchical",
            "ServiceNow Export": "sliding_window",  # Conversation-heavy format
            "RSS/Atom Feed": "hierarchical",
            "Maven POM": "hierarchical",
            "Spring Configuration": "hierarchical",
            "DocBook Documentation": "content_aware",
            "Log4j Configuration": "hierarchical",
            "SVG Graphics": "hierarchical",
        }

        return strategy_map.get(doc_type, "sliding_window")

    def _create_config_for_document(self, analysis) -> ChunkingConfig:
        """Create optimal chunking configuration for document"""
        # Handle both SpecializedAnalysis objects and legacy dict formats
        if hasattr(analysis, 'type_name'):
            # SpecializedAnalysis object (new format)
            doc_type = analysis.type_name
        elif isinstance(analysis, dict):
            # Legacy dictionary format
            doc_type = analysis.get("document_type", {}).get("type_name", "")
        else:
            doc_type = ""

        # Base configuration
        config = ChunkingConfig()

        # Adjust based on document type
        if "Documentation" in doc_type:
            config.max_chunk_size = 4000  # Larger chunks for documentation
            config.preserve_hierarchy = True
            config.include_parent_context = True
        elif "Configuration" in doc_type:
            config.max_chunk_size = 2000  # Smaller chunks for configs
            config.preserve_hierarchy = True
        elif "Feed" in doc_type:
            config.max_chunk_size = 1500  # Individual items
            config.overlap_size = 0  # No overlap needed

        return config

    def _post_process_chunks(
        self, chunks: List[XMLChunk], analysis
    ) -> List[XMLChunk]:
        """Post-process chunks to add additional metadata"""
        # Handle both SpecializedAnalysis objects and legacy dict formats
        if hasattr(analysis, 'type_name'):
            # SpecializedAnalysis object (new format)
            doc_type = analysis.type_name
        elif isinstance(analysis, dict):
            # Legacy dictionary format
            document_type = analysis.get("document_type", {})
            if hasattr(document_type, 'type_name'):
                # DocumentTypeInfo object from analyze_document
                doc_type = document_type.type_name
            else:
                # Dictionary format (legacy)
                doc_type = document_type.get("type_name", "")
        else:
            doc_type = ""

        for i, chunk in enumerate(chunks):
            # Add document context
            chunk.metadata["document_type"] = doc_type
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(chunks)

            # Add navigation info
            if i > 0:
                chunk.metadata["previous_chunk"] = chunks[i - 1].chunk_id
            if i < len(chunks) - 1:
                chunk.metadata["next_chunk"] = chunks[i + 1].chunk_id

        return chunks


# Example usage
if __name__ == "__main__":
    # Example: Using the chunking orchestrator
    from src.core.analyzer import XMLDocumentAnalyzer

    # Analyze document first
    analyzer = XMLDocumentAnalyzer()
    analysis = analyzer.analyze_document("sample_data/example.xml")

    # Chunk the document
    orchestrator = ChunkingOrchestrator()
    chunks = orchestrator.chunk_document(
        "sample_data/example.xml",
        analysis,
        strategy="auto",  # Let it choose the best strategy
    )

    # Display results
    print(f"Document chunked into {len(chunks)} chunks")
    for chunk in chunks[:3]:  # Show first 3 chunks
        print(f"\nChunk {chunk.chunk_id}:")
        print(f"  Path: {chunk.element_path}")
        print(f"  Tokens: ~{chunk.token_estimate}")
        print(f"  Elements: {', '.join(chunk.elements_included[:5])}")
        print(f"  Content preview: {chunk.content[:100]}...")
