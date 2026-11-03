# Optional Local AI Drafting

CareerPilot can use a local Ollama server to generate an additional cover-letter draft. All deterministic matching, resume extraction, job discovery, application tracking, and DOCX template generation work without an LLM.

## Configure

1. Install and start Ollama locally.
2. Pull a model suitable for instruction following.
3. In the repository root `.env`, set:

```dotenv
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=your-installed-model-name
```

4. Restart the CareerPilot backend.
5. In Applications, choose **Local AI cover letter**.

The backend only accepts Ollama URLs on loopback addresses. It sends the saved candidate profile and the selected job description to the local model. Job descriptions are treated as untrusted reference data, not instructions.

## Important

- The generated letter is a draft, not verified truth.
- The prompt prohibits inventing candidate facts, but local language models can still make mistakes.
- Review every sentence against your actual experience before using it.
- No candidate data is sent to a cloud AI provider by this integration.
- Set `AI_PROVIDER=none` to disable local AI drafting.
