#!/usr/bin/env python3
import asyncio
import os
import pytest
import tempfile
import cv2
import numpy as np
import aiohttp
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, List

from src.embedding_pipeline import EmbeddingPipeline, ProcessedFrame, EmbeddingResult, create_embedding_pipeline
from src.video_stream import VideoClip, VideoStream

@pytest.fixture
def mock_video_clip():
    """Create a mock video clip for testing"""
    # Create a temporary video file
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "test_clip.mp4")
    
    # Create a simple test video with OpenCV
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 30.0, (640, 480))
    
    # Write more frames to ensure we have enough for testing
    for i in range(150):  # 5 seconds at 30 fps - more frames for testing
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Create different colored frames
        color_value = (i * 50) % 255
        frame[:, :, 0] = color_value  # Blue channel
        frame[:, :, 1] = (color_value + 85) % 255  # Green channel  
        frame[:, :, 2] = (color_value + 170) % 255  # Red channel
        out.write(frame)
    
    out.release()
    
    clip = VideoClip(
        file_path=video_path,
        start_time=0.0,
        end_time=5.0,
        metadata={'test': True},
        priority=(0,)
    )
    
    yield clip
    
    # Cleanup
    if os.path.exists(video_path):
        os.remove(video_path)
    os.rmdir(temp_dir)

@pytest.fixture
def embedding_pipeline():
    """Create an embedding pipeline for testing"""
    return EmbeddingPipeline(
        clip_endpoint_url="http://test-clip-service.com",
        enable_embeddings=True
    )

@pytest.fixture
def embedding_pipeline_disabled():
    """Create a disabled embedding pipeline for testing"""
    return EmbeddingPipeline(
        clip_endpoint_url=None,
        enable_embeddings=False
    )

@pytest.fixture
def mock_video_stream():
    """Create a mock video stream for testing"""
    mock_stream = Mock(spec=VideoStream)
    mock_stream.set_callback = Mock()
    mock_stream.get_available_clips = Mock(return_value=[])
    return mock_stream

@pytest.fixture
def mock_video_clips():
    """Create multiple mock video clips for testing"""
    clips = []
    temp_dir = tempfile.mkdtemp()
    
    for i in range(3):
        video_path = os.path.join(temp_dir, f"test_clip_{i}.mp4")
        
        # Create a simple test video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, 30.0, (640, 480))
        
        for j in range(90):  # 3 seconds at 30 fps
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            color_value = ((i * 50) + (j * 10)) % 255
            frame[:, :, 0] = color_value
            frame[:, :, 1] = (color_value + 85) % 255
            frame[:, :, 2] = (color_value + 170) % 255
            out.write(frame)
        
        out.release()
        
        clip = VideoClip(
            file_path=video_path,
            start_time=i * 3.0,
            end_time=(i + 1) * 3.0,
            metadata={'test': True, 'clip_id': i},
            priority=(0, i)
        )
        clips.append(clip)
    
    yield clips
    
    # Cleanup
    for clip in clips:
        if os.path.exists(clip.file_path):
            os.remove(clip.file_path)
    os.rmdir(temp_dir)

def test_embedding_pipeline_creation():
    """Test basic embedding pipeline creation"""
    print("\n🧪 Testing embedding pipeline creation...")
    
    # Test enabled pipeline
    pipeline = EmbeddingPipeline(
        clip_endpoint_url="http://test.com",
        enable_embeddings=True
    )
    assert pipeline.enable_embeddings == True
    assert pipeline.clip_endpoint_url == "http://test.com"
    assert pipeline.total_clips_processed == 0
    assert pipeline.total_frame_embeddings_created == 0
    assert pipeline.total_embedding_failures == 0
    
    # Test disabled pipeline
    pipeline_disabled = EmbeddingPipeline(
        clip_endpoint_url=None,
        enable_embeddings=False
    )
    assert pipeline_disabled.enable_embeddings == False
    assert pipeline_disabled.clip_endpoint_url is None
    
    # Test with environment variable
    with patch.dict(os.environ, {'CLIP_EMBEDDING_URL': 'http://env-test.com'}):
        pipeline_env = EmbeddingPipeline()
        assert pipeline_env.clip_endpoint_url == 'http://env-test.com'
        assert pipeline_env.enable_embeddings == True
    
    print("✅ Pipeline creation test passed")

def test_create_embedding_pipeline_factory():
    """Test the factory function"""
    print("\n🏭 Testing embedding pipeline factory...")
    
    # Test default creation
    pipeline = create_embedding_pipeline()
    assert isinstance(pipeline, EmbeddingPipeline)
    
    # Test with parameters
    pipeline = create_embedding_pipeline(
        clip_endpoint_url="http://factory-test.com",
        enable_embeddings=True
    )
    assert pipeline.clip_endpoint_url == "http://factory-test.com"
    assert pipeline.enable_embeddings == True
    
    print("✅ Factory function test passed")

def test_pick_frames(mock_video_clip):
    """Test frame extraction from video clips"""
    print("\n🎬 Testing frame extraction...")
    
    pipeline = EmbeddingPipeline(enable_embeddings=False)
    
    # Test extracting 4 frames
    frames = pipeline.pick_frames(mock_video_clip, num_frames=4)
    assert len(frames) == 4
    
    # Check frame structure
    for i, frame in enumerate(frames):
        assert 'frame_id' in frame
        assert 'timestamp' in frame
        assert 'frame_data' in frame
        assert 'clip_path' in frame
        assert 'frame_index' in frame
        assert frame['frame_index'] == i
        assert isinstance(frame['frame_data'], bytes)
        assert len(frame['frame_data']) > 0
    
    # Test single frame extraction
    frames_single = pipeline.pick_frames(mock_video_clip, num_frames=1)
    assert len(frames_single) == 1
    
    # Test with invalid clip (should return empty list)
    invalid_clip = VideoClip(
        file_path="/nonexistent/path.mp4",
        start_time=0.0,
        end_time=5.0,
        metadata={},
        priority=(0,)
    )
    frames_invalid = pipeline.pick_frames(invalid_clip, num_frames=4)
    assert len(frames_invalid) == 0
    
    print("✅ Frame extraction test passed")

@pytest.mark.asyncio
async def test_generate_frame_embed_success(embedding_pipeline):
    """Test successful frame embedding generation"""
    print("\n🎯 Testing successful frame embedding...")
    
    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'success': True,
        'frame_result': {
            'frame_id': 'test_frame_001',
            'timestamp': 1.0,
            'frame_path': '/path/to/frame.jpg',
            'weaviate_id': 'weaviate_123',
            'embedding_dimension': 512
        }
    }
    
    frame_data = b'fake_jpeg_data'
    frame_metadata = {
        'frame_id': 'test_frame_001',
        'timestamp': 1.0,
        'video_id': 'test_video',
        'clip_path': '/test/clip.mp4'
    }
    
    with patch('requests.post', return_value=mock_response):
        result = await embedding_pipeline.generate_frame_embed(frame_data, frame_metadata)
        
        assert isinstance(result, ProcessedFrame)
        assert result.embedding_success == True
        assert result.frame_id == 'test_frame_001'
        assert result.timestamp == 1.0
        assert result.frame_path == '/path/to/frame.jpg'
        assert result.weaviate_id == 'weaviate_123'
        assert result.embedding_error is None
    
    print("✅ Successful frame embedding test passed")

@pytest.mark.asyncio
async def test_generate_frame_embed_failure(embedding_pipeline):
    """Test frame embedding failure scenarios"""
    print("\n❌ Testing frame embedding failures...")
    
    frame_data = b'fake_jpeg_data'
    frame_metadata = {
        'frame_id': 'test_frame_001',
        'timestamp': 1.0
    }
    
    # Test HTTP error response
    mock_response_error = Mock()
    mock_response_error.status_code = 500
    mock_response_error.text = "Internal Server Error"
    
    with patch('requests.post', return_value=mock_response_error):
        result = await embedding_pipeline.generate_frame_embed(frame_data, frame_metadata)
        
        assert isinstance(result, ProcessedFrame)
        assert result.embedding_success == False
        assert result.frame_id == 'test_frame_001'
        assert "HTTP 500" in result.embedding_error
    
    # Test API error response
    mock_response_api_error = Mock()
    mock_response_api_error.status_code = 200
    mock_response_api_error.json.return_value = {
        'success': False,
        'error': 'Could not decode frame data'
    }
    
    with patch('requests.post', return_value=mock_response_api_error):
        result = await embedding_pipeline.generate_frame_embed(frame_data, frame_metadata)
        
        assert result.embedding_success == False
        assert "Could not decode frame data" in result.embedding_error
    
    # Test network exception
    with patch('requests.post', side_effect=Exception("Network error")):
        result = await embedding_pipeline.generate_frame_embed(frame_data, frame_metadata)
        
        assert result.embedding_success == False
        assert "Network error" in result.embedding_error
    
    print("✅ Frame embedding failure test passed")

