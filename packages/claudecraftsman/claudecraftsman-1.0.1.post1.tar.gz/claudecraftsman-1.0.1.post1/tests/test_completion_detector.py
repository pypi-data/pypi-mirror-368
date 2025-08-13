"""
Test the intelligent completion detection system.
"""

import pytest

from claudecraftsman.core.completion_detector import CompletionDetector


@pytest.fixture
def detector():
    """Create a completion detector instance."""
    return CompletionDetector()


@pytest.fixture
def temp_docs_dir(tmp_path):
    """Create temporary docs directory."""
    docs_dir = tmp_path / ".claude" / "docs" / "current"
    docs_dir.mkdir(parents=True)
    return docs_dir


def test_plan_with_success_criteria_complete(detector, temp_docs_dir):
    """Test detection of complete plan with all success criteria met."""
    content = """# Document Organization Enforcement Implementation Plan

## Success Criteria
- [x] No documents can be created in root of current/
- [x] All documents automatically organized by type
- [x] Registry always current with all documents
- [x] Completed documents auto-archived
- [x] Zero manual organization required

## Phase 1: Implementation ✅ COMPLETE
Details here...

## Phase 2: Testing ✅ COMPLETE
More details...

## Phase 3: Deployment ✅ COMPLETE
Final details...

## STATUS: COMPLETE
"""

    doc_path = temp_docs_dir / "plans" / "PLAN-test-2025-08-06.md"
    doc_path.parent.mkdir(exist_ok=True)
    doc_path.write_text(content)

    result = detector.analyze_document(doc_path)

    assert result["is_complete"] is True
    assert result["confidence"] >= 0.8
    assert len(result["criteria_met"]) > 0
    assert len(result["criteria_pending"]) == 0
    assert "criteria" in result["reason"].lower()


def test_plan_with_partial_criteria(detector, temp_docs_dir):
    """Test detection of incomplete plan with partial criteria."""
    content = """# Feature Implementation Plan

## Success Criteria
- [x] Feature designed
- [x] Code implemented
- [ ] Tests written
- [ ] Documentation updated
- [ ] Performance validated

## Phase 1: Design ✅ COMPLETE
Done...

## Phase 2: Implementation ✅ COMPLETE
Done...

## Phase 3: Testing
In progress...
"""

    doc_path = temp_docs_dir / "plans" / "PLAN-partial-2025-08-06.md"
    doc_path.parent.mkdir(exist_ok=True)
    doc_path.write_text(content)

    result = detector.analyze_document(doc_path)

    print(f"DEBUG: Result = {result}")
    assert result["is_complete"] is False
    # With 2/5 criteria complete (0.4), multiplied by 0.8 = 0.32
    assert 0.3 <= result["confidence"] < 0.4
    assert len(result["criteria_met"]) == 2
    assert len(result["criteria_pending"]) == 3
    assert "pending" in result["reason"].lower()


def test_plan_with_phases_all_complete(detector, temp_docs_dir):
    """Test plan with all phases marked complete."""
    content = """# Phased Implementation Plan

## Overview
Three phase implementation...

### Phase 1: Foundation ✅ COMPLETE
- Built foundation

### Phase 2: Features ✅ COMPLETE
- Added features

### Phase 3: Polish ✅ COMPLETE
- Final polish

## Next Steps
~~Deploy to production~~ ✅ COMPLETE
~~Monitor performance~~ ✅ COMPLETE
"""

    doc_path = temp_docs_dir / "plans" / "PLAN-phases-2025-08-06.md"
    doc_path.parent.mkdir(exist_ok=True)
    doc_path.write_text(content)

    result = detector.analyze_document(doc_path)

    assert result["is_complete"] is True
    assert result["confidence"] >= 0.9
    assert any("Phase" in criterion for criterion in result["criteria_met"])


def test_impl_with_benefits_achieved(detector, temp_docs_dir):
    """Test implementation document with benefits section."""
    content = """# Framework Enforcement Implementation

## Overview
Implementation of framework enforcement...

## Implementation Details
Code changes...

## Benefits Achieved
1. 100% Compliance - Framework standards automatically enforced
2. Zero Manual Overhead - No need to remember conventions
3. Always Current State - Registry and workflow state auto-updated
4. Complete Git History - Every operation tracked
5. Developer Experience - Helpful error messages

## Testing
All tests passing...

## STATUS: Phase 2 COMPLETE
"""

    doc_path = temp_docs_dir / "implementation" / "IMPL-enforcement-2025-08-06.md"
    doc_path.parent.mkdir(exist_ok=True)
    doc_path.write_text(content)

    result = detector.analyze_document(doc_path)

    print(f"DEBUG: Result = {result}")
    assert result["is_complete"] is True
    assert result["confidence"] >= 0.95
    assert "Explicit completion marker found" in result["criteria_met"]


