# voice-ai-backend

A language-agnostic **microservice** that converts voice recordings into structured expense transactions.
Built with FastAPI + Groq (Whisper STT + LLaMA NLP). Can be consumed by any client — Flutter, React Native, web, CLI, etc.

---

## Features

- **POST /v1/voice** — Upload an audio file, get back structured expense JSON
- Automatic multi-item splitting ("bread 73 and coffee 125" → two transactions)
- Supports m4a, wav, mp3, ogg, webm, mp4
- CORS configurable for any frontend
- Docker-first, single-command deploy
- `/health` endpoint for uptime monitoring

---

## Quick Start

### 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + [Docker Compose](https://docs.docker.com/compose/)
- A free [Groq API key](https://console.groq.com)

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set your GROQ_API_KEY
```

### 3. Run with Docker Compose

```bash
docker compose up --build
```

API is now live at `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

---

## API Reference

### `GET /health`

```json
{ "status": "ok", "version": "1.0.0", "service": "voice-expense-ai" }
```

### `POST /v1/voice`

| Field | Type | Description |
|-------|------|-------------|
| `file` | `multipart/form-data` | Audio file (m4a / wav / mp3 / ogg / webm / mp4) |

**Response**

```json
{
  "status": "success",
  "text": "7-11 bread 73 and a latte 125",
  "transactions": [
    { "amount": 73.0, "description": "7-11 bread", "category": "food" },
    { "amount": 125.0, "description": "latte",      "category": "drink" }
  ]
}
```

**Categories**: `food` · `drink` · `transport` · `shopping` · `housing` · `health` · `entertainment` · `other`

**Example cURL**

```bash
curl -X POST http://localhost:8000/v1/voice \
  -F "file=@recording.wav"
```

---

## Development (without Docker)

### Requirements

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)

```bash
poetry install
cp .env.example .env   # fill in GROQ_API_KEY
poetry run uvicorn app.main:app --reload
```

Run tests:

```bash
poetry run pytest tests/ -v
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | — | Groq API key (Whisper + LLaMA) |
| `PORT` | No | `8000` | Port to listen on |
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed origins |

---

## Deployment

### Fly.io

```bash
fly launch
fly secrets set GROQ_API_KEY=your_key_here
fly deploy
```

### Railway

```bash
railway up
railway variables set GROQ_API_KEY=your_key_here
```

### Self-hosted VPS

```bash
git clone <this-repo>
cd voice-expense-ai-backend
cp .env.example .env && nano .env
docker compose up -d
```

---

## Using as a Git Submodule

If you want to embed this backend inside another project:

```bash
# Inside your main project
git submodule add <this-repo-url> backend
git submodule update --init --recursive
```

Update the submodule later:

```bash
git submodule update --remote backend
```

---

## Integration Examples

### Flutter / Dart

```dart
final response = await dio.post(
  'http://localhost:8000/v1/voice',
  data: FormData.fromMap({
    'file': await MultipartFile.fromFile(path, filename: 'audio.wav'),
  }),
);
final transactions = response.data['transactions'] as List;
```

### JavaScript / Fetch

```js
const form = new FormData();
form.append('file', audioBlob, 'recording.wav');

const res = await fetch('http://localhost:8000/v1/voice', {
  method: 'POST',
  body: form,
});
const { transactions } = await res.json();
```

### Python

```python
import httpx

with open("recording.wav", "rb") as f:
    r = httpx.post("http://localhost:8000/v1/voice", files={"file": f})
print(r.json()["transactions"])
```

---

## License

MIT