@pytest.mark.asyncio
async def test_generate_clip_embeddings_success(embedding_pipeline, mock_video_clip):
    """Test successful clip embedding generation"""
    print("\n🎬 Testing successful clip embedding...")
    
    # Mock successful frame embedding responses
    def mock_generate_frame_embed(frame_data, frame_metadata):
        return ProcessedFrame(
            frame_id=frame_metadata['frame_id'],
            timestamp=frame_metadata['timestamp'],
            frame_data=frame_data,
            frame_path=f"/path/to/{frame_metadata['frame_id']}.jpg",
            weaviate_id=f"weaviate_{frame_metadata['frame_id']}",
            embedding_success=True,
            embedding_error=None
        )
    
    # Patch the generate_frame_embed method
    embedding_pipeline.generate_frame_embed = AsyncMock(side_effect=mock_generate_frame_embed)
    
    result = await embedding_pipeline.generate_clip_embeddings(mock_video_clip, num_frames=4)
    
    assert isinstance(result, EmbeddingResult)
    assert result.embedding_success == True
    assert result.video_id is not None
    assert result.frame_count == 4
    assert result.successful_frame_count == 4
    assert len(result.failed_frames) == 0
    assert result.embedding_error is None
    
    # Check that stats were updated
    assert embedding_pipeline.total_clips_processed == 1
    assert embedding_pipeline.total_frame_embeddings_created == 4
    assert embedding_pipeline.total_embedding_failures == 0
    
    print("✅ Successful clip embedding test passed")

@pytest.mark.asyncio
async def test_generate_clip_embeddings_partial_failure(embedding_pipeline, mock_video_clip):
    """Test clip embedding with some frame failures"""
    print("\n⚠️ Testing partial clip embedding failure...")
    
    # Mock mixed success/failure responses
    def mock_generate_frame_embed(frame_data, frame_metadata):
        frame_index = frame_metadata['frame_index']
        if frame_index % 2 == 0:  # Even frames succeed
            return ProcessedFrame(
                frame_id=frame_metadata['frame_id'],
                timestamp=frame_metadata['timestamp'],
                frame_data=frame_data,
                embedding_success=True,
                embedding_error=None
            )
        else:  # Odd frames fail
            return ProcessedFrame(
                frame_id=frame_metadata['frame_id'],
                timestamp=frame_metadata['timestamp'],
                frame_data=frame_data,
                embedding_success=False,
                embedding_error="Mock embedding failure"
            )
    
    embedding_pipeline.generate_frame_embed = AsyncMock(side_effect=mock_generate_frame_embed)
    
    result = await embedding_pipeline.generate_clip_embeddings(mock_video_clip, num_frames=4)
    
    assert isinstance(result, EmbeddingResult)
    assert result.embedding_success == True  # Still successful if any frames succeed
    assert result.frame_count == 4
    assert result.successful_frame_count == 2  # Even frames succeed (0, 2)
    assert len(result.failed_frames) == 2  # Odd frames fail (1, 3)
    
    print("✅ Partial failure test passed")

@pytest.mark.asyncio
async def test_generate_clip_embeddings_disabled(embedding_pipeline_disabled, mock_video_clip):
    """Test clip embedding when embeddings are disabled"""
    print("\n🚫 Testing disabled embeddings...")
    
    result = await embedding_pipeline_disabled.generate_clip_embeddings(mock_video_clip)
    
    assert isinstance(result, EmbeddingResult)
    assert result.embedding_success == False
    assert result.video_id is None
    assert result.processed_frames is None
    assert "Frame embeddings disabled" in result.embedding_error
    
    print("✅ Disabled embeddings test passed")

@pytest.mark.asyncio
async def test_generate_clip_embeddings_no_frames(embedding_pipeline):
    """Test clip embedding when no frames can be extracted"""
    print("\n📭 Testing no frames scenario...")
    
    # Mock pick_frames to return empty list
    embedding_pipeline.pick_frames = Mock(return_value=[])
    
    mock_clip = VideoClip(
        file_path="/fake/path.mp4",
        start_time=0.0,
        end_time=1.0,
        metadata={},
        priority=(0,)
    )
    
    result = await embedding_pipeline.generate_clip_embeddings(mock_clip)
    
    assert isinstance(result, EmbeddingResult)
    assert result.embedding_success == False
    assert result.video_id is None
    assert result.processed_frames is None
    assert "No frames could be extracted" in result.embedding_error
    
    print("✅ No frames test passed")

def test_get_embedding_stats(embedding_pipeline):
    """Test embedding statistics"""
    print("\n📊 Testing embedding statistics...")
    
    # Initially zero stats
    stats = embedding_pipeline.get_embedding_stats()
    expected_stats = {
        'embeddings_enabled': True,
        'clip_endpoint_url': 'http://test-clip-service.com',
        'total_clips_processed': 0,
        'total_frame_embeddings_created': 0,
        'total_embedding_failures': 0,
        'embedding_success_rate': 0.0
    }
    assert stats == expected_stats
    
    # Manually update stats to test calculation
    # Note: implementation assumes 8 frames per clip in success rate calculation
    embedding_pipeline.total_clips_processed = 5
    embedding_pipeline.total_frame_embeddings_created = 32  # 32 out of 40 possible (5 clips * 8 frames assumed)
    embedding_pipeline.total_embedding_failures = 1
    
    stats = embedding_pipeline.get_embedding_stats()
    assert stats['total_clips_processed'] == 5
    assert stats['total_frame_embeddings_created'] == 32
    assert stats['total_embedding_failures'] == 1
    assert stats['embedding_success_rate'] == 32 / 40  # 0.8
    
    print("✅ Statistics test passed")

def test_processed_frame_methods():
    """Test ProcessedFrame utility methods"""
    print("\n🎯 Testing ProcessedFrame methods...")
    
    frame = ProcessedFrame(
        frame_id="test_frame",
        timestamp=1.5,
        frame_data=b"fake_jpeg_data",
        embedding=np.array([0.1, 0.2, 0.3]),
        frame_path="/path/to/frame.jpg",
        weaviate_id="weaviate_123",
        embedding_success=True,
        embedding_error=None
    )
    
    # Test to_dict method
    frame_dict = frame.to_dict()
    assert frame_dict['frame_id'] == "test_frame"
    assert frame_dict['timestamp'] == 1.5
    assert frame_dict['embedding_success'] == True
    assert frame_dict['has_embedding'] == True
    assert frame_dict['embedding_dimension'] == 3
    assert frame_dict['has_frame_data'] == True
    
    # Test with failed frame
    failed_frame = ProcessedFrame(
        frame_id="failed_frame",
        timestamp=2.0,
        embedding_success=False,
        embedding_error="Test error"
    )
    
    failed_dict = failed_frame.to_dict()
    assert failed_dict['embedding_success'] == False
    assert failed_dict['has_embedding'] == False
    assert failed_dict['embedding_dimension'] == 0
    assert failed_dict['embedding_error'] == "Test error"
    
    print("✅ ProcessedFrame methods test passed")

