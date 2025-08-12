#!/usr/bin/env python3

import pytest
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from api.api_server import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_recorder_data():
    return {
        "buffer_duration": 30,
        "include_apps": ["Chrome", "Slack"],
        "recording_mode": "full_screen",
        "chunk_duration": 5.0,
        "max_clips": 20,
        "video_priority": 0,
        "context_priority": 0,
        "visual_task": "Test recording session"
    }

@pytest.fixture
def sample_query_data():
    return {
        "prompt": "What am I working on right now?",
        "interval_seconds": 30.0
    }

class TestAPIRoot:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Inframe Context API"
        assert data["version"] == "1.0.0"
        assert "recorders" in data["endpoints"]
        assert "queries" in data["endpoints"]
        assert "context" in data["endpoints"]

class TestRecorderEndpoints:
    def test_create_recorder(self, client):
        request_data = {"openai_api_key": "test-key", "cache_file": "/tmp/test"}
        response = client.post("/recorders", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "recorder_id" in data
    
    def test_add_recorder(self, client, sample_recorder_data):
        # First create a recorder
        create_data = {"openai_api_key": "test-key", "cache_file": "/tmp/test"}
        create_response = client.post("/recorders", json=create_data)
        assert create_response.status_code == 200
        recorder_id = create_response.json()["recorder_id"]
        
        # Then add a recorder configuration
        add_data = {
            "recorder_id": recorder_id,
            **sample_recorder_data
        }
        response = client.post("/recorders/add", json=add_data)
        assert response.status_code == 200
        data = response.json()
        assert "internal_recorder_id" in data
        return recorder_id, data["internal_recorder_id"]
    
    def test_start_recorder(self, client, sample_recorder_data):
        # Create and add recorder
        recorder_id, internal_recorder_id = self.test_add_recorder(client, sample_recorder_data)
        
        # Start recording
        response = client.post(f"/recorders/{recorder_id}/start/{internal_recorder_id}")
        assert response.status_code == 200
        data = response.json()
        assert "internal_recorder_id" in data
    
    def test_stop_recorder(self, client, sample_recorder_data):
        # Create, add, and start recorder
        recorder_id, internal_recorder_id = self.test_add_recorder(client, sample_recorder_data)
        
        # Stop recording
        response = client.post(f"/recorders/{recorder_id}/stop/{internal_recorder_id}")
        if response.status_code != 200:
            print(f"Error response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "internal_recorder_id" in data
    
    def test_get_recorder_status(self, client, sample_recorder_data):
        # Create and add recorder
        recorder_id, internal_recorder_id = self.test_add_recorder(client, sample_recorder_data)
        
        # Get status
        response = client.get(f"/recorders/{recorder_id}/status/{internal_recorder_id}")
        assert response.status_code == 200
        data = response.json()
        assert "buffer_duration" in data
        assert "recording_mode" in data

class TestQueryEndpoints:
    def test_create_query(self, client):
        request_data = {
            "api_key": "test-key",
            "model": "gpt-4"
        }
        response = client.post("/queries", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "query_id" in data
    
    def test_add_query(self, client, sample_query_data):
        # First create a query
        create_data = {"api_key": "test-key", "model": "gpt-4"}
        create_response = client.post("/queries", json=create_data)
        assert create_response.status_code == 200
        query_id = create_response.json()["query_id"]
        
        # Create a recorder (don't start it yet)
        recorder_data = {"openai_api_key": "test-key", "cache_file": "/tmp/test"}
        recorder_response = client.post("/recorders", json=recorder_data)
        assert recorder_response.status_code == 200
        recorder_id = recorder_response.json()["recorder_id"]
        
        # Then add a query (should work even if recorder not started)
        add_data = {
            "query_id": query_id,
            "recorder_id": recorder_id,
            **sample_query_data
        }
        response = client.post("/queries/add", json=add_data)
        assert response.status_code == 200
        data = response.json()
        assert "internal_query_id" in data
        return query_id, data["internal_query_id"]
    
    def test_start_query(self, client, sample_query_data):
        # Create and add query
        query_id, internal_query_id = self.test_add_query(client, sample_query_data)
        
        # Try to start query without starting recorder - should fail
        response = client.post(f"/queries/{query_id}/start/{internal_query_id}")
        assert response.status_code == 500  # Should fail because recorder not running
        error_detail = response.json()["detail"]
        assert "Failed to start query" in error_detail
    
    def test_start_query_with_running_recorder(self, client, sample_query_data):
        # Create and add query
        query_id, internal_query_id = self.test_add_query(client, sample_query_data)
        
        # Get recorder info and start it
        # We need to get the recorder_id from the query somehow...
        # For now, let's create a fresh setup
        recorder_data = {"openai_api_key": "test-key", "cache_file": "/tmp/test"}
        recorder_response = client.post("/recorders", json=recorder_data)
        recorder_id = recorder_response.json()["recorder_id"]
        
        # Add recorder configuration
        recorder_config = {
            "recorder_id": recorder_id,
            "buffer_duration": 30,
            "recording_mode": "full_screen"
        }
        add_recorder_response = client.post("/recorders/add", json=recorder_config)
        internal_recorder_id = add_recorder_response.json()["internal_recorder_id"]
        
        # Start the recorder
        start_recorder_response = client.post(f"/recorders/{recorder_id}/start/{internal_recorder_id}")
        assert start_recorder_response.status_code == 200
        
        # Create new query for this running recorder
        create_data = {"api_key": "test-key", "model": "gpt-4"}
        create_response = client.post("/queries", json=create_data)
        new_query_id = create_response.json()["query_id"]
        
        add_query_data = {
            "query_id": new_query_id,
            "recorder_id": recorder_id,
            **sample_query_data
        }
        add_query_response = client.post("/queries/add", json=add_query_data)
        new_internal_query_id = add_query_response.json()["internal_query_id"]
        
        # Now start query - should succeed
        response = client.post(f"/queries/{new_query_id}/start/{new_internal_query_id}")
        assert response.status_code == 200
        data = response.json()
        assert "internal_query_id" in data

    def test_stop_query(self, client, sample_query_data):
        # Create, add, and start query
        query_id, internal_query_id = self.test_add_query(client, sample_query_data)
        
        # Stop query (should work even if not started)
        response = client.post(f"/queries/{query_id}/stop/{internal_query_id}")
        assert response.status_code == 200
        data = response.json()
        assert "internal_query_id" in data

class TestAPIErrorHandling:
    def test_invalid_recording_mode(self, client):
        # First create a recorder
        create_data = {"openai_api_key": "test-key", "cache_file": "/tmp/test"}
        create_response = client.post("/recorders", json=create_data)
        assert create_response.status_code == 200
        recorder_id = create_response.json()["recorder_id"]
        
        request_data = {
            "recorder_id": recorder_id,
            "recording_mode": "invalid_mode",
            "buffer_duration": 30
        }
        response = client.post("/recorders/add", json=request_data)
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        response = client.post("/recorders", json={})
        assert response.status_code == 422
    
    def test_invalid_json(self, client):
        response = client.post("/recorders", data="invalid json", headers={"Content-Type": "application/json"})
        assert response.status_code == 422

class TestAPIIntegration:
    def test_full_workflow_api_only(self, client, sample_recorder_data, sample_query_data):
        """Test API workflow without actually starting heavy recording systems"""
        # Create recorder
        create_data = {"openai_api_key": "test-key", "cache_file": "/tmp/test"}
        create_response = client.post("/recorders", json=create_data)
        assert create_response.status_code == 200
        recorder_id = create_response.json()["recorder_id"]
        
        # Add recorder configuration
        add_data = {
            "recorder_id": recorder_id,
            **sample_recorder_data
        }
        add_response = client.post("/recorders/add", json=add_data)
        assert add_response.status_code == 200
        internal_recorder_id = add_response.json()["internal_recorder_id"]
        
        # Create query
        create_query_data = {"openai_api_key": "test-key", "model": "gpt-4o-mini"}
        create_query_response = client.post("/queries", json=create_query_data)
        assert create_query_response.status_code == 200
        query_id = create_query_response.json()["query_id"]
        
        # Add query configuration
        add_query_data = {
            "query_id": query_id,
            "recorder_id": recorder_id,
            **sample_query_data
        }
        add_query_response = client.post("/queries/add", json=add_query_data)
        assert add_query_response.status_code == 200
        internal_query_id = add_query_response.json()["internal_query_id"]
        
        # Try to start query (should fail because recorder is not running)
        start_query_response = client.post(f"/queries/{query_id}/start/{internal_query_id}")
        assert start_query_response.status_code == 500
        assert "Failed to start query" in start_query_response.json()["detail"]
        
        print("✅ API workflow test completed (without heavy recording)")

    def test_shutdown_endpoint(self, client, sample_recorder_data):
        """Test the shutdown endpoint"""
        # Create a recorder first
        create_data = {"openai_api_key": "test-key", "cache_file": "/tmp/test"}
        create_response = client.post("/recorders", json=create_data)
        assert create_response.status_code == 200
        recorder_id = create_response.json()["recorder_id"]
        
        # Add recorder configuration
        add_data = {
            "recorder_id": recorder_id,
            **sample_recorder_data
        }
        add_response = client.post("/recorders/add", json=add_data)
        assert add_response.status_code == 200
        
        # Now shutdown the system
        shutdown_response = client.post("/shutdown")
        assert shutdown_response.status_code == 200
        
        response_data = shutdown_response.json()
        assert "message" in response_data
        assert "System shutdown complete" in response_data["message"]
        assert "results" in response_data
        
        # Try to access the recorder after shutdown (should fail)
        status_response = client.get(f"/recorders/{recorder_id}/status/test")
        assert status_response.status_code == 404  # Recorder should be gone

    @pytest.mark.slow
    def test_full_workflow(self, client, sample_recorder_data, sample_query_data):
        """Full workflow including actual recording - marked as slow test"""
        # Create recorder
        create_data = {"openai_api_key": "test-key", "cache_file": "/tmp/test"}
        create_response = client.post("/recorders", json=create_data)
        assert create_response.status_code == 200
        recorder_id = create_response.json()["recorder_id"]
        
        # Add recorder configuration
        add_data = {
            "recorder_id": recorder_id,
            **sample_recorder_data
        }
        add_response = client.post("/recorders/add", json=add_data)
        assert add_response.status_code == 200
        internal_recorder_id = add_response.json()["internal_recorder_id"]
        
        # Start recording
        start_response = client.post(f"/recorders/{recorder_id}/start/{internal_recorder_id}")
        assert start_response.status_code == 200
        
        # Stop recording
        stop_response = client.post(f"/recorders/{recorder_id}/stop/{internal_recorder_id}")
        assert stop_response.status_code == 200 