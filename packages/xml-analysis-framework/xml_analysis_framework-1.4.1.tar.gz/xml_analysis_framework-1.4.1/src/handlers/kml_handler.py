#!/usr/bin/env python3
"""
KML (Keyhole Markup Language) Handler

Analyzes KML files used by Google Earth, Google Maps, and other
geographic visualization applications. Extracts placemarks, paths,
polygons, styles, and other geographic features.
"""

import sys
import os
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base import XMLHandler, DocumentTypeInfo, SpecializedAnalysis  # noqa: E402


class KMLHandler(XMLHandler):
    """Handler for KML geographic data files"""

    KML_NAMESPACE = "http://www.opengis.net/kml/2.2"
    EARTH_NAMESPACE = "http://earth.google.com/kml/2.2"

    def _get_namespace(self, root: Element) -> str:
        """Extract namespace prefix from root element"""
        if "}" in root.tag:
            return root.tag.split("}")[0] + "}"
        return ""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for KML namespace
        if any(
            "opengis.net/kml" in uri or "earth.google.com/kml" in uri
            for uri in namespaces.values()
        ):
            return True, 1.0

        # Check root element
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if root_tag.lower() == "kml":
            # Check for KML-specific elements
            kml_elements = [
                "Document",
                "Folder",
                "Placemark",
                "Point",
                "LineString",
                "Polygon",
            ]
            found = sum(
                1 for elem in kml_elements if root.find(f".//{elem}") is not None
            )
            if found >= 2:
                return True, min(found * 0.2, 0.9)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Detect KML version
        version = "2.2"  # Default
        for uri in namespaces.values():
            if "kml/2.1" in uri:
                version = "2.1"
            elif "kml/2.0" in uri:
                version = "2.0"

        # Detect KML variant
        variant = "standard"
        # Use namespace-aware search for Google Earth extensions
        gx_namespace = "http://www.google.com/kml/ext/2.2"
        if root.find(f".//{{{gx_namespace}}}Tour") is not None:
            variant = "google_earth_tour"
        elif root.find(".//NetworkLink") is not None:
            variant = "network_linked"

        return DocumentTypeInfo(
            type_name="KML Geographic Data",
            confidence=0.95,
            version=version,
            metadata={
                "standard": "OGC KML",
                "category": "geographic",
                "variant": variant,
                "application": "Google Earth/Maps",
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "structure": self._analyze_structure(root),
            "placemarks": self._analyze_placemarks(root),
            "geometries": self._analyze_geometries(root),
            "styles": self._analyze_styles(root),
            "overlays": self._analyze_overlays(root),
            "network_links": self._analyze_network_links(root),
            "tours": self._analyze_tours(root),
            "data_quality": self._assess_data_quality(root),
        }

        recommendations = [
            "Visualize in Google Earth or compatible GIS software",
            "Extract coordinates for spatial analysis",
            "Convert to other GIS formats (GeoJSON, Shapefile)",
            "Analyze for data completeness and accuracy",
            "Optimize file size for web deployment",
            "Validate against KML schema",
            "Extract metadata for cataloging",
        ]

        ai_use_cases = [
            "Geospatial pattern recognition",
            "Location clustering and classification",
            "Route optimization and analysis",
            "Geographic feature extraction",
            "Spatial relationship discovery",
            "Area and distance calculations",
            "Terrain and elevation analysis",
            "Geographic anomaly detection",
            "Location-based recommendations",
        ]

        # Get document type info  
        doc_type = self.detect_type(file_path, root=root, namespaces={})
        
        return SpecializedAnalysis(
            # From DocumentTypeInfo
            type_name=doc_type.type_name,
            confidence=doc_type.confidence,
            version=doc_type.version,
            schema_uri=doc_type.schema_uri,
            metadata=doc_type.metadata,
            # Analysis fields
            key_findings=findings,
            recommendations=recommendations,
            data_inventory={
                "total_features": findings["structure"]["total_features"],
                "placemarks": len(findings["placemarks"]),
                "geometries": findings["geometries"]["total"],
                "styles": len(findings["styles"]),
                "overlays": findings["overlays"]["total"],
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._calculate_quality_metrics(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "geographic_bounds": self._extract_bounds(root),
            "feature_collection": self._extract_features(root),
            "style_definitions": self._extract_style_definitions(root),
            "metadata": self._extract_metadata(root),
            "coordinate_systems": self._extract_coordinate_info(root),
        }

    def _analyze_structure(self, root: Element) -> Dict[str, Any]:
        """Analyze overall KML document structure"""
        structure = {
            "documents": 0,
            "folders": 0,
            "features": [],
            "total_features": 0,
            "max_depth": 0,
            "has_schema": False,
            "has_extended_data": False,
        }

        # Get namespace
        ns = self._get_namespace(root)

        # Count structural elements using namespace
        structure["documents"] = len(root.findall(f".//{ns}Document"))
        structure["folders"] = len(root.findall(f".//{ns}Folder"))

        # Find all features
        feature_types = [
            "Placemark",
            "GroundOverlay",
            "ScreenOverlay",
            "PhotoOverlay",
            "NetworkLink",
            "Tour",
        ]

        for feature_type in feature_types:
            count = len(root.findall(f".//{ns}{feature_type}"))
            if count > 0:
                structure["features"].append({"type": feature_type, "count": count})
                structure["total_features"] += count

        # Check for schemas and extended data
        structure["has_schema"] = root.find(f".//{ns}Schema") is not None
        structure["has_extended_data"] = root.find(f".//{ns}ExtendedData") is not None

        # Calculate depth
        structure["max_depth"] = self._calculate_max_depth(root)

        return structure

    def _analyze_placemarks(self, root: Element) -> List[Dict[str, Any]]:
        """Analyze Placemark elements"""
        placemarks = []
        ns = self._get_namespace(root)

        for placemark in root.findall(f".//{ns}Placemark")[
            :100
        ]:  # Limit for performance
            pm_info = {
                "name": None,
                "description": None,
                "geometry_type": None,
                "style_url": None,
                "visibility": True,
                "has_extended_data": False,
                "snippet": None,
            }

            # Extract basic info
            name = placemark.find(f"{ns}name")
            if name is not None and name.text:
                pm_info["name"] = name.text.strip()

            desc = placemark.find(f"{ns}description")
            if desc is not None and desc.text:
                pm_info["description"] = desc.text.strip()[:200]  # Truncate

            snippet = placemark.find(f"{ns}snippet")
            if snippet is not None and snippet.text:
                pm_info["snippet"] = snippet.text.strip()

            # Geometry type
            for geom_type in ["Point", "LineString", "Polygon", "MultiGeometry"]:
                if placemark.find(f".//{ns}{geom_type}") is not None:
                    pm_info["geometry_type"] = geom_type
                    break

            # Style reference
            style_url = placemark.find(f"{ns}styleUrl")
            if style_url is not None and style_url.text:
                pm_info["style_url"] = style_url.text

            # Visibility
            visibility = placemark.find(f"{ns}visibility")
            if visibility is not None and visibility.text == "0":
                pm_info["visibility"] = False

            # Extended data
            pm_info["has_extended_data"] = (
                placemark.find(f"{ns}ExtendedData") is not None
            )

            placemarks.append(pm_info)

        return placemarks

    def _analyze_geometries(self, root: Element) -> Dict[str, Any]:
        """Analyze geometric elements"""
        geometries = {
            "total": 0,
            "points": 0,
            "lines": 0,
            "polygons": 0,
            "multi_geometries": 0,
            "models": 0,
            "coordinate_count": 0,
            "altitude_modes": {},
        }

        ns = self._get_namespace(root)

        # Count geometry types
        geometries["points"] = len(root.findall(f".//{ns}Point"))
        geometries["lines"] = len(root.findall(f".//{ns}LineString"))
        geometries["polygons"] = len(root.findall(f".//{ns}Polygon"))
        geometries["multi_geometries"] = len(root.findall(f".//{ns}MultiGeometry"))
        geometries["models"] = len(root.findall(f".//{ns}Model"))

        geometries["total"] = sum(
            [
                geometries["points"],
                geometries["lines"],
                geometries["polygons"],
                geometries["multi_geometries"],
                geometries["models"],
            ]
        )

        # Count coordinates
        for coords in root.findall(f".//{ns}coordinates"):
            if coords.text:
                # Rough count of coordinate tuples
                geometries["coordinate_count"] += len(coords.text.strip().split())

        # Analyze altitude modes
        for mode_elem in root.findall(f".//{ns}altitudeMode"):
            if mode_elem.text:
                mode_text = mode_elem.text.strip()
                geometries["altitude_modes"][mode_text] = (
                    geometries["altitude_modes"].get(mode_text, 0) + 1
                )

        return geometries

    def _analyze_styles(self, root: Element) -> List[Dict[str, Any]]:
        """Analyze style definitions"""
        styles = []

        for style in root.findall(".//Style"):
            style_info = {
                "id": style.get("id"),
                "icon_style": None,
                "line_style": None,
                "poly_style": None,
                "label_style": None,
                "balloon_style": None,
            }

            # Icon style
            icon_style = style.find(".//IconStyle")
            if icon_style is not None:
                style_info["icon_style"] = {
                    "color": self._get_element_text(icon_style, "color"),
                    "scale": self._get_element_text(icon_style, "scale"),
                    "icon_href": self._get_element_text(icon_style, ".//href"),
                }

            # Line style
            line_style = style.find(".//LineStyle")
            if line_style is not None:
                style_info["line_style"] = {
                    "color": self._get_element_text(line_style, "color"),
                    "width": self._get_element_text(line_style, "width"),
                }

            # Polygon style
            poly_style = style.find(".//PolyStyle")
            if poly_style is not None:
                style_info["poly_style"] = {
                    "color": self._get_element_text(poly_style, "color"),
                    "fill": self._get_element_text(poly_style, "fill") != "0",
                    "outline": self._get_element_text(poly_style, "outline") != "0",
                }

            # Label style
            label_style = style.find(".//LabelStyle")
            if label_style is not None:
                style_info["label_style"] = {
                    "color": self._get_element_text(label_style, "color"),
                    "scale": self._get_element_text(label_style, "scale"),
                }

            # Balloon style
            balloon_style = style.find(".//BalloonStyle")
            if balloon_style is not None:
                style_info["balloon_style"] = {
                    "bg_color": self._get_element_text(balloon_style, "bgColor"),
                    "text_color": self._get_element_text(balloon_style, "textColor"),
                }

            styles.append(style_info)

        return styles[:50]  # Limit

    def _analyze_overlays(self, root: Element) -> Dict[str, Any]:
        """Analyze overlay elements"""
        overlays = {
            "total": 0,
            "ground_overlays": [],
            "screen_overlays": [],
            "photo_overlays": [],
        }

        # Ground overlays
        for overlay in root.findall(".//GroundOverlay")[:20]:
            overlay_info = {
                "name": self._get_element_text(overlay, "name"),
                "icon_href": self._get_element_text(overlay, ".//Icon/href"),
                "has_lat_lon_box": overlay.find(".//LatLonBox") is not None,
            }
            overlays["ground_overlays"].append(overlay_info)

        # Screen overlays
        for overlay in root.findall(".//ScreenOverlay")[:20]:
            overlay_info = {
                "name": self._get_element_text(overlay, "name"),
                "icon_href": self._get_element_text(overlay, ".//Icon/href"),
            }
            overlays["screen_overlays"].append(overlay_info)

        # Photo overlays
        for overlay in root.findall(".//PhotoOverlay")[:20]:
            overlay_info = {
                "name": self._get_element_text(overlay, "name"),
                "icon_href": self._get_element_text(overlay, ".//Icon/href"),
                "has_view_volume": overlay.find(".//ViewVolume") is not None,
            }
            overlays["photo_overlays"].append(overlay_info)

        overlays["total"] = (
            len(overlays["ground_overlays"])
            + len(overlays["screen_overlays"])
            + len(overlays["photo_overlays"])
        )

        return overlays

    def _analyze_network_links(self, root: Element) -> List[Dict[str, Any]]:
        """Analyze NetworkLink elements"""
        network_links = []

        for link in root.findall(".//NetworkLink")[:20]:
            link_info = {
                "name": self._get_element_text(link, "name"),
                "href": self._get_element_text(link, ".//href"),
                "refresh_mode": self._get_element_text(link, ".//refreshMode"),
                "refresh_interval": self._get_element_text(link, ".//refreshInterval"),
                "view_refresh_mode": self._get_element_text(link, ".//viewRefreshMode"),
            }
            network_links.append(link_info)

        return network_links

    def _analyze_tours(self, root: Element) -> Dict[str, Any]:
        """Analyze Google Earth Tour elements"""
        tours = {"count": 0, "tour_info": []}

        # Look for gx:Tour elements
        for tour in root.findall(".//{http://www.google.com/kml/ext/2.2}Tour")[:10]:
            tour_info = {
                "name": self._get_element_text(tour, "name"),
                "playlist_items": 0,
            }

            # Count playlist items
            playlist = tour.find(".//{http://www.google.com/kml/ext/2.2}Playlist")
            if playlist is not None:
                tour_info["playlist_items"] = len(list(playlist))

            tours["tour_info"].append(tour_info)

        tours["count"] = len(tours["tour_info"])

        return tours

    def _assess_data_quality(self, root: Element) -> Dict[str, Any]:
        """Assess the quality of KML data"""
        quality = {
            "has_names": 0,
            "has_descriptions": 0,
            "has_coordinates": 0,
            "uses_styles": 0,
            "organized_folders": False,
            "uses_schemas": False,
            "coordinate_precision": "unknown",
        }

        # Check feature completeness
        placemarks = root.findall(".//Placemark")
        if placemarks:
            quality["has_names"] = sum(
                1 for p in placemarks if p.find("name") is not None
            ) / len(placemarks)
            quality["has_descriptions"] = sum(
                1 for p in placemarks if p.find("description") is not None
            ) / len(placemarks)
            quality["has_coordinates"] = sum(
                1 for p in placemarks if p.find(".//coordinates") is not None
            ) / len(placemarks)
            quality["uses_styles"] = sum(
                1 for p in placemarks if p.find("styleUrl") is not None
            ) / len(placemarks)

        # Check organization
        quality["organized_folders"] = len(root.findall(".//Folder")) > 0
        quality["uses_schemas"] = root.find(".//Schema") is not None

        # Check coordinate precision
        coords_sample = root.find(".//coordinates")
        if coords_sample is not None and coords_sample.text:
            coord_parts = coords_sample.text.strip().split(",")
            if len(coord_parts) >= 2:
                decimal_places = (
                    len(coord_parts[0].split(".")[-1]) if "." in coord_parts[0] else 0
                )
                if decimal_places >= 6:
                    quality["coordinate_precision"] = "high"
                elif decimal_places >= 4:
                    quality["coordinate_precision"] = "medium"
                else:
                    quality["coordinate_precision"] = "low"

        return quality

    def _extract_bounds(self, root: Element) -> Dict[str, float]:
        """Extract geographic bounds from coordinates"""
        bounds = {"north": -90.0, "south": 90.0, "east": -180.0, "west": 180.0}

        # Look for explicit bounds
        lat_lon_box = root.find(".//LatLonBox")
        if lat_lon_box is not None:
            bounds["north"] = float(self._get_element_text(lat_lon_box, "north", "-90"))
            bounds["south"] = float(self._get_element_text(lat_lon_box, "south", "90"))
            bounds["east"] = float(self._get_element_text(lat_lon_box, "east", "-180"))
            bounds["west"] = float(self._get_element_text(lat_lon_box, "west", "180"))
        else:
            # Calculate from coordinates
            for coords_elem in root.findall(".//coordinates"):
                if coords_elem.text:
                    coords = coords_elem.text.strip().split()
                    for coord in coords:
                        parts = coord.split(",")
                        if len(parts) >= 2:
                            try:
                                lon = float(parts[0])
                                lat = float(parts[1])
                                bounds["north"] = max(bounds["north"], lat)
                                bounds["south"] = min(bounds["south"], lat)
                                bounds["east"] = max(bounds["east"], lon)
                                bounds["west"] = min(bounds["west"], lon)
                            except ValueError:
                                continue

        return bounds

    def _extract_features(self, root: Element) -> List[Dict[str, Any]]:
        """Extract key features for analysis"""
        features = []

        for placemark in root.findall(".//Placemark")[:50]:  # Limit
            feature = {"type": "Feature", "properties": {}, "geometry": None}

            # Properties
            name = placemark.find("name")
            if name is not None and name.text:
                feature["properties"]["name"] = name.text.strip()

            desc = placemark.find("description")
            if desc is not None and desc.text:
                feature["properties"]["description"] = desc.text.strip()[:500]

            # Geometry
            point = placemark.find(".//Point/coordinates")
            if point is not None and point.text:
                coords = point.text.strip().split(",")
                if len(coords) >= 2:
                    feature["geometry"] = {
                        "type": "Point",
                        "coordinates": [float(coords[0]), float(coords[1])],
                    }

            line = placemark.find(".//LineString/coordinates")
            if line is not None and line.text:
                feature["geometry"] = {
                    "type": "LineString",
                    "coordinates": self._parse_coordinate_string(line.text),
                }

            polygon = placemark.find(
                ".//Polygon/outerBoundaryIs/LinearRing/coordinates"
            )
            if polygon is not None and polygon.text:
                feature["geometry"] = {
                    "type": "Polygon",
                    "coordinates": [self._parse_coordinate_string(polygon.text)],
                }

            if feature["geometry"]:
                features.append(feature)

        return features

    def _parse_coordinate_string(self, coord_string: str) -> List[List[float]]:
        """Parse KML coordinate string into coordinate array"""
        coordinates = []
        coords = coord_string.strip().split()

        for coord in coords:
            parts = coord.split(",")
            if len(parts) >= 2:
                try:
                    coordinates.append([float(parts[0]), float(parts[1])])
                except ValueError:
                    continue

        return coordinates

    def _extract_style_definitions(self, root: Element) -> Dict[str, Dict[str, Any]]:
        """Extract style definitions for reuse"""
        styles = {}

        for style in root.findall(".//Style"):
            style_id = style.get("id")
            if style_id:
                style_def = {}

                # Extract color from first found style element
                for style_type in ["IconStyle", "LineStyle", "PolyStyle", "LabelStyle"]:
                    style_elem = style.find(f".//{style_type}")
                    if style_elem is not None:
                        color = self._get_element_text(style_elem, "color")
                        if color:
                            style_def["color"] = color
                            break

                if style_def:
                    styles[style_id] = style_def

        return styles

    def _extract_metadata(self, root: Element) -> Dict[str, Any]:
        """Extract document metadata"""
        metadata = {
            "name": self._get_element_text(root, ".//Document/name"),
            "description": self._get_element_text(root, ".//Document/description"),
            "author": None,
            "link": None,
            "address": None,
            "snippet": self._get_element_text(root, ".//Document/Snippet"),
        }

        # Author info
        author = root.find(".//atom:author", {"atom": "http://www.w3.org/2005/Atom"})
        if author is not None:
            metadata["author"] = self._get_element_text(
                author, "atom:name", namespaces={"atom": "http://www.w3.org/2005/Atom"}
            )

        # Link
        link = root.find(".//atom:link", {"atom": "http://www.w3.org/2005/Atom"})
        if link is not None:
            metadata["link"] = link.get("href")

        # Address
        address = root.find(".//address")
        if address is not None and address.text:
            metadata["address"] = address.text.strip()

        return metadata

    def _extract_coordinate_info(self, root: Element) -> Dict[str, Any]:
        """Extract coordinate system information"""
        coord_info = {
            "altitude_modes_used": [],
            "has_3d_coordinates": False,
            "coordinate_precision": "unknown",
            "uses_tessellation": False,
        }

        # Check altitude modes
        altitude_modes = set()
        for mode in root.findall(".//altitudeMode"):
            if mode.text:
                altitude_modes.add(mode.text.strip())
        coord_info["altitude_modes_used"] = list(altitude_modes)

        # Check for 3D coordinates
        for coords in root.findall(".//coordinates"):
            if coords.text and coords.text.strip():
                # Check if any coordinate has altitude
                coord_parts = coords.text.strip().split()[0].split(",")
                if len(coord_parts) >= 3:
                    coord_info["has_3d_coordinates"] = True
                    break

        # Check tessellation
        coord_info["uses_tessellation"] = root.find('.//tessellate[.="1"]') is not None

        return coord_info

    def _calculate_max_depth(self, element: Element, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        if not list(element):
            return current_depth

        max_child_depth = current_depth
        for child in element:
            child_depth = self._calculate_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def _get_element_text(
        self,
        parent: Element,
        path: str,
        default: str = None,
        namespaces: Dict[str, str] = None,
    ) -> Optional[str]:
        """Safely get element text"""
        elem = parent.find(path, namespaces) if namespaces else parent.find(path)
        if elem is not None and elem.text:
            return elem.text.strip()
        return default

    def _calculate_quality_metrics(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics for the KML data"""
        metrics = {
            "completeness": 0.0,
            "organization": 0.0,
            "richness": 0.0,
            "precision": 0.0,
            "overall": 0.0,
        }

        # Completeness (based on names, descriptions, coordinates)
        quality_data = findings.get("data_quality", {})
        completeness_factors = [
            quality_data.get("has_names", 0),
            quality_data.get("has_descriptions", 0) * 0.5,  # Less weight
            quality_data.get("has_coordinates", 0),
            quality_data.get("uses_styles", 0) * 0.5,
        ]
        metrics["completeness"] = sum(completeness_factors) / 3.0

        # Organization (folders, schemas)
        if quality_data.get("organized_folders"):
            metrics["organization"] += 0.5
        if quality_data.get("uses_schemas"):
            metrics["organization"] += 0.5

        # Richness (variety of features, styles, extended data)
        structure = findings.get("structure", {})
        if structure.get("total_features", 0) > 10:
            metrics["richness"] += 0.3
        if len(findings.get("styles", [])) > 5:
            metrics["richness"] += 0.3
        if structure.get("has_extended_data"):
            metrics["richness"] += 0.4

        # Precision (coordinate precision)
        precision_map = {"high": 1.0, "medium": 0.7, "low": 0.4, "unknown": 0.5}
        metrics["precision"] = precision_map.get(
            quality_data.get("coordinate_precision", "unknown"), 0.5
        )

        # Overall
        metrics["overall"] = (
            metrics["completeness"] * 0.4
            + metrics["organization"] * 0.2
            + metrics["richness"] * 0.2
            + metrics["precision"] * 0.2
        )

        return metrics