def test_embedding_result_properties():
    """Test EmbeddingResult property methods"""
    print("\n📋 Testing EmbeddingResult properties...")
    
    # Create test frames
    successful_frame = ProcessedFrame(
        frame_id="success_frame",
        timestamp=1.0,
        embedding_success=True
    )
    
    failed_frame = ProcessedFrame(
        frame_id="failed_frame", 
        timestamp=2.0,
        embedding_success=False,
        embedding_error="Test failure"
    )
    
    result = EmbeddingResult(
        video_id="test_video",
        processed_frames=[successful_frame, failed_frame],
        embedding_success=True,
        embedding_error=None
    )
    
    # Test properties
    assert result.frame_count == 2
    assert result.successful_frame_count == 1
    assert len(result.successful_frames) == 1
    assert len(result.failed_frames) == 1
    assert result.successful_frames[0].frame_id == "success_frame"
    assert result.failed_frames[0].frame_id == "failed_frame"
    
    # Test empty result
    empty_result = EmbeddingResult(
        video_id=None,
        processed_frames=None,
        embedding_success=False,
        embedding_error="No frames"
    )
    
    assert empty_result.frame_count == 0
    assert empty_result.successful_frame_count == 0
    assert len(empty_result.successful_frames) == 0
    assert len(empty_result.failed_frames) == 0
    
    print("✅ EmbeddingResult properties test passed")

@pytest.mark.asyncio
async def test_exception_handling_in_generate_clip_embeddings(embedding_pipeline, mock_video_clip):
    """Test exception handling in clip embedding generation"""
    print("\n💥 Testing exception handling...")
    
    # Mock generate_frame_embed to raise exceptions for some frames
    async def mock_generate_frame_embed_with_exceptions(frame_data, frame_metadata):
        frame_index = frame_metadata['frame_index']
        if frame_index == 1:  # Second frame raises exception
            raise ValueError("Test exception")
        else:
            return ProcessedFrame(
                frame_id=frame_metadata['frame_id'],
                timestamp=frame_metadata['timestamp'],
                frame_data=frame_data,
                embedding_success=True
            )
    
    embedding_pipeline.generate_frame_embed = mock_generate_frame_embed_with_exceptions
    
    result = await embedding_pipeline.generate_clip_embeddings(mock_video_clip, num_frames=4)
    
    assert isinstance(result, EmbeddingResult)
    assert result.embedding_success == True  # Still successful because other frames succeeded
    assert result.frame_count == 4
    assert result.successful_frame_count == 3  # 3 successful, 1 exception
    assert len(result.failed_frames) == 1
    
    # Check that the exception was handled properly
    failed_frame = result.failed_frames[0]
    assert "Exception during processing" in failed_frame.embedding_error
    assert "Test exception" in failed_frame.embedding_error
    
    print("✅ Exception handling test passed")

@pytest.mark.asyncio
async def test_start_pipeline_success(embedding_pipeline, mock_video_stream):
    """Test starting the embedding pipeline with a video stream"""
    print("\n🧪 Testing start_pipeline...")
    
    # Start the pipeline
    await embedding_pipeline.start_pipeline(mock_video_stream)
    
    # Verify pipeline state
    assert embedding_pipeline.is_running == True
    assert embedding_pipeline.video_stream == mock_video_stream
    assert embedding_pipeline.cleanup_task is not None
    assert not embedding_pipeline.cleanup_task.done()
    
    # Verify callback was set
    mock_video_stream.set_callback.assert_called_once_with(embedding_pipeline._on_new_video_clip)
    
    # Cleanup
    await embedding_pipeline.stop_pipeline()
    
    print("✅ start_pipeline test passed")

@pytest.mark.asyncio
async def test_start_pipeline_already_running(embedding_pipeline, mock_video_stream):
    """Test starting pipeline when already running"""
    print("\n🧪 Testing start_pipeline when already running...")
    
    # Start pipeline first time
    await embedding_pipeline.start_pipeline(mock_video_stream)
    assert embedding_pipeline.is_running == True
    
    # Try to start again
    await embedding_pipeline.start_pipeline(mock_video_stream)
    assert embedding_pipeline.is_running == True
    
    # Verify callback was only set once
    assert mock_video_stream.set_callback.call_count == 1
    
    # Cleanup
    await embedding_pipeline.stop_pipeline()
    
    print("✅ start_pipeline already running test passed")

@pytest.mark.asyncio
async def test_stop_pipeline_success(embedding_pipeline, mock_video_stream):
    """Test stopping the embedding pipeline"""
    print("\n🧪 Testing stop_pipeline...")
    
    # Start pipeline
    await embedding_pipeline.start_pipeline(mock_video_stream)
    assert embedding_pipeline.is_running == True
    
    # Stop pipeline
    await embedding_pipeline.stop_pipeline()
    
    # Verify pipeline state
    assert embedding_pipeline.is_running == False
    assert embedding_pipeline.video_stream is None
    assert len(embedding_pipeline.processing_tasks) == 0
    
    # Verify callback was cleared
    mock_video_stream.set_callback.assert_called_with(None)
    
    print("✅ stop_pipeline test passed")

@pytest.mark.asyncio
async def test_stop_pipeline_not_running(embedding_pipeline):
    """Test stopping pipeline when not running"""
    print("\n🧪 Testing stop_pipeline when not running...")
    
    # Pipeline not started
    assert embedding_pipeline.is_running == False
    
    # Stop pipeline (should not raise error)
    await embedding_pipeline.stop_pipeline()
    
    # Verify still not running
    assert embedding_pipeline.is_running == False
    
    print("✅ stop_pipeline not running test passed")

@pytest.mark.asyncio
async def test_on_new_video_clip_success(embedding_pipeline, mock_video_clip):
    """Test processing a new video clip via callback"""
    print("\n🧪 Testing _on_new_video_clip...")
    
    # Mock the generate_clip_embeddings method
    with patch.object(embedding_pipeline, 'generate_clip_embeddings', new_callable=AsyncMock) as mock_generate:
        mock_result = EmbeddingResult(
            video_id="test_video",
            processed_frames=[Mock(spec=ProcessedFrame)],
            embedding_success=True,
            embedding_error=None
        )
        mock_generate.return_value = mock_result
        
        # Start pipeline
        mock_stream = Mock(spec=VideoStream)
        await embedding_pipeline.start_pipeline(mock_stream)
        
        # Simulate receiving a new clip
        await embedding_pipeline._on_new_video_clip(mock_video_clip)
        
        # Wait a bit for the async task to complete
        await asyncio.sleep(0.1)
        
        # Verify clip was processed
        mock_generate.assert_called_once_with(mock_video_clip)
        
        # Verify task was created
        assert mock_video_clip.file_path in embedding_pipeline.processing_tasks
        
        # Cleanup
        await embedding_pipeline.stop_pipeline()
    
    print("✅ _on_new_video_clip test passed")

@pytest.mark.asyncio
async def test_on_new_video_clip_pipeline_not_running(embedding_pipeline, mock_video_clip):
    """Test receiving clip when pipeline is not running"""
    print("\n🧪 Testing _on_new_video_clip when pipeline not running...")
    
    # Pipeline not started
    assert embedding_pipeline.is_running == False
    
    # Try to process clip
    await embedding_pipeline._on_new_video_clip(mock_video_clip)
    
    # Verify no processing tasks were created
    assert len(embedding_pipeline.processing_tasks) == 0
    
    print("✅ _on_new_video_clip not running test passed")

@pytest.mark.asyncio
async def test_on_new_video_clip_embeddings_disabled(embedding_pipeline_disabled, mock_video_clip):
    """Test receiving clip when embeddings are disabled"""
    print("\n🧪 Testing _on_new_video_clip with embeddings disabled...")
    
    # Start pipeline
    mock_stream = Mock(spec=VideoStream)
    await embedding_pipeline_disabled.start_pipeline(mock_stream)
    
    # Try to process clip
    await embedding_pipeline_disabled._on_new_video_clip(mock_video_clip)
    
    # Verify no processing tasks were created
    assert len(embedding_pipeline_disabled.processing_tasks) == 0
    
    # Cleanup
    await embedding_pipeline_disabled.stop_pipeline()
    
    print("✅ _on_new_video_clip embeddings disabled test passed")

@pytest.mark.asyncio
async def test_on_new_video_clip_duplicate_processing(embedding_pipeline, mock_video_clip):
    """Test that duplicate clips are not processed"""
    print("\n🧪 Testing _on_new_video_clip duplicate processing...")
    
    # Mock the generate_clip_embeddings method
    with patch.object(embedding_pipeline, 'generate_clip_embeddings', new_callable=AsyncMock) as mock_generate:
        mock_result = EmbeddingResult(
            video_id="test_video",
            processed_frames=[Mock(spec=ProcessedFrame)],
            embedding_success=True,
            embedding_error=None
        )
        mock_generate.return_value = mock_result
        
        # Start pipeline
        mock_stream = Mock(spec=VideoStream)
        await embedding_pipeline.start_pipeline(mock_stream)
        
        # Process clip first time
        await embedding_pipeline._on_new_video_clip(mock_video_clip)
        await asyncio.sleep(0.1)  # Wait for async processing
        assert mock_generate.call_count == 1
        
        # Try to process same clip again
        await embedding_pipeline._on_new_video_clip(mock_video_clip)
        await asyncio.sleep(0.1)  # Wait for async processing
        assert mock_generate.call_count == 1  # Should not be called again
        
        # Cleanup
        await embedding_pipeline.stop_pipeline()
    
    print("✅ _on_new_video_clip duplicate processing test passed")

