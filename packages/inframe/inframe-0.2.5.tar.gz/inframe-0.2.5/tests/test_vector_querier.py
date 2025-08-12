#!/usr/bin/env python3
import asyncio
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

from src.vector_querier import VectorQuerier, FrameSearchResult, create_vector_querier
from src.embedding_pipeline import ProcessedFrame

@pytest.fixture
def mock_weaviate_client():
    """Create a mock Weaviate client"""
    client = Mock()
    client.is_ready.return_value = True
    client.query = Mock()
    return client

@pytest.fixture
def vector_querier(mock_weaviate_client):
    """Create a VectorQuerier with mocked dependencies"""
    with patch('src.vector_querier.weaviate.Client', return_value=mock_weaviate_client):
        querier = VectorQuerier(
            clip_endpoint_url="http://test-clip-service.com",
            weaviate_endpoint_url="http://test-weaviate.com"
        )
        return querier

@pytest.fixture
def sample_processed_frames():
    """Create sample ProcessedFrame objects for testing"""
    return [
        ProcessedFrame(
            frame_id="test_video_frame_000",
            timestamp=1.0,
            frame_path="/path/to/frame_000.jpg",
            weaviate_id="weaviate_123",
            embedding_success=True
        ),
        ProcessedFrame(
            frame_id="test_video_frame_001", 
            timestamp=5.0,
            frame_path="/path/to/frame_001.jpg",
            weaviate_id="weaviate_456",
            embedding_success=True
        ),
        ProcessedFrame(
            frame_id="test_video_frame_002",
            timestamp=10.0,
            frame_path="/path/to/frame_002.jpg", 
            weaviate_id="weaviate_789",
            embedding_success=True
        )
    ]

def test_vector_querier_creation():
    """Test VectorQuerier initialization"""
    print("\n🧪 Testing VectorQuerier creation...")
    
    with patch('src.vector_querier.weaviate.Client') as mock_client_class:
        mock_client = Mock()
        mock_client.is_ready.return_value = True
        mock_client_class.return_value = mock_client
        
        # Test with explicit URLs
        querier = VectorQuerier(
            clip_endpoint_url="http://test-clip.com",
            weaviate_endpoint_url="http://test-weaviate.com"
        )
        
        assert querier.clip_endpoint_url == "http://test-clip.com"
        assert querier.weaviate_endpoint_url == "http://test-weaviate.com"
        assert querier.total_queries_processed == 0
        
    print("✅ VectorQuerier creation test passed")

def test_vector_querier_creation_with_env_vars():
    """Test VectorQuerier creation with environment variables"""
    print("\n🌍 Testing VectorQuerier creation with env vars...")
    
    with patch.dict('os.environ', {
        'CLIP_EMBEDDING_URL': 'http://env-clip.com',
        'WEAVIATE_URL': 'http://env-weaviate.com',
        'WEAVIATE_API_KEY': 'test-key'
    }):
        with patch('src.vector_querier.weaviate.Client') as mock_client_class:
            mock_client = Mock()
            mock_client.is_ready.return_value = True
            mock_client_class.return_value = mock_client
            
            querier = VectorQuerier()
            
            assert querier.clip_endpoint_url == "http://env-clip.com"
            assert querier.weaviate_endpoint_url == "http://env-weaviate.com"
            assert querier.weaviate_api_key == "test-key"
    
    print("✅ Environment variables test passed")

def test_vector_querier_creation_missing_urls():
    """Test VectorQuerier creation with missing URLs"""
    print("\n❌ Testing VectorQuerier creation with missing URLs...")
    
    # Test missing CLIP URL
    with pytest.raises(ValueError, match="CLIP embedding URL must be provided"):
        VectorQuerier(weaviate_endpoint_url="http://test-weaviate.com")
    
    # Test missing Weaviate URL
    with pytest.raises(ValueError, match="Weaviate URL must be provided"):
        VectorQuerier(clip_endpoint_url="http://test-clip.com")
    
    print("✅ Missing URLs validation test passed")

def test_create_vector_querier_factory():
    """Test the factory function"""
    print("\n🏭 Testing vector querier factory...")
    
    with patch('src.vector_querier.weaviate.Client') as mock_client_class:
        mock_client = Mock()
        mock_client.is_ready.return_value = True
        mock_client_class.return_value = mock_client
        
        querier = create_vector_querier(
            clip_endpoint_url="http://factory-clip.com",
            weaviate_endpoint_url="http://factory-weaviate.com"
        )
        
        assert isinstance(querier, VectorQuerier)
        assert querier.clip_endpoint_url == "http://factory-clip.com"
        assert querier.weaviate_endpoint_url == "http://factory-weaviate.com"
    
    print("✅ Factory function test passed")

