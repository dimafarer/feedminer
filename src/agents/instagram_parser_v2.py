"""
Enhanced Instagram JSON Parser Agent for FeedMiner v0.2.0.

This enhanced version supports multi-model AI integration with runtime provider switching
between Anthropic API and AWS Bedrock. Features include:

- Multi-provider AI support (Anthropic + Bedrock)
- Runtime model selection and switching
- Performance benchmarking and comparison
- Fallback support for reliability
- Extensible architecture for additional models

SUPPORTED FORMATS:
1. Real Instagram Export Format: {"saved_saved_media": [...]}
2. FeedMiner Enhanced Format: {"type": "instagram_saved", "content": {"saved_posts": [...]}}
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import boto3
from pydantic import BaseModel, Field
import sys
sys.path.append('/opt/python/lib/python3.12/site-packages')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai.providers import AIProviderManager, ModelConfiguration


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
    url: Optional[str] = Field(default=None, description="URL to the Instagram post")
    interest_category: Optional[str] = Field(default=None, description="Categorized interest area")


class GoalRecommendation(BaseModel):
    """AI-generated goal recommendation."""
    goal_area: str = Field(description="Area of goal (e.g., 'Physical Fitness', 'Learning')")
    evidence_strength: str = Field(description="Strength of evidence (High, Medium, Low)")
    specific_goals: List[str] = Field(description="Specific, measurable goal recommendations")
    timeline: str = Field(description="Recommended timeline (30-day, 90-day, 1-year)")
    success_probability: float = Field(description="Estimated success probability (0-1)")
    supporting_evidence: List[str] = Field(description="Evidence from saved content")


class BehavioralInsight(BaseModel):
    """Behavioral pattern insight."""
    pattern_type: str = Field(description="Type of pattern (learning_style, motivation, etc.)")
    description: str = Field(description="Description of the pattern")
    evidence: List[str] = Field(description="Supporting evidence")
    goal_relevance: str = Field(description="How this relates to goal achievement")


class ContentCategory(BaseModel):
    """Content category classification."""
    name: str = Field(description="Category name")
    confidence: float = Field(description="Confidence score 0-1")
    post_count: int = Field(description="Number of posts in this category")
    percentage: float = Field(description="Percentage of total content")
    reasoning: str = Field(description="Why this category was chosen")


class InstagramAnalysisResult(BaseModel):
    """Complete analysis result for Instagram content with goal-oriented insights."""
    total_posts: int = Field(description="Total number of posts analyzed")
    analysis_timestamp: str = Field(description="When analysis was performed")
    ai_provider: str = Field(description="AI provider used for analysis")
    ai_model: str = Field(description="Specific AI model used")
    processing_time_ms: int = Field(description="Time taken for AI processing")
    
    # Goal-oriented analysis
    goal_recommendations: List[GoalRecommendation] = Field(description="AI-generated goal recommendations")
    behavioral_insights: List[BehavioralInsight] = Field(description="Behavioral patterns discovered")
    
    # Content analysis
    categories: List[ContentCategory] = Field(description="Identified content categories")
    top_authors: List[Dict[str, Any]] = Field(description="Most saved authors")
    date_range: Dict[str, str] = Field(description="Date range of saved content")
    
    # Summary
    summary: str = Field(description="Overall summary focusing on goal-setting potential")
    confidence_score: float = Field(description="Overall confidence in analysis (0-1)")


class EnhancedInstagramParserAgent:
    """Enhanced Instagram parser with multi-model AI support."""
    
    def __init__(self, preferred_provider: str = None, preferred_model: str = None):
        """Initialize the enhanced Instagram parser agent."""
        self.preferred_provider = preferred_provider or os.environ.get('PREFERRED_AI_PROVIDER', 'anthropic')
        self.preferred_model = preferred_model or os.environ.get('PREFERRED_AI_MODEL')
        
        # Initialize AI provider manager
        self.ai_manager = AIProviderManager(
            primary_provider=self.preferred_provider,
            fallback_provider='bedrock' if self.preferred_provider == 'anthropic' else 'anthropic'
        )
        
        # AWS clients for data persistence
        self.dynamodb = boto3.resource('dynamodb')
        self.s3 = boto3.client('s3')
        
        # Environment variables
        self.content_table_name = os.environ.get('CONTENT_TABLE')
        self.jobs_table_name = os.environ.get('JOBS_TABLE')
        self.content_bucket = os.environ.get('CONTENT_BUCKET')
    
    async def parse_instagram_export(self, raw_data: Dict[str, Any], provider_config: ModelConfiguration = None) -> InstagramAnalysisResult:
        """
        Parse Instagram saved content export and extract goal-oriented insights.
        
        Args:
            raw_data: Raw Instagram export data
            provider_config: AI provider configuration (optional)
            
        Returns:
            Structured analysis result with goal recommendations
        """
        start_time = datetime.now()
        
        # Extract and normalize posts
        posts = self._extract_posts(raw_data)
        
        # Build goal-oriented analysis prompt
        prompt = self._build_goal_analysis_prompt(posts)
        
        # Configure AI provider
        if not provider_config:
            provider_config = ModelConfiguration(
                provider=self.preferred_provider,
                model=self.preferred_model or self._get_default_model(self.preferred_provider),
                temperature=0.7,
                max_tokens=4000
            )
        
        # Run analysis with AI
        ai_response = await self.ai_manager.generate(prompt, provider_config)
        
        end_time = datetime.now()
        processing_time = int((end_time - start_time).total_seconds() * 1000)
        
        if ai_response["success"]:
            # Parse AI response into structured format
            analysis = self._parse_ai_response(ai_response["content"], posts)
            analysis.ai_provider = ai_response["provider"]
            analysis.ai_model = ai_response["model"]
            analysis.processing_time_ms = ai_response["latency_ms"]
            analysis.analysis_timestamp = end_time.isoformat()
        else:
            # Create fallback analysis if AI fails
            analysis = self._create_fallback_analysis(posts)
            analysis.ai_provider = "fallback"
            analysis.ai_model = "rule_based"
            analysis.processing_time_ms = processing_time
            analysis.analysis_timestamp = end_time.isoformat()
        
        return analysis
    
    def _extract_posts(self, raw_data: Dict[str, Any]) -> List[InstagramPost]:
        """Extract and normalize Instagram posts from raw export data."""
        posts = []
        
        # Handle Real Instagram Export Format
        if 'saved_saved_media' in raw_data:
            for item in raw_data['saved_saved_media']:
                title = item.get('title', 'unknown')
                string_map_data = item.get('string_map_data', {})
                saved_on = string_map_data.get('Saved on', {})
                
                href = saved_on.get('href', '')
                timestamp = saved_on.get('timestamp', 0)
                
                # Extract post ID from URL
                post_id = self._extract_post_id_from_url(href)
                
                # Determine media type from URL
                media_type = 'reel' if '/reel/' in href else 'post' if '/p/' in href else 'unknown'
                
                # Convert timestamp to ISO format
                saved_at = datetime.fromtimestamp(timestamp).isoformat() if timestamp else 'unknown'
                
                posts.append(InstagramPost(
                    post_id=post_id,
                    author=title,
                    caption=f"Content from @{title}",
                    media_type=media_type,
                    saved_at=saved_at,
                    url=href,
                    hashtags=[],
                    location=None,
                    engagement=None
                ))
        
        # Handle Enhanced FeedMiner Format
        elif 'content' in raw_data and 'saved_posts' in raw_data['content']:
            for post_data in raw_data['content']['saved_posts']:
                posts.append(InstagramPost(**post_data))
        
        # Handle Direct Posts Array
        elif isinstance(raw_data, list):
            for post_data in raw_data:
                posts.append(InstagramPost(**post_data))
        
        return posts
    
    def _extract_post_id_from_url(self, url: str) -> str:
        """Extract Instagram post ID from URL."""
        if '/reel/' in url:
            return url.split('/reel/')[-1].split('/')[0]
        elif '/p/' in url:
            return url.split('/p/')[-1].split('/')[0]
        else:
            # Generate ID from URL or use hash
            return str(hash(url))[-8:] if url else 'unknown'
    
    def _build_goal_analysis_prompt(self, posts: List[InstagramPost]) -> str:
        """Build comprehensive goal-oriented analysis prompt."""
        
        # Analyze post patterns
        author_counts = {}
        media_type_counts = {}
        recent_posts = []
        
        for post in posts:
            author_counts[post.author] = author_counts.get(post.author, 0) + 1
            media_type_counts[post.media_type] = media_type_counts.get(post.media_type, 0) + 1
            if post.saved_at != 'unknown':
                recent_posts.append(post)
        
        # Sort by save date
        recent_posts.sort(key=lambda x: x.saved_at, reverse=True)
        
        # Top authors
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Media type preferences
        total_posts = len(posts)
        media_preferences = {
            media_type: (count, round(count/total_posts*100, 1))
            for media_type, count in media_type_counts.items()
        }
        
        prompt = f"""