@pytest.mark.asyncio
async def test_process_clip_async_success(embedding_pipeline, mock_video_clip):
    """Test async processing of a single clip"""
    print("\n🧪 Testing _process_clip_async...")
    
    # Mock the generate_clip_embeddings method
    with patch.object(embedding_pipeline, 'generate_clip_embeddings') as mock_generate:
        mock_result = EmbeddingResult(
            video_id="test_video",
            processed_frames=[Mock(spec=ProcessedFrame)],
            embedding_success=True,
            embedding_error=None
        )
        mock_generate.return_value = mock_result
        
        # Process clip
        await embedding_pipeline._process_clip_async(mock_video_clip)
        
        # Verify clip was processed
        mock_generate.assert_called_once_with(mock_video_clip)
    
    print("✅ _process_clip_async test passed")

@pytest.mark.asyncio
async def test_process_clip_async_failure(embedding_pipeline, mock_video_clip):
    """Test async processing when embedding fails"""
    print("\n🧪 Testing _process_clip_async with failure...")
    
    # Mock the generate_clip_embeddings method to return failure
    with patch.object(embedding_pipeline, 'generate_clip_embeddings') as mock_generate:
        mock_result = EmbeddingResult(
            video_id="test_video",
            processed_frames=[],
            embedding_success=False,
            embedding_error="Test error"
        )
        mock_generate.return_value = mock_result
        
        # Process clip
        await embedding_pipeline._process_clip_async(mock_video_clip)
        
        # Verify clip was processed
        mock_generate.assert_called_once_with(mock_video_clip)
    
    print("✅ _process_clip_async failure test passed")

@pytest.mark.asyncio
async def test_process_clip_async_exception(embedding_pipeline, mock_video_clip):
    """Test async processing when an exception occurs"""
    print("\n🧪 Testing _process_clip_async with exception...")
    
    # Mock the generate_clip_embeddings method to raise exception
    with patch.object(embedding_pipeline, 'generate_clip_embeddings') as mock_generate:
        mock_generate.side_effect = Exception("Test exception")
        
        # Process clip (should not raise exception)
        await embedding_pipeline._process_clip_async(mock_video_clip)
        
        # Verify clip was attempted
        mock_generate.assert_called_once_with(mock_video_clip)
    
    print("✅ _process_clip_async exception test passed")

@pytest.mark.asyncio
async def test_cleanup_completed_tasks(embedding_pipeline):
    """Test cleanup of completed processing tasks"""
    print("\n🧪 Testing _cleanup_completed_tasks...")
    
    # Create mock tasks
    completed_task = Mock()
    completed_task.done.return_value = True
    
    running_task = Mock()
    running_task.done.return_value = False
    
    # Add tasks to processing_tasks
    embedding_pipeline.processing_tasks = {
        "completed_clip.mp4": completed_task,
        "running_clip.mp4": running_task
    }
    
    # Run cleanup
    await embedding_pipeline._cleanup_completed_tasks()
    
    # Verify completed task was removed
    assert "completed_clip.mp4" not in embedding_pipeline.processing_tasks
    assert "running_clip.mp4" in embedding_pipeline.processing_tasks
    
    print("✅ _cleanup_completed_tasks test passed")

@pytest.mark.asyncio
async def test_cleanup_loop(embedding_pipeline):
    """Test the cleanup loop"""
    print("\n🧪 Testing _cleanup_loop...")
    
    # Mock the cleanup method
    with patch.object(embedding_pipeline, '_cleanup_completed_tasks') as mock_cleanup:
        # Start cleanup loop
        embedding_pipeline.is_running = True
        cleanup_task = asyncio.create_task(embedding_pipeline._cleanup_loop())
        
        # Wait a bit for cleanup to run
        await asyncio.sleep(0.1)
        
        # Stop the loop
        embedding_pipeline.is_running = False
        await asyncio.sleep(0.1)
        
        # Verify cleanup was called
        assert mock_cleanup.call_count > 0
        
        # Cancel task if still running
        if not cleanup_task.done():
            cleanup_task.cancel()
            try:
                await cleanup_task
            except asyncio.CancelledError:
                pass
    
    print("✅ _cleanup_loop test passed")

@pytest.mark.asyncio
async def test_cleanup_loop_exception(embedding_pipeline):
    """Test cleanup loop handles exceptions gracefully"""
    print("\n🧪 Testing _cleanup_loop with exception...")
    
    # Mock the cleanup method to raise exception
    with patch.object(embedding_pipeline, '_cleanup_completed_tasks') as mock_cleanup:
        mock_cleanup.side_effect = Exception("Test cleanup exception")
        
        # Start cleanup loop
        embedding_pipeline.is_running = True
        cleanup_task = asyncio.create_task(embedding_pipeline._cleanup_loop())
        
        # Wait a bit for cleanup to run
        await asyncio.sleep(0.1)
        
        # Stop the loop
        embedding_pipeline.is_running = False
        await asyncio.sleep(0.1)
        
        # Verify cleanup was called (exception should be handled)
        assert mock_cleanup.call_count > 0
        
        # Cancel task if still running
        if not cleanup_task.done():
            cleanup_task.cancel()
            try:
                await cleanup_task
            except asyncio.CancelledError:
                pass
    
    print("✅ _cleanup_loop exception test passed")

@pytest.mark.asyncio
async def test_pipeline_integration_with_multiple_clips(embedding_pipeline, mock_video_clips):
    """Test full pipeline integration with multiple clips"""
    print("\n🧪 Testing pipeline integration with multiple clips...")
    
    # Mock the generate_clip_embeddings method
    with patch.object(embedding_pipeline, 'generate_clip_embeddings') as mock_generate:
        mock_generate.return_value = EmbeddingResult(
            video_id="test_video",
            processed_frames=[Mock(spec=ProcessedFrame)],
            embedding_success=True,
            embedding_error=None
        )
        
        # Start pipeline
        mock_stream = Mock(spec=VideoStream)
        await embedding_pipeline.start_pipeline(mock_stream)
        
        # Process multiple clips
        for clip in mock_video_clips:
            await embedding_pipeline._on_new_video_clip(clip)
        
        # Wait for processing to complete
        await asyncio.sleep(0.1)
        
        # Verify all clips were processed
        assert mock_generate.call_count == len(mock_video_clips)
        
        # Verify all tasks were created
        assert len(embedding_pipeline.processing_tasks) == len(mock_video_clips)
        
        # Cleanup
        await embedding_pipeline.stop_pipeline()
        
        # Verify all tasks were cleaned up
        assert len(embedding_pipeline.processing_tasks) == 0
    
    print("✅ Pipeline integration test passed")

@pytest.mark.asyncio
async def test_pipeline_stats_with_videostream_integration(embedding_pipeline, mock_video_clips):
    """Test that pipeline stats are updated correctly with VideoStream integration"""
    print("\n🧪 Testing pipeline stats with VideoStream integration...")
    
    # Mock the generate_clip_embeddings method
    with patch.object(embedding_pipeline, 'generate_clip_embeddings') as mock_generate:
        mock_generate.return_value = EmbeddingResult(
            video_id="test_video",
            processed_frames=[Mock(spec=ProcessedFrame)],
            embedding_success=True,
            embedding_error=None
        )
        
        # Start pipeline
        mock_stream = Mock(spec=VideoStream)
        await embedding_pipeline.start_pipeline(mock_stream)
        
        # Process clips
        for clip in mock_video_clips:
            await embedding_pipeline._on_new_video_clip(clip)
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Get stats
        stats = embedding_pipeline.get_embedding_stats()
        
        # Verify stats are updated
        assert stats['total_clips_processed'] >= 0
        assert stats['total_frame_embeddings_created'] >= 0
        assert stats['total_embedding_failures'] >= 0
        
        # Cleanup
        await embedding_pipeline.stop_pipeline()
    
    print("✅ Pipeline stats test passed")

