# Pinned, reproducible. Replace the digest below with the one from:
#   docker pull python:3.12.7-slim-bookworm && docker inspect --format='{{index .RepoDigests 0}}' python:3.12.7-slim-bookworm
# (harbor lint --extend-select unpinned-image wants a digest.)
FROM python:3.12.7-slim-bookworm@sha256:60d9996b6a8a3689d36db740b49f4327be3be09a21122bd02fb8895abb38b50d

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=UTC

# tzdata: zoneinfo for America/Chicago, America/New_York. git: used by solution/solve.sh (git apply).
RUN apt-get update \
 && apt-get install -y --no-install-recommends tzdata less git \
 && rm -rf /var/lib/apt/lists/*

# Exact pins (harbor lint: unpinned-python-dependency). Confirm these resolve in Phase 0, then freeze.
RUN pip install \
    pandas==2.2.3 \
    numpy==2.1.3 \
    pyyaml==6.0.2 \
    pytest==8.3.3

WORKDIR /app
# Only the seed application. NEVER copy tests/ or solution/ here (harbor lint: agent-image-test-leak).
COPY app/ /app/
RUN mkdir -p /app/out /logs/verifier /logs/agent
