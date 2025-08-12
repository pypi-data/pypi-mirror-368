#!/usr/bin/env python3
"""
Simple test script to verify Weaviate database integration
This script tests actual database operations with the Modal service
"""

import asyncio
import os
import tempfile
import cv2
import numpy as np
from src.embedding_pipeline import EmbeddingPipeline
from src.video_stream import VideoClip

async def test_weaviate_integration():
    """Test actual Weaviate database integration"""
    print("🗄️ Testing Weaviate database integration...")
    
    # Create a test video clip
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "weaviate_integration_test.mp4")
    
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
            clip_endpoint_url=os.getenv("CLIP_EMBEDDING_URL"),
            enable_embeddings=True
        )
        
        print(f"🔮 Processing clip: {clip.file_path}")
        
        # Generate embeddings
        result = await pipeline.generate_clip_embeddings(clip, num_frames=4)
        
        if result.embedding_success:
            print(f"✅ Successfully embedded {result.successful_frame_count} frames")
            
            # Check Weaviate storage
            frames_with_weaviate_ids = [f for f in result.successful_frames if f.weaviate_id]
            print(f"📊 Frames stored in Weaviate: {len(frames_with_weaviate_ids)}/{result.successful_frame_count}")
            
            # Verify each successful frame has a Weaviate ID
            for frame in result.successful_frames:
                if frame.embedding_success:
                    if frame.weaviate_id:
                        print(f"   ✅ Frame {frame.frame_id} stored in Weaviate with ID: {frame.weaviate_id}")
                    else:
                        print(f"   ⚠️ Frame {frame.frame_id} missing Weaviate ID")
            
            # Test database statistics
            print("📊 Checking database statistics...")
            stats = pipeline.get_statistics()
            print(f"   - Total clips processed: {stats['clips_processed']}")
            print(f"   - Total frame embeddings: {stats['frames_embedded']}")
            print(f"   - Total failures: {stats['embedding_failures']}")
            print(f"   - Pipeline running: {stats['is_running']}")
            print(f"   - Embeddings enabled: {stats['enable_embeddings']}")
            
            # Summary
            print("\n📋 Integration Test Summary:")
            print(f"   - Video processed: {clip.file_path}")
            print(f"   - Frames extracted: {result.frame_count}")
            print(f"   - Frames embedded: {result.successful_frame_count}")
            print(f"   - Frames stored in Weaviate: {len(frames_with_weaviate_ids)}")
            print(f"   - Video ID: {result.video_id}")
            
            if len(frames_with_weaviate_ids) == result.successful_frame_count:
                print("   ✅ All embedded frames successfully stored in Weaviate!")
            else:
                print(f"   ⚠️ Only {len(frames_with_weaviate_ids)}/{result.successful_frame_count} frames stored in Weaviate")
        
        else:
            print(f"❌ Embedding failed: {result.embedding_error}")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        os.rmdir(temp_dir)
        print("🧹 Cleanup completed")

async def test_text_query_integration():
    """Test text query integration with Weaviate"""
    print("\n🔤 Testing text query integration...")
    
    # Test query
    query = "What programming languages are being used?"
    
    try:
        # Create embedding pipeline
        pipeline = EmbeddingPipeline(
            clip_endpoint_url=os.getenv("CLIP_EMBEDDING_URL"),
            enable_embeddings=True
        )
        
        print(f"🔤 Testing text query: '{query}'")
        
        # This would require the actual Modal service to be running
        # For now, we'll just verify the pipeline is configured correctly
        if pipeline.enable_embeddings and pipeline.clip_endpoint_url:
            print("   ✅ Text query pipeline configured correctly")
            print(f"   - Endpoint URL: {pipeline.clip_endpoint_url}")
            print(f"   - Embeddings enabled: {pipeline.enable_embeddings}")
        else:
            print("   ⚠️ Text query pipeline not properly configured")
        
    except Exception as e:
        print(f"❌ Text query integration test failed: {e}")

if __name__ == "__main__":
    print("🧪 Running Weaviate integration tests...")
    
    # Run the tests
    asyncio.run(test_weaviate_integration())
    asyncio.run(test_text_query_integration())
    
    print("\n✅ Integration tests completed!") 