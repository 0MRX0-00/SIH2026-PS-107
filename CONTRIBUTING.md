# Contributing to e-BIS Sahayak

Thank you for your interest in contributing to **e-BIS Sahayak** (Smart India Hackathon 2026 - Problem Statement #107)! We welcome contributions from developers, standards experts, translators, and open-source enthusiasts.

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Development Setup

### 1. Prerequisites
- **Python**: 3.10 or higher (recommended: 3.11+)
- **Node.js**: 18.x or higher (recommended: 20 LTS or 22 LTS)
- **Git**
- Optional: **Docker** and **Docker Compose**

### 2. Getting Started
1. **Fork and Clone** the repository:
   ```bash
   git clone https://github.com/0MRX0-00/SIH2026-PS-107.git
   cd SIH2026-PS-107
   ```
2. **Set up Environment Variables**:
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   ```
3. **Set up the Backend**:
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate

   pip install -r requirements.txt
   python -m app.preflight
   ```
4. **Set up the Frontend**:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

---

## Testing Guidelines

Before opening a pull request, please run all automated checks:

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```
All tests must pass with zero external network dependencies.

### Frontend Validation
```bash
cd frontend
npm run build
```
Verify that the Next.js production build succeeds with no type errors or unhandled warnings.

### Multilingual Parity
If you add or modify any UI copy:
- Ensure you update all three localization files:
  - `frontend/src/locales/en.json`
  - `frontend/src/locales/hi.json`
  - `frontend/src/locales/ta.json`
- Maintain 100% key parity across all 3 files.

---

## Pull Request Guidelines

1. Create a feature branch: `git checkout -b feat/your-feature-name` or `fix/your-fix-name`.
2. Commit with meaningful messages adhering to Conventional Commits:
   - `feat: add new laboratory search filter`
   - `fix: resolve rate limiter boundary condition`
   - `docs: update setup instructions`
3. Never commit `.env` files, API keys, or personal credentials.
4. Open a pull request against `main` using our PR template.

---

## License
By contributing to e-BIS Sahayak, you agree that your contributions will be licensed under the project's [Apache 2.0 License](LICENSE).