You are an expert behavioral analyst specializing in extracting goal-setting insights from social media behavior. 
Analyze the following Instagram saved content to identify meaningful goals this person could pursue.

INSTAGRAM SAVED CONTENT ANALYSIS:
Total Posts Saved: {len(posts)}

TOP AUTHORS SAVED FROM:
{chr(10).join([f"- @{author}: {count} saves" for author, count in top_authors])}

CONTENT TYPE PREFERENCES:
{chr(10).join([f"- {media_type}: {count} saves ({percentage}%)" for media_type, (count, percentage) in media_preferences.items()])}

SAMPLE OF RECENT SAVES:
{chr(10).join([f"- @{post.author} ({post.media_type}) - {post.saved_at[:10]}" for post in recent_posts[:15]])}

GOAL-ORIENTED ANALYSIS INSTRUCTIONS:

1. IDENTIFY GOAL AREAS: Look for patterns in the accounts saved from to identify potential goal areas:
   - Fitness accounts → Physical fitness goals
   - Educational accounts → Learning/skill development goals  
   - Business accounts → Professional/entrepreneurship goals
   - Creative accounts → Artistic/creative expression goals
   - Tech accounts → Technology/innovation goals

2. ASSESS EVIDENCE STRENGTH:
   - HIGH: 6+ saves from related accounts, consistent pattern
   - MEDIUM: 3-5 saves from related accounts
   - LOW: 1-2 saves, exploratory interest