@pytest.mark.asyncio
async def test_embed_text_query_success(vector_querier):
    """Test successful text query embedding"""
    print("\n🎯 Testing successful text embedding...")
    
    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'success': True,
        'embedding': [0.1, 0.2, 0.3, 0.4, 0.5]
    }
    
    query = "person sitting at desk"
    
    with patch('requests.post', return_value=mock_response):
        embedding = await vector_querier.embed_text_query(query)
        
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (5,)
        np.testing.assert_array_almost_equal(embedding, [0.1, 0.2, 0.3, 0.4, 0.5])
    
    print("✅ Successful text embedding test passed")

@pytest.mark.asyncio
async def test_embed_text_query_failure(vector_querier):
    """Test text query embedding failures"""
    print("\n❌ Testing text embedding failures...")
    
    query = "test query"
    
    # Test HTTP error
    mock_response_error = Mock()
    mock_response_error.status_code = 500
    mock_response_error.text = "Internal Server Error"
    
    with patch('requests.post', return_value=mock_response_error):
        embedding = await vector_querier.embed_text_query(query)
        assert embedding is None
        assert vector_querier.total_query_embedding_failures == 1
    
    # Test API error response
    mock_response_api_error = Mock()
    mock_response_api_error.status_code = 200
    mock_response_api_error.json.return_value = {
        'success': False,
        'error': 'Invalid query format'
    }
    
    with patch('requests.post', return_value=mock_response_api_error):
        embedding = await vector_querier.embed_text_query(query)
        assert embedding is None
        assert vector_querier.total_query_embedding_failures == 2
    
    # Test network exception
    with patch('requests.post', side_effect=Exception("Network error")):
        embedding = await vector_querier.embed_text_query(query)
        assert embedding is None
        assert vector_querier.total_query_embedding_failures == 3
    
    print("✅ Text embedding failure test passed")

@pytest.mark.asyncio
async def test_search_frames_success(vector_querier, sample_processed_frames):
    """Test successful frame search"""
    print("\n🔍 Testing successful frame search...")
    
    # Mock text embedding
    mock_embedding = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    vector_querier.embed_text_query = Mock(return_value=mock_embedding)
    
    # Mock Weaviate search response
    mock_weaviate_response = {
        'data': {
            'Get': {
                'VideoFrame': [
                    {
                        'frame_id': 'test_video_frame_000',
                        'video_id': 'test_video_123',
                        'timestamp': 1.0,
                        'frame_path': '/path/to/frame_000.jpg',
                        'weaviate_id': 'weaviate_123',
                        'embedding_success': True,
                        '_additional': {
                            'certainty': 0.95,
                            'distance': 0.05
                        }
                    },
                    {
                        'frame_id': 'test_video_frame_001',
                        'video_id': 'test_video_123', 
                        'timestamp': 5.0,
                        'frame_path': '/path/to/frame_001.jpg',
                        'weaviate_id': 'weaviate_456',
                        'embedding_success': True,
                        '_additional': {
                            'certainty': 0.87,
                            'distance': 0.13
                        }
                    }
                ]
            }
        }
    }
    
    # Configure mock query builder
    mock_query_builder = Mock()
    mock_query_builder.get.return_value = mock_query_builder
    mock_query_builder.with_near_vector.return_value = mock_query_builder
    mock_query_builder.with_limit.return_value = mock_query_builder
    mock_query_builder.with_additional.return_value = mock_query_builder
    mock_query_builder.do.return_value = mock_weaviate_response
    
    vector_querier.weaviate_client.query = mock_query_builder
    
    # Perform search
    query = "person sitting at desk"
    results = await vector_querier.search_frames(query, top_k=5, min_similarity=0.8)
    
    # Verify results
    assert len(results) == 2
    assert vector_querier.total_queries_processed == 1
    assert vector_querier.total_search_operations == 1
    
    # Check first result
    result1 = results[0]
    assert isinstance(result1, FrameSearchResult)
    assert result1.similarity_score == 0.95
    assert result1.distance == 0.05
    assert result1.video_id == 'test_video_123'
    assert result1.frame.frame_id == 'test_video_frame_000'
    assert result1.frame.timestamp == 1.0
    
    # Check second result
    result2 = results[1]
    assert result2.similarity_score == 0.87
    assert result2.frame.frame_id == 'test_video_frame_001'
    
    print("✅ Successful frame search test passed")

