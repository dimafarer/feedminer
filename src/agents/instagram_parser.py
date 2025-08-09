"""
Instagram JSON Parser Agent for FeedMiner.

This Strands agent specializes in parsing Instagram saved content exports,
extracting goal-oriented insights, and categorizing content for personal development.

SUPPORTED FORMATS:
1. Real Instagram Export Format: {"saved_saved_media": [...]}
2. FeedMiner Enhanced Format: {"type": "instagram_saved", "content": {"saved_posts": [...]}}

The agent automatically detects format and transforms real Instagram exports
into enhanced format with goal-setting insights and behavioral analysis.
"""

import json
import os
import psutil
from datetime import datetime
from typing import Dict, List, Any, Optional
import boto3
from decimal import Decimal
# Use Strands with Anthropic directly (simple version)
from strands import Agent
from strands.models.anthropic import AnthropicModel
from pydantic import BaseModel, Field

# Import WebSocket streaming utilities  
try:
    from websocket_stream import broadcast_reasoning_step
except ImportError:
    try:
        from ..utils.websocket_stream import broadcast_reasoning_step
    except ImportError:
        # Fallback for when running directly
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from utils.websocket_stream import broadcast_reasoning_step


class InstagramPost(BaseModel):
    """Structured representation of an Instagram post."""
    post_id: str = Field(description="Unique Instagram post identifier")
    author: str = Field(description="Username of the post author")
    caption: str = Field(description="Post caption text")
    media_type: str = Field(description="Type of media (photo, video, carousel, reel)")
    saved_at: str = Field(description="When the post was saved")
    hashtags: List[str] = Field(default=[], description="Hashtags used in the post")
    location: Optional[str] = Field(default=None, description="Location tagged in post")
    engagement: Optional[Dict[str, int]] = Field(default=None, description="Likes, comments, etc.")
    interaction_type: str = Field(default="saved", description="Type of interaction (saved, liked, posted, commented)")
    timestamp: int = Field(default=0, description="Timestamp of the interaction")


class ContentCategory(BaseModel):
    """Content category classification."""
    name: str = Field(description="Category name (e.g., 'Technology', 'Food', 'Travel')")
    confidence: float = Field(description="Confidence score 0-1")
    reasoning: str = Field(description="Why this category was chosen")


class ContentInsight(BaseModel):
    """Extracted insight from content."""
    type: str = Field(description="Type of insight (theme, trend, preference)")
    description: str = Field(description="Description of the insight")
    evidence: List[str] = Field(description="Supporting evidence from the content")
    relevance_score: float = Field(description="How relevant this insight is (0-1)")


class InstagramAnalysisResult(BaseModel):
    """Complete analysis result for Instagram content."""
    total_posts: int = Field(description="Total number of posts analyzed")
    categories: List[ContentCategory] = Field(description="Identified content categories")
    insights: List[ContentInsight] = Field(description="Extracted insights")
    top_authors: List[Dict[str, Any]] = Field(description="Most saved authors")
    date_range: Dict[str, str] = Field(description="Date range of saved content")
    summary: str = Field(description="Overall summary of saved content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the analysis")


