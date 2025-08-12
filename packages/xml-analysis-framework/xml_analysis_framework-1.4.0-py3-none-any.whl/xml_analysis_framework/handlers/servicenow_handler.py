#!/usr/bin/env python3
"""
ServiceNow Handler

Analyzes ServiceNow export XML files containing incidents, problems, changes,
and other ITSM records. Handles the complex structure of ServiceNow exports
including journal fields, attachments, and relationships.

Key features:
- Incident ticket analysis with full conversation history
- SLA and escalation tracking
- Assignment and workflow analysis
- Attachment metadata extraction
- Support for custom fields (u_ prefix)
"""

import re
import sys
import os
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base import XMLHandler, DocumentTypeInfo, SpecializedAnalysis  # noqa: E402


class ServiceNowHandler(XMLHandler):
    """Handler for ServiceNow export XML documents"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        """Check if this is a ServiceNow export file"""
        score = 0.0

        # Check root element
        if root.tag == "unload":
            score += 0.4

        # Check for ServiceNow-specific elements
        if root.find(".//incident") is not None:
            score += 0.3
        if root.find(".//sys_journal_field") is not None:
            score += 0.2
        if root.find(".//sys_attachment") is not None:
            score += 0.1

        # Check for ServiceNow-specific attributes
        for elem in root.iter():
            if elem.get("display_value") is not None:
                score += 0.1
                break

        return score > 0.5, min(score, 1.0)

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        """Detect ServiceNow document type and extract metadata"""
        # Identify primary record type
        record_types = []
        for child in root:
            if child.tag not in [
                "sys_journal_field",
                "sys_attachment",
                "sys_attachment_doc",
            ]:
                record_types.append(child.tag)

        primary_type = record_types[0] if record_types else "unknown"

        # Extract system info
        metadata = {
            "primary_record_type": primary_type,
            "total_records": len(record_types),
            "has_journal_entries": root.find(".//sys_journal_field") is not None,
            "has_attachments": root.find(".//sys_attachment") is not None,
        }

        return DocumentTypeInfo(
            type_name=f"ServiceNow {primary_type.title()}",
            confidence=0.95,
            metadata=metadata,
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        """Perform comprehensive analysis of ServiceNow data"""
        findings = {}

        # Analyze primary record (incident, problem, change, etc.)
        primary_record = self._get_primary_record(root)
        if primary_record is not None:
            findings.update(self._analyze_primary_record(primary_record))

        # Analyze journal entries (comments/work notes)
        journal_analysis = self._analyze_journal_entries(root)
        findings["journal_analysis"] = journal_analysis

        # Analyze attachments
        attachment_analysis = self._analyze_attachments(root)
        findings["attachment_analysis"] = attachment_analysis

        # Extract SLA and performance metrics
        findings["sla_metrics"] = self._extract_sla_metrics(primary_record)

        # Assignment and workflow analysis
        findings["workflow_analysis"] = self._analyze_workflow(primary_record, root)

        recommendations = self._generate_recommendations(findings)
        ai_use_cases = self._identify_ai_use_cases(findings)

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
            data_inventory=self._create_data_inventory(root),
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._calculate_quality_metrics(root),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        """Extract structured data from ServiceNow export"""
        primary_record = self._get_primary_record(root)

        data = {
            "ticket_info": self._extract_ticket_info(primary_record),
            "conversation_thread": self._extract_conversation_thread(root),
            "attachments": self._extract_attachment_info(root),
            "timeline": self._extract_timeline(primary_record, root),
            "people_involved": self._extract_people(primary_record, root),
        }

        return data

    def _get_primary_record(self, root: Element) -> Optional[Element]:
        """Get the primary record element (incident, problem, etc.)"""
        for child in root:
            if child.tag not in [
                "sys_journal_field",
                "sys_attachment",
                "sys_attachment_doc",
            ]:
                return child
        return None

    def _analyze_primary_record(self, record: Element) -> Dict[str, Any]:
        """Analyze the primary ServiceNow record"""
        analysis = {
            "record_type": record.tag,
            "record_action": record.get("action", "unknown"),
            "state": self._get_field_value(record, "state"),
            "priority": self._get_field_value(record, "priority"),
            "impact": self._get_field_value(record, "impact"),
            "urgency": self._get_field_value(record, "urgency"),
            "category": self._get_field_value(record, "category"),
            "subcategory": self._get_field_value(record, "subcategory"),
            "assignment_group": self._get_field_display_value(
                record, "assignment_group"
            ),
            "assigned_to": self._get_field_display_value(record, "assigned_to"),
            "short_description": self._get_field_value(record, "short_description"),
            "close_code": self._get_field_value(record, "close_code"),
            "resolution_time": self._calculate_resolution_time(record),
        }

        # Add custom field summary
        custom_fields = self._extract_custom_fields(record)
        if custom_fields:
            analysis["custom_fields_count"] = len(custom_fields)
            analysis["key_custom_fields"] = list(custom_fields.keys())[:10]

        return analysis

    def _analyze_journal_entries(self, root: Element) -> Dict[str, Any]:
        """Analyze journal entries (comments and work notes)"""
        entries = root.findall(".//sys_journal_field")

        comments = []
        work_notes = []

        for entry in entries:
            element_type = self._get_field_value(entry, "element")
            if element_type == "comments":
                comments.append(entry)
            elif element_type == "work_notes":
                work_notes.append(entry)

        return {
            "total_entries": len(entries),
            "comments_count": len(comments),
            "work_notes_count": len(work_notes),
            "unique_contributors": self._count_unique_contributors(entries),
            "conversation_duration": self._calculate_conversation_duration(entries),
        }

    def _analyze_attachments(self, root: Element) -> Dict[str, Any]:
        """Analyze attachments in the export"""
        attachments = root.findall(".//sys_attachment")

        analysis = {
            "total_attachments": len(attachments),
            "attachment_types": {},
            "total_size_bytes": 0,
        }

        for attachment in attachments:
            content_type = self._get_field_value(attachment, "content_type")
            if content_type:
                analysis["attachment_types"][content_type] = (
                    analysis["attachment_types"].get(content_type, 0) + 1
                )

            size = self._get_field_value(attachment, "size_bytes")
            if size and size.isdigit():
                analysis["total_size_bytes"] += int(size)

        return analysis

    def _extract_sla_metrics(self, record: Optional[Element]) -> Dict[str, Any]:
        """Extract SLA and performance metrics"""
        if record is None:
            return {}

        metrics = {
            "made_sla": self._get_field_value(record, "made_sla") == "true",
            "sla_percentage": self._get_field_value(record, "u_sla_percentage"),
            "breach_time": self._get_field_value(record, "u_breach_time"),
            "business_duration": self._get_field_value(record, "business_duration"),
            "calendar_duration": self._get_field_value(record, "calendar_duration"),
            "escalation_level": self._get_field_value(record, "u_escalation_level"),
        }

        return {k: v for k, v in metrics.items() if v}

    def _analyze_workflow(
        self, record: Optional[Element], root: Element
    ) -> Dict[str, Any]:
        """Analyze workflow and assignment patterns"""
        if record is None:
            return {}

        analysis = {
            "reassignment_count": self._get_field_value(record, "reassignment_count"),
            "reopen_count": self._get_field_value(record, "reopen_count"),
            "escalation": self._get_field_value(record, "escalation"),
            "approval_status": self._get_field_value(record, "approval"),
            "state_transitions": self._analyze_state_transitions(record, root),
        }

        return analysis

    def _extract_ticket_info(self, record: Optional[Element]) -> Dict[str, Any]:
        """Extract core ticket information"""
        if record is None:
            return {}

        return {
            "number": self._get_field_value(record, "number"),
            "sys_id": self._get_field_value(record, "sys_id"),
            "opened_at": self._get_field_value(record, "opened_at"),
            "closed_at": self._get_field_value(record, "closed_at"),
            "resolved_at": self._get_field_value(record, "resolved_at"),
            "state": self._get_field_value(record, "state"),
            "state_text": self._get_field_value(record, "u_state_text"),
            "short_description": self._get_field_value(record, "short_description"),
            "description": self._get_field_value(record, "description"),
            "close_notes": self._get_field_value(record, "close_notes"),
        }

    def _extract_conversation_thread(self, root: Element) -> List[Dict[str, Any]]:
        """Extract and structure the conversation thread"""
        entries = root.findall(".//sys_journal_field")

        thread = []
        for entry in entries:
            thread_entry = {
                "type": self._get_field_value(entry, "element"),
                "created_on": self._get_field_value(entry, "sys_created_on"),
                "created_by": self._get_field_value(entry, "sys_created_by"),
                "value": self._get_field_value(entry, "value"),
            }
            thread.append(thread_entry)

        # Sort by timestamp
        thread.sort(key=lambda x: x["created_on"] if x["created_on"] else "")

        return thread

    def _extract_attachment_info(self, root: Element) -> List[Dict[str, Any]]:
        """Extract attachment information"""
        attachments = root.findall(".//sys_attachment")

        attachment_list = []
        for attachment in attachments:
            info = {
                "file_name": self._get_field_value(attachment, "file_name"),
                "content_type": self._get_field_value(attachment, "content_type"),
                "size_bytes": self._get_field_value(attachment, "size_bytes"),
                "created_on": self._get_field_value(attachment, "sys_created_on"),
                "created_by": self._get_field_value(attachment, "sys_created_by"),
            }
            attachment_list.append(info)

        return attachment_list

    def _extract_timeline(
        self, record: Optional[Element], root: Element
    ) -> List[Dict[str, Any]]:
        """Extract timeline of events"""
        events = []

        if record:
            # Add main record events
            opened_at = self._get_field_value(record, "opened_at")
            if opened_at:
                events.append(
                    {
                        "timestamp": opened_at,
                        "event": "Ticket Opened",
                        "details": self._get_field_display_value(record, "opened_by"),
                    }
                )

            resolved_at = self._get_field_value(record, "resolved_at")
            if resolved_at:
                events.append(
                    {
                        "timestamp": resolved_at,
                        "event": "Ticket Resolved",
                        "details": self._get_field_display_value(record, "resolved_by"),
                    }
                )

            closed_at = self._get_field_value(record, "closed_at")
            if closed_at:
                events.append(
                    {
                        "timestamp": closed_at,
                        "event": "Ticket Closed",
                        "details": self._get_field_display_value(record, "closed_by"),
                    }
                )

        # Add journal entries
        for entry in root.findall(".//sys_journal_field"):
            timestamp = self._get_field_value(entry, "sys_created_on")
            if timestamp:
                events.append(
                    {
                        "timestamp": timestamp,
                        "event": f"{self._get_field_value(entry, 'element')} added",
                        "details": self._get_field_value(entry, "sys_created_by"),
                    }
                )

        # Sort by timestamp
        events.sort(key=lambda x: x["timestamp"] if x["timestamp"] else "")

        return events

    def _extract_people(
        self, record: Optional[Element], root: Element
    ) -> Dict[str, List[str]]:
        """Extract all people involved in the ticket"""
        people = {"requesters": [], "assignees": [], "commenters": [], "resolvers": []}

        if record:
            # Requester/Caller
            caller = self._get_field_display_value(record, "caller_id")
            if caller:
                people["requesters"].append(caller)
            requested_for = self._get_field_display_value(record, "requested_for")
            if requested_for and requested_for != caller:
                people["requesters"].append(requested_for)

            # Assignees
            assigned_to = self._get_field_display_value(record, "assigned_to")
            if assigned_to:
                people["assignees"].append(assigned_to)

            # Resolvers
            resolved_by = self._get_field_display_value(record, "resolved_by")
            if resolved_by:
                people["resolvers"].append(resolved_by)
            closed_by = self._get_field_display_value(record, "closed_by")
            if closed_by and closed_by != resolved_by:
                people["resolvers"].append(closed_by)

        # Commenters
        for entry in root.findall(".//sys_journal_field"):
            commenter = self._get_field_value(entry, "sys_created_by")
            if commenter and commenter not in people["commenters"]:
                people["commenters"].append(commenter)

        return people

    def _extract_custom_fields(self, record: Element) -> Dict[str, str]:
        """Extract custom fields (u_ prefix)"""
        custom_fields = {}

        for child in record:
            if child.tag.startswith("u_") and child.text:
                custom_fields[child.tag] = child.text.strip()

        return custom_fields

    def _get_field_value(
        self, element: Optional[Element], field_name: str
    ) -> Optional[str]:
        """Get text value of a field"""
        if element is None:
            return None
        field = element.find(f".//{field_name}")
        if field is not None and field.text:
            return field.text.strip()
        return None

    def _get_field_display_value(
        self, element: Optional[Element], field_name: str
    ) -> Optional[str]:
        """Get display_value attribute of a field"""
        if element is None:
            return None
        field = element.find(f".//{field_name}")
        if field is not None:
            return field.get("display_value", field.text)
        return None

    def _calculate_resolution_time(self, record: Element) -> Optional[str]:
        """Calculate time to resolution"""
        opened = self._get_field_value(record, "opened_at")
        resolved = self._get_field_value(record, "resolved_at")

        if opened and resolved:
            try:
                opened_dt = datetime.fromisoformat(opened.replace(" ", "T"))
                resolved_dt = datetime.fromisoformat(resolved.replace(" ", "T"))
                duration = resolved_dt - opened_dt
                return str(duration)
            except Exception:
                pass

        return None

    def _count_unique_contributors(self, entries: List[Element]) -> int:
        """Count unique contributors to journal entries"""
        contributors = set()
        for entry in entries:
            created_by = self._get_field_value(entry, "sys_created_by")
            if created_by:
                contributors.add(created_by)
        return len(contributors)

    def _calculate_conversation_duration(self, entries: List[Element]) -> Optional[str]:
        """Calculate duration of conversation"""
        timestamps = []
        for entry in entries:
            timestamp = self._get_field_value(entry, "sys_created_on")
            if timestamp:
                timestamps.append(timestamp)

        if len(timestamps) >= 2:
            timestamps.sort()
            try:
                first = datetime.fromisoformat(timestamps[0].replace(" ", "T"))
                last = datetime.fromisoformat(timestamps[-1].replace(" ", "T"))
                duration = last - first
                return str(duration)
            except Exception:
                pass

        return None

    def _analyze_state_transitions(self, record: Element, root: Element) -> List[str]:
        """Analyze state transitions from journal entries"""
        # This would require parsing work notes for state changes
        # For now, return basic transition
        _ = self._get_field_value(record, "state")  # State for potential future use
        state_text = self._get_field_value(record, "u_state_text")

        transitions = []
        if state_text:
            transitions.append(f"Final state: {state_text}")

        return transitions

    def _create_data_inventory(self, root: Element) -> Dict[str, int]:
        """Create inventory of data types found"""
        inventory = {
            "incidents": len(root.findall(".//incident")),
            "problems": len(root.findall(".//problem")),
            "changes": len(root.findall(".//change")),
            "journal_entries": len(root.findall(".//sys_journal_field")),
            "attachments": len(root.findall(".//sys_attachment")),
            "total_fields": 0,
        }

        # Count fields in primary record
        primary = self._get_primary_record(root)
        if primary:
            inventory["total_fields"] = len(list(primary))

        return inventory

    def _generate_recommendations(self, findings: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # SLA recommendations
        if (
            "sla_metrics" in findings
            and findings["sla_metrics"].get("made_sla") is False
        ):
            recommendations.append(
                "Analyze SLA breach patterns to improve service delivery"
            )

        # Workflow recommendations
        workflow = findings.get("workflow_analysis", {})
        if (
            workflow.get("reassignment_count")
            and int(workflow["reassignment_count"]) > 3
        ):
            recommendations.append(
                "High reassignment count - review assignment rules and skills mapping"
            )

        if workflow.get("reopen_count") and int(workflow["reopen_count"]) > 0:
            recommendations.append(
                "Ticket was reopened - analyze root cause to prevent recurrence"
            )

        # Journal recommendations
        journal = findings.get("journal_analysis", {})
        if journal.get("work_notes_count", 0) > journal.get("comments_count", 0) * 2:
            recommendations.append(
                "High internal communication - consider improving customer updates"
            )

        # General recommendations
        recommendations.extend(
            [
                "Extract conversation patterns for chatbot training",
                "Analyze resolution patterns for knowledge base creation",
                "Mine ticket data for predictive incident prevention",
            ]
        )

        return recommendations

    def _identify_ai_use_cases(self, findings: Dict[str, Any]) -> List[str]:
        """Identify AI/ML use cases based on the data"""
        use_cases = [
            "Automated ticket categorization and routing",
            "SLA breach prediction and prevention",
            "Similar incident detection and solution recommendation",
            "Sentiment analysis on customer communications",
            "Workload prediction and resource optimization",
            "Knowledge extraction from resolution notes",
            "Automated response generation for common issues",
            "Assignment recommendation based on skills and availability",
            "Problem pattern detection across incidents",
            "Predictive maintenance from incident trends",
        ]

        # Add specific use cases based on findings
        if findings.get("attachment_analysis", {}).get("total_attachments", 0) > 0:
            use_cases.append("Image analysis for screenshot error detection")

        if findings.get("journal_analysis", {}).get("total_entries", 0) > 10:
            use_cases.append("Conversation summarization for handoffs")

        return use_cases

    def _calculate_quality_metrics(self, root: Element) -> Dict[str, float]:
        """Calculate data quality metrics"""
        primary = self._get_primary_record(root)

        if not primary:
            return {"completeness": 0.0, "consistency": 0.0, "richness": 0.0}

        # Completeness - check key fields
        key_fields = [
            "number",
            "short_description",
            "opened_at",
            "state",
            "priority",
            "assigned_to",
        ]
        filled_fields = sum(
            1 for field in key_fields if self._get_field_value(primary, field)
        )
        completeness = filled_fields / len(key_fields)

        # Consistency - check data formats
        consistency_score = 1.0
        # Check date formats
        date_fields = ["opened_at", "closed_at", "resolved_at", "sys_created_on"]
        for field in date_fields:
            value = self._get_field_value(primary, field)
            if value and not re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", value):
                consistency_score -= 0.1

        # Richness - amount of supplementary data
        journal_count = len(root.findall(".//sys_journal_field"))
        attachment_count = len(root.findall(".//sys_attachment"))
        custom_fields = len([f for f in primary if f.tag.startswith("u_")])

        richness = min(
            1.0, (journal_count * 0.1 + attachment_count * 0.05 + custom_fields * 0.02)
        )

        return {
            "completeness": completeness,
            "consistency": max(0.0, consistency_score),
            "richness": richness,
        }