@pytest.mark.asyncio
async def test_search_frames_with_similarity_filter(vector_querier):
    """Test frame search with minimum similarity filtering"""
    print("\n🎚️ Testing frame search with similarity filter...")
    
    # Mock text embedding
    mock_embedding = np.array([0.1, 0.2, 0.3])
    vector_querier.embed_text_query = Mock(return_value=mock_embedding)
    
    # Mock Weaviate response with mixed similarity scores
    mock_weaviate_response = {
        'data': {
            'Get': {
                'VideoFrame': [
                    {
                        'frame_id': 'high_similarity_frame',
                        'video_id': 'test_video',
                        'timestamp': 1.0,
                        'frame_path': '/path/to/high.jpg',
                        'weaviate_id': 'high_123',
                        'embedding_success': True,
                        '_additional': {
                            'certainty': 0.9,  # High similarity
                            'distance': 0.1
                        }
                    },
                    {
                        'frame_id': 'low_similarity_frame',
                        'video_id': 'test_video',
                        'timestamp': 2.0,
                        'frame_path': '/path/to/low.jpg',
                        'weaviate_id': 'low_456',
                        'embedding_success': True,
                        '_additional': {
                            'certainty': 0.3,  # Low similarity
                            'distance': 0.7
                        }
                    }
                ]
            }
        }
    }
    
    # Configure mock query builder
    mock_query_builder = Mock()
    mock_query_builder.get.return_value = mock_query_builder
    mock_query_builder.with_near_vector.return_value = mock_query_builder
    mock_query_builder.with_limit.return_value = mock_query_builder
    mock_query_builder.with_additional.return_value = mock_query_builder
    mock_query_builder.do.return_value = mock_weaviate_response
    
    vector_querier.weaviate_client.query = mock_query_builder
    
    # Search with high minimum similarity (should filter out low similarity frame)
    results = await vector_querier.search_frames("test query", min_similarity=0.7)
    
    assert len(results) == 1
    assert results[0].frame.frame_id == 'high_similarity_frame'
    assert results[0].similarity_score == 0.9
    
    print("✅ Similarity filter test passed")

@pytest.mark.asyncio
async def test_search_frames_embedding_failure(vector_querier):
    """Test frame search when text embedding fails"""
    print("\n💥 Testing frame search with embedding failure...")
    
    # Mock failed text embedding
    vector_querier.embed_text_query = Mock(return_value=None)
    
    results = await vector_querier.search_frames("test query")
    
    assert len(results) == 0
    assert vector_querier.total_queries_processed == 1
    assert vector_querier.total_search_operations == 0  # Search not attempted
    
    print("✅ Embedding failure test passed")

def test_get_frame_by_id_success(vector_querier):
    """Test successful frame retrieval by ID"""
    print("\n🎯 Testing successful frame retrieval by ID...")
    
    # Mock Weaviate response
    mock_weaviate_response = {
        'data': {
            'Get': {
                'VideoFrame': [
                    {
                        'frame_id': 'test_frame_123',
                        'video_id': 'test_video_456',
                        'timestamp': 10.5,
                        'frame_path': '/path/to/test_frame.jpg',
                        'weaviate_id': 'weaviate_789',
                        'embedding_success': True
                    }
                ]
            }
        }
    }
    
    # Configure mock query builder
    mock_query_builder = Mock()
    mock_query_builder.get.return_value = mock_query_builder
    mock_query_builder.with_where.return_value = mock_query_builder
    mock_query_builder.with_limit.return_value = mock_query_builder
    mock_query_builder.do.return_value = mock_weaviate_response
    
    vector_querier.weaviate_client.query = mock_query_builder
    
    # Retrieve frame
    frame = vector_querier.get_frame_by_id('test_frame_123')
    
    assert frame is not None
    assert isinstance(frame, ProcessedFrame)
    assert frame.frame_id == 'test_frame_123'
    assert frame.timestamp == 10.5
    assert frame.frame_path == '/path/to/test_frame.jpg'
    assert frame.embedding_success == True
    
    print("✅ Successful frame retrieval test passed")

def test_get_frame_by_id_not_found(vector_querier):
    """Test frame retrieval when frame not found"""
    print("\n🔍 Testing frame retrieval when not found...")
    
    # Mock empty Weaviate response
    mock_weaviate_response = {
        'data': {
            'Get': {
                'VideoFrame': []
            }
        }
    }
    
    # Configure mock query builder
    mock_query_builder = Mock()
    mock_query_builder.get.return_value = mock_query_builder
    mock_query_builder.with_where.return_value = mock_query_builder
    mock_query_builder.with_limit.return_value = mock_query_builder
    mock_query_builder.do.return_value = mock_weaviate_response
    
    vector_querier.weaviate_client.query = mock_query_builder
    
    # Try to retrieve non-existent frame
    frame = vector_querier.get_frame_by_id('nonexistent_frame')
    
    assert frame is None
    
    print("✅ Frame not found test passed")

