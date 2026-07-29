import json

import pytest

from payrun.cli.main import main


@pytest.fixture
def config_path(tmp_path):
    db_path = tmp_path / "payrun.db"
    path = tmp_path / "payrun.config.json"
    path.write_text(
        json.dumps(
            {
                "database_path": str(db_path),
                "currency": "USD",
                "plan_year": 2026,
                "frequency": "MONTHLY",
            }
        )
    )
    return path


def _run(config_path, *args) -> int:
    return main(["--config", str(config_path), *args])


def _add_salaried_employee(config_path, employee_id="E0001") -> None:
    assert (
        _run(
            config_path,
            "employees",
            "add",
            "--id",
            employee_id,
            "--first-name",
            "Jordan",
            "--last-name",
            "Lee",
            "--frequency",
            "MONTHLY",
            "--hire-date",
            "2020-01-01",
            "--pay-type",
            "SALARIED",
            "--amount",
            "78000.00",
        )
        == 0
    )


def test_employees_add_succeeds(config_path):
    assert _run(config_path, "employees", "add", "--id", "E0001", "--first-name", "Jordan",
                "--last-name", "Lee", "--frequency", "MONTHLY", "--hire-date", "2020-01-01",
                "--pay-type", "SALARIED", "--amount", "78000.00") == 0


def test_employees_add_duplicate_id_fails(config_path, capsys):
    _add_salaried_employee(config_path)
    exit_code = _run(
        config_path, "employees", "add", "--id", "E0001", "--first-name", "Jordan",
        "--last-name", "Lee", "--frequency", "MONTHLY", "--hire-date", "2020-01-01",
        "--pay-type", "SALARIED", "--amount", "78000.00",
    )
    assert exit_code == 1
    assert "error:" in capsys.readouterr().err


def test_employees_add_invalid_amount_fails(config_path, capsys):
    exit_code = _run(
        config_path, "employees", "add", "--id", "E0001", "--first-name", "Jordan",
        "--last-name", "Lee", "--frequency", "MONTHLY", "--hire-date", "2020-01-01",
        "--pay-type", "SALARIED", "--amount", "not-a-number",
    )
    assert exit_code == 1
    assert "error:" in capsys.readouterr().err


def test_import_missing_file_fails(config_path, capsys):
    exit_code = _run(config_path, "import", str(config_path.parent / "missing.csv"))
    assert exit_code == 1
    assert "error:" in capsys.readouterr().err


def test_run_with_no_matching_employees_fails(config_path, capsys):
    exit_code = _run(config_path, "run", "--period", "2026-03-01")
    assert exit_code == 1
    assert "error:" in capsys.readouterr().err


def test_run_with_period_not_on_schedule_fails(config_path, capsys):
    _add_salaried_employee(config_path)
    exit_code = _run(config_path, "run", "--period", "2026-03-05")
    assert exit_code == 1
    assert "error:" in capsys.readouterr().err


def test_payslip_for_unrun_period_fails(config_path, capsys):
    _add_salaried_employee(config_path)
    exit_code = _run(config_path, "payslip", "--employee", "E0001", "--period", "2026-03-01")
    assert exit_code == 1
    assert "error:" in capsys.readouterr().err


def test_full_vertical_slice(config_path, tmp_path, capsys):
    _add_salaried_employee(config_path, "E0001")
    assert _run(
        config_path, "employees", "add", "--id", "E0002", "--first-name", "Ada",
        "--last-name", "Okafor", "--frequency", "MONTHLY", "--hire-date", "2020-01-01",
        "--pay-type", "HOURLY", "--amount", "30.00",
    ) == 0

    csv_path = tmp_path / "timesheet.csv"
    csv_path.write_text(
        "employee_id,work_date,hours\n"
        "E0002,2026-03-02,8.00\n"
        "E0002,2026-03-03,8.00\n"
    )
    assert _run(config_path, "import", str(csv_path)) == 0

    assert _run(config_path, "run", "--period", "2026-03-01") == 0
    run_output = capsys.readouterr().out
    assert "2 employees" in run_output

    assert _run(config_path, "payslip", "--employee", "E0001", "--period", "2026-03-01") == 0
    payslip_output = capsys.readouterr().out
    assert "Employee: E0001" in payslip_output
    assert "Net:" in payslip_output

    assert _run(config_path, "register", "--period", "2026-03-01") == 0
    register_output = capsys.readouterr().out
    lines = register_output.splitlines()
    assert lines[0] == "Pay Run Register: 2026-03-01..2026-03-31"
    assert any(line.startswith("E0001:") for line in lines)
    assert any(line.startswith("E0002:") for line in lines)


def test_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0


def test_missing_command_exits_nonzero():
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code != 0
