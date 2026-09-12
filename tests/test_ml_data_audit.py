"""
Unit Tests for Machine Learning Data Sufficiency & Quality Audit Gate
Tests verification of rejection for 1-day fixture and approval for multi-day benchmark data.
"""

import os
import json
import tempfile
from ml.config import SINGLE_DAY_FIXTURE_PATH
from ml.data_audit import DataAuditor
from ml.generate_benchmark_data import generate_multiday_benchmark


def test_data_audit_rejects_single_day_fixture():
    """Verifies that the Data Sufficiency Gate halts on the 1-day fixture."""
    auditor = DataAuditor(SINGLE_DAY_FIXTURE_PATH)
    audit_res = auditor.audit()

    assert audit_res["gate_passed"] is False
    assert audit_res["status"] == "NOT READY"
    assert audit_res["unique_days"] == 1
    assert audit_res["total_records"] == 288
    assert len(audit_res["failure_reasons"]) >= 2
    # Ensure reason mentions temporal depth and record volume
    reasons_text = " ".join(audit_res["failure_reasons"])
    assert "temporal depth" in reasons_text.lower()
    assert "record volume" in reasons_text.lower()


def test_data_audit_approves_multiday_benchmark():
    """Verifies that the Data Sufficiency Gate passes for 14-day calibrated benchmark."""
    # Generate benchmark in memory and write to temp file
    data = generate_multiday_benchmark(num_days=14, seed=42)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(data, tmp)
        tmp_path = tmp.name

    try:
        auditor = DataAuditor(tmp_path)
        audit_res = auditor.audit()

        assert audit_res["gate_passed"] is True
        assert audit_res["status"] == "READY"
        assert audit_res["unique_days"] == 14
        assert audit_res["total_records"] >= 1000
        assert audit_res["unique_roads"] >= 12
        assert len(audit_res["failure_reasons"]) == 0
        assert audit_res["is_simulated"] is True
        assert audit_res["data_classification"] == "SIMULATED"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