def test_get_frames_by_video_id(vector_querier):
    """Test retrieving all frames for a video"""
    print("\n📹 Testing frame retrieval by video ID...")
    
    # Mock Weaviate response with multiple frames
    mock_weaviate_response = {
        'data': {
            'Get': {
                'VideoFrame': [
                    {
                        'frame_id': 'video_123_frame_000',
                        'video_id': 'video_123',
                        'timestamp': 1.0,
                        'frame_path': '/path/to/frame_000.jpg',
                        'weaviate_id': 'weaviate_1',
                        'embedding_success': True
                    },
                    {
                        'frame_id': 'video_123_frame_001',
                        'video_id': 'video_123',
                        'timestamp': 5.0,
                        'frame_path': '/path/to/frame_001.jpg',
                        'weaviate_id': 'weaviate_2',
                        'embedding_success': True
                    },
                    {
                        'frame_id': 'video_123_frame_002',
                        'video_id': 'video_123',
                        'timestamp': 10.0,
                        'frame_path': '/path/to/frame_002.jpg',
                        'weaviate_id': 'weaviate_3',
                        'embedding_success': False
                    }
                ]
            }
        }
    }
    
    # Configure mock query builder
    mock_query_builder = Mock()
    mock_query_builder.get.return_value = mock_query_builder
    mock_query_builder.with_where.return_value = mock_query_builder
    mock_query_builder.with_sort.return_value = mock_query_builder
    mock_query_builder.do.return_value = mock_weaviate_response
    
    vector_querier.weaviate_client.query = mock_query_builder
    
    # Retrieve frames for video
    frames = vector_querier.get_frames_by_video_id('video_123')
    
    assert len(frames) == 3
    assert all(isinstance(frame, ProcessedFrame) for frame in frames)
    assert frames[0].frame_id == 'video_123_frame_000'
    assert frames[1].frame_id == 'video_123_frame_001'
    assert frames[2].frame_id == 'video_123_frame_002'
    
    # Check timestamps
    assert frames[0].timestamp == 1.0
    assert frames[1].timestamp == 5.0
    assert frames[2].timestamp == 10.0
    
    # Check embedding success flags
    assert frames[0].embedding_success == True
    assert frames[1].embedding_success == True
    assert frames[2].embedding_success == False
    
    print("✅ Video frames retrieval test passed")

def test_get_search_stats(vector_querier):
    """Test search statistics"""
    print("\n📊 Testing search statistics...")
    
    # Initially zero stats
    stats = vector_querier.get_search_stats()
    expected_stats = {
        'total_queries_processed': 0,
        'total_query_embedding_failures': 0,
        'total_search_operations': 0,
        'query_success_rate': 0.0,
        'clip_endpoint_url': 'http://test-clip-service.com',
        'weaviate_endpoint_url': 'http://test-weaviate.com'
    }
    assert stats == expected_stats
    
    # Manually update stats to test calculation
    vector_querier.total_queries_processed = 10
    vector_querier.total_query_embedding_failures = 2
    vector_querier.total_search_operations = 8
    
    stats = vector_querier.get_search_stats()
    assert stats['total_queries_processed'] == 10
    assert stats['total_query_embedding_failures'] == 2
    assert stats['total_search_operations'] == 8
    assert stats['query_success_rate'] == 0.8  # (10-2)/10
    
    print("✅ Search statistics test passed")

def test_frame_search_result_to_dict():
    """Test FrameSearchResult serialization"""
    print("\n📋 Testing FrameSearchResult serialization...")
    
    # Create test frame
    frame = ProcessedFrame(
        frame_id="test_frame",
        timestamp=5.5,
        embedding_success=True
    )
    
    # Create search result
    result = FrameSearchResult(
        frame=frame,
        similarity_score=0.89,
        distance=0.11,
        video_id="test_video_123"
    )
    
    # Test serialization
    result_dict = result.to_dict()
    
    assert 'frame' in result_dict
    assert 'similarity_score' in result_dict
    assert 'distance' in result_dict
    assert 'video_id' in result_dict
    
    assert result_dict['similarity_score'] == 0.89
    assert result_dict['distance'] == 0.11
    assert result_dict['video_id'] == "test_video_123"
    assert isinstance(result_dict['frame'], dict)
    
    print("✅ FrameSearchResult serialization test passed")

def test_weaviate_connection_failure():
    """Test VectorQuerier creation when Weaviate connection fails"""
    print("\n💥 Testing Weaviate connection failure...")
    
    with patch('src.vector_querier.weaviate.Client') as mock_client_class:
        mock_client = Mock()
        mock_client.is_ready.return_value = False  # Simulate connection failure
        mock_client_class.return_value = mock_client
        
        with pytest.raises(ConnectionError, match="Cannot connect to Weaviate"):
            VectorQuerier(
                clip_endpoint_url="http://test-clip.com",
                weaviate_endpoint_url="http://test-weaviate.com"
            )
    
    print("✅ Weaviate connection failure test passed")

if __name__ == "__main__":
    print("🧪 Running vector querier tests...")
    pytest.main([__file__, "-v"]) 