"""
Instagram JSON Parser Agent for FeedMiner.

This Strands agent specializes in parsing Instagram saved content exports,
extracting meaningful insights, and categorizing content for better organization.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import boto3
from strands import Agent, BedrockModel
from strands.tools import StructuredOutput
from pydantic import BaseModel, Field


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


class InstagramParserAgent:
    """Strands agent for parsing and analyzing Instagram saved content."""
    
    def __init__(self):
        """Initialize the Instagram parser agent."""
        # Initialize Strands agent with Bedrock model
        self.agent = Agent(
            name="Instagram Content Parser",
            model=BedrockModel(
                model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
            ),
            description="""You are an expert at analyzing Instagram saved content. 
            You understand social media trends, content categories, and user behavior patterns.
            Extract meaningful insights from Instagram post data."""
        )
        
        # Add structured output tool for analysis results
        self.agent.add_tool(
            StructuredOutput(InstagramAnalysisResult),
            name="format_analysis_result"
        )
        
        # DynamoDB and S3 clients for data persistence
        self.dynamodb = boto3.resource('dynamodb')
        self.s3 = boto3.client('s3')
        
        # Environment variables
        self.content_table_name = os.environ.get('CONTENT_TABLE')
        self.jobs_table_name = os.environ.get('JOBS_TABLE')
        self.content_bucket = os.environ.get('CONTENT_BUCKET')
    
    async def parse_instagram_export(self, raw_data: Dict[str, Any]) -> InstagramAnalysisResult:
        """
        Parse Instagram saved content export and extract insights.
        
        Args:
            raw_data: Raw Instagram export data
            
        Returns:
            Structured analysis result
        """
        # Extract posts from the raw data
        posts = self._extract_posts(raw_data)
        
        # Create analysis prompt
        prompt = self._build_analysis_prompt(posts)
        
        # Run analysis with the agent
        response = await self.agent.run(
            prompt,
            tools=["format_analysis_result"]
        )
        
        # Extract the structured result
        for message in response.messages:
            for content in message.content:
                if hasattr(content, 'name') and content.name == 'format_analysis_result':
                    return InstagramAnalysisResult.model_validate(content.input)
        
        # Fallback if structured output fails
        return self._create_fallback_analysis(posts)
    
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
        
        Use the format_analysis_result tool to structure your response.
        """
    
    def _create_fallback_analysis(self, posts: List[InstagramPost]) -> InstagramAnalysisResult:
        """Create a basic analysis if AI processing fails."""
        # Basic category detection based on hashtags
        categories = self._detect_categories_from_hashtags(posts)
        
        # Top authors
        author_counts = {}
        for post in posts:
            author_counts[post.author] = author_counts.get(post.author, 0) + 1
        
        top_authors = [
            {"author": author, "post_count": count}
            for author, count in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Date range
        dates = [post.saved_at for post in posts if post.saved_at]
        date_range = {
            "earliest": min(dates) if dates else "unknown",
            "latest": max(dates) if dates else "unknown"
        }
        
        return InstagramAnalysisResult(
            total_posts=len(posts),
            categories=categories,
            insights=[
                ContentInsight(
                    type="preference",
                    description="User saves diverse content types",
                    evidence=[f"{len(posts)} posts from {len(author_counts)} different authors"],
                    relevance_score=0.8
                )
            ],
            top_authors=top_authors,
            date_range=date_range,
            summary=f"Analysis of {len(posts)} saved Instagram posts from {len(author_counts)} authors."
        )
    
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
    
    async def save_analysis_result(self, content_id: str, analysis: InstagramAnalysisResult) -> bool:
        """Save analysis result to DynamoDB and S3."""
        try:
            # Save to DynamoDB
            table = self.dynamodb.Table(self.content_table_name)
            table.update_item(
                Key={'contentId': content_id},
                UpdateExpression='SET analysis = :analysis, analysisTimestamp = :timestamp, #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':analysis': analysis.model_dump(),
                    ':timestamp': datetime.now().isoformat(),
                    ':status': 'analyzed'
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
        # S3 trigger event
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            # Download content from S3
            response = agent.s3.get_object(Bucket=bucket, Key=key)
            raw_data = json.loads(response['Body'].read())
            
            # Extract content ID from S3 key
            content_id = key.split('/')[-1].replace('.json', '')
            
            # Run analysis
            import asyncio
            analysis = asyncio.run(agent.parse_instagram_export(raw_data))
            
            # Save results
            agent.save_analysis_result(content_id, analysis)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Instagram analysis completed'})
    }