3. GENERATE SPECIFIC GOALS: For each identified area, create:
   - Specific, measurable goals aligned with the content saved
   - Realistic timelines (30-day, 90-day, 1-year)
   - Success probability estimates based on engagement patterns

4. BEHAVIORAL INSIGHTS: Analyze:
   - Learning style preferences (visual vs text, quick vs detailed)
   - Motivation patterns from temporal saving behavior
   - Content consumption habits that support goal achievement

Please provide your analysis in this structured format:

GOAL RECOMMENDATIONS:
[List 3-5 specific goal areas with evidence strength and recommendations]

BEHAVIORAL INSIGHTS:
[Key patterns that would help with goal achievement]

CONTENT CATEGORIES:
[Main interest categories with percentages]

SUMMARY:
[Overall assessment of goal-setting potential and recommended approach]

Focus on actionable insights that would help this person set and achieve meaningful goals based on their demonstrated interests through saved content.
"""
        
        return prompt
    
    def _parse_ai_response(self, ai_content: str, posts: List[InstagramPost]) -> InstagramAnalysisResult:
        """Parse AI response into structured analysis result."""
        
        # This is a simplified parser - in production, you'd want more robust parsing
        # or use structured output tools from the AI providers
        
        # Extract basic statistics
        total_posts = len(posts)
        author_counts = {}
        for post in posts:
            author_counts[post.author] = author_counts.get(post.author, 0) + 1
        
        top_authors = [
            {"author": author, "post_count": count}
            for author, count in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Date range
        dates = [post.saved_at for post in posts if post.saved_at != 'unknown']
        date_range = {
            "earliest": min(dates) if dates else "unknown",
            "latest": max(dates) if dates else "unknown"
        }
        
        # Create structured result (in production, this would parse the AI response)
        return InstagramAnalysisResult(
            total_posts=total_posts,
            analysis_timestamp=datetime.now().isoformat(),
            ai_provider="pending",  # Will be set by caller
            ai_model="pending",     # Will be set by caller
            processing_time_ms=0,   # Will be set by caller
            
            goal_recommendations=[
                GoalRecommendation(
                    goal_area="AI Analysis Generated",
                    evidence_strength="High",
                    specific_goals=["Goals extracted from AI response"],
                    timeline="Based on AI analysis",
                    success_probability=0.85,
                    supporting_evidence=["AI-identified patterns"]
                )
            ],
            
            behavioral_insights=[
                BehavioralInsight(
                    pattern_type="ai_analysis",
                    description="Patterns identified by AI",
                    evidence=["Content saving behavior"],
                    goal_relevance="Directly supports goal achievement"
                )
            ],
            
            categories=[
                ContentCategory(
                    name="AI Categorized",
                    confidence=0.9,
                    post_count=total_posts,
                    percentage=100.0,
                    reasoning="AI-based categorization"
                )
            ],
            
            top_authors=top_authors,
            date_range=date_range,
            summary=ai_content[:500] + "..." if len(ai_content) > 500 else ai_content,
            confidence_score=0.8
        )
    
    def _create_fallback_analysis(self, posts: List[InstagramPost]) -> InstagramAnalysisResult:
        """Create rule-based analysis if AI processing fails."""
        
        # Basic statistics
        total_posts = len(posts)
        author_counts = {}
        media_type_counts = {}
        
        for post in posts:
            author_counts[post.author] = author_counts.get(post.author, 0) + 1
            media_type_counts[post.media_type] = media_type_counts.get(post.media_type, 0) + 1
        
        # Top authors
        top_authors = [
            {"author": author, "post_count": count}
            for author, count in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Date range
        dates = [post.saved_at for post in posts if post.saved_at != 'unknown']
        date_range = {
            "earliest": min(dates) if dates else "unknown",
            "latest": max(dates) if dates else "unknown"
        }
        
        # Rule-based goal detection
        goal_recommendations = self._detect_goals_from_authors(author_counts)
        
        # Basic categories
        categories = [
            ContentCategory(
                name="Mixed Content",
                confidence=0.7,
                post_count=total_posts,
                percentage=100.0,
                reasoning=f"Analysis of {total_posts} saved posts"
            )
        ]
        
        return InstagramAnalysisResult(
            total_posts=total_posts,
            analysis_timestamp=datetime.now().isoformat(),
            ai_provider="fallback",
            ai_model="rule_based",
            processing_time_ms=0,
            
            goal_recommendations=goal_recommendations,
            
            behavioral_insights=[
                BehavioralInsight(
                    pattern_type="content_diversity",
                    description=f"Saves content from {len(author_counts)} different authors",
                    evidence=[f"Content variety across {len(media_type_counts)} media types"],
                    goal_relevance="Diverse interests suggest multiple potential goal areas"
                )
            ],
            
            categories=categories,
            top_authors=top_authors,
            date_range=date_range,
            summary=f"Rule-based analysis of {total_posts} Instagram saves from {len(author_counts)} authors. Multiple potential goal areas identified.",
            confidence_score=0.6
        )
    
    def _detect_goals_from_authors(self, author_counts: Dict[str, int]) -> List[GoalRecommendation]:
        """Rule-based goal detection from author patterns."""
        
        # Define author patterns for different goal areas
        fitness_keywords = ['fit', 'gym', 'workout', 'health', 'train', 'muscle', 'weight']
        learning_keywords = ['academy', 'edu', 'tutorial', 'learn', 'course', 'study', 'skill']
        business_keywords = ['business', 'entrepreneur', 'brand', 'marketing', 'startup', 'ceo']
        creative_keywords = ['art', 'design', 'creative', 'music', 'photo', 'draw', 'paint']
        tech_keywords = ['tech', 'code', 'dev', 'ai', 'data', 'programming', 'software']
        
        goal_areas = {
            'Physical Fitness': fitness_keywords,
            'Learning & Development': learning_keywords,
            'Business & Entrepreneurship': business_keywords,
            'Creative Expression': creative_keywords,
            'Technology & Innovation': tech_keywords
        }
        
        recommendations = []
        
        for goal_area, keywords in goal_areas.items():
            matching_authors = []
            total_saves = 0
            
            for author, count in author_counts.items():
                if any(keyword in author.lower() for keyword in keywords):
                    matching_authors.append(f"@{author}")
                    total_saves += count
            
            if matching_authors:
                evidence_strength = "High" if total_saves >= 6 else "Medium" if total_saves >= 3 else "Low"
                
                recommendations.append(GoalRecommendation(
                    goal_area=goal_area,
                    evidence_strength=evidence_strength,
                    specific_goals=[f"Develop skills in {goal_area.lower()}", f"Follow content from {len(matching_authors)} related accounts"],
                    timeline="90-day development plan",
                    success_probability=0.7 if evidence_strength == "High" else 0.6 if evidence_strength == "Medium" else 0.4,
                    supporting_evidence=[f"{total_saves} saves from {len(matching_authors)} related accounts: {', '.join(matching_authors[:3])}"]
                ))
        
        return recommendations
    
    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider."""
        defaults = {
            "anthropic": "claude-3-5-sonnet-20241022",
            "bedrock": "anthropic.claude-3-5-sonnet-20241022-v2:0"
        }
        return defaults.get(provider, "")
    
    async def save_analysis_result(self, content_id: str, analysis: InstagramAnalysisResult) -> bool:
        """Save analysis result to DynamoDB and S3."""
        try:
            # Save to DynamoDB
            table = self.dynamodb.Table(self.content_table_name)
            table.update_item(
                Key={'contentId': content_id},
                UpdateExpression='SET analysis = :analysis, analysisTimestamp = :timestamp, #status = :status, aiProvider = :provider, aiModel = :model',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':analysis': analysis.model_dump(),
                    ':timestamp': analysis.analysis_timestamp,
                    ':status': 'analyzed',
                    ':provider': analysis.ai_provider,
                    ':model': analysis.ai_model
                }
            )
            
            # Save detailed result to S3
            s3_key = f"analysis/{content_id}/instagram_analysis_v2.json"
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
    
    async def compare_providers(self, raw_data: Dict[str, Any], providers: List[str] = None) -> Dict[str, InstagramAnalysisResult]:
        """Compare analysis results across multiple AI providers."""
        if not providers:
            providers = self.ai_manager.get_available_providers()
        
        results = {}
        
        for provider in providers:
            try:
                config = ModelConfiguration(
                    provider=provider,
                    model=self._get_default_model(provider),
                    temperature=0.7,
                    max_tokens=4000
                )
                
                analysis = await self.parse_instagram_export(raw_data, config)
                results[provider] = analysis
                
            except Exception as e:
                print(f"Failed to analyze with provider {provider}: {e}")
                continue
        
        return results


