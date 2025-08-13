"""
Enhanced completion detection for documents based on success criteria.

This module analyzes document content to determine if success criteria
have been met, making intelligent decisions about document completion.
"""

import re
from pathlib import Path
from typing import Any, cast

from rich.console import Console

console = Console()


class CompletionDetector:
    """Detects document completion based on success criteria analysis."""

    def __init__(self) -> None:
        """Initialize the completion detector."""
        # Document type specific patterns
        self.doc_type_patterns = {
            "PLAN": {
                "criteria_headers": [
                    r"## Success Criteria",
                    r"## Acceptance Criteria",
                    r"## Definition of Done",
                    r"## Goals",
                ],
                "completion_markers": [
                    r"## PLAN STATUS: COMPLETE",
                    r"All.*phases.*complete",
                    r"Plan.*successfully.*implemented",
                ],
                "phase_pattern": r"### Phase \d+:.*?(?:✅\s*COMPLETE|COMPLETE\s*✅)",
                "next_steps_pattern": r"## Next Steps.*?(?:~~[^~]+~~\s*✅\s*COMPLETE)",
            },
            "IMPL": {
                "criteria_headers": [
                    r"## Benefits Achieved",
                    r"## Implementation Complete",
                    r"## Results",
                    r"## Deliverables",
                ],
                "completion_markers": [
                    r"## STATUS:.*Phase.*COMPLETE",
                    r"Implementation.*complete",
                    r"Successfully implemented",
                    r"All.*phases.*complete",
                ],
            },
            "ANALYSIS": {
                "criteria_headers": [
                    r"## Summary",
                    r"## Findings",
                    r"## Next Steps",
                ],
                "completion_markers": [
                    r"Analysis complete",
                    r"Analysis.*complete",
                ],
                "conclusion_pattern": r"## Conclusion",
            },
            "RECOMMENDATIONS": {
                "criteria_headers": [
                    r"## Recommendations",
                    r"## Proposed Solution",
                    r"## Next Steps",
                ],
                "completion_markers": [
                    r"Recommendations provided",
                    r"## Conclusion",
                ],
            },
        }

    def analyze_document(self, filepath: Path) -> dict[str, Any]:
        """
        Analyze a document for completion based on its content.

        Returns:
            Dictionary with analysis results including:
            - is_complete: Boolean indicating if document is complete
            - confidence: Float 0-1 indicating confidence in assessment
            - criteria_met: List of criteria that were satisfied
            - criteria_pending: List of criteria not yet satisfied
            - reason: String explaining the determination
        """
        if not filepath.exists():
            return {
                "is_complete": False,
                "confidence": 0.0,
                "criteria_met": [],
                "criteria_pending": [],
                "reason": "File does not exist",
            }

        content = filepath.read_text()
        doc_type = self._extract_doc_type(filepath.name)

        # Get patterns for this document type
        patterns = self.doc_type_patterns.get(doc_type, {})

        # First analyze success criteria to get detailed information
        criteria_analysis = self._analyze_success_criteria(content, doc_type)

        # Check phase completion for plans
        if doc_type == "PLAN":
            phase_analysis = self._analyze_phases(content)
            criteria_analysis["phase_completion"] = phase_analysis

        # Check for explicit completion markers
        explicit_complete = self._check_explicit_markers(content, cast(dict[str, Any], patterns))

        # If explicitly complete AND has criteria, merge the analyses
        if explicit_complete and (
            criteria_analysis.get("has_criteria")
            or (
                doc_type == "PLAN"
                and criteria_analysis.get("phase_completion", {}).get("total_phases", 0) > 0
            )
        ):
            result = self._calculate_completion(criteria_analysis, doc_type, content)
            # Boost confidence due to explicit marker
            result["confidence"] = max(result["confidence"], 0.95)
            result["is_complete"] = True
            if "Explicit completion marker found" not in result["criteria_met"]:
                result["criteria_met"].append("Explicit completion marker found")
            return result
        elif explicit_complete:
            # No criteria to analyze, just the marker
            return {
                "is_complete": True,
                "confidence": 1.0,
                "criteria_met": ["Explicit completion marker found"],
                "criteria_pending": [],
                "reason": "Document explicitly marked as complete",
            }

        # No explicit marker, do full analysis
        # Calculate overall completion
        return self._calculate_completion(criteria_analysis, doc_type, content)

    def _extract_doc_type(self, filename: str) -> str:
        """Extract document type from filename."""
        # Handle compound types
        if "TECH-SPEC" in filename:
            return "TECH-SPEC"

        # Extract primary type
        match = re.match(r"^([A-Z]+)-", filename)
        if match:
            return match.group(1)
        return "UNKNOWN"

    def _check_explicit_markers(self, content: str, patterns: dict[str, Any]) -> bool:
        """Check for explicit completion markers."""
        completion_markers = patterns.get("completion_markers", [])

        for marker in completion_markers:
            if re.search(marker, content, re.IGNORECASE | re.MULTILINE):
                return True

        # Check for STATUS: COMPLETE at end of document
        lines = content.strip().split("\n")
        if lines:
            last_lines = "\n".join(lines[-5:])
            if re.search(r"STATUS:\s*(?:Phase \d+\s*)?COMPLETE", last_lines, re.IGNORECASE):
                return True

        return False

    def _analyze_success_criteria(self, content: str, doc_type: str) -> dict[str, Any]:
        """Analyze success criteria or equivalent sections."""
        patterns = self.doc_type_patterns.get(doc_type, {})
        if not isinstance(patterns, dict):
            return {}
        criteria_headers = patterns.get("criteria_headers", [])

        # Find success criteria section
        criteria_section = None
        for header_pattern in criteria_headers:
            match = re.search(
                f"{header_pattern}(.*?)(?=##|\\Z)",
                content,
                re.IGNORECASE | re.MULTILINE | re.DOTALL,
            )
            if match:
                criteria_section = match.group(1)
                break

        if not criteria_section:
            return {
                "has_criteria": False,
                "total_criteria": 0,
                "completed_criteria": 0,
                "criteria_details": [],
            }

        # Analyze individual criteria
        criteria_details = []

        # Check for checkbox style criteria
        checkbox_pattern = r"- \[([ xX])\] (.+)"
        checkboxes = re.findall(checkbox_pattern, criteria_section)
        for checkbox, criterion in checkboxes:
            is_complete = checkbox.lower() == "x"
            criteria_details.append(
                {"criterion": criterion.strip(), "complete": is_complete, "type": "checkbox"}
            )

        # Check for strikethrough style (~~text~~) and numbered lists
        # First handle strikethrough items
        strikethrough_items = re.findall(r"~~(.+?)~~", criteria_section)
        for item in strikethrough_items:
            criteria_details.append(
                {"criterion": item.strip(), "complete": True, "type": "strikethrough"}
            )

        # Then handle numbered lists looking for incomplete items
        # Process line by line to handle numbered lists properly
        lines = criteria_section.strip().split("\n")
        for line in lines:
            line = line.strip()
            # Match numbered or bulleted list items
            list_match = re.match(r"^(?:\d+\.|[-*])\s+(.+)$", line)
            if list_match:
                full_text = list_match.group(1)
                # Skip if it contains strikethrough (already handled)
                if "~~" in full_text:
                    continue
                # Skip if it starts with checkbox (already handled)
                if full_text.startswith("["):
                    continue

                # Check if already handled
                item_text = re.sub(r"\s*✅\s*COMPLETE\s*$", "", full_text).strip()
                if item_text and not any(
                    item_text in cd["criterion"] or cd["criterion"] in item_text
                    for cd in criteria_details
                ):
                    is_complete = "✅ COMPLETE" in full_text
                    criteria_details.append(
                        {"criterion": item_text, "complete": is_complete, "type": "list"}
                    )

        # Check for percentage completion
        percentage_match = re.search(r"(\d+)%\s*complete", criteria_section, re.IGNORECASE)
        percentage_complete = int(percentage_match.group(1)) if percentage_match else None

        completed = sum(1 for c in criteria_details if c["complete"])
        total = len(criteria_details)

        return {
            "has_criteria": True,
            "total_criteria": total,
            "completed_criteria": completed,
            "percentage_complete": percentage_complete,
            "criteria_details": criteria_details,
        }

    def _analyze_phases(self, content: str) -> dict[str, Any]:
        """Analyze phase completion for plans."""
        # Find all phases
        phase_pattern = r"### Phase (\d+):(.*?)(?=### Phase|\Z)"
        phases = re.findall(phase_pattern, content, re.DOTALL)

        phase_details = []
        for phase_num, phase_content in phases:
            # Check if phase is marked complete
            is_complete = bool(re.search(r"✅\s*COMPLETE|COMPLETE\s*✅", phase_content[:200]))
            phase_details.append({"phase": int(phase_num), "complete": is_complete})

        completed = sum(1 for p in phase_details if p["complete"])
        total = len(phase_details)

        return {
            "total_phases": total,
            "completed_phases": completed,
            "phase_details": phase_details,
        }

    def _calculate_completion(
        self, analysis: dict[str, Any], doc_type: str, content: str = ""
    ) -> dict[str, Any]:
        """Calculate overall completion based on analysis."""
        criteria_met = []
        criteria_pending = []
        confidence = 0.0

        # Check success criteria
        if analysis.get("has_criteria"):
            total = analysis["total_criteria"]
            completed = analysis["completed_criteria"]

            if total > 0:
                completion_rate = completed / total

                for detail in analysis["criteria_details"]:
                    if detail["complete"]:
                        criteria_met.append(detail["criterion"])
                    else:
                        criteria_pending.append(detail["criterion"])

                # High confidence if all criteria met
                if completion_rate == 1.0:
                    confidence = 0.95
                elif completion_rate >= 0.8:
                    confidence = 0.7
                elif completion_rate >= 0.4:
                    confidence = completion_rate * 0.8
                else:
                    confidence = completion_rate * 0.5

        # Check phase completion for plans
        if doc_type == "PLAN" and "phase_completion" in analysis:
            phase_data = analysis["phase_completion"]
            if phase_data["total_phases"] > 0:
                phase_completion_rate = phase_data["completed_phases"] / phase_data["total_phases"]

                # Add phase information
                for phase in phase_data["phase_details"]:
                    phase_desc = f"Phase {phase['phase']}"
                    if phase["complete"]:
                        criteria_met.append(phase_desc)
                    else:
                        criteria_pending.append(phase_desc)

                # Adjust confidence based on phases
                if phase_completion_rate == 1.0:
                    confidence = max(confidence, 0.9)
                else:
                    confidence = max(confidence, phase_completion_rate * 0.6)

        # For ANALYSIS and RECOMMENDATIONS documents, check for conclusion sections
        if doc_type in ["ANALYSIS", "RECOMMENDATIONS"]:
            patterns = self.doc_type_patterns.get(doc_type, {})
            if not isinstance(patterns, dict):
                return {}
            conclusion_pattern = patterns.get("conclusion_pattern", r"## Conclusion")

            # Check if document has conclusion
            has_conclusion = bool(re.search(conclusion_pattern, content, re.IGNORECASE))
            if has_conclusion:
                # For these document types, having a conclusion is sufficient for completion
                confidence = max(confidence, 0.8)
                criteria_met.append("Document has conclusion section")
        # For other documents without explicit criteria
        elif not analysis.get("has_criteria") or analysis.get("total_criteria", 0) == 0:
            # Generic documents might still have completion indicators
            pass

        # Determine completion
        is_complete = confidence >= 0.8  # 80% confidence threshold

        # Generate reason
        if is_complete:
            if len(criteria_met) > 0:
                reason = f"Completed {len(criteria_met)} criteria"
            else:
                reason = "Document appears complete based on structure"
        else:
            if len(criteria_pending) > 0:
                reason = f"{len(criteria_pending)} criteria still pending"
            else:
                reason = "Insufficient evidence of completion"

        return {
            "is_complete": is_complete,
            "confidence": confidence,
            "criteria_met": criteria_met,
            "criteria_pending": criteria_pending,
            "reason": reason,
        }

    def suggest_completion_additions(self, filepath: Path) -> list[str]:
        """Suggest what to add to mark a document as complete."""
        doc_type = self._extract_doc_type(filepath.name)
        suggestions = []

        # Always suggest adding explicit status marker
        suggestions.append("Add '## STATUS: COMPLETE' at the end of the document")

        # Type-specific suggestions
        if doc_type == "PLAN":
            suggestions.append("Mark all phases as '✅ COMPLETE'")
            suggestions.append("Strike through completed next steps with ~~text~~")
            suggestions.append("Update success criteria with checkboxes: - [x] Completed item")
        elif doc_type == "IMPL":
            suggestions.append("Add '## Benefits Achieved' section listing accomplishments")
            suggestions.append("Document all deliverables in a '## Results' section")
        elif doc_type in ["ANALYSIS", "RECOMMENDATIONS"]:
            suggestions.append("Add a '## Conclusion' section summarizing findings")

        return suggestions
