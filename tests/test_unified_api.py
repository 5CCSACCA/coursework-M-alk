"""
Stage 3: Unified API Tests (BitNet + YOLO)
"""
import json
import os
import sys
import time

import pytest
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")
TEST_IMAGE = os.getenv("TEST_IMAGE", "test_image.jpeg")
DEFAULT_TIMEOUT = 5


def _require_api():
    try:
        return requests.get(f"{API_URL}/health", timeout=DEFAULT_TIMEOUT)
    except requests.exceptions.ConnectionError as exc:
        raise AssertionError(
            f"API server not reachable at {API_URL}. "
            "Start it with: bash scripts/start_api.sh"
        ) from exc


def test_health_check():
    """Health check test"""
    response = _require_api()
    assert response.status_code == 200, f"Health endpoint returned {response.status_code}"
    payload = response.json()
    assert "status" in payload
    assert payload["status"] in {"ok", "degraded"}


def test_bitnet_completion():
    """BitNet text generation test"""
    _require_api()
    prompt = "What is artificial intelligence?"

    start_time = time.time()
    response = requests.post(
        f"{API_URL}/bitnet/completion",
        json={
            "prompt": f"Answer briefly: {prompt}",
            "n_predict": 20,
            "temperature": 0.7,
        },
        timeout=60,
    )
    elapsed = time.time() - start_time

    assert response.status_code == 200, f"BitNet endpoint failed: {response.text}"
    result = response.json()
    assert result.get("content"), "BitNet response missing content"
    assert elapsed < 120, "BitNet completion took too long"


@pytest.mark.skipif(not os.path.exists(TEST_IMAGE), reason="test image missing")
def test_yolo_detection():
    """YOLO detection test"""
    _require_api()

    with open(TEST_IMAGE, "rb") as f:
        files = {"file": ("test_image.jpeg", f, "image/jpeg")}
        response = requests.post(
            f"{API_URL}/yolo/detect",
            files=files,
            timeout=30,
        )

    assert response.status_code == 200, f"YOLO endpoint failed: {response.text}"
    result = response.json()
    assert "detections" in result
    assert "total_objects" in result


def main():
    """Run tests with pytest"""
    import pytest as _pytest

    exit_code = _pytest.main([__file__])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