def test_analysis_with_conclusion(detector, temp_docs_dir):
    """Test analysis document with conclusion section."""
    content = """# System Performance Analysis

## Methodology
Analysis approach...

## Findings
- Finding 1
- Finding 2
- Finding 3

## Recommendations
- Recommendation 1
- Recommendation 2

## Conclusion
Based on our analysis, the system performs well under normal load but
requires optimization for peak traffic scenarios.
"""

    doc_path = temp_docs_dir / "analysis" / "ANALYSIS-performance-2025-08-06.md"
    doc_path.parent.mkdir(exist_ok=True)
    doc_path.write_text(content)

    result = detector.analyze_document(doc_path)

    assert result["is_complete"] is True
    assert result["confidence"] >= 0.8
    assert "Document has conclusion section" in result["criteria_met"]


def test_document_without_criteria(detector, temp_docs_dir):
    """Test document without explicit success criteria."""
    content = """# Technical Notes

## Overview
Some technical information...

## Details
More details here...

## Summary
Final thoughts...
"""

    doc_path = temp_docs_dir / "technical" / "TECH-notes-2025-08-06.md"
    doc_path.parent.mkdir(exist_ok=True)
    doc_path.write_text(content)

    result = detector.analyze_document(doc_path)

    assert result["is_complete"] is False
    assert result["confidence"] < 0.8
    assert "Insufficient evidence" in result["reason"]


def test_strikethrough_style_criteria(detector, temp_docs_dir):
    """Test detection of strikethrough style completion markers."""
    content = """# Task List

## Goals
1. ~~Design system architecture~~ ✅ COMPLETE
2. ~~Implement core features~~ ✅ COMPLETE
3. ~~Write comprehensive tests~~
4. Deploy to production
5. Monitor and optimize

Three out of five tasks completed.
"""

    doc_path = temp_docs_dir / "plans" / "PLAN-tasks-2025-08-06.md"
    doc_path.parent.mkdir(exist_ok=True)
    doc_path.write_text(content)

    result = detector.analyze_document(doc_path)

    print(f"DEBUG: Result = {result}")
    assert result["is_complete"] is False
    # With 3/5 = 0.6 completion rate, confidence = 0.6 * 0.8 = 0.48
    assert 0.45 <= result["confidence"] < 0.5
    assert len(result["criteria_met"]) == 3
    assert len(result["criteria_pending"]) == 2


def test_percentage_completion(detector, temp_docs_dir):
    """Test detection of percentage completion."""
    content = """# Progress Report

## Success Criteria
- Feature A implemented
- Feature B implemented
- Feature C in progress
- Feature D planned

Current status: 50% complete

## Next Steps
Continue with remaining features...
"""

    doc_path = temp_docs_dir / "reports" / "REPORT-progress-2025-08-06.md"
    doc_path.parent.mkdir(exist_ok=True)
    doc_path.write_text(content)

    result = detector.analyze_document(doc_path)

    assert result["is_complete"] is False
    assert result["confidence"] < 0.8


def test_suggestion_generation(detector, temp_docs_dir):
    """Test generation of completion suggestions."""
    doc_path = temp_docs_dir / "plans" / "PLAN-test-2025-08-06.md"
    doc_path.parent.mkdir(exist_ok=True)
    doc_path.write_text("# Test Plan\n\nSome content...")

    suggestions = detector.suggest_completion_additions(doc_path)

    assert len(suggestions) > 0
    assert any("STATUS: COMPLETE" in s for s in suggestions)
    assert any("✅ COMPLETE" in s for s in suggestions)


def test_compound_document_type(detector, temp_docs_dir):
    """Test handling of compound document types like TECH-SPEC."""
    content = """# Technical Specification

## Architecture
System design...

## Implementation
Technical details...

## Deliverables
- API implementation
- Database schema
- Documentation

## STATUS: COMPLETE
"""

    doc_path = temp_docs_dir / "specs" / "TECH-SPEC-api-2025-08-06.md"
    doc_path.parent.mkdir(exist_ok=True)
    doc_path.write_text(content)

    result = detector.analyze_document(doc_path)

    assert result["is_complete"] is True
    assert result["confidence"] == 1.0
    assert "explicitly marked as complete" in result["reason"]