# Lambda handler function for enhanced Instagram parser
def handler(event, context):
    """AWS Lambda handler for enhanced Instagram parser with multi-model support."""
    print(f"Enhanced Instagram parser received event: {json.dumps(event)}")
    
    # Extract configuration from event or environment
    preferred_provider = event.get('provider') or os.environ.get('PREFERRED_AI_PROVIDER', 'anthropic')
    preferred_model = event.get('model') or os.environ.get('PREFERRED_AI_MODEL')
    
    # Initialize enhanced agent
    agent = EnhancedInstagramParserAgent(
        preferred_provider=preferred_provider,
        preferred_model=preferred_model
    )
    
    try:
        # Process S3 trigger events
        if 'Records' in event:
            for record in event['Records']:
                bucket = record['s3']['bucket']['name']
                key = record['s3']['object']['key']
                
                # Download content from S3
                response = agent.s3.get_object(Bucket=bucket, Key=key)
                raw_data = json.loads(response['Body'].read())
                
                # Extract content ID from S3 key
                content_id = key.split('/')[-1].replace('.json', '')
                
                # Run enhanced analysis
                import asyncio
                analysis = asyncio.run(agent.parse_instagram_export(raw_data))
                
                # Save results
                asyncio.run(agent.save_analysis_result(content_id, analysis))
                
                print(f"Enhanced Instagram analysis completed for {content_id} using {analysis.ai_provider}:{analysis.ai_model}")
        
        # Direct invocation
        elif 'content_data' in event:
            content_id = event.get('content_id', 'direct_invocation')
            raw_data = event['content_data']
            
            # Create provider configuration if specified
            provider_config = None
            if 'provider_config' in event:
                provider_config = ModelConfiguration(**event['provider_config'])
            
            # Run analysis
            import asyncio
            analysis = asyncio.run(agent.parse_instagram_export(raw_data, provider_config))
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'contentId': content_id,
                    'analysis': analysis.model_dump(),
                    'provider': analysis.ai_provider,
                    'model': analysis.ai_model,
                    'processing_time_ms': analysis.processing_time_ms
                })
            }
    
    except Exception as e:
        print(f"Error in enhanced Instagram parser: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Enhanced Instagram analysis completed'})
    }