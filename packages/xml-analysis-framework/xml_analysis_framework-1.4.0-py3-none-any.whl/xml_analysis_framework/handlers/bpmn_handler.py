#!/usr/bin/env python3
"""
BPMN (Business Process Model and Notation) Handler

Analyzes BPMN 2.0 XML files to extract process definitions,
activities, gateways, events, and flows for process mining
and optimization.

FIXED VERSION: Replaced all local-name() XPath usage with ElementTree-compatible methods.
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


class BPMNHandler(XMLHandler):
    """Handler for BPMN 2.0 process definition files"""

    def _find_elements_by_local_name(
        self, root: Element, local_name: str
    ) -> List[Element]:
        """Find elements by local name, ignoring namespace prefixes"""
        elements = []
        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag == local_name:
                elements.append(elem)
        return elements

    def _find_element_by_local_name(
        self, root: Element, local_name: str
    ) -> Optional[Element]:
        """Find first element by local name, ignoring namespace prefixes"""
        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag == local_name:
                return elem
        return None

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for BPMN namespace
        if any(
            "bpmn" in uri.lower() or "omg.org/spec/BPMN" in uri
            for uri in namespaces.values()
        ):
            return True, 1.0

        # Check for BPMN root element
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if root_tag == "definitions":
            # Check for BPMN elements using namespace-aware search
            bpmn_elements = ["process", "startEvent", "endEvent", "task", "gateway"]
            found = sum(
                1
                for elem in bpmn_elements
                if self._find_elements_by_local_name(root, elem)
            )
            if found >= 2:
                return True, min(found * 0.2, 0.9)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Extract BPMN version
        version = "2.0"  # Default
        for uri in namespaces.values():
            if "BPMN/2" in uri:
                version = "2.0"
            elif "BPMN/1" in uri:
                version = "1.2"

        # Check if it's executable
        executable = root.get("isExecutable", "false") == "true"

        return DocumentTypeInfo(
            type_name="BPMN Process Definition",
            confidence=0.95,
            version=version,
            metadata={
                "standard": "OMG BPMN",
                "category": "business_process",
                "executable": executable,
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "processes": self._analyze_processes(root),
            "activities": self._analyze_activities(root),
            "gateways": self._analyze_gateways(root),
            "events": self._analyze_events(root),
            "flows": self._analyze_flows(root),
            "lanes": self._analyze_lanes(root),
            "data_objects": self._analyze_data_objects(root),
            "complexity_metrics": self._calculate_complexity_metrics(root),
        }

        recommendations = [
            "Analyze process bottlenecks and optimization opportunities",
            "Generate process documentation and training materials",
            "Validate against BPMN best practices",
            "Extract for process mining and analytics",
            "Monitor process execution patterns",
            "Identify automation candidates",
        ]

        ai_use_cases = [
            "Process optimization recommendations",
            "Bottleneck detection and analysis",
            "Process mining and discovery",
            "Compliance checking",
            "Resource allocation optimization",
            "Process simulation",
            "Automated documentation generation",
            "Process variant analysis",
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
                "processes": len(findings["processes"]),
                "activities": findings["activities"]["total"],
                "gateways": findings["gateways"]["total"],
                "events": findings["events"]["total"],
                "flows": len(findings["flows"]),
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_process_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "process_hierarchy": self._extract_process_hierarchy(root),
            "activity_sequences": self._extract_activity_sequences(root),
            "decision_points": self._extract_decision_points(root),
            "resource_assignments": self._extract_resource_assignments(root),
            "process_metrics": self._extract_process_metrics(root),
        }

    def _analyze_processes(self, root: Element) -> List[Dict[str, Any]]:
        """Analyze process definitions"""
        processes = []

        for process in self._find_elements_by_local_name(root, "process"):
            process_info = {
                "id": process.get("id"),
                "name": process.get("name"),
                "is_executable": process.get("isExecutable", "false") == "true",
                "process_type": process.get("processType", "None"),
                "is_closed": process.get("isClosed", "false") == "true",
                "elements": {
                    "activities": len(
                        self._find_elements_by_local_name(process, "task")
                        + self._find_elements_by_local_name(process, "subProcess")
                        + self._find_elements_by_local_name(process, "callActivity")
                    ),
                    "gateways": len(
                        self._find_elements_by_local_name(process, "exclusiveGateway")
                        + self._find_elements_by_local_name(process, "parallelGateway")
                        + self._find_elements_by_local_name(process, "inclusiveGateway")
                        + self._find_elements_by_local_name(
                            process, "eventBasedGateway"
                        )
                    ),
                    "events": len(
                        self._find_elements_by_local_name(process, "startEvent")
                        + self._find_elements_by_local_name(process, "endEvent")
                        + self._find_elements_by_local_name(
                            process, "intermediateThrowEvent"
                        )
                        + self._find_elements_by_local_name(
                            process, "intermediateCatchEvent"
                        )
                    ),
                },
            }

            # Extract documentation
            doc = self._find_element_by_local_name(process, "documentation")
            if doc is not None and doc.text:
                process_info["documentation"] = doc.text.strip()

            processes.append(process_info)

        return processes

    def _analyze_activities(self, root: Element) -> Dict[str, Any]:
        """Analyze all activities (tasks, subprocesses, etc.)"""
        activities = {
            "total": 0,
            "by_type": {},
            "manual_tasks": [],
            "service_tasks": [],
            "user_tasks": [],
            "script_tasks": [],
            "subprocesses": [],
            "call_activities": [],
        }

        # Analyze different task types
        task_types = [
            ("task", "generic"),
            ("userTask", "user"),
            ("serviceTask", "service"),
            ("scriptTask", "script"),
            ("manualTask", "manual"),
            ("businessRuleTask", "business_rule"),
            ("sendTask", "send"),
            ("receiveTask", "receive"),
        ]

        for task_elem, task_type in task_types:
            tasks = self._find_elements_by_local_name(root, task_elem)
            activities["by_type"][task_type] = len(tasks)
            activities["total"] += len(tasks)

            # Store specific task details
            for task in tasks:
                task_info = {
                    "id": task.get("id"),
                    "name": task.get("name"),
                    "type": task_type,
                }

                if task_type == "user":
                    activities["user_tasks"].append(task_info)
                elif task_type == "service":
                    activities["service_tasks"].append(task_info)
                elif task_type == "script":
                    activities["script_tasks"].append(task_info)
                elif task_type == "manual":
                    activities["manual_tasks"].append(task_info)

        # Analyze subprocesses
        for subprocess in self._find_elements_by_local_name(root, "subProcess"):
            subprocess_info = {
                "id": subprocess.get("id"),
                "name": subprocess.get("name"),
                "triggered_by_event": subprocess.get("triggeredByEvent", "false")
                == "true",
                "is_expanded": subprocess.get("isExpanded", "true") == "true",
                "child_activities": len(
                    self._find_elements_by_local_name(subprocess, "task")
                ),
            }
            activities["subprocesses"].append(subprocess_info)
            activities["total"] += 1

        # Analyze call activities
        for call_activity in self._find_elements_by_local_name(root, "callActivity"):
            call_info = {
                "id": call_activity.get("id"),
                "name": call_activity.get("name"),
                "called_element": call_activity.get("calledElement"),
            }
            activities["call_activities"].append(call_info)
            activities["total"] += 1

        return activities

    def _analyze_gateways(self, root: Element) -> Dict[str, Any]:
        """Analyze gateways (decision points)"""
        gateways = {
            "total": 0,
            "exclusive": [],
            "parallel": [],
            "inclusive": [],
            "event_based": [],
            "complex": [],
        }

        gateway_types = [
            ("exclusiveGateway", "exclusive"),
            ("parallelGateway", "parallel"),
            ("inclusiveGateway", "inclusive"),
            ("eventBasedGateway", "event_based"),
            ("complexGateway", "complex"),
        ]

        for gateway_elem, gateway_type in gateway_types:
            for gateway in self._find_elements_by_local_name(root, gateway_elem):
                gateway_info = {
                    "id": gateway.get("id"),
                    "name": gateway.get("name"),
                    "gateway_direction": gateway.get("gatewayDirection", "Unspecified"),
                    "incoming_flows": len(
                        self._find_elements_by_local_name(gateway, "incoming")
                    ),
                    "outgoing_flows": len(
                        self._find_elements_by_local_name(gateway, "outgoing")
                    ),
                }

                gateways[gateway_type].append(gateway_info)
                gateways["total"] += 1

        return gateways

    def _analyze_events(self, root: Element) -> Dict[str, Any]:
        """Analyze events (start, end, intermediate)"""
        events = {
            "total": 0,
            "start_events": [],
            "end_events": [],
            "intermediate_throw": [],
            "intermediate_catch": [],
            "boundary_events": [],
        }

        # Start events
        for event in self._find_elements_by_local_name(root, "startEvent"):
            event_info = {
                "id": event.get("id"),
                "name": event.get("name"),
                "is_interrupting": event.get("isInterrupting", "true") == "true",
                "event_type": self._determine_event_type(event),
            }
            events["start_events"].append(event_info)
            events["total"] += 1

        # End events
        for event in self._find_elements_by_local_name(root, "endEvent"):
            event_info = {
                "id": event.get("id"),
                "name": event.get("name"),
                "event_type": self._determine_event_type(event),
            }
            events["end_events"].append(event_info)
            events["total"] += 1

        # Intermediate throw events
        for event in self._find_elements_by_local_name(root, "intermediateThrowEvent"):
            event_info = {
                "id": event.get("id"),
                "name": event.get("name"),
                "event_type": self._determine_event_type(event),
            }
            events["intermediate_throw"].append(event_info)
            events["total"] += 1

        # Intermediate catch events
        for event in self._find_elements_by_local_name(root, "intermediateCatchEvent"):
            event_info = {
                "id": event.get("id"),
                "name": event.get("name"),
                "event_type": self._determine_event_type(event),
            }
            events["intermediate_catch"].append(event_info)
            events["total"] += 1

        # Boundary events
        for event in self._find_elements_by_local_name(root, "boundaryEvent"):
            event_info = {
                "id": event.get("id"),
                "name": event.get("name"),
                "attached_to": event.get("attachedToRef"),
                "cancel_activity": event.get("cancelActivity", "true") == "true",
                "event_type": self._determine_event_type(event),
            }
            events["boundary_events"].append(event_info)
            events["total"] += 1

        return events

    def _determine_event_type(self, event: Element) -> str:
        """Determine the specific type of event"""
        event_types = [
            "messageEventDefinition",
            "timerEventDefinition",
            "errorEventDefinition",
            "signalEventDefinition",
            "compensateEventDefinition",
            "conditionalEventDefinition",
            "escalationEventDefinition",
            "linkEventDefinition",
            "terminateEventDefinition",
        ]

        for event_type in event_types:
            if self._find_element_by_local_name(event, event_type) is not None:
                return event_type.replace("EventDefinition", "").lower()

        return "none"

    def _analyze_flows(self, root: Element) -> List[Dict[str, Any]]:
        """Analyze sequence flows"""
        flows = []

        for flow in self._find_elements_by_local_name(root, "sequenceFlow"):
            flow_info = {
                "id": flow.get("id"),
                "name": flow.get("name"),
                "source": flow.get("sourceRef"),
                "target": flow.get("targetRef"),
                "is_default": self._is_default_flow(root, flow),
                "condition": None,
            }

            # Extract condition expression
            condition = self._find_element_by_local_name(flow, "conditionExpression")
            if condition is not None and condition.text:
                flow_info["condition"] = condition.text.strip()

            flows.append(flow_info)

        return flows

    def _is_default_flow(self, root: Element, flow: Element) -> bool:
        """Check if a flow is marked as default"""
        flow_id = flow.get("id")

        # Check gateways for default flow references
        for elem in root.iter():
            if elem.get("default") == flow_id:
                return True

        return False

    def _analyze_lanes(self, root: Element) -> List[Dict[str, Any]]:
        """Analyze lanes and pools (organizational units)"""
        lanes = []

        for lane in self._find_elements_by_local_name(root, "lane"):
            lane_info = {
                "id": lane.get("id"),
                "name": lane.get("name"),
                "flow_node_refs": [],
            }

            # Get referenced flow nodes
            for ref in self._find_elements_by_local_name(lane, "flowNodeRef"):
                if ref.text:
                    lane_info["flow_node_refs"].append(ref.text)

            lanes.append(lane_info)

        return lanes

    def _analyze_data_objects(self, root: Element) -> List[Dict[str, Any]]:
        """Analyze data objects and data stores"""
        data_objects = []

        # Data objects
        for data_obj in self._find_elements_by_local_name(root, "dataObject"):
            data_objects.append(
                {
                    "id": data_obj.get("id"),
                    "name": data_obj.get("name"),
                    "type": "data_object",
                    "is_collection": data_obj.get("isCollection", "false") == "true",
                }
            )

        # Data object references
        for data_ref in self._find_elements_by_local_name(root, "dataObjectReference"):
            data_objects.append(
                {
                    "id": data_ref.get("id"),
                    "name": data_ref.get("name"),
                    "type": "data_object_reference",
                    "data_object_ref": data_ref.get("dataObjectRef"),
                }
            )

        # Data stores
        for data_store in self._find_elements_by_local_name(root, "dataStore"):
            data_objects.append(
                {
                    "id": data_store.get("id"),
                    "name": data_store.get("name"),
                    "type": "data_store",
                    "capacity": data_store.get("capacity"),
                    "is_unlimited": data_store.get("isUnlimited", "false") == "true",
                }
            )

        return data_objects

    def _calculate_complexity_metrics(self, root: Element) -> Dict[str, Any]:
        """Calculate process complexity metrics"""
        total_activities = len(self._find_elements_by_local_name(root, "task"))
        total_gateways = (
            len(self._find_elements_by_local_name(root, "exclusiveGateway"))
            + len(self._find_elements_by_local_name(root, "parallelGateway"))
            + len(self._find_elements_by_local_name(root, "inclusiveGateway"))
        )
        total_events = len(self._find_elements_by_local_name(root, "startEvent")) + len(
            self._find_elements_by_local_name(root, "endEvent")
        )
        total_flows = len(self._find_elements_by_local_name(root, "sequenceFlow"))

        # Calculate metrics
        metrics = {
            "cyclomatic_complexity": total_gateways + 1,  # Simplified McCabe complexity
            "activity_complexity": total_activities,
            "control_flow_complexity": total_gateways * 2 + total_events,
            "size_metrics": {
                "total_elements": total_activities + total_gateways + total_events,
                "total_flows": total_flows,
            },
            "complexity_score": 0.0,
        }

        # Calculate overall complexity score (0-1)
        if metrics["size_metrics"]["total_elements"] > 0:
            complexity_factors = [
                min(metrics["cyclomatic_complexity"] / 10, 1.0) * 0.4,
                min(metrics["activity_complexity"] / 30, 1.0) * 0.3,
                min(metrics["control_flow_complexity"] / 20, 1.0) * 0.3,
            ]
            metrics["complexity_score"] = sum(complexity_factors)

        return metrics

    def _extract_process_hierarchy(self, root: Element) -> Dict[str, Any]:
        """Extract process hierarchy and relationships"""
        hierarchy = {}

        for process in self._find_elements_by_local_name(root, "process"):
            process_id = process.get("id")
            hierarchy[process_id] = {
                "name": process.get("name"),
                "subprocesses": [],
                "call_activities": [],
            }

            # Find subprocesses
            for subprocess in self._find_elements_by_local_name(process, "subProcess"):
                hierarchy[process_id]["subprocesses"].append(
                    {"id": subprocess.get("id"), "name": subprocess.get("name")}
                )

            # Find call activities
            for call_activity in self._find_elements_by_local_name(
                process, "callActivity"
            ):
                hierarchy[process_id]["call_activities"].append(
                    {
                        "id": call_activity.get("id"),
                        "name": call_activity.get("name"),
                        "called_element": call_activity.get("calledElement"),
                    }
                )

        return hierarchy

    def _extract_activity_sequences(self, root: Element) -> List[List[str]]:
        """Extract common activity sequences"""
        sequences = []

        # Build flow graph
        flow_graph = {}
        for flow in self._find_elements_by_local_name(root, "sequenceFlow"):
            source = flow.get("sourceRef")
            target = flow.get("targetRef")
            if source not in flow_graph:
                flow_graph[source] = []
            flow_graph[source].append(target)

        # Find paths from start to end events
        start_events = [
            e.get("id") for e in self._find_elements_by_local_name(root, "startEvent")
        ]
        end_events = [
            e.get("id") for e in self._find_elements_by_local_name(root, "endEvent")
        ]

        # Simple path extraction (limited to prevent explosion)
        for start in start_events[:3]:  # Limit starts
            paths = self._find_paths(flow_graph, start, end_events, max_paths=5)
            sequences.extend(paths)

        return sequences[:10]  # Limit total sequences

    def _find_paths(
        self,
        graph: Dict[str, List[str]],
        start: str,
        ends: List[str],
        max_paths: int = 5,
    ) -> List[List[str]]:
        """Find paths in graph (simplified DFS)"""
        paths = []

        def dfs(node: str, path: List[str], visited: set):
            if len(paths) >= max_paths:
                return

            if node in ends:
                paths.append(path + [node])
                return

            if node in visited or len(path) > 20:  # Prevent infinite loops
                return

            visited.add(node)

            if node in graph:
                for next_node in graph[node]:
                    dfs(next_node, path + [node], visited.copy())

        dfs(start, [], set())
        return paths

    def _extract_decision_points(self, root: Element) -> List[Dict[str, Any]]:
        """Extract decision points and their conditions"""
        decision_points = []

        # Exclusive gateways with conditions
        for gateway in self._find_elements_by_local_name(root, "exclusiveGateway"):
            gateway_id = gateway.get("id")
            decision = {
                "id": gateway_id,
                "name": gateway.get("name"),
                "type": "exclusive",
                "conditions": [],
            }

            # Find outgoing flows with conditions
            for flow in self._find_elements_by_local_name(root, "sequenceFlow"):
                if flow.get("sourceRef") == gateway_id:
                    condition = self._find_element_by_local_name(
                        flow, "conditionExpression"
                    )
                    if condition is not None and condition.text:
                        decision["conditions"].append(
                            {
                                "flow_id": flow.get("id"),
                                "target": flow.get("targetRef"),
                                "condition": condition.text.strip(),
                            }
                        )

            if decision["conditions"]:
                decision_points.append(decision)

        return decision_points[:10]  # Limit

    def _extract_resource_assignments(self, root: Element) -> List[Dict[str, Any]]:
        """Extract resource assignments from lanes and tasks"""
        assignments = []

        # From lanes
        for lane in self._find_elements_by_local_name(root, "lane"):
            lane_name = lane.get("name")
            for ref in self._find_elements_by_local_name(lane, "flowNodeRef"):
                if ref.text:
                    assignments.append(
                        {
                            "resource": lane_name,
                            "activity": ref.text,
                            "type": "lane_assignment",
                        }
                    )

        # From user tasks with assignments
        for task in self._find_elements_by_local_name(root, "userTask"):
            # Check for resource role
            resource_role = self._find_element_by_local_name(task, "resourceRole")
            if resource_role is not None:
                resource_ref = self._find_element_by_local_name(
                    resource_role, "resourceRef"
                )
                if resource_ref is not None and resource_ref.text:
                    assignments.append(
                        {
                            "resource": resource_ref.text,
                            "activity": task.get("id"),
                            "type": "resource_role",
                        }
                    )

            # Check for performers
            performer = self._find_element_by_local_name(task, "performer")
            if performer is not None:
                resource_ref = self._find_element_by_local_name(
                    performer, "resourceRef"
                )
                if resource_ref is not None and resource_ref.text:
                    assignments.append(
                        {
                            "resource": resource_ref.text,
                            "activity": task.get("id"),
                            "type": "performer",
                        }
                    )

        return assignments[:20]  # Limit

    def _extract_process_metrics(self, root: Element) -> Dict[str, Any]:
        """Extract process metrics and KPIs"""
        metrics = {
            "process_count": len(self._find_elements_by_local_name(root, "process")),
            "avg_activities_per_process": 0.0,
            "gateway_distribution": {},
            "event_distribution": {},
            "automation_potential": 0.0,
        }

        # Calculate averages
        total_activities = 0
        processes = self._find_elements_by_local_name(root, "process")

        for process in processes:
            total_activities += len(self._find_elements_by_local_name(process, "task"))

        if processes:
            metrics["avg_activities_per_process"] = total_activities / len(processes)

        # Gateway distribution
        gateway_types = [
            "exclusiveGateway",
            "parallelGateway",
            "inclusiveGateway",
            "eventBasedGateway",
        ]
        for gw_type in gateway_types:
            count = len(self._find_elements_by_local_name(root, gw_type))
            if count > 0:
                metrics["gateway_distribution"][gw_type] = count

        # Event distribution
        event_types = [
            "startEvent",
            "endEvent",
            "intermediateThrowEvent",
            "intermediateCatchEvent",
            "boundaryEvent",
        ]
        for event_type in event_types:
            count = len(self._find_elements_by_local_name(root, event_type))
            if count > 0:
                metrics["event_distribution"][event_type] = count

        # Automation potential (ratio of service/script tasks to all tasks)
        service_tasks = len(self._find_elements_by_local_name(root, "serviceTask"))
        script_tasks = len(self._find_elements_by_local_name(root, "scriptTask"))
        total_tasks = len(self._find_elements_by_local_name(root, "task"))

        if total_tasks > 0:
            metrics["automation_potential"] = (
                service_tasks + script_tasks
            ) / total_tasks

        return metrics

    def _assess_process_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess process model quality"""
        # Completeness - all activities have names
        completeness = 0.0
        total_activities = findings["activities"]["total"]
        if total_activities > 0:
            # Estimate based on typical patterns
            completeness = 0.7  # Placeholder - would need detailed name checking

        # Correctness - proper start/end events
        correctness = 0.0
        has_start = len(findings["events"]["start_events"]) > 0
        has_end = len(findings["events"]["end_events"]) > 0
        if has_start and has_end:
            correctness = 1.0
        elif has_start or has_end:
            correctness = 0.5

        # Complexity management
        complexity_score = findings["complexity_metrics"]["complexity_score"]
        complexity_quality = max(
            0, 1.0 - complexity_score
        )  # Lower complexity is better

        # Best practices
        best_practices = 0.0

        # Check for lane usage (organization)
        if findings["lanes"]:
            best_practices += 0.25

        # Check for proper gateway usage
        if findings["gateways"]["total"] > 0:
            # Prefer exclusive gateways over complex ones
            exclusive_ratio = (
                len(findings["gateways"]["exclusive"]) / findings["gateways"]["total"]
            )
            best_practices += exclusive_ratio * 0.25

        # Check for documentation
        doc_count = sum(1 for p in findings["processes"] if "documentation" in p)
        if doc_count > 0:
            best_practices += 0.25

        # Check for proper event usage
        if findings["events"]["total"] >= 2:  # At least start and end
            best_practices += 0.25

        return {
            "completeness": completeness,
            "correctness": correctness,
            "complexity_management": complexity_quality,
            "best_practices": min(best_practices, 1.0),
            "overall": (
                completeness + correctness + complexity_quality + best_practices
            )
            / 4,
        }