class InstagramParserAgent:
    """Strands agent for parsing and analyzing Instagram saved content."""
    
    def _log_memory_usage(self, stage: str):
        """Log current memory usage for monitoring."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            print(f"💾 MEMORY [{stage}]: {memory_info.rss / 1024 / 1024:.1f}MB RSS, {memory_info.vms / 1024 / 1024:.1f}MB VMS")
        except Exception as e:
            print(f"Could not get memory info: {e}")

    def __init__(self):
        """Initialize the Instagram parser agent."""
        self._log_memory_usage("INIT_START")
        
        # Check if API key is available
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        print(f"API key available: {bool(api_key)} (length: {len(api_key) if api_key else 0})")
        
        # Initialize Strands agent with Anthropic directly
        anthropic_model = AnthropicModel(
            model_id="claude-3-5-sonnet-20241022",
            api_key=api_key,
            max_tokens=4096
        )
        
        self.agent = Agent(
            name="Instagram Content Parser",
            model=anthropic_model,
            system_prompt="""You are an expert at analyzing Instagram saved content. 
            You understand social media trends, content categories, and user behavior patterns.
            Extract meaningful insights from Instagram post data and provide structured analysis."""
        )
        
        # Structured output will be handled through agent.structured_output() method
        
        # DynamoDB and S3 clients for data persistence
        self.dynamodb = boto3.resource('dynamodb')
        self.s3 = boto3.client('s3')
        
        # Environment variables
        self.content_table_name = os.environ.get('CONTENT_TABLE')
        self.jobs_table_name = os.environ.get('JOBS_TABLE')
        self.content_bucket = os.environ.get('CONTENT_BUCKET')
    
    async def parse_instagram_export(self, raw_data: Dict[str, Any], content_id: str = None) -> InstagramAnalysisResult:
        """
        Parse Instagram saved content export and extract insights.
        
        Args:
            raw_data: Raw Instagram export data
            content_id: Content ID for WebSocket streaming (optional)
            
        Returns:
            Structured analysis result
        """
        # Stream initial reasoning step
        if content_id:
            broadcast_reasoning_step(
                content_id=content_id,
                step="data_extraction",
                reasoning="Starting analysis by extracting Instagram posts from the raw export data...",
                progress=0.1
            )
        
        # Extract posts from the raw data
        posts = self._extract_posts(raw_data)
        
        if content_id:
            broadcast_reasoning_step(
                content_id=content_id,
                step="post_extraction_complete",
                reasoning=f"Successfully extracted {len(posts)} posts from the export. Now analyzing content patterns and themes...",
                progress=0.2
            )
        
        # Create analysis prompt
        prompt = self._build_analysis_prompt(posts)
        
        if content_id:
            broadcast_reasoning_step(
                content_id=content_id,
                step="ai_analysis_starting",
                reasoning="Preparing detailed analysis prompt for the AI model. Looking for behavioral patterns, content categories, and goal opportunities...",
                progress=0.3
            )
        
        # Run analysis with structured output using Strands
        try:
            if content_id:
                broadcast_reasoning_step(
                    content_id=content_id,
                    step="ai_processing",
                    reasoning="The AI model is now processing your content. Analyzing themes, interests, and behavioral patterns to generate personalized insights...",
                    progress=0.5
                )
            
            # Use the agent's structured output method with correct parameters
            result = await self.agent.structured_output_async(
                output_model=InstagramAnalysisResult,
                prompt=prompt
            )
            
            if content_id:
                broadcast_reasoning_step(
                    content_id=content_id,
                    step="analysis_complete",
                    reasoning=f"Analysis complete! Found {len(result.categories)} content categories and {len(result.insights)} key insights about your interests and goals.",
                    progress=1.0
                )
            
            return result
        except Exception as e:
            if content_id:
                broadcast_reasoning_step(
                    content_id=content_id,
                    step="analysis_error",
                    reasoning=f"Analysis encountered an error: {str(e)}. This might be due to content format or AI processing issues.",
                    progress=0.0
                )
            print(f"🚨 CRITICAL ERROR: Strands structured output failed: {e}")
            raise Exception(f"AI analysis failed for Instagram content: {str(e)}") from e
    
    async def parse_multi_type_instagram_export(self, raw_data: Dict[str, Any], export_info: Dict[str, Any], content_id: str = None) -> InstagramAnalysisResult:
        """
        Parse multi-data-type Instagram export with consolidated analysis.
        
        Args:
            raw_data: Combined Instagram export data with multiple data types
            export_info: Export metadata including data types
            content_id: Content ID for WebSocket streaming (optional)
            
        Returns:
            Structured analysis result combining all data types
        """
        # Extract data directly from root level (not from combined_data)
        data_types = export_info.get('dataTypes', [])
        
        if content_id:
            broadcast_reasoning_step(
                content_id=content_id,
                step="multi_type_analysis_start",
                reasoning=f"Starting comprehensive analysis of your Instagram data. Processing {len(data_types)} data types: {', '.join(data_types)}...",
                progress=0.05
            )
        
        print(f"Processing multi-type export with data types: {data_types}")
        print(f"Raw data keys: {list(raw_data.keys())}")
        self._log_memory_usage("BEFORE_PROCESSING")
        
        # Extract posts from all data types with sampling for large datasets
        all_posts = []
        all_interactions = []
        # Debug mode: intelligent sampling based on dataset size
        debug_mode = os.environ.get('DEBUG_MODE', 'true').lower() == 'true'
        
        # Calculate total items across all data types first
        total_items = 0
        for data_type in data_types:
            if data_type in raw_data:
                data_section = raw_data[data_type]
                print(f"Data type {data_type} structure: {list(data_section.keys()) if isinstance(data_section, dict) else type(data_section)}")
                
                if data_type == 'saved_posts':
                    count = len(data_section.get('saved_saved_media', []))
                    total_items += count
                    print(f"Found {count} saved_posts items")
                elif data_type == 'liked_posts':
                    count = len(data_section.get('likes_media_likes', []))
                    total_items += count  
                    print(f"Found {count} liked_posts items")
                elif data_type == 'comments':
                    if isinstance(data_section, dict):
                        count = len(data_section.get('comments_media_comments', []))
                    elif isinstance(data_section, list):
                        count = len(data_section)
                    else:
                        count = 0
                    total_items += count
                    print(f"Found {count} comments items")
                elif data_type == 'user_posts':
                    if isinstance(data_section, dict):
                        count = len(data_section.get('content', []))
                    elif isinstance(data_section, list):
                        count = len(data_section)
                    else:
                        count = 0
                    total_items += count
                    print(f"Found {count} user_posts items")
                elif data_type == 'following':
                    count = len(data_section.get('relationships_following', []))
                    total_items += count
                    print(f"Found {count} following items")
            else:
                print(f"Data type {data_type} not found in raw_data")
        
        # Smart sampling: scale sample size based on total items
        if debug_mode:
            if total_items == 0:
                # If counting failed, default to 100 per type (Phase 1 requirement)
                sample_size_per_type = 100
            elif total_items <= 20:
                sample_size_per_type = max(10, total_items // len(data_types))  # At least 10 per type
            elif total_items <= 100:
                sample_size_per_type = 20  # 20 per type for medium datasets
            elif total_items <= 500:
                sample_size_per_type = 50  # 50 per type for large datasets  
            else:
                sample_size_per_type = 100  # 100 per type for very large datasets (Phase 1)
        else:
            sample_size_per_type = 200  # Full analysis mode
        
        print(f"🐛 DEBUG MODE: {'ENABLED' if debug_mode else 'DISABLED'} - Total items: {total_items}, Processing {sample_size_per_type} items per data type ({len(data_types)} types)")
        
        if content_id:
            broadcast_reasoning_step(
                content_id=content_id,
                step="data_sampling_strategy",
                reasoning=f"Found {total_items} total items across all data types. Using smart sampling to analyze {sample_size_per_type} items per type for optimal analysis quality while managing processing time.",
                progress=0.1
            )
        
        current_progress = 0.1
        progress_per_type = 0.5 / len(data_types)  # Allocate 50% of progress for data processing
        
        for i, data_type in enumerate(data_types):
            if data_type in raw_data:
                if content_id:
                    broadcast_reasoning_step(
                        content_id=content_id,
                        step=f"processing_{data_type}",
                        reasoning=f"Now processing your {data_type.replace('_', ' ')} data ({i+1} of {len(data_types)}). Extracting behavioral patterns and interaction preferences...",
                        progress=current_progress
                    )
                
                if data_type == 'saved_posts':
                    saved_data = raw_data[data_type].get('saved_saved_media', [])
                    # Sample the data if it's too large
                    sampled_data = saved_data[:sample_size_per_type] if len(saved_data) > sample_size_per_type else saved_data
                    
                    # Convert raw saved posts to InstagramPost objects
                    for item in sampled_data:
                        # Extract timestamp from string_map_data
                        timestamp = 0
                        saved_at = 'unknown'
                        href = ''
                        
                        if 'string_map_data' in item and item['string_map_data']:
                            saved_on_data = item['string_map_data'].get('Saved on', {})
                            if 'timestamp' in saved_on_data:
                                timestamp = saved_on_data['timestamp']
                                saved_at = datetime.fromtimestamp(timestamp).isoformat() if timestamp else 'unknown'
                            if 'href' in saved_on_data:
                                href = saved_on_data['href']
                        
                        # Extract media type from URL
                        media_type = 'unknown'
                        if '/reel/' in href:
                            media_type = 'reel'
                        elif '/p/' in href:
                            media_type = 'photo'
                        
                        post = InstagramPost(
                            post_id=f"saved_{item.get('title', 'unknown')}_{timestamp}",
                            author=item.get('title', 'unknown'),
                            caption=f"Saved content from @{item.get('title', 'unknown')}",
                            media_type=media_type,
                            saved_at=saved_at,
                            hashtags=[],
                            interaction_type='saved'
                        )
                        all_posts.append(post)
                    print(f"Processed {len(sampled_data)} of {len(saved_data)} {data_type} items")
                    
                elif data_type == 'liked_posts':
                    # Convert liked posts to post format for analysis
                    raw_liked_data = raw_data[data_type].get('likes_media_likes', [])
                    # Sample the data if it's too large
                    sampled_liked_data = raw_liked_data[:sample_size_per_type] if len(raw_liked_data) > sample_size_per_type else raw_liked_data
                    
                    for item in sampled_liked_data:
                        # Extract timestamp and convert to ISO format
                        timestamp = 0
                        saved_at = 'unknown'
                        
                        if 'string_list_data' in item and item['string_list_data']:
                            for string_item in item['string_list_data']:
                                if 'timestamp' in string_item:
                                    timestamp = string_item['timestamp']
                                    saved_at = datetime.fromtimestamp(timestamp).isoformat() if timestamp else 'unknown'
                                    break
                        
                        post = InstagramPost(
                            post_id=f"liked_{item.get('title', 'unknown')}",
                            author=item.get('title', 'unknown'),
                            caption=f"Liked content from @{item.get('title', 'unknown')}",
                            media_type='unknown',
                            saved_at=saved_at,
                            hashtags=[],
                            interaction_type='liked'
                        )
                        all_posts.append(post)
                    print(f"Processed {len(sampled_liked_data)} of {len(raw_liked_data)} {data_type} items")
                
                elif data_type == 'comments':
                    # Process comments data - handle both dict and list formats
                    comments_section = raw_data[data_type]
                    if isinstance(comments_section, dict):
                        raw_comments_data = comments_section.get('comments_media_comments', [])
                    elif isinstance(comments_section, list):
                        raw_comments_data = comments_section
                    else:
                        raw_comments_data = []
                    
                    sampled_comments_data = raw_comments_data[:sample_size_per_type] if len(raw_comments_data) > sample_size_per_type else raw_comments_data
                    
                    for item in sampled_comments_data:
                        # Extract comment data and convert to post format
                        timestamp = 0
                        saved_at = 'unknown'
                        comment_text = 'Unknown comment'
                        media_owner = 'unknown'
                        
                        # Handle comments format: string_map_data with Comment, Media Owner, Time
                        if 'string_map_data' in item and item['string_map_data']:
                            string_data = item['string_map_data']
                            
                            # Extract timestamp
                            if 'Time' in string_data and 'timestamp' in string_data['Time']:
                                timestamp = string_data['Time']['timestamp'] 
                                saved_at = datetime.fromtimestamp(timestamp).isoformat() if timestamp else 'unknown'
                            
                            # Extract comment text
                            if 'Comment' in string_data and 'value' in string_data['Comment']:
                                comment_text = string_data['Comment']['value']
                            
                            # Extract media owner
                            if 'Media Owner' in string_data and 'value' in string_data['Media Owner']:
                                media_owner = string_data['Media Owner']['value']
                        
                        post = InstagramPost(
                            post_id=f"comment_{timestamp}",
                            author=media_owner,
                            caption=f"Commented: '{comment_text}' on @{media_owner}'s post",
                            media_type='comment',
                            saved_at=saved_at,
                            hashtags=[],
                            interaction_type='commented'
                        )
                        all_posts.append(post)
                    print(f"Processed {len(sampled_comments_data)} of {len(raw_comments_data)} {data_type} items")
                    
                elif data_type == 'user_posts':
                    # Process user's own posts - handle both dict and list formats
                    user_posts_section = raw_data[data_type]
                    if isinstance(user_posts_section, dict):
                        raw_user_posts = user_posts_section.get('content', [])
                    elif isinstance(user_posts_section, list):
                        raw_user_posts = user_posts_section
                    else:
                        raw_user_posts = []
                    
                    sampled_user_posts = raw_user_posts[:sample_size_per_type] if len(raw_user_posts) > sample_size_per_type else raw_user_posts
                    
                    for item in sampled_user_posts:
                        # Extract user post data - handle nested media structure
                        timestamp = 0
                        saved_at = 'unknown'
                        title = 'Own post'
                        media_type = 'unknown'
                        
                        # Check if item has nested media array
                        if 'media' in item and item['media'] and len(item['media']) > 0:
                            media_item = item['media'][0]  # Get first media item
                            timestamp = media_item.get('creation_timestamp', 0)
                            title = media_item.get('title', 'Own post')
                            
                            # Determine media type from metadata or URI
                            if 'media_metadata' in media_item:
                                if 'photo_metadata' in media_item['media_metadata']:
                                    media_type = 'photo'
                                elif 'video_metadata' in media_item['media_metadata']:
                                    media_type = 'video'
                        else:
                            # Fallback for different structure
                            timestamp = item.get('creation_timestamp', 0)
                            title = item.get('title', 'Own post')
                            media_type = item.get('media_type', 'unknown')
                        
                        saved_at = datetime.fromtimestamp(timestamp).isoformat() if timestamp else 'unknown'
                        
                        post = InstagramPost(
                            post_id=f"user_post_{timestamp}",
                            author="user",  # User's own post
                            caption=title,
                            media_type=media_type,
                            saved_at=saved_at,
                            hashtags=[],
                            interaction_type='posted'
                        )
                        all_posts.append(post)
                    print(f"Processed {len(sampled_user_posts)} of {len(raw_user_posts)} {data_type} items")
                    
                elif data_type == 'following':
                    # Process following data
                    raw_following_data = raw_data[data_type].get('relationships_following', [])
                    sampled_following_data = raw_following_data[:sample_size_per_type] if len(raw_following_data) > sample_size_per_type else raw_following_data
                    
                    for item in sampled_following_data:
                        # Extract following data
                        timestamp = 0
                        saved_at = 'unknown'
                        
                        if 'string_list_data' in item and item['string_list_data']:
                            for string_item in item['string_list_data']:
                                if 'timestamp' in string_item:
                                    timestamp = string_item['timestamp']
                                    saved_at = datetime.fromtimestamp(timestamp).isoformat() if timestamp else 'unknown'
                                    break
                        
                        post = InstagramPost(
                            post_id=f"following_{item.get('string_list_data', [{}])[0].get('value', 'unknown')}",
                            author=item.get('string_list_data', [{}])[0].get('value', 'unknown'),
                            caption=f"Following @{item.get('string_list_data', [{}])[0].get('value', 'unknown')}",
                            media_type='profile',
                            saved_at=saved_at,
                            hashtags=[],
                            interaction_type='following'
                        )
                        all_posts.append(post)
                    print(f"Processed {len(sampled_following_data)} of {len(raw_following_data)} {data_type} items")
                
                current_progress += progress_per_type
        
        print(f"Extracted {len(all_posts)} sampled posts from {len(data_types)} data types for analysis")
        self._log_memory_usage("AFTER_EXTRACTION")
        
        if content_id:
            broadcast_reasoning_step(
                content_id=content_id,
                step="data_extraction_complete",
                reasoning=f"Data extraction complete! Successfully processed {len(all_posts)} items across {len(data_types)} data types. Now preparing for AI analysis to identify your behavioral patterns and goals.",
                progress=0.6
            )
        
        # Create enhanced analysis prompt for multi-type data
        prompt = self._build_multi_type_analysis_prompt(all_posts, data_types, export_info)
        
        if content_id:
            broadcast_reasoning_step(
                content_id=content_id,
                step="ai_analysis_preparation",
                reasoning="Preparing comprehensive analysis prompt that combines all your Instagram interactions. The AI will analyze cross-platform patterns between saved posts, likes, comments, and following behaviors.",
                progress=0.7
            )
        
        # Run analysis with structured output using Strands
        try:
            if content_id:
                broadcast_reasoning_step(
                    content_id=content_id,
                    step="ai_deep_analysis",
                    reasoning="AI is now performing deep behavioral analysis across all your Instagram data types. This includes identifying interest patterns, motivation cycles, learning preferences, and personalized goal opportunities...",
                    progress=0.8
                )
            
            # Use the agent's structured output method with correct parameters
            self._log_memory_usage("BEFORE_MULTI_AI_CALL")
            result = await self.agent.structured_output_async(
                output_model=InstagramAnalysisResult,
                prompt=prompt
            )
            self._log_memory_usage("AFTER_MULTI_AI_CALL")
            
            if content_id:
                broadcast_reasoning_step(
                    content_id=content_id,
                    step="analysis_finalization",
                    reasoning=f"AI analysis complete! Generated comprehensive insights with {len(result.categories) if hasattr(result, 'categories') else 'multiple'} content categories and detailed behavioral patterns. Finalizing results...",
                    progress=0.95
                )
                
        except Exception as e:
            if content_id:
                broadcast_reasoning_step(
                    content_id=content_id,
                    step="analysis_error",
                    reasoning=f"Multi-type analysis encountered an error: {str(e)}. This might be due to data complexity or AI processing limits.",
                    progress=0.0
                )
            print(f"🚨 CRITICAL ERROR: Multi-type AI analysis failed: {e}")
            self._log_memory_usage("AI_CALL_FAILED")
            raise Exception(f"Multi-type Instagram analysis failed: {str(e)}") from e
        
        # Add metadata about the multi-type analysis
        result.metadata = {
            'data_types_analyzed': data_types,
            'total_items_available': total_items,  # Total items found in raw data
            'total_items_processed': len(all_posts),  # Actual items processed by AI 
            'sampled_items_analyzed': len(all_posts),  # Track sampling info (same as processed)
            'export_info': export_info,
            'analysis_type': 'multi_type_consolidated',
            'debug_mode': debug_mode,
            'sample_size_per_type': sample_size_per_type
        }
        
        if content_id:
            broadcast_reasoning_step(
                content_id=content_id,
                step="analysis_complete",
                reasoning=f"Multi-type analysis successfully completed! Your Instagram behavioral profile is ready with insights from {len(data_types)} data types and {len(all_posts)} interactions.",
                progress=1.0
            )
            
        return result
    
    def _extract_posts(self, raw_data: Dict[str, Any]) -> List[InstagramPost]:
        """Extract and normalize Instagram posts from raw export data."""
        posts = []
        
        # Handle different export formats
        if 'content' in raw_data and 'saved_posts' in raw_data['content']:
            # FeedMiner format
            for post_data in raw_data['content']['saved_posts']:
                posts.append(InstagramPost(**post_data))
        elif 'saved_posts' in raw_data:
            # Direct export format
            for post_data in raw_data['saved_posts']:
                posts.append(InstagramPost(**post_data))
        elif isinstance(raw_data, list):
            # Array of posts
            for post_data in raw_data:
                posts.append(InstagramPost(**post_data))
        
        return posts
    
    def _build_analysis_prompt(self, posts: List[InstagramPost]) -> str:
        """Build analysis prompt for the agent."""
        posts_summary = "\n".join([
            f"- Post by @{post.author}: {post.caption[:100]}{'...' if len(post.caption) > 100 else ''}"
            f" [Tags: {', '.join(post.hashtags[:3])}] [{post.media_type}]"
            for post in posts[:10]  # Limit to first 10 for prompt
        ])
        
        if len(posts) > 10:
            posts_summary += f"\n... and {len(posts) - 10} more posts"
        
        return f"""
        Analyze the following Instagram saved content and provide structured insights:
        
        Total Posts: {len(posts)}
        
        Sample Posts:
        {posts_summary}
        
        Please analyze this content and provide:
        1. Content categories with confidence scores
        2. Key insights about the user's interests and behavior
        3. Top authors/accounts they save from
        4. Overall summary of their saved content preferences
        
        Provide your response as structured output using the InstagramAnalysisResult model.
        """
    
    def _build_multi_type_analysis_prompt(self, posts: List[InstagramPost], data_types: List[str], export_info: Dict[str, Any]) -> str:
        """Build analysis prompt for multi-data-type Instagram export."""
        posts_summary = "\n".join([
            f"- Post by @{post.author}: {post.caption[:100]}{'...' if len(post.caption) > 100 else ''}"
            f" [Tags: {', '.join(post.hashtags[:3])}] [{post.media_type}] [Type: {getattr(post, 'interaction_type', 'saved')}]"
            for post in posts[:15]  # Show more for multi-type analysis
        ])
        
        if len(posts) > 15:
            posts_summary += f"\n... and {len(posts) - 15} more posts"
        
        # Count items by type for the prompt
        type_counts = {}
        for post in posts:
            interaction_type = getattr(post, 'interaction_type', 'saved')
            type_counts[interaction_type] = type_counts.get(interaction_type, 0) + 1
        
        type_summary = "\n".join([f"- {type_name}: {count} items" for type_name, count in type_counts.items()])
        
        return f"""
        Analyze the following comprehensive Instagram data export with multiple interaction types:
        
        EXPORT OVERVIEW:
        - Data types included: {', '.join(data_types)}
        - Total items analyzed: {len(posts)}
        - Export date: {export_info.get('extractedAt', 'Unknown')}
        
        INTERACTION TYPE BREAKDOWN:
        {type_summary}
        
        SAMPLE CONTENT:
        {posts_summary}
        
        This is a comprehensive analysis of multiple Instagram interaction types. Please provide:
        1. Content categories with confidence scores (analyze all interaction types together)
        2. Behavioral patterns based on different interaction types (saved vs liked vs posted content)
        3. Interest evolution and trends across different interaction types
        4. Personalized goals that leverage insights from all data types
        5. Cross-interaction insights (e.g., consistency between saved and liked content)
        6. Overall behavioral profile based on the complete dataset
        
        Focus on providing a holistic analysis that combines insights from all {len(data_types)} data types 
        to create a comprehensive behavioral and interest profile.
        
        Provide your response as structured output using the InstagramAnalysisResult model.
        """
    
    def _create_fallback_analysis(self, posts: List[InstagramPost]) -> InstagramAnalysisResult:
        """DEPRECATED: Fallback analysis removed for development - should fail explicitly."""
        raise Exception("🚨 DEVELOPMENT MODE: Fallback analysis disabled - AI processing must succeed")
    
    def _detect_categories_from_hashtags(self, posts: List[InstagramPost]) -> List[ContentCategory]:
        """Basic category detection from hashtags."""
        hashtag_categories = {
            'technology': ['#ai', '#tech', '#coding', '#programming', '#software'],
            'food': ['#food', '#recipe', '#cooking', '#restaurant', '#foodie'],
            'travel': ['#travel', '#vacation', '#wanderlust', '#explore', '#adventure'],
            'fitness': ['#fitness', '#workout', '#gym', '#health', '#exercise'],
            'fashion': ['#fashion', '#style', '#outfit', '#ootd', '#clothing'],
            'photography': ['#photography', '#photo', '#camera', '#art', '#photographer']
        }
        
        category_scores = {}
        total_hashtags = 0
        
        for post in posts:
            for hashtag in post.hashtags:
                total_hashtags += 1
                for category, tags in hashtag_categories.items():
                    if hashtag.lower() in tags:
                        category_scores[category] = category_scores.get(category, 0) + 1
        
        categories = []
        for category, count in category_scores.items():
            confidence = count / max(total_hashtags, 1)
            categories.append(ContentCategory(
                name=category.title(),
                confidence=confidence,
                reasoning=f"Found {count} relevant hashtags"
            ))
        
        return sorted(categories, key=lambda x: x.confidence, reverse=True)
    
    def _convert_floats_to_decimals(self, obj):
        """Convert float values to Decimal for DynamoDB compatibility."""
        if isinstance(obj, dict):
            return {k: self._convert_floats_to_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_floats_to_decimals(v) for v in obj]
        elif isinstance(obj, float):
            return Decimal(str(obj))
        else:
            return obj

    async def save_analysis_result(self, content_id: str, analysis: InstagramAnalysisResult) -> bool:
        """Save analysis result to DynamoDB and S3."""
        try:
            # Convert analysis to dict and handle float->Decimal conversion for DynamoDB
            analysis_dict = analysis.model_dump()
            analysis_dict_decimal = self._convert_floats_to_decimals(analysis_dict)
            
            # Save to DynamoDB
            table = self.dynamodb.Table(self.content_table_name)
            table.update_item(
                Key={'contentId': content_id},
                UpdateExpression='SET analysis = :analysis, analysisTimestamp = :timestamp, #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':analysis': analysis_dict_decimal,
                    ':timestamp': datetime.now().isoformat(),
                    ':status': 'completed'
                }
            )
            
            # Save detailed result to S3
            s3_key = f"analysis/{content_id}/instagram_analysis.json"
            self.s3.put_object(
                Bucket=self.content_bucket,
                Key=s3_key,
                Body=json.dumps(analysis.model_dump(), indent=2),
                ContentType='application/json'
            )
            
            return True
            
        except Exception as e:
            print(f"Error saving analysis result: {e}")
            return False


# Lambda handler function
def handler(event, context):
    """AWS Lambda handler for Instagram parser agent."""
    print(f"Received event: {json.dumps(event)}")
    
    # Initialize agent
    agent = InstagramParserAgent()
    
    # Extract content data from event
    if 'Records' in event:
        # S3 trigger event (legacy support)
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            # Download content from S3
            response = agent.s3.get_object(Bucket=bucket, Key=key)
            raw_data = json.loads(response['Body'].read())
            
            # Extract content ID from S3 key
            content_id = key.split('/')[-1].replace('.json', '')
            
            # Run analysis with streaming reasoning
            import asyncio
            analysis = asyncio.run(agent.parse_instagram_export(raw_data, content_id))
            
            # Save results
            asyncio.run(agent.save_analysis_result(content_id, analysis))
    
    elif 'contentId' in event:
        # Orchestrator invocation
        content_id = event['contentId']
        content_type = event.get('contentType', 'instagram_export')
        s3_key = event.get('s3Key')
        metadata = event.get('metadata', {})
        
        print(f"Processing {content_type} content {content_id} from S3 key: {s3_key}")
        agent._log_memory_usage("HANDLER_START")
        
        # Download content from S3
        bucket = os.environ.get('CONTENT_BUCKET')
        if not bucket:
            print("CONTENT_BUCKET environment variable not set")
            return {'statusCode': 500, 'body': json.dumps({'error': 'Missing bucket configuration'})}
        
        try:
            # Download consolidated.json
            response = agent.s3.get_object(Bucket=bucket, Key=s3_key)
            raw_data = json.loads(response['Body'].read())
            
            agent._log_memory_usage("AFTER_S3_DOWNLOAD")
            
            # Extract export info from metadata for multi-type analysis
            export_info = {
                'extractedAt': metadata.get('M', {}).get('extractedAt', {}).get('S', 'unknown'),
                'dataTypes': [item.get('S') for item in metadata.get('M', {}).get('analyzableTypes', {}).get('L', [])],
                'totalDataPoints': int(metadata.get('M', {}).get('totalDataPoints', {}).get('N', '0'))
            }
            
            print(f"Export info: {export_info}")
            
            # Run multi-type analysis with streaming reasoning
            import asyncio
            analysis = asyncio.run(agent.parse_multi_type_instagram_export(raw_data, export_info, content_id))
            
            agent._log_memory_usage("AFTER_AI_ANALYSIS")
            
            # Save results
            success = asyncio.run(agent.save_analysis_result(content_id, analysis))
            
            agent._log_memory_usage("AFTER_SAVE")
            
            if success:
                print(f"Successfully completed analysis for {content_id}")
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Instagram analysis completed successfully',
                        'contentId': content_id,
                        'totalPosts': analysis.total_posts
                    })
                }
            else:
                print(f"Failed to save analysis for {content_id}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Failed to save analysis results'})
                }
                
        except Exception as e:
            print(f"🚨🚨🚨 CRITICAL PROCESSING ERROR for {content_id}: {e}")
            print(f"🚨 ERROR TYPE: {type(e).__name__}")
            print(f"🚨 ERROR DETAILS: {str(e)}")
            agent._log_memory_usage("ERROR")
            
            # Update status to failed with prominent error message
            try:
                table = agent.dynamodb.Table(agent.content_table_name)
                table.update_item(
                    Key={'contentId': content_id},
                    UpdateExpression='SET #status = :status, errorMessage = :error, processingError = :processing_error',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':status': 'failed',
                        ':error': f"🚨 ANALYSIS FAILED: {str(e)}",
                        ':processing_error': {
                            'error_type': type(e).__name__,
                            'error_message': str(e),
                            'failed_at': 'analysis_phase'
                        }
                    }
                )
                print(f"🚨 Updated {content_id} status to FAILED in database")
            except Exception as db_error:
                print(f"🚨🚨 DOUBLE ERROR: Failed to update error status: {db_error}")
            
            # Re-raise the error to make it visible in CloudWatch and stop processing
            raise Exception(f"🚨 DEVELOPMENT MODE - ANALYSIS FAILED: {str(e)}") from e
    
    else:
        print("Unknown event format")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid event format'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Instagram analysis completed'})
    }