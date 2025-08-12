#!/usr/bin/env bash
set -e  # 에러 발생 시 즉시 종료

# 1. 가상환경 생성 (없으면)
if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv .venv
fi

# 2. 가상환경 활성화
source .venv/bin/activate

# 3. 패키지 설치 (개발 모드)
echo "[INFO] Installing dependencies..."
pip install --upgrade pip
pip install -e ".[dev]"

# 4. Playwright 브라우저 설치
echo "[INFO] Installing Playwright browser..."
playwright install chromium

# 5. pytest 실행
echo "[INFO] Running tests..."
pytest -q
