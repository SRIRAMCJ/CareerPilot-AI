import re
from io import BytesIO

from docx import Document
from pypdf import PdfReader

SKILL_TERMS = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "SQL", "FastAPI",
    "Django", "Flask", "React", "Next.js", "Node.js", "AWS", "Azure", "GCP",
    "Docker", "Kubernetes", "PostgreSQL", "MongoDB", "Redis", "Git",
    "Machine Learning", "Deep Learning", "LLM", "RAG", "LangChain",
    "TensorFlow", "PyTorch", "Scikit-learn", "REST API", "GraphQL",
]


def extract_text(content: bytes, file_type: str) -> str:
    if file_type == "pdf":
        reader = PdfReader(BytesIO(content))
        if reader.is_encrypted:
            raise ValueError("Password-protected PDFs are not supported. Upload an unlocked PDF.")
        pages = reader.pages[:40]
        text = "\n".join(page.extract_text() or "" for page in pages)
    elif file_type == "docx":
        document = Document(BytesIO(content))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        for table in document.tables:
            for row in table.rows:
                paragraphs.append(" | ".join(cell.text for cell in row.cells))
        text = "\n".join(paragraphs)
    else:
        raise ValueError("Only PDF and DOCX resumes are supported.")
    return re.sub(r"[ \t]+", " ", text).strip()[:150_000]


def extract_facts(text: str) -> dict:
    lowered = text.casefold()
    skills = [
        skill for skill in SKILL_TERMS
        if re.search(rf"(?<![\w+#.]){re.escape(skill.casefold())}(?![\w+#.])", lowered)
    ]
    email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I)
    phone_match = re.search(r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)", text)
    return {
        "skills": skills,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
    }
