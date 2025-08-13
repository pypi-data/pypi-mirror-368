"""
Tests for ClaudeCraftsman quality gates validation.
"""

from pathlib import Path

from claudecraftsman.core.validation import QualityGates, QualityReport, ValidationResult


def test_validation_result_model():
    """Test ValidationResult pydantic model."""
    result = ValidationResult(step="Test Step", passed=True, message="Test passed", severity="info")

    assert result.step == "Test Step"
    assert result.passed is True
    assert result.severity == "info"
    assert result.timestamp is not None


def test_quality_report_overall_calculation():
    """Test QualityReport overall pass calculation."""
    results = [
        ValidationResult(step="Step 1", passed=True, message="OK"),
        ValidationResult(step="Step 2", passed=False, message="Failed", severity="error"),
        ValidationResult(step="Step 3", passed=False, message="Warning", severity="warning"),
    ]

    report = QualityReport(
        project="test",
        phase="testing",
        overall_passed=False,  # Will be recalculated
        validation_results=results,
    )

    # Should fail because Step 2 has error severity
    assert report.overall_passed is False


def test_syntax_validation(tmp_path: Path):
    """Test Python syntax validation."""
    # Create a valid Python file
    valid_file = tmp_path / "valid.py"
    valid_file.write_text("def hello():\n    print('Hello, world!')")

    # Create an invalid Python file
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("def hello(\n    print('Missing parenthesis'")

    gates = QualityGates()
    gates.project_root = tmp_path

    result = gates._validate_syntax()

    # Should fail due to syntax error
    assert result.passed is False
    assert "syntax error" in result.message.lower()


def test_quality_checklist_generation():
    """Test quality checklist markdown generation."""
    gates = QualityGates()
    checklist = gates.create_quality_checklist()

    # Should contain all 8 steps
    assert "Step 1: Syntax Validation" in checklist
    assert "Step 2: Type Checking" in checklist
    assert "Step 3: Lint Standards" in checklist
    assert "Step 4: Security Analysis" in checklist
    assert "Step 5: Test Coverage" in checklist
    assert "Step 6: Performance Analysis" in checklist
    assert "Step 7: Documentation" in checklist
    assert "Step 8: Integration" in checklist

    # Should have craftsman standards
    assert "Craftsman Standards" in checklist