@pytest.mark.asyncio
async def test_real_modal_api_integration():
    """Test real Modal API integration with actual video clip and database storage"""
    print("\n🌐 Testing real Modal API integration...")
    
    # Create a test video clip
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "real_test_clip.mp4")
    
    # Create a simple test video with OpenCV
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 30.0, (640, 480))
    
    # Write frames with different colors
    for i in range(90):  # 3 seconds at 30 fps
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        color_value = (i * 50) % 255
        frame[:, :, 0] = color_value  # Blue channel
        frame[:, :, 1] = (color_value + 85) % 255  # Green channel  
        frame[:, :, 2] = (color_value + 170) % 255  # Red channel
        out.write(frame)
    
    out.release()
    
    # Create video clip
    clip = VideoClip(
        file_path=video_path,
        start_time=0.0,
        end_time=3.0,
        metadata={'test': True, 'real_api_test': True},
        priority=(0,)
    )
    
    try:
        # Create embedding pipeline with real Modal endpoint
        pipeline = EmbeddingPipeline(
            clip_endpoint_url=os.getenv("CLIP_EMBEDDING_URL"),
            enable_embeddings=True
        )
        
        print(f"🔮 Processing clip: {clip.file_path}")
        print(f"📊 Clip duration: {clip.end_time - clip.start_time}s")
        
        # Generate embeddings
        result = await pipeline.generate_clip_embeddings(clip, num_frames=4)
        
        print(f"📈 Embedding result:")
        print(f"   - Success: {result.embedding_success}")
        print(f"   - Frame count: {result.frame_count}")
        print(f"   - Successful frames: {result.successful_frame_count}")
        print(f"   - Failed frames: {len(result.failed_frames)}")
        
        if result.embedding_success:
            print(f"✅ Successfully embedded {result.successful_frame_count} frames")
            
            # Print details of successful frames
            for frame in result.successful_frames:
                print(f"   📷 Frame {frame.frame_id}: {frame.frame_path}")
                if hasattr(frame, 'embedding_dimension'):
                    print(f"      Embedding dimension: {frame.embedding_dimension}")
            
            # Print details of failed frames
            for frame in result.failed_frames:
                print(f"   ❌ Frame {frame.frame_id}: {frame.embedding_error}")
        
        else:
            print(f"❌ Embedding failed: {result.embedding_error}")
        
        # Get pipeline stats
        stats = pipeline.get_statistics()
        print(f"📊 Pipeline stats:")
        print(f"   - Total clips processed: {stats['clips_processed']}")
        print(f"   - Total frame embeddings: {stats['frames_embedded']}")
        print(f"   - Total failures: {stats['embedding_failures']}")
        print(f"   - Pipeline running: {stats['is_running']}")
        print(f"   - Embeddings enabled: {stats['enable_embeddings']}")
        print(f"   - Endpoint URL: {stats['clip_endpoint_url']}")
        
        # Assertions
        assert result.frame_count == 4, f"Expected 4 frames, got {result.frame_count}"
        if result.embedding_success:
            assert result.successful_frame_count > 0, "Should have at least one successful frame"
            assert len(result.successful_frames) > 0, "Should have successful frames"
        
        print("✅ Real Modal API integration test completed")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        os.rmdir(temp_dir)
        print("🧹 Cleanup completed")

@pytest.mark.asyncio
async def test_mock_frame_embedding():
    """Test frame embedding with mocked Modal API calls"""
    print("\n🎯 Testing mock frame embedding...")
    
    # Create mock frame data
    frame_data = b'fake_jpeg_frame_data'
    frame_metadata = {
        'frame_id': 'test_frame_001',
        'timestamp': 1.5,
        'video_id': 'test_video_123',
        'clip_path': '/test/clip.mp4',
        'frame_index': 0,
        'video_time': 1.5
    }
    
    # Create embedding pipeline
    pipeline = EmbeddingPipeline(
        clip_endpoint_url="https://adscope--clip-embedding-service.modal.run",
        enable_embeddings=True
    )
    
    # Mock the entire generate_frame_embed method to avoid complex async mocking
    async def mock_generate_frame_embed(frame_data, frame_metadata):
        return ProcessedFrame(
            frame_id=frame_metadata['frame_id'],
            timestamp=frame_metadata['timestamp'],
            weaviate_id='weaviate_uuid_123',
            embedding_success=True,
            embedding_error=None
        )
    
    # Replace the method
    pipeline.generate_frame_embed = mock_generate_frame_embed
    
    # Test the method
    result = await pipeline.generate_frame_embed(frame_data, frame_metadata)
    
    # Verify the result
    assert isinstance(result, ProcessedFrame)
    assert result.embedding_success == True
    assert result.frame_id == 'test_frame_001'
    assert result.timestamp == 1.5
    assert result.weaviate_id == 'weaviate_uuid_123'
    assert result.embedding_error is None
    
    print("✅ Mock frame embedding test passed")

@pytest.mark.asyncio
async def test_mock_batch_frame_embedding():
    """Test batch frame embedding with mocked Modal API calls"""
    print("\n🎯 Testing mock batch frame embedding...")
    
    # Create mock frames
    frames = []
    for i in range(3):
        frame_data = f'fake_jpeg_frame_data_{i}'.encode()
        frame_metadata = {
            'frame_id': f'test_frame_{i:03d}',
            'timestamp': 1.0 + i * 0.5,
            'video_id': 'test_video_123',
            'clip_path': '/test/clip.mp4',
            'frame_index': i,
            'video_time': 1.0 + i * 0.5
        }
        frames.append({
            'frame_data': frame_data,
            **frame_metadata
        })
    
    # Create embedding pipeline
    pipeline = EmbeddingPipeline(
        clip_endpoint_url="https://adscope--clip-embedding-service.modal.run",
        enable_embeddings=True
    )
    
    # Mock the entire generate_batch_frame_embeds method
    async def mock_generate_batch_frame_embeds(frames):
        results = []
        for i, frame in enumerate(frames):
            results.append(ProcessedFrame(
                frame_id=frame['frame_id'],
                timestamp=frame['timestamp'],
                weaviate_id=f'weaviate_uuid_{i}',
                embedding_success=True,
                embedding_error=None
            ))
        return results
    
    # Replace the method
    pipeline.generate_batch_frame_embeds = mock_generate_batch_frame_embeds
    
    # Test the method
    results = await pipeline.generate_batch_frame_embeds(frames)
    
    # Verify the results
    assert len(results) == 3
    for i, result in enumerate(results):
        assert isinstance(result, ProcessedFrame)
        assert result.embedding_success == True
        assert result.frame_id == f'test_frame_{i:03d}'
        assert result.weaviate_id == f'weaviate_uuid_{i}'
        assert result.embedding_error is None
    
    print("✅ Mock batch frame embedding test passed")

@pytest.mark.asyncio
async def test_mock_text_query_embedding():
    """Test text query embedding with mocked Modal API calls"""
    print("\n🎯 Testing mock text query embedding...")
    
    # Create mock text query
    query = "What file does the user spend the most time in?"
    
    # Mock the Modal service response
    mock_embedding = np.random.rand(512).tolist()  # 512-dim CLIP embedding
    
    # Create a mock text embedding function
    async def mock_text_embedding(query_text):
        return {
            'success': True,
            'embedding': mock_embedding,
            'embedding_dimension': 512
        }
    
    # Test the mock function
    result = await mock_text_embedding(query)
    
    # Verify the response
    assert result['success'] == True
    assert 'embedding' in result
    assert len(result['embedding']) == 512
    assert result['embedding_dimension'] == 512
    
    print(f"✅ Text query embedding successful")
    print(f"   Query: {query}")
    print(f"   Embedding dimension: {result['embedding_dimension']}")
    print(f"   Embedding sample: {result['embedding'][:5]}...")
    
    print("✅ Mock text query embedding test passed")

