import asyncio

from app.routers import browser_automation


class FakeFileInput:
    def __init__(self):
        self.path = None

    async def get_attribute(self, name):
        return {"name": "resume_upload", "id": "resume-upload", "accept": ".pdf,.docx",
                "aria-label": "Upload resume"}.get(name)

    async def set_input_files(self, path):
        self.path = path


class FakeLocator:
    def __init__(self, fields):
        self.fields = fields

    async def count(self):
        return len(self.fields)

    def nth(self, index):
        return self.fields[index]


class FakePage:
    def __init__(self, fields):
        self.fields = fields

    def locator(self, selector):
        assert selector == 'input[type="file"]'
        return FakeLocator(self.fields)


def test_selected_resume_is_attached_only_to_resume_upload(tmp_path, monkeypatch):
    resume_path = tmp_path / "candidate.pdf"
    resume_path.write_bytes(b"%PDF-test")
    field = FakeFileInput()
    record = {"id": 4, "stored_path": str(resume_path), "filename": "candidate.pdf"}
    monkeypatch.setattr(browser_automation, "list_resume_records", lambda: [{"id": 4}])
    monkeypatch.setattr(browser_automation, "get_resume_record", lambda resume_id: record if resume_id == 4 else None)

    result = asyncio.run(browser_automation._attach_selected_resume(FakePage([field]), 4))

    assert result["status"] == "attached_for_review"
    assert result["resume_id"] == 4
    assert field.path == str(resume_path)


def test_resume_is_not_attached_to_unlabelled_file_input(tmp_path, monkeypatch):
    resume_path = tmp_path / "candidate.docx"
    resume_path.write_bytes(b"PK-test")
    class UnlabelledInput(FakeFileInput):
        async def get_attribute(self, name):
            return {"name": "upload", "id": "file", "accept": "*/*",
                    "aria-label": "Upload file"}.get(name)
    record = {"id": 5, "stored_path": str(resume_path), "filename": "candidate.docx"}
    monkeypatch.setattr(browser_automation, "list_resume_records", lambda: [{"id": 5}])
    monkeypatch.setattr(browser_automation, "get_resume_record", lambda resume_id: record)

    result = asyncio.run(browser_automation._attach_selected_resume(FakePage([UnlabelledInput()]), 5))

    assert result["status"] == "not_attached"
