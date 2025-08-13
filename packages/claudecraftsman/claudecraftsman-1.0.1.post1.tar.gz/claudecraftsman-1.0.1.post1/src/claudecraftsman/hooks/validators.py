"""
Framework validation hooks for ClaudeCraftsman.

Provides deterministic enforcement of framework standards through
Claude Code lifecycle hooks.
"""

import re
from pathlib import Path

from claudecraftsman.core.config import get_config


class FrameworkValidator:
    """Validates operations against ClaudeCraftsman framework standards."""

    def __init__(self) -> None:
        """Initialize validator with framework configuration."""
        self.config = get_config()
        self.session_mcp_tools: list[str] = []
        self.time_context_established = False

    def validate_naming_convention(self, filepath: str) -> tuple[bool, str]:
        """
        Validate file naming follows TYPE-name-YYYY-MM-DD.md format.

        Args:
            filepath: Path to file being created/edited

        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(filepath)
        filename = path.name

        # Skip validation for non-markdown files
        if not filename.endswith(".md"):
            return True, ""

        # Skip validation for files outside .claude/docs/
        if ".claude/docs/" not in str(path):
            return True, ""

        # Pattern: TYPE-name-YYYY-MM-DD.md
        pattern = r"^[A-Z]+-[\w-]+-\d{4}-\d{2}-\d{2}\.md$"

        if not re.match(pattern, filename):
            return False, (
                f"Filename '{filename}' doesn't follow TYPE-name-YYYY-MM-DD.md format. "
                f"Examples: PRD-project-2025-08-06.md, TECH-SPEC-feature-2025-08-06.md"
            )

        return True, ""

    def validate_file_location(self, filepath: str) -> tuple[bool, str]:
        """
        Validate file is being created in approved location.

        Args:
            filepath: Path to file being created/edited

        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(filepath)

        # Check if it's a framework document in the root of current/
        path_str = str(path).replace("\\", "/")
        if ".claude/docs/current/" in path_str:
            # Extract the part after .claude/docs/current/
            current_idx = path_str.find(".claude/docs/current/") + len(".claude/docs/current/")
            rel_from_current = path_str[current_idx:]

            # If it's directly in current/ (no subdirectory), it's invalid
            if "/" not in rel_from_current and path.name != "registry.md":
                # Check if it's a document that should be organized
                if re.match(r"^[A-Z]+-", path.name):
                    return False, (
                        f"Document '{path.name}' cannot be in root of docs/current/. "
                        f"It should be organized in an appropriate subdirectory "
                        f"(e.g., plans/, implementation/, architecture/, etc.)"
                    )

        # Framework document locations
        approved_patterns = [
            r"\.claude/docs/current/",
            r"\.claude/docs/archive/",
            r"\.claude/context/",
            r"\.claude/agents/",
            r"\.claude/commands/",
            r"\.claude/project-mgt/",
            r"src/claudecraftsman/",  # Source code
            r"tests/",  # Test files
        ]

        filepath_str = str(path).replace("\\", "/")

        for pattern in approved_patterns:
            if re.search(pattern, filepath_str):
                return True, ""

        # Special case for project root files
        if path.parent == Path(".") or path.parent == Path("/workspace"):
            allowed_root = ["README.md", "CLAUDE.md", "pyproject.toml", "hooks.json"]
            if path.name in allowed_root:
                return True, ""

        return False, (
            f"File location '{filepath}' not in approved directories. "
            f"Use .claude/docs/current/ for documentation, "
            f".claude/context/ for state files, or appropriate project directories."
        )

    def validate_time_context(self) -> tuple[bool, str]:
        """
        Check if time context has been established using MCP tool.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.time_context_established:
            return False, (
                "Time context not established. Use MCP time tool first to get current datetime. "
                "This ensures all timestamps are accurate and consistent."
            )
        return True, ""

    def validate_research_evidence(self, filename: str) -> tuple[bool, str]:
        """
        Check if research MCP tools were used for documents requiring research.

        Args:
            filename: Name of file being created

        Returns:
            Tuple of (is_valid, error_message)
        """
        research_docs = ["PRD-", "SPEC-", "PLAN-", "ARCH-", "RESEARCH-"]

        # Check if this is a research document
        if not any(filename.startswith(prefix) for prefix in research_docs):
            return True, ""

        # Check if research tools were used
        research_tools = ["searxng", "crawl4ai", "context7"]
        if not any(tool in self.session_mcp_tools for tool in research_tools):
            return False, (
                f"Research document '{filename}' requires MCP research tools. "
                f"Use searxng, crawl4ai, or context7 to gather evidence before creating this document."
            )

        return True, ""

    def validate_citations(self, content: str) -> tuple[bool, str]:
        """
        Validate that content includes proper citations.

        Args:
            content: Document content

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Skip validation for short content or code files
        if len(content) < 500:
            return True, ""

        # Look for citation markers [text]^[n]
        citation_pattern = r"\[([^\]]+)\]\^\[(\d+)\]"
        citations = re.findall(citation_pattern, content)

        # Check if this appears to be a document that should have citations
        research_indicators = [
            "market analysis",
            "research",
            "study",
            "report",
            "according to",
            "survey",
            "data shows",
            "statistics",
        ]

        content_lower = content.lower()
        has_research_content = any(indicator in content_lower for indicator in research_indicators)

        if not citations and has_research_content:
            return False, (
                "Document appears to contain research claims but lacks citations. "
                "Use [Statement]^[1] format with a Sources section at the end."
            )

        # If citations exist, check for sources section
        if citations:
            sources_pattern = r"(?:Sources|References|Citations):"
            if not re.search(sources_pattern, content, re.IGNORECASE):
                return False, (
                    "Citations found but no Sources section. "
                    "Add a Sources section at the end with numbered references."
                )

        return True, ""

    def validate_hardcoded_dates(self, content: str) -> tuple[bool, str]:
        """
        Check for hardcoded dates that should use MCP time tool.

        Args:
            content: Document content

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Pattern for dates like 2025-08-06 or August 6, 2025
        date_patterns = [
            r"\b202[0-9]-[0-1][0-9]-[0-3][0-9]\b",  # YYYY-MM-DD
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+202[0-9]\b",  # Month DD, YYYY
        ]

        # Exceptions where hardcoded dates are acceptable
        exceptions = [
            r"Date:\s*202[0-9]",  # Document headers
            r"\*Date:\s*202[0-9]",  # Markdown document headers
            r"Created:\s*202[0-9]",  # Creation dates
            r"Modified:\s*202[0-9]",  # Modification dates
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Check if this match is part of an exception
                match_pos = match.start()
                is_exception = False

                for exc_pattern in exceptions:
                    # Check if exception pattern exists near the match
                    surrounding = content[max(0, match_pos - 20) : match_pos + 20]
                    if re.search(exc_pattern, surrounding, re.IGNORECASE):
                        is_exception = True
                        break

                if not is_exception:
                    return False, (
                        f"Hardcoded date '{match.group()}' found. "
                        f"Use MCP time tool to get current date dynamically."
                    )

        return True, ""

    def record_mcp_tool_usage(self, tool_name: str) -> None:
        """Record that an MCP tool was used in this session."""
        if tool_name not in self.session_mcp_tools:
            self.session_mcp_tools.append(tool_name)

        # Special handling for time tool
        if tool_name == "time":
            self.time_context_established = True

    def validate_all(self, filepath: str, content: str | None = None) -> list[tuple[str, str]]:
        """
        Run all validations and return list of violations.

        Args:
            filepath: Path to file
            content: Optional file content for content validations

        Returns:
            List of (validation_name, error_message) tuples
        """
        violations = []

        # File-based validations
        valid, error = self.validate_naming_convention(filepath)
        if not valid:
            violations.append(("naming_convention", error))

        valid, error = self.validate_file_location(filepath)
        if not valid:
            violations.append(("file_location", error))

        valid, error = self.validate_time_context()
        if not valid:
            violations.append(("time_context", error))

        filename = Path(filepath).name
        valid, error = self.validate_research_evidence(filename)
        if not valid:
            violations.append(("research_evidence", error))

        # Content-based validations
        if content:
            valid, error = self.validate_citations(content)
            if not valid:
                violations.append(("citations", error))

            valid, error = self.validate_hardcoded_dates(content)
            if not valid:
                violations.append(("hardcoded_dates", error))

        return violations