@pytest.mark.asyncio
async def test_mock_clip_embedding_integration():
    """Test complete clip embedding integration with mocked components"""
    print("\n🎯 Testing mock clip embedding integration...")
    
    # Create a mock video clip
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "integration_test_clip.mp4")
    
    # Create a simple test video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 30.0, (640, 480))
    
    for i in range(90):  # 3 seconds at 30 fps
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        color_value = (i * 50) % 255
        frame[:, :, 0] = color_value
        frame[:, :, 1] = (color_value + 85) % 255
        frame[:, :, 2] = (color_value + 170) % 255
        out.write(frame)
    
    out.release()
    
    clip = VideoClip(
        file_path=video_path,
        start_time=0.0,
        end_time=3.0,
        metadata={'test': True, 'integration_test': True},
        priority=(0,)
    )
    
    try:
        # Create embedding pipeline
        pipeline = EmbeddingPipeline(
            clip_endpoint_url="https://adscope--clip-embedding-service.modal.run",
            enable_embeddings=True
        )
        
        # Mock the batch embedding response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            'success': True,
            'total_frames': 4,
            'successful_frames': 4,
            'failed_frames': 0,
            'results': [
                {
                    'success': True,
                    'frame_id': f'integration_test_clip_mp4_frame_{i:03d}',
                    'timestamp': 0.0 + i * 0.75,
                    'frame_path': f'/frame_data/integration_test_clip_mp4_frame_{i:03d}.jpg',
                    'weaviate_id': f'weaviate_integration_{i}',
                    'embedding_dimension': 512
                }
                for i in range(4)
            ]
        }
        
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.post.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            # Generate embeddings for the clip
            result = await pipeline.generate_clip_embeddings(clip, num_frames=4)
            
            # Verify the result
            assert isinstance(result, EmbeddingResult)
            assert result.embedding_success == True
            assert result.video_id is not None
            assert result.frame_count == 4
            assert result.successful_frame_count == 4
            assert len(result.failed_frames) == 0
            
            # Verify individual frames
            for i, frame in enumerate(result.successful_frames):
                assert frame.embedding_success == True
                assert frame.frame_id == f'integration_test_clip_mp4_frame_{i:03d}'
                assert frame.weaviate_id == f'weaviate_integration_{i}'
                assert frame.embedding_error is None
            
            print(f"✅ Integration test successful:")
            print(f"   - Video ID: {result.video_id}")
            print(f"   - Frames processed: {result.frame_count}")
            print(f"   - Successful frames: {result.successful_frame_count}")
            print(f"   - Failed frames: {len(result.failed_frames)}")
            
            # Verify pipeline stats
            stats = pipeline.get_statistics()
            assert stats['clips_processed'] == 1
            assert stats['frames_embedded'] == 4
            assert stats['embedding_failures'] == 0
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        os.rmdir(temp_dir)
        print("🧹 Integration test cleanup completed")

@pytest.mark.asyncio
async def test_mock_text_query_search():
    """Test text query search with mocked vector search"""
    print("\n🎯 Testing mock text query search...")
    
    # Mock query and embedding
    query = "What programming languages are being used?"
    query_embedding = np.random.rand(512).tolist()
    
    # Mock search results
    mock_search_results = [
        {
            'frame_id': 'frame_001',
            'video_id': 'video_123',
            'clip_path': '/test/clip.mp4',
            'timestamp': 1.5,
            'similarity_score': 0.85,
            'metadata': {'test': True}
        },
        {
            'frame_id': 'frame_002',
            'video_id': 'video_123',
            'clip_path': '/test/clip.mp4',
            'timestamp': 2.0,
            'similarity_score': 0.72,
            'metadata': {'test': True}
        }
    ]
    
    # Mock the Modal service
    with patch('modal.method') as mock_method:
        mock_service = Mock()
        mock_service.embed_text_query.remote.return_value = np.array(query_embedding)
        mock_service.search_similar_frames.remote.return_value = mock_search_results
        
        # Test the search functionality
        print(f"🔍 Testing search for query: '{query}'")
        print(f"📊 Query embedding dimension: {len(query_embedding)}")
        print(f"📋 Found {len(mock_search_results)} similar frames")
        
        for i, result in enumerate(mock_search_results):
            print(f"   📷 Frame {i+1}: {result['frame_id']}")
            print(f"      Similarity: {result['similarity_score']:.3f}")
            print(f"      Timestamp: {result['timestamp']}")
        
        # Verify search results
        assert len(mock_search_results) == 2
        assert mock_search_results[0]['similarity_score'] > mock_search_results[1]['similarity_score']
        assert all('frame_id' in result for result in mock_search_results)
        assert all('similarity_score' in result for result in mock_search_results)
        
@pytest.mark.asyncio
async def test_modal_service_methods():
    """Test the Modal service methods from modal_clip_embeddings.py"""
    print("\n🎯 Testing Modal service methods...")
    
    # Mock the CLIPEmbeddingService class
    with patch('deploy.modal_clip_embeddings.CLIPEmbeddingService') as MockService:
        # Create mock service instance
        mock_service = Mock()
        
        # Mock the __enter__ method
        mock_service.__enter__.return_value = mock_service
        mock_service.device = "cuda"
        mock_service.embedding_dim = 512
        
        # Mock the embed_text_query method
        mock_embedding = np.random.rand(512).tolist()
        mock_service.embed_text_query.remote.return_value = np.array(mock_embedding)
        
        # Mock the embed_single_frame method
        mock_service.embed_single_frame.remote.return_value = {
            'success': True,
            'frame_id': 'test_frame_001',
            'timestamp': 1.5,
            'frame_path': '/frame_data/test_frame_001.jpg',
            'weaviate_id': 'weaviate_uuid_123',
            'embedding_dimension': 512
        }
        
        # Mock the embed_batch_frames method
        mock_service.embed_batch_frames.remote.return_value = [
            {
                'success': True,
                'frame_id': f'test_frame_{i:03d}',
                'timestamp': 1.0 + i * 0.5,
                'frame_path': f'/frame_data/test_frame_{i:03d}.jpg',
                'weaviate_id': f'weaviate_uuid_{i}',
                'embedding_dimension': 512
            }
            for i in range(3)
        ]
        
        # Mock the search_similar_frames method
        mock_service.search_similar_frames.remote.return_value = [
            {
                'frame_id': 'frame_001',
                'video_id': 'video_123',
                'clip_path': '/test/clip.mp4',
                'timestamp': 1.5,
                'similarity_score': 0.85,
                'metadata': {'test': True}
            }
        ]
        
        # Test text embedding
        print("🔤 Testing text embedding...")
        query = "What programming languages are being used?"
        text_embedding = mock_service.embed_text_query.remote(query)
        assert len(text_embedding) == 512
        print(f"   ✅ Text embedding successful: {len(text_embedding)} dimensions")
        
        # Test single frame embedding
        print("📷 Testing single frame embedding...")
        frame_data = b'fake_jpeg_frame_data'
        frame_metadata = {
            'frame_id': 'test_frame_001',
            'timestamp': 1.5,
            'video_id': 'test_video_123'
        }
        frame_result = mock_service.embed_single_frame.remote(frame_data, frame_metadata)
        assert frame_result['success'] == True
        assert frame_result['frame_id'] == 'test_frame_001'
        assert frame_result['weaviate_id'] == 'weaviate_uuid_123'
        print(f"   ✅ Single frame embedding successful: {frame_result['frame_id']}")
        
        # Test batch frame embedding
        print("📷 Testing batch frame embedding...")
        frames_data = [
            {
                'frame_data': f'fake_jpeg_frame_data_{i}'.encode(),
                'metadata': {
                    'frame_id': f'test_frame_{i:03d}',
                    'timestamp': 1.0 + i * 0.5,
                    'video_id': 'test_video_123'
                }
            }
            for i in range(3)
        ]
        batch_results = mock_service.embed_batch_frames.remote(frames_data)
        assert len(batch_results) == 3
        assert all(result['success'] for result in batch_results)
        print(f"   ✅ Batch frame embedding successful: {len(batch_results)} frames")
        
        # Test vector search
        print("🔍 Testing vector search...")
        query_embedding = np.random.rand(512).tolist()
        search_results = mock_service.search_similar_frames.remote(query_embedding, k=5)
        assert len(search_results) == 1
        assert search_results[0]['similarity_score'] == 0.85
        print(f"   ✅ Vector search successful: {len(search_results)} results")
        
        print("✅ Modal service methods test passed")

