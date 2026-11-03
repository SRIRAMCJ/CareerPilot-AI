import sqlite3

from app.core import submission_database


def _database(tmp_path, monkeypatch):
    path = tmp_path / "careerpilot.db"
    monkeypatch.setattr(submission_database, "_database_path", lambda: path)
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE applications (id INTEGER PRIMARY KEY)")
        connection.execute("INSERT INTO applications (id) VALUES (7)")
    return path


def test_submission_attempt_can_only_be_claimed_once(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)

    first = submission_database.claim_submission_attempt(7, "https://jobs.example/apply")
    second = submission_database.claim_submission_attempt(7, "https://jobs.example/apply")

    assert first is not None
    assert first["status"] == "started"
    assert second is None


def test_submission_attempt_records_click_without_claiming_application_success(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    attempt = submission_database.claim_submission_attempt(7, "https://jobs.example/apply")

    updated = submission_database.finish_submission_attempt(attempt["id"], "clicked")
    fetched = submission_database.get_submission_attempt(7)

    assert updated["status"] == "clicked"
    assert fetched["status"] == "clicked"
    assert fetched["finished_at"] is not None
    assert submission_database.claim_submission_attempt(7, "https://jobs.example/apply") is None


def test_unknown_outcome_remains_locked_against_duplicate_submission(tmp_path, monkeypatch):
    _database(tmp_path, monkeypatch)
    attempt = submission_database.claim_submission_attempt(7, "https://jobs.example/apply")

    submission_database.finish_submission_attempt(attempt["id"], "outcome_unknown")

    assert submission_database.get_submission_attempt(7)["status"] == "outcome_unknown"
    assert submission_database.claim_submission_attempt(7, "https://jobs.example/apply") is None
