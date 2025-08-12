#!/usr/bin/env python3
"""
GPX (GPS Exchange Format) Handler

Analyzes GPX files containing GPS tracking data, routes, and waypoints.
Supports GPX 1.0 and 1.1 formats with comprehensive track analysis,
elevation profiling, and fitness metrics calculation.
"""

import math
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base import XMLHandler, DocumentTypeInfo, SpecializedAnalysis  # noqa: E402


class GPXHandler(XMLHandler):
    """Handler for GPX GPS tracking files"""

    GPX_NAMESPACE_10 = "http://www.topografix.com/GPX/1/0"
    GPX_NAMESPACE_11 = "http://www.topografix.com/GPX/1/1"

    def _get_namespace(self, root: Element) -> str:
        """Extract namespace prefix from root element"""
        if "}" in root.tag:
            return root.tag.split("}")[0] + "}"
        return ""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for GPX namespace
        if any("topografix.com/GPX" in uri for uri in namespaces.values()):
            return True, 1.0

        # Check root element
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if root_tag.lower() == "gpx":
            # Check for GPX-specific elements
            ns = self._get_namespace(root)
            gpx_elements = ["wpt", "rte", "trk", "trkpt", "rtept"]
            found = sum(
                1 for elem in gpx_elements if root.find(f".//{ns}{elem}") is not None
            )
            if found >= 1:
                return True, min(found * 0.3, 0.9)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Detect GPX version
        version = root.get("version", "1.1")

        # Detect GPX content type
        ns = self._get_namespace(root)
        content_type = "mixed"

        has_waypoints = root.find(f".//{ns}wpt") is not None
        has_routes = root.find(f".//{ns}rte") is not None
        has_tracks = root.find(f".//{ns}trk") is not None

        if has_tracks and not has_waypoints and not has_routes:
            content_type = "track_log"
        elif has_routes and not has_tracks and not has_waypoints:
            content_type = "route_plan"
        elif has_waypoints and not has_tracks and not has_routes:
            content_type = "waypoint_collection"

        return DocumentTypeInfo(
            type_name="GPX GPS Data",
            confidence=0.95,
            version=version,
            metadata={
                "standard": "GPX (GPS Exchange Format)",
                "category": "gps_tracking",
                "content_type": content_type,
                "application": "GPS/Navigation",
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "metadata": self._analyze_metadata(root),
            "waypoints": self._analyze_waypoints(root),
            "routes": self._analyze_routes(root),
            "tracks": self._analyze_tracks(root),
            "statistics": self._calculate_statistics(root),
            "elevation_profile": self._analyze_elevation(root),
            "temporal_analysis": self._analyze_temporal_data(root),
            "geographic_bounds": self._calculate_bounds(root),
        }

        recommendations = [
            "Visualize GPS tracks on interactive maps",
            "Calculate fitness metrics and performance statistics",
            "Analyze elevation gain/loss and terrain difficulty",
            "Extract route planning and navigation data",
            "Compare tracks for performance improvement",
            "Generate heatmaps and activity patterns",
            "Export to other GPS formats (KML, GeoJSON)",
            "Validate GPS data quality and accuracy",
        ]

        ai_use_cases = [
            "Route optimization and path planning",
            "Activity recognition and classification",
            "Anomaly detection in GPS tracks",
            "Fitness performance analysis",
            "Terrain difficulty assessment",
            "Travel pattern recognition",
            "Location clustering and POI discovery",
            "Speed and pace analysis",
            "Elevation profile optimization",
            "GPS data quality assessment",
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
                "waypoints": findings["waypoints"]["count"],
                "routes": findings["routes"]["count"],
                "tracks": findings["tracks"]["count"],
                "track_points": findings["statistics"]["total_points"],
                "time_span_hours": findings["temporal_analysis"].get(
                    "duration_hours", 0
                ),
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_data_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "track_data": self._extract_track_coordinates(root),
            "waypoint_data": self._extract_waypoint_data(root),
            "route_data": self._extract_route_data(root),
            "activity_summary": self._extract_activity_summary(root),
            "device_info": self._extract_device_info(root),
        }

    def _analyze_metadata(self, root: Element) -> Dict[str, Any]:
        """Analyze GPX metadata"""
        ns = self._get_namespace(root)
        metadata = {}

        # Basic metadata
        metadata_elem = root.find(f"{ns}metadata")
        if metadata_elem is not None:
            metadata.update(
                {
                    "name": self._get_element_text(metadata_elem, f"{ns}name"),
                    "description": self._get_element_text(metadata_elem, f"{ns}desc"),
                    "author": self._extract_author_info(metadata_elem, ns),
                    "copyright": self._extract_copyright_info(metadata_elem, ns),
                    "link": self._extract_link_info(metadata_elem, ns),
                    "time": self._get_element_text(metadata_elem, f"{ns}time"),
                    "keywords": self._get_element_text(metadata_elem, f"{ns}keywords"),
                }
            )

            # Bounds
            bounds_elem = metadata_elem.find(f"{ns}bounds")
            if bounds_elem is not None:
                metadata["bounds"] = {
                    "minlat": float(bounds_elem.get("minlat", 0)),
                    "minlon": float(bounds_elem.get("minlon", 0)),
                    "maxlat": float(bounds_elem.get("maxlat", 0)),
                    "maxlon": float(bounds_elem.get("maxlon", 0)),
                }

        # Root-level metadata
        metadata.update(
            {
                "version": root.get("version"),
                "creator": root.get("creator"),
                "xmlns": root.get("xmlns"),
            }
        )

        return metadata

    def _analyze_waypoints(self, root: Element) -> Dict[str, Any]:
        """Analyze waypoints"""
        ns = self._get_namespace(root)
        waypoints = {
            "count": 0,
            "points": [],
            "elevation_range": {"min": float("inf"), "max": float("-inf")},
            "categories": {},
        }

        for wpt in root.findall(f"{ns}wpt")[:200]:  # Limit for performance
            waypoint = {
                "lat": float(wpt.get("lat", 0)),
                "lon": float(wpt.get("lon", 0)),
                "name": self._get_element_text(wpt, f"{ns}name"),
                "description": self._get_element_text(wpt, f"{ns}desc"),
                "elevation": self._get_element_float(wpt, f"{ns}ele"),
                "time": self._get_element_text(wpt, f"{ns}time"),
                "symbol": self._get_element_text(wpt, f"{ns}sym"),
                "type": self._get_element_text(wpt, f"{ns}type"),
                "comment": self._get_element_text(wpt, f"{ns}cmt"),
            }

            # Track elevation range
            if waypoint["elevation"] is not None:
                waypoints["elevation_range"]["min"] = min(
                    waypoints["elevation_range"]["min"], waypoint["elevation"]
                )
                waypoints["elevation_range"]["max"] = max(
                    waypoints["elevation_range"]["max"], waypoint["elevation"]
                )

            # Categorize by type/symbol
            category = waypoint.get("type") or waypoint.get("symbol") or "other"
            waypoints["categories"][category] = (
                waypoints["categories"].get(category, 0) + 1
            )

            waypoints["points"].append(waypoint)

        waypoints["count"] = len(waypoints["points"])

        # Handle case where no elevation data
        if waypoints["elevation_range"]["min"] == float("inf"):
            waypoints["elevation_range"] = {"min": None, "max": None}

        return waypoints

    def _analyze_routes(self, root: Element) -> Dict[str, Any]:
        """Analyze planned routes"""
        ns = self._get_namespace(root)
        routes = {"count": 0, "routes": []}

        for rte in root.findall(f"{ns}rte")[:50]:  # Limit for performance
            route = {
                "name": self._get_element_text(rte, f"{ns}name"),
                "description": self._get_element_text(rte, f"{ns}desc"),
                "comment": self._get_element_text(rte, f"{ns}cmt"),
                "source": self._get_element_text(rte, f"{ns}src"),
                "number": self._get_element_int(rte, f"{ns}number"),
                "type": self._get_element_text(rte, f"{ns}type"),
                "points": [],
            }

            # Analyze route points
            for rtept in rte.findall(f"{ns}rtept")[:1000]:  # Limit points
                point = {
                    "lat": float(rtept.get("lat", 0)),
                    "lon": float(rtept.get("lon", 0)),
                    "elevation": self._get_element_float(rtept, f"{ns}ele"),
                    "name": self._get_element_text(rtept, f"{ns}name"),
                    "description": self._get_element_text(rtept, f"{ns}desc"),
                }
                route["points"].append(point)

            route["point_count"] = len(route["points"])
            route["distance_km"] = (
                self._calculate_distance(route["points"]) if route["points"] else 0
            )

            routes["routes"].append(route)

        routes["count"] = len(routes["routes"])
        return routes

    def _analyze_tracks(self, root: Element) -> Dict[str, Any]:
        """Analyze GPS tracks"""
        ns = self._get_namespace(root)
        tracks = {"count": 0, "tracks": []}

        for trk in root.findall(f"{ns}trk")[:50]:  # Limit for performance
            track = {
                "name": self._get_element_text(trk, f"{ns}name"),
                "description": self._get_element_text(trk, f"{ns}desc"),
                "comment": self._get_element_text(trk, f"{ns}cmt"),
                "source": self._get_element_text(trk, f"{ns}src"),
                "number": self._get_element_int(trk, f"{ns}number"),
                "type": self._get_element_text(trk, f"{ns}type"),
                "segments": [],
            }

            # Analyze track segments
            for trkseg in trk.findall(f"{ns}trkseg"):
                segment = {"points": []}

                for trkpt in trkseg.findall(f"{ns}trkpt")[
                    :5000
                ]:  # Limit points per segment
                    point = {
                        "lat": float(trkpt.get("lat", 0)),
                        "lon": float(trkpt.get("lon", 0)),
                        "elevation": self._get_element_float(trkpt, f"{ns}ele"),
                        "time": self._get_element_text(trkpt, f"{ns}time"),
                        "speed": self._get_element_float(trkpt, f"{ns}speed"),
                        "course": self._get_element_float(trkpt, f"{ns}course"),
                        "hdop": self._get_element_float(trkpt, f"{ns}hdop"),
                        "vdop": self._get_element_float(trkpt, f"{ns}vdop"),
                        "pdop": self._get_element_float(trkpt, f"{ns}pdop"),
                    }
                    segment["points"].append(point)

                segment["point_count"] = len(segment["points"])
                segment["distance_km"] = (
                    self._calculate_distance(segment["points"])
                    if segment["points"]
                    else 0
                )
                segment["duration_minutes"] = (
                    self._calculate_duration(segment["points"])
                    if segment["points"]
                    else 0
                )

                track["segments"].append(segment)

            track["total_points"] = sum(seg["point_count"] for seg in track["segments"])
            track["total_distance_km"] = sum(
                seg["distance_km"] for seg in track["segments"]
            )
            track["total_duration_minutes"] = sum(
                seg["duration_minutes"] for seg in track["segments"]
            )

            tracks["tracks"].append(track)

        tracks["count"] = len(tracks["tracks"])
        return tracks

    def _calculate_statistics(self, root: Element) -> Dict[str, Any]:
        """Calculate comprehensive GPS statistics"""
        ns = self._get_namespace(root)
        stats = {
            "total_points": 0,
            "total_distance_km": 0.0,
            "total_duration_hours": 0.0,
            "max_speed_kmh": 0.0,
            "avg_speed_kmh": 0.0,
            "elevation_gain_m": 0.0,
            "elevation_loss_m": 0.0,
            "max_elevation_m": float("-inf"),
            "min_elevation_m": float("inf"),
        }

        all_points = []

        # Collect all track points
        for trk in root.findall(f"{ns}trk"):
            for trkseg in trk.findall(f"{ns}trkseg"):
                for trkpt in trkseg.findall(f"{ns}trkpt"):
                    point_data = {
                        "lat": float(trkpt.get("lat", 0)),
                        "lon": float(trkpt.get("lon", 0)),
                        "elevation": self._get_element_float(trkpt, f"{ns}ele"),
                        "time": self._get_element_text(trkpt, f"{ns}time"),
                        "speed": self._get_element_float(trkpt, f"{ns}speed"),
                    }
                    all_points.append(point_data)

        if not all_points:
            return stats

        stats["total_points"] = len(all_points)
        stats["total_distance_km"] = self._calculate_distance(all_points)
        stats["total_duration_hours"] = (
            self._calculate_duration(all_points) / 60.0
        )  # Convert to hours

        # Speed analysis
        speeds = [p["speed"] for p in all_points if p["speed"] is not None]
        if speeds:
            stats["max_speed_kmh"] = max(speeds) * 3.6  # Convert m/s to km/h

        if stats["total_duration_hours"] > 0:
            stats["avg_speed_kmh"] = (
                stats["total_distance_km"] / stats["total_duration_hours"]
            )

        # Elevation analysis
        elevations = [p["elevation"] for p in all_points if p["elevation"] is not None]
        if elevations:
            stats["max_elevation_m"] = max(elevations)
            stats["min_elevation_m"] = min(elevations)

            # Calculate elevation gain/loss
            gain, loss = self._calculate_elevation_change(elevations)
            stats["elevation_gain_m"] = gain
            stats["elevation_loss_m"] = loss
        else:
            stats["max_elevation_m"] = None
            stats["min_elevation_m"] = None

        return stats

    def _analyze_elevation(self, root: Element) -> Dict[str, Any]:
        """Analyze elevation profile"""
        ns = self._get_namespace(root)
        elevation_data = {
            "has_elevation": False,
            "profile_points": [],
            "statistics": {},
            "gradient_analysis": {},
        }

        # Collect elevation points from tracks
        all_points = []
        for trk in root.findall(f"{ns}trk"):
            for trkseg in trk.findall(f"{ns}trkseg"):
                for trkpt in trkseg.findall(f"{ns}trkpt"):
                    elevation = self._get_element_float(trkpt, f"{ns}ele")
                    if elevation is not None:
                        all_points.append(
                            {
                                "lat": float(trkpt.get("lat", 0)),
                                "lon": float(trkpt.get("lon", 0)),
                                "elevation": elevation,
                                "distance": 0,  # Will be calculated
                            }
                        )

        if not all_points:
            return elevation_data

        elevation_data["has_elevation"] = True

        # Calculate distances
        cumulative_distance = 0
        for i, point in enumerate(all_points):
            if i > 0:
                dist = self._haversine_distance(
                    all_points[i - 1]["lat"],
                    all_points[i - 1]["lon"],
                    point["lat"],
                    point["lon"],
                )
                cumulative_distance += dist
            point["distance"] = cumulative_distance

        # Sample points for profile (reduce density for large tracks)
        sample_rate = max(1, len(all_points) // 500)  # Max 500 points
        elevation_data["profile_points"] = all_points[::sample_rate]

        # Calculate statistics
        elevations = [p["elevation"] for p in all_points]
        if elevations:
            elevation_data["statistics"] = {
                "min": min(elevations),
                "max": max(elevations),
                "range": max(elevations) - min(elevations),
                "mean": sum(elevations) / len(elevations),
                "gain": 0,
                "loss": 0,
            }

            # Calculate gain/loss
            gain, loss = self._calculate_elevation_change(elevations)
            elevation_data["statistics"]["gain"] = gain
            elevation_data["statistics"]["loss"] = loss

        # Gradient analysis
        if len(all_points) > 1:
            gradients = []
            for i in range(1, len(all_points)):
                distance_diff = (
                    all_points[i]["distance"] - all_points[i - 1]["distance"]
                )
                elevation_diff = (
                    all_points[i]["elevation"] - all_points[i - 1]["elevation"]
                )
                if distance_diff > 0:
                    gradient = (
                        elevation_diff / (distance_diff * 1000)
                    ) * 100  # Percentage
                    gradients.append(gradient)

            if gradients:
                elevation_data["gradient_analysis"] = {
                    "max_gradient": max(gradients),
                    "min_gradient": min(gradients),
                    "avg_gradient": sum(gradients) / len(gradients),
                    "steep_sections": len(
                        [g for g in gradients if abs(g) > 10]
                    ),  # >10% grade
                }

        return elevation_data

    def _analyze_temporal_data(self, root: Element) -> Dict[str, Any]:
        """Analyze temporal aspects of GPS data"""
        ns = self._get_namespace(root)
        temporal = {
            "has_timestamps": False,
            "start_time": None,
            "end_time": None,
            "duration_hours": 0,
            "time_gaps": [],
            "activity_periods": [],
        }

        # Collect timestamps from tracks
        timestamps = []
        for trk in root.findall(f"{ns}trk"):
            for trkseg in trk.findall(f"{ns}trkseg"):
                for trkpt in trkseg.findall(f"{ns}trkpt"):
                    time_str = self._get_element_text(trkpt, f"{ns}time")
                    if time_str:
                        try:
                            # Parse ISO format timestamp
                            timestamp = datetime.fromisoformat(
                                time_str.replace("Z", "+00:00")
                            )
                            timestamps.append(timestamp)
                        except ValueError:
                            continue

        if not timestamps:
            return temporal

        temporal["has_timestamps"] = True
        timestamps.sort()

        temporal["start_time"] = timestamps[0].isoformat()
        temporal["end_time"] = timestamps[-1].isoformat()
        temporal["duration_hours"] = (
            timestamps[-1] - timestamps[0]
        ).total_seconds() / 3600

        # Detect time gaps (>5 minutes between points)
        gaps = []
        for i in range(1, len(timestamps)):
            gap_seconds = (timestamps[i] - timestamps[i - 1]).total_seconds()
            if gap_seconds > 300:  # 5 minutes
                gaps.append(
                    {
                        "start": timestamps[i - 1].isoformat(),
                        "end": timestamps[i].isoformat(),
                        "duration_minutes": gap_seconds / 60,
                    }
                )

        temporal["time_gaps"] = gaps[:20]  # Limit

        return temporal

    def _calculate_bounds(self, root: Element) -> Dict[str, float]:
        """Calculate geographic bounds"""
        ns = self._get_namespace(root)
        bounds = {"north": -90.0, "south": 90.0, "east": -180.0, "west": 180.0}

        found_points = False

        # Check all points (waypoints, route points, track points)
        for element_type in ["wpt", "rtept", "trkpt"]:
            for point in root.findall(f".//{ns}{element_type}"):
                lat = float(point.get("lat", 0))
                lon = float(point.get("lon", 0))

                bounds["north"] = max(bounds["north"], lat)
                bounds["south"] = min(bounds["south"], lat)
                bounds["east"] = max(bounds["east"], lon)
                bounds["west"] = min(bounds["west"], lon)
                found_points = True

        if not found_points:
            return {"north": 0, "south": 0, "east": 0, "west": 0}

        return bounds

    def _extract_track_coordinates(self, root: Element) -> List[Dict[str, Any]]:
        """Extract track coordinates for analysis"""
        ns = self._get_namespace(root)
        tracks = []

        for trk in root.findall(f"{ns}trk")[:10]:  # Limit tracks
            track_data = {
                "name": self._get_element_text(trk, f"{ns}name"),
                "segments": [],
            }

            for trkseg in trk.findall(f"{ns}trkseg"):
                segment_points = []
                for trkpt in trkseg.findall(f"{ns}trkpt")[:1000]:  # Limit points
                    point = {
                        "lat": float(trkpt.get("lat", 0)),
                        "lon": float(trkpt.get("lon", 0)),
                        "elevation": self._get_element_float(trkpt, f"{ns}ele"),
                        "time": self._get_element_text(trkpt, f"{ns}time"),
                    }
                    segment_points.append(point)

                if segment_points:
                    track_data["segments"].append(segment_points)

            if track_data["segments"]:
                tracks.append(track_data)

        return tracks

    def _extract_waypoint_data(self, root: Element) -> List[Dict[str, Any]]:
        """Extract waypoint data"""
        ns = self._get_namespace(root)
        waypoints = []

        for wpt in root.findall(f"{ns}wpt")[:100]:  # Limit waypoints
            waypoint = {
                "lat": float(wpt.get("lat", 0)),
                "lon": float(wpt.get("lon", 0)),
                "name": self._get_element_text(wpt, f"{ns}name"),
                "description": self._get_element_text(wpt, f"{ns}desc"),
                "elevation": self._get_element_float(wpt, f"{ns}ele"),
                "symbol": self._get_element_text(wpt, f"{ns}sym"),
                "type": self._get_element_text(wpt, f"{ns}type"),
            }
            waypoints.append(waypoint)

        return waypoints

    def _extract_route_data(self, root: Element) -> List[Dict[str, Any]]:
        """Extract route data"""
        ns = self._get_namespace(root)
        routes = []

        for rte in root.findall(f"{ns}rte")[:10]:  # Limit routes
            route_points = []
            for rtept in rte.findall(f"{ns}rtept")[:500]:  # Limit points
                point = {
                    "lat": float(rtept.get("lat", 0)),
                    "lon": float(rtept.get("lon", 0)),
                    "elevation": self._get_element_float(rtept, f"{ns}ele"),
                    "name": self._get_element_text(rtept, f"{ns}name"),
                }
                route_points.append(point)

            if route_points:
                route = {
                    "name": self._get_element_text(rte, f"{ns}name"),
                    "points": route_points,
                }
                routes.append(route)

        return routes

    def _extract_activity_summary(self, root: Element) -> Dict[str, Any]:
        """Extract activity summary"""
        metadata = self._analyze_metadata(root)
        stats = self._calculate_statistics(root)

        return {
            "activity_name": metadata.get("name"),
            "activity_type": "GPS Track",
            "total_distance_km": stats["total_distance_km"],
            "total_duration_hours": stats["total_duration_hours"],
            "average_speed_kmh": stats["avg_speed_kmh"],
            "elevation_gain_m": stats["elevation_gain_m"],
            "creator": metadata.get("creator"),
        }

    def _extract_device_info(self, root: Element) -> Dict[str, Any]:
        """Extract device and software information"""
        return {
            "creator": root.get("creator"),
            "version": root.get("version"),
            "namespace": self._get_namespace(root).strip("{}"),
        }

    def _assess_data_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess GPX data quality"""
        metrics = {
            "completeness": 0.0,
            "temporal_consistency": 0.0,
            "spatial_accuracy": 0.0,
            "metadata_richness": 0.0,
            "overall": 0.0,
        }

        # Completeness (based on elevation and time data)
        stats = findings["statistics"]
        elevation_data = findings["elevation_profile"]
        temporal_data = findings["temporal_analysis"]

        completeness_factors = []
        if elevation_data["has_elevation"]:
            completeness_factors.append(1.0)
        else:
            completeness_factors.append(0.3)

        if temporal_data["has_timestamps"]:
            completeness_factors.append(1.0)
        else:
            completeness_factors.append(0.3)

        if stats["total_points"] > 100:
            completeness_factors.append(1.0)
        elif stats["total_points"] > 10:
            completeness_factors.append(0.7)
        else:
            completeness_factors.append(0.3)

        metrics["completeness"] = sum(completeness_factors) / len(completeness_factors)

        # Temporal consistency
        if temporal_data["has_timestamps"]:
            gap_penalty = min(len(temporal_data["time_gaps"]) * 0.1, 0.5)
            metrics["temporal_consistency"] = max(0.5, 1.0 - gap_penalty)
        else:
            metrics["temporal_consistency"] = 0.3

        # Spatial accuracy (rough estimate based on point density)
        if stats["total_distance_km"] > 0 and stats["total_points"] > 0:
            points_per_km = stats["total_points"] / stats["total_distance_km"]
            if points_per_km > 100:  # Very dense
                metrics["spatial_accuracy"] = 1.0
            elif points_per_km > 20:  # Good density
                metrics["spatial_accuracy"] = 0.8
            elif points_per_km > 5:  # Reasonable density
                metrics["spatial_accuracy"] = 0.6
            else:  # Sparse
                metrics["spatial_accuracy"] = 0.4
        else:
            metrics["spatial_accuracy"] = 0.5

        # Metadata richness
        metadata = findings["metadata"]
        richness_score = 0
        if metadata.get("name"):
            richness_score += 0.25
        if metadata.get("description"):
            richness_score += 0.25
        if metadata.get("creator"):
            richness_score += 0.25
        if metadata.get("bounds"):
            richness_score += 0.25

        metrics["metadata_richness"] = richness_score

        # Overall
        metrics["overall"] = (
            metrics["completeness"] * 0.3
            + metrics["temporal_consistency"] * 0.25
            + metrics["spatial_accuracy"] * 0.25
            + metrics["metadata_richness"] * 0.2
        )

        return metrics

    # Utility methods
    def _extract_author_info(
        self, metadata_elem: Element, ns: str
    ) -> Optional[Dict[str, str]]:
        """Extract author information"""
        author_elem = metadata_elem.find(f"{ns}author")
        if author_elem is not None:
            return {
                "name": self._get_element_text(author_elem, f"{ns}name"),
                "email": self._get_element_text(author_elem, f"{ns}email"),
            }
        return None

    def _extract_copyright_info(
        self, metadata_elem: Element, ns: str
    ) -> Optional[Dict[str, str]]:
        """Extract copyright information"""
        copyright_elem = metadata_elem.find(f"{ns}copyright")
        if copyright_elem is not None:
            return {
                "author": copyright_elem.get("author"),
                "year": self._get_element_text(copyright_elem, f"{ns}year"),
                "license": self._get_element_text(copyright_elem, f"{ns}license"),
            }
        return None

    def _extract_link_info(
        self, metadata_elem: Element, ns: str
    ) -> Optional[Dict[str, str]]:
        """Extract link information"""
        link_elem = metadata_elem.find(f"{ns}link")
        if link_elem is not None:
            return {
                "href": link_elem.get("href"),
                "text": self._get_element_text(link_elem, f"{ns}text"),
                "type": self._get_element_text(link_elem, f"{ns}type"),
            }
        return None

    def _calculate_distance(self, points: List[Dict[str, Any]]) -> float:
        """Calculate total distance in kilometers"""
        if len(points) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(1, len(points)):
            dist = self._haversine_distance(
                points[i - 1]["lat"],
                points[i - 1]["lon"],
                points[i]["lat"],
                points[i]["lon"],
            )
            total_distance += dist

        return total_distance

    def _calculate_duration(self, points: List[Dict[str, Any]]) -> float:
        """Calculate duration in minutes"""
        timestamps = [p.get("time") for p in points if p.get("time")]
        if len(timestamps) < 2:
            return 0.0

        try:
            start = datetime.fromisoformat(timestamps[0].replace("Z", "+00:00"))
            end = datetime.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
            return (end - start).total_seconds() / 60.0
        except (ValueError, IndexError):
            return 0.0

    def _calculate_elevation_change(
        self, elevations: List[float]
    ) -> Tuple[float, float]:
        """Calculate elevation gain and loss"""
        if len(elevations) < 2:
            return 0.0, 0.0

        gain = 0.0
        loss = 0.0

        for i in range(1, len(elevations)):
            diff = elevations[i] - elevations[i - 1]
            if diff > 0:
                gain += diff
            else:
                loss += abs(diff)

        return gain, loss

    def _haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula (km)"""
        R = 6371.0  # Earth radius in kilometers

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _get_element_text(self, parent: Element, path: str) -> Optional[str]:
        """Safely get element text"""
        elem = parent.find(path)
        if elem is not None and elem.text:
            return elem.text.strip()
        return None

    def _get_element_float(self, parent: Element, path: str) -> Optional[float]:
        """Safely get element as float"""
        text = self._get_element_text(parent, path)
        if text:
            try:
                return float(text)
            except ValueError:
                pass
        return None

    def _get_element_int(self, parent: Element, path: str) -> Optional[int]:
        """Safely get element as int"""
        text = self._get_element_text(parent, path)
        if text:
            try:
                return int(text)
            except ValueError:
                pass
        return None