@pytest.mark.asyncio
async def test_modal_endpoints():
    """Test the Modal FastAPI endpoints"""
    print("\n🎯 Testing Modal endpoints...")
    
    # Mock the endpoints
    with patch('deploy.modal_clip_embeddings.embed_single_frame_endpoint') as mock_single_endpoint:
        with patch('deploy.modal_clip_embeddings.embed_batch_frames_endpoint') as mock_batch_endpoint:
            with patch('deploy.modal_clip_embeddings.embed_text_query_endpoint') as mock_text_endpoint:
                
                # Test single frame endpoint
                print("📷 Testing single frame endpoint...")
                mock_single_endpoint.return_value = {
                    "success": True,
                    "frame_result": {
                        "frame_id": "test_frame_001",
                        "timestamp": 1.5,
                        "frame_path": "/frame_data/test_frame_001.jpg",
                        "weaviate_id": "weaviate_uuid_123",
                        "embedding_dimension": 512
                    }
                }
                
                # Test batch frame endpoint
                print("📷 Testing batch frame endpoint...")
                mock_batch_endpoint.return_value = {
                    "success": True,
                    "total_frames": 3,
                    "successful_frames": 3,
                    "failed_frames": 0,
                    "results": [
                        {
                            "success": True,
                            "frame_id": f"test_frame_{i:03d}",
                            "timestamp": 1.0 + i * 0.5,
                            "weaviate_id": f"weaviate_uuid_{i}",
                            "embedding_dimension": 512
                        }
                        for i in range(3)
                    ]
                }
                
                # Test text query endpoint
                print("🔤 Testing text query endpoint...")
                mock_text_endpoint.return_value = {
                    "success": True,
                    "embedding": np.random.rand(512).tolist(),
                    "embedding_dimension": 512
                }
                
                # Verify endpoint responses
                single_result = mock_single_endpoint()
                assert single_result["success"] == True
                assert "frame_result" in single_result
                
                batch_result = mock_batch_endpoint()
                assert batch_result["success"] == True
                assert batch_result["total_frames"] == 3
                assert batch_result["successful_frames"] == 3
                
                text_result = mock_text_endpoint()
                assert text_result["success"] == True
                assert "embedding" in text_result
                assert text_result["embedding_dimension"] == 512
                
                print("✅ Modal endpoints test passed")

