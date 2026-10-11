"""
Portable Clean Submission Packager for e-BIS Sahayak (SIH 2026 Problem Statement #107).
Builds a sanitized, portable zip archive with POSIX paths (forward slashes only),
excluding all secrets, environment files, node_modules, build caches, and venvs.
"""
import os
import sys
import zipfile
import shutil

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST_DIR = os.path.join(ROOT_DIR, "dist")
OUTPUT_ZIP = os.path.join(DIST_DIR, "ebis_sahayak_sih2026_clean_submission.zip")
TEST_EXTRACT_DIR = os.path.join(DIST_DIR, "clean_extracted_verification")

EXCLUDED_DIR_NAMES = {
    ".git",
    "node_modules",
    ".next",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".kilo",
    ".gemini",
    "dist",
    "backups",
}

EXCLUDED_FILE_PATTERNS = {
    ".env",
    ".env.local",
    ".env.development.local",
    ".env.test.local",
    ".env.production.local",
    ".DS_Store",
    "Thumbs.db",
    "load_test_results.json",
    "evaluation_report.json",
    "tsconfig.tsbuildinfo",
}

EXCLUDED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".log",
    ".zip",
    ".tar.gz",
    ".tgz",
    ".tsbuildinfo",
}


def should_include(rel_path: str) -> bool:
    # Normalize path separators
    norm_path = rel_path.replace("\\", "/")
    parts = norm_path.split("/")

    # Check excluded directory names in path
    for part in parts:
        if part in EXCLUDED_DIR_NAMES:
            return False

    filename = parts[-1]

    # Check exact excluded filenames
    if filename in EXCLUDED_FILE_PATTERNS:
        return False

    # Check excluded file extensions
    _, ext = os.path.splitext(filename)
    if ext in EXCLUDED_EXTENSIONS:
        return False

    return True


def create_clean_zip():
    os.makedirs(DIST_DIR, exist_ok=True)
    if os.path.exists(OUTPUT_ZIP):
        os.remove(OUTPUT_ZIP)

    included_files = []

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ROOT_DIR):
            # Exclude directories in place so os.walk doesn't traverse them
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES]

            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, ROOT_DIR)

                if should_include(rel_path):
                    # Enforce strict POSIX portable relative paths inside the archive
                    posix_arcname = rel_path.replace("\\", "/")
                    zf.write(abs_path, arcname=posix_arcname)
                    included_files.append(posix_arcname)

    print(f"[SUCCESS] Packaged clean submission zip: {OUTPUT_ZIP}")
    print(f"[INFO] Total files archived: {len(included_files)}")
    zip_size_kb = os.path.getsize(OUTPUT_ZIP) / 1024
    print(f"[INFO] Archive size: {zip_size_kb:.2f} KB ({zip_size_kb / 1024:.2f} MB)")
    return OUTPUT_ZIP, included_files


def verify_extracted_archive(zip_path: str):
    if os.path.exists(TEST_EXTRACT_DIR):
        shutil.rmtree(TEST_EXTRACT_DIR)
    os.makedirs(TEST_EXTRACT_DIR, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        # Check all file names for illegal backslashes or absolute paths
        for info in zf.infolist():
            if "\\" in info.filename:
                raise ValueError(f"Non-portable path with backslash found: {info.filename}")
            if info.filename.startswith("/") or info.filename.startswith(".."):
                raise ValueError(f"Illegal leading slash or relative escape found: {info.filename}")

        zf.extractall(TEST_EXTRACT_DIR)

    extracted_count = sum(len(files) for _, _, files in os.walk(TEST_EXTRACT_DIR))
    print(f"[SUCCESS] Extraction verified cleanly at: {TEST_EXTRACT_DIR}")
    print(f"[INFO] Total extracted files: {extracted_count}")

    # Verify essential files exist in extracted package
    essential_files = [
        "backend/app/main.py",
        "backend/app/core/config.py",
        "backend/app/services/official_source_service.py",
        "backend/app/services/query_service.py",
        "backend/app/services/groq_service.py",
        "backend/requirements.txt",
        "frontend/package.json",
        "frontend/src/app/page.tsx",
        "docker-compose.yml",
        ".env.example",
        ".env.production.example",
        "README.md",
    ]

    for ef in essential_files:
        p = os.path.join(TEST_EXTRACT_DIR, ef)
        if not os.path.exists(p):
            raise FileNotFoundError(f"Essential file missing from clean archive: {ef}")

    print("[SUCCESS] All essential application files verified in clean extraction.")
    return extracted_count


if __name__ == "__main__":
    zip_p, files = create_clean_zip()
    verify_extracted_archive(zip_p)
