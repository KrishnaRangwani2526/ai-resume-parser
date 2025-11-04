# tests/test_api.py

import pytest
from httpx import AsyncClient
from src.main import app   # ✅ updated to match your folder structure
import io


@pytest.mark.asyncio
async def test_health():
    """
    ✅ Test: Health check endpoint should return status 'ok'
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data


@pytest.mark.asyncio
async def test_upload_and_get():
    """
    ✅ Test: Upload a resume and then fetch it by ID
    """
    # Simulate a text resume file
    sample_text = b"""
    John Doe
    john@example.com
    Experienced Python developer with AWS and Docker
    2020 - 2022 Software Engineer at Acme Corp
    """

    files = {"file": ("resume.txt", io.BytesIO(sample_text), "text/plain")}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Upload the resume
        upload_response = await ac.post("/upload", files=files)
        assert upload_response.status_code in (200, 201)

        upload_data = upload_response.json()
        assert "resume_id" in upload_data
        resume_id = upload_data["resume_id"]

        # Fetch the uploaded resume by ID
        get_response = await ac.get(f"/resume/{resume_id}")
        assert get_response.status_code == 200

        resume_data = get_response.json()
        assert resume_data["resume_id"] == resume_id
        assert "extracted_data" in resume_data


@pytest.mark.asyncio
async def test_match_endpoint():
    """
    ✅ Test: Upload a resume, then match it with a job description
    """
    # Simulate a text resume file
    sample_text = b"""
    Jane Doe
    jane@example.com
    Data Engineer skilled in Python, SQL, and ETL pipelines
    2019 - 2021 Data Engineer at XYZ Tech
    """

    files = {"file": ("resume.txt", io.BytesIO(sample_text), "text/plain")}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Upload the resume
        upload_response = await ac.post("/upload", files=files)
        assert upload_response.status_code in (200, 201)

        upload_data = upload_response.json()
        assert "resume_id" in upload_data
        resume_id = upload_data["resume_id"]

        # Match resume with a sample job description
        match_payload = {
            "job_description": "Looking for a Python Data Engineer with SQL experience"
        }

        match_response = await ac.post(f"/match/{resume_id}", json=match_payload)
        assert match_response.status_code == 200

        match_data = match_response.json()
        assert "score" in match_data
        assert "recommendation" in match_data