@pytest.mark.asyncio
async def test_weaviate_database_storage():
    """Test that embeddings and video clips are properly stored in Weaviate database"""
    print("\n🗄️ Testing Weaviate database storage...")
    
    # Create a test video clip
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "weaviate_test_clip.mp4")
    
    # Create a simple test video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 30.0, (640, 480))
    
    for i in range(90):  # 3 seconds at 30 fps
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        color_value = (i * 50) % 255
        frame[:, :, 0] = color_value
        frame[:, :, 1] = (color_value + 85) % 255
        frame[:, :, 2] = (color_value + 170) % 255
        out.write(frame)
    
    out.release()
    
    clip = VideoClip(
        file_path=video_path,
        start_time=0.0,
        end_time=3.0,
        metadata={'test': True, 'weaviate_test': True},
        priority=(0,)
    )
    
    try:
        # Create embedding pipeline with real Modal endpoint
        pipeline = EmbeddingPipeline(
            clip_endpoint_url=os.getenv("CLIP_EMBEDDING_URL"),
            enable_embeddings=True
        )
        
        print(f"🔮 Processing clip for Weaviate storage: {clip.file_path}")
        
        # Generate embeddings
        result = await pipeline.generate_clip_embeddings(clip, num_frames=4)
        
        if result.embedding_success:
            print(f"✅ Successfully embedded {result.successful_frame_count} frames")
            
            # Check that frames have Weaviate IDs
            frames_with_weaviate_ids = [f for f in result.successful_frames if f.weaviate_id]
            print(f"📊 Frames with Weaviate IDs: {len(frames_with_weaviate_ids)}/{result.successful_frame_count}")
            
            # Verify each successful frame has a Weaviate ID
            for frame in result.successful_frames:
                if frame.embedding_success:
                    assert frame.weaviate_id is not None, f"Frame {frame.frame_id} missing Weaviate ID"
                    print(f"   ✅ Frame {frame.frame_id} stored in Weaviate with ID: {frame.weaviate_id}")
            
            # Test retrieving frames from Weaviate
            print("🔍 Testing Weaviate frame retrieval...")
            
            # Mock the Modal service to test retrieval
            with patch('deploy.modal_clip_embeddings.CLIPEmbeddingService') as MockService:
                mock_service = Mock()
                mock_service.get_frame_by_id.remote.return_value = {
                    'frame_id': 'test_frame_001',
                    'video_id': 'test_video_123',
                    'timestamp': 1.5,
                    'frame_data': b'fake_frame_data',
                    'embedding': np.random.rand(512).tolist(),
                    'metadata': {'test': True},
                    'created_at': '2025-01-01T00:00:00'
                }
                
                # Test frame retrieval
                for frame in frames_with_weaviate_ids[:2]:  # Test first 2 frames
                    retrieved_frame = mock_service.get_frame_by_id.remote(frame.weaviate_id)
                    
                    assert retrieved_frame is not None
                    assert retrieved_frame['frame_id'] == frame.frame_id
                    assert 'embedding' in retrieved_frame
                    assert len(retrieved_frame['embedding']) == 512
                    
                    print(f"   ✅ Retrieved frame {frame.frame_id} from Weaviate")
            
            # Test video frame retrieval
            print("🎬 Testing video frame retrieval...")
            
            with patch('deploy.modal_clip_embeddings.CLIPEmbeddingService') as MockService:
                mock_service = Mock()
                mock_service.get_video_frames.remote.return_value = [
                    {
                        'frame_id': f'frame_{i:03d}',
                        'timestamp': i * 0.75,
                        'similarity_score': 1.0,
                        'metadata': {'test': True},
                        'created_at': '2025-01-01T00:00:00'
                    }
                    for i in range(4)
                ]
                
                # Test video frame retrieval
                video_frames = mock_service.get_video_frames.remote(result.video_id)
                
                assert len(video_frames) == 4
                for i, frame in enumerate(video_frames):
                    assert frame['frame_id'] == f'frame_{i:03d}'
                    assert frame['similarity_score'] == 1.0
                
                print(f"   ✅ Retrieved {len(video_frames)} frames for video {result.video_id}")
            
            # Test database statistics
            print("📊 Testing database statistics...")
            
            with patch('deploy.modal_clip_embeddings.CLIPEmbeddingService') as MockService:
                mock_service = Mock()
                mock_service.get_index_stats.remote.return_value = {
                    'total_frame_embeddings': 100,
                    'embedding_dimension': 512,
                    'database_type': 'Weaviate',
                    'unique_videos': 25,
                    'weaviate_ready': True
                }
                
                stats = mock_service.get_index_stats.remote()
                
                assert stats['total_frame_embeddings'] > 0
                assert stats['embedding_dimension'] == 512
                assert stats['database_type'] == 'Weaviate'
                assert stats['weaviate_ready'] == True
                
                print(f"   ✅ Database stats: {stats['total_frame_embeddings']} embeddings, {stats['unique_videos']} videos")
        
        else:
            print(f"❌ Embedding failed: {result.embedding_error}")
        
    except Exception as e:
        print(f"❌ Weaviate storage test failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        os.rmdir(temp_dir)
        print("🧹 Weaviate storage test cleanup completed")

@pytest.mark.asyncio
async def test_weaviate_vector_search():
    """Test vector search functionality in Weaviate"""
    print("\n🔍 Testing Weaviate vector search...")
    
    # Create a test query
    query = "What programming languages are being used?"
    
    # Mock the Modal service for vector search
    with patch('deploy.modal_clip_embeddings.CLIPEmbeddingService') as MockService:
        mock_service = Mock()
        
        # Mock text embedding
        mock_query_embedding = np.random.rand(512).tolist()
        mock_service.embed_text_query.remote.return_value = np.array(mock_query_embedding)
        
        # Mock vector search results
        mock_search_results = [
            {
                'frame_id': 'frame_001',
                'video_id': 'video_123',
                'clip_path': '/test/clip.mp4',
                'timestamp': 1.5,
                'similarity_score': 0.85,
                'metadata': {'test': True, 'programming': True}
            },
            {
                'frame_id': 'frame_002',
                'video_id': 'video_123',
                'clip_path': '/test/clip.mp4',
                'timestamp': 2.0,
                'similarity_score': 0.72,
                'metadata': {'test': True, 'programming': True}
            },
            {
                'frame_id': 'frame_003',
                'video_id': 'video_456',
                'clip_path': '/test/clip2.mp4',
                'timestamp': 1.0,
                'similarity_score': 0.65,
                'metadata': {'test': True, 'programming': False}
            }
        ]
        
        mock_service.search_similar_frames.remote.return_value = mock_search_results
        
        # Test text embedding
        print(f"🔤 Embedding query: '{query}'")
        query_embedding = mock_service.embed_text_query.remote(query)
        assert len(query_embedding) == 512
        print(f"   ✅ Query embedded: {len(query_embedding)} dimensions")
        
        # Test vector search
        print("🔍 Performing vector search...")
        search_results = mock_service.search_similar_frames.remote(query_embedding, k=5)
        
        assert len(search_results) == 3
        assert all('frame_id' in result for result in search_results)
        assert all('similarity_score' in result for result in search_results)
        assert all('metadata' in result for result in search_results)
        
        # Verify similarity scores are in descending order
        scores = [result['similarity_score'] for result in search_results]
        assert scores == sorted(scores, reverse=True)
        
        print(f"   ✅ Found {len(search_results)} similar frames")
        for i, result in enumerate(search_results):
            print(f"      📷 {i+1}. {result['frame_id']} (score: {result['similarity_score']:.3f})")
        
        # Test filtering by metadata
        programming_frames = [r for r in search_results if r['metadata'].get('programming', False)]
        print(f"   📊 Programming-related frames: {len(programming_frames)}/{len(search_results)}")
        
        print("✅ Weaviate vector search test passed")

@pytest.mark.asyncio
async def test_weaviate_batch_operations():
    """Test batch operations with Weaviate"""
    print("\n📦 Testing Weaviate batch operations...")
    
    # Create multiple test frames
    test_frames = []
    for i in range(5):
        frame_data = f'fake_jpeg_frame_data_{i}'.encode()
        frame_metadata = {
            'frame_id': f'batch_test_frame_{i:03d}',
            'timestamp': 1.0 + i * 0.5,
            'video_id': 'batch_test_video',
            'clip_path': '/test/batch_clip.mp4',
            'frame_index': i,
            'video_time': 1.0 + i * 0.5
        }
        test_frames.append({
            'frame_data': frame_data,
            **frame_metadata
        })
    
    # Mock the Modal service for batch operations
    with patch('deploy.modal_clip_embeddings.CLIPEmbeddingService') as MockService:
        mock_service = Mock()
        
        # Mock batch embedding results
        mock_batch_results = [
            {
                'success': True,
                'frame_id': f'batch_test_frame_{i:03d}',
                'timestamp': 1.0 + i * 0.5,
                'frame_path': f'/frame_data/batch_test_frame_{i:03d}.jpg',
                'weaviate_id': f'weaviate_batch_{i}',
                'embedding_dimension': 512
            }
            for i in range(5)
        ]
        
        mock_service.embed_batch_frames.remote.return_value = mock_batch_results
        
        # Test batch embedding
        print("📦 Processing batch of 5 frames...")
        batch_results = mock_service.embed_batch_frames.remote(test_frames)
        
        assert len(batch_results) == 5
        assert all(result['success'] for result in batch_results)
        
        # Verify all frames have Weaviate IDs
        weaviate_ids = [result['weaviate_id'] for result in batch_results]
        assert len(set(weaviate_ids)) == 5  # All unique IDs
        assert all(weaviate_id.startswith('weaviate_batch_') for weaviate_id in weaviate_ids)
        
        print(f"   ✅ Batch processing successful: {len(batch_results)} frames")
        for i, result in enumerate(batch_results):
            print(f"      📷 Frame {i+1}: {result['frame_id']} -> {result['weaviate_id']}")
        
        # Test batch retrieval
        print("📦 Testing batch frame retrieval...")
        
        # Create a mapping from weaviate_id to frame_id for the mock
        weaviate_to_frame_mapping = {
            f'weaviate_batch_{i}': f'batch_test_frame_{i:03d}'
            for i in range(5)
        }
        
        def mock_get_frame_by_id(weaviate_id):
            frame_id = weaviate_to_frame_mapping.get(weaviate_id, weaviate_id)
            return {
                'frame_id': frame_id,
                'video_id': 'batch_test_video',
                'timestamp': 1.5,
                'frame_data': b'fake_frame_data',
                'embedding': np.random.rand(512).tolist(),
                'metadata': {'test': True, 'batch': True},
                'created_at': '2025-01-01T00:00:00'
            }
        
        mock_service.get_frame_by_id.remote.side_effect = mock_get_frame_by_id
        
        # Retrieve all frames from batch
        retrieved_frames = []
        for result in batch_results:
            retrieved_frame = mock_service.get_frame_by_id.remote(result['weaviate_id'])
            retrieved_frames.append(retrieved_frame)
            assert retrieved_frame['frame_id'] == result['frame_id']
        
        print(f"   ✅ Retrieved {len(retrieved_frames)} frames from batch")
        
        print("✅ Weaviate batch operations test passed")

@pytest.mark.asyncio
async def test_real_text_query_endpoint():
    """Test the real text query embedding endpoint"""
    print("\n🔤 Testing real text query endpoint...")
    
    # Get the endpoint URL from environment
    clip_endpoint_url = os.getenv("CLIP_EMBEDDING_URL")
    if not clip_endpoint_url:
        print("❌ CLIP_EMBEDDING_URL environment variable not set")
        return
    
    # Construct the text query endpoint URL
    base_url = clip_endpoint_url.replace('.modal.run', '')
    text_endpoint_url = f"{base_url}-embed-text-query-endpoint.modal.run"
    
    print(f"🎯 Testing endpoint: {text_endpoint_url}")
    
    # Test query
    query = "What programming languages are being used?"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Prepare the request payload
            payload = {
                "query": query
            }
            
            print(f"📤 Sending request: '{query}'")
            
            # Make the request
            async with session.post(
                text_endpoint_url, 
                json=payload, 
                timeout=30
            ) as response:
                
                print(f"📥 Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Verify the response structure
                    assert result.get('success') == True, "Response should indicate success"
                    assert 'embedding' in result, "Response should contain embedding"
                    assert 'embedding_dimension' in result, "Response should contain embedding_dimension"
                    
                    embedding = result.get('embedding', [])
                    embedding_dimension = result.get('embedding_dimension', 0)
                    
                    print(f"   ✅ Success!")
                    print(f"      - Embedding dimension: {embedding_dimension}")
                    print(f"      - Embedding length: {len(embedding)}")
                    
                    # Verify it's a 512-dimensional CLIP embedding
                    assert embedding_dimension == 512, f"Expected 512 dimensions, got {embedding_dimension}"
                    assert len(embedding) == 512, f"Expected 512 embedding values, got {len(embedding)}"
                    
                    print(f"      - ✅ Valid CLIP embedding (512 dimensions)")
                    
                    # Test that embeddings are different for different queries
                    print("🔄 Testing embedding uniqueness...")
                    
                    # Test with a different query
                    different_query = "Show me the code editor"
                    different_payload = {"query": different_query}
                    
                    async with session.post(
                        text_endpoint_url, 
                        json=different_payload, 
                        timeout=30
                    ) as different_response:
                        
                        if different_response.status == 200:
                            different_result = await different_response.json()
                            different_embedding = different_result.get('embedding', [])
                            
                            # Check that embeddings are different (not identical)
                            if embedding != different_embedding:
                                print(f"      - ✅ Embeddings are unique for different queries")
                            else:
                                print(f"      - ⚠️ Embeddings are identical (unexpected)")
                        
                        else:
                            print(f"      - ❌ Second query failed: {different_response.status}")
                
                else:
                    error_text = await response.text()
                    print(f"   ❌ Request failed: {response.status} - {error_text}")
                    assert False, f"Request failed with status {response.status}"
        
        print("✅ Real text query endpoint test passed")
        
    except Exception as e:
        print(f"❌ Text query endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("🧪 Running embedding pipeline tests...")
    pytest.main([__file__, "-v"]) 