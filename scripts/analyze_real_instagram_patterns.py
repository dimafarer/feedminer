#!/usr/bin/env python3
"""
Real Instagram Pattern Analysis for Goal Setting

This script analyzes real Instagram saved posts and likes to identify:
1. Interest patterns that suggest goals and motivations
2. Behavioral patterns for goal achievement
3. Content themes that reveal values and aspirations
4. Temporal patterns that show consistency and habits
"""

import json
import sys
import requests
from datetime import datetime, timezone
from collections import defaultdict, Counter
from pathlib import Path
import re

# FeedMiner API configuration
FEEDMINER_API_BASE = "https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev"

def extract_patterns_from_saved_posts(data):
    """Extract goal-oriented patterns from saved Instagram posts."""
    print("🔍 Analyzing Saved Posts for Goal-Setting Patterns")
    print("=" * 60)
    
    saved_posts = data.get("saved_saved_media", [])
    print(f"📊 Total Saved Posts: {len(saved_posts)}")
    
    # Extract usernames and content types
    authors = []
    content_types = defaultdict(int)
    timestamps = []
    urls = []
    
    for post in saved_posts:
        author = post.get("title", "unknown")
        authors.append(author)
        
        # Extract URL and timestamp
        string_map = post.get("string_map_data", {})
        saved_info = string_map.get("Saved on", {})
        
        if "href" in saved_info:
            url = saved_info["href"]
            urls.append(url)
            
            # Determine content type from URL
            if "/reel/" in url:
                content_types["reels"] += 1
            elif "/p/" in url:
                content_types["posts"] += 1
            else:
                content_types["other"] += 1
        
        if "timestamp" in saved_info:
            timestamps.append(saved_info["timestamp"])
    
    # Analyze author patterns for interests/goals
    author_counts = Counter(authors)
    print(f"\\n🎯 TOP SAVED AUTHORS (Interest Indicators):")
    for author, count in author_counts.most_common(10):
        print(f"   {author}: {count} saves")
        
        # Categorize likely interests based on username patterns
        category = categorize_author_intent(author)
        if category:
            print(f"      → Likely Interest: {category}")
    
    # Content type preferences
    print(f"\\n📱 CONTENT TYPE PREFERENCES:")
    total_content = sum(content_types.values())
    for content_type, count in content_types.items():
        percentage = (count / total_content) * 100
        print(f"   {content_type.title()}: {count} ({percentage:.1f}%)")
    
    # Temporal patterns
    if timestamps:
        analyze_saving_patterns(timestamps)
    
    return {
        "authors": author_counts,
        "content_types": dict(content_types),
        "total_saves": len(saved_posts),
        "top_interests": identify_interest_categories(author_counts),
        "goal_indicators": extract_goal_indicators(author_counts)
    }

def categorize_author_intent(username):
    """Categorize username to suggest user interests and potential goals."""
    username_lower = username.lower()
    
    # Fitness and health goals
    if any(word in username_lower for word in ['fit', 'gym', 'workout', 'health', 'muscle', 'protein', 'coach', 'trainer', 'spartan']):
        return "🏋️ Fitness & Health Goals"
    
    # Business and entrepreneurship
    if any(word in username_lower for word in ['business', 'entrepreneur', 'launch', 'brand', 'startup', 'success', 'ceo']):
        return "💼 Business & Entrepreneurship"
    
    # Education and learning
    if any(word in username_lower for word in ['academy', 'learn', 'teach', 'education', 'course', 'tutorial', 'expert']):
        return "📚 Learning & Skill Development"
    
    # Creative and artistic
    if any(word in username_lower for word in ['music', 'art', 'creative', 'design', 'photo', 'video']):
        return "🎨 Creative & Artistic Pursuits"
    
    # Personal development
    if any(word in username_lower for word in ['mindset', 'growth', 'motivation', 'inspire', 'life', 'personal']):
        return "🧠 Personal Development"
    
    # Technology and innovation
    if any(word in username_lower for word in ['tech', 'code', 'data', 'ai', 'digital', 'innovation']):
        return "💻 Technology & Innovation"
    
    return None

def identify_interest_categories(author_counts):
    """Identify main interest categories based on saved content."""
    categories = defaultdict(int)
    
    for author, count in author_counts.items():
        category = categorize_author_intent(author)
        if category:
            # Remove emoji and get category name
            category_name = category.split(' ', 1)[1] if ' ' in category else category
            categories[category_name] += count
    
    return dict(categories)

def extract_goal_indicators(author_counts):
    """Extract specific goal indicators from saved content patterns."""
    goal_indicators = []
    
    # Fitness goals
    fitness_authors = [author for author in author_counts if any(word in author.lower() for word in ['fit', 'gym', 'workout', 'trainer', 'spartan'])]
    if fitness_authors:
        total_fitness_saves = sum(author_counts[author] for author in fitness_authors)
        goal_indicators.append({
            "goal_area": "Physical Fitness",
            "evidence_strength": "High" if total_fitness_saves > 10 else "Medium",
            "specific_indicators": fitness_authors[:5],
            "save_count": total_fitness_saves,
            "suggested_goals": [
                "Establish consistent workout routine",
                "Improve physical strength and endurance",
                "Learn new fitness techniques and exercises"
            ]
        })
    
    # Business/entrepreneurship goals
    business_authors = [author for author in author_counts if any(word in author.lower() for word in ['business', 'brand', 'launch', 'entrepreneur'])]
    if business_authors:
        total_business_saves = sum(author_counts[author] for author in business_authors)
        goal_indicators.append({
            "goal_area": "Business & Entrepreneurship",
            "evidence_strength": "High" if total_business_saves > 5 else "Medium",
            "specific_indicators": business_authors[:5],
            "save_count": total_business_saves,
            "suggested_goals": [
                "Develop business or personal brand",
                "Learn entrepreneurship skills",
                "Build professional network"
            ]
        })
    
    # Learning goals
    learning_authors = [author for author in author_counts if any(word in author.lower() for word in ['academy', 'teach', 'expert', 'tutorial'])]
    if learning_authors:
        total_learning_saves = sum(author_counts[author] for author in learning_authors)
        goal_indicators.append({
            "goal_area": "Continuous Learning",
            "evidence_strength": "High" if total_learning_saves > 5 else "Medium", 
            "specific_indicators": learning_authors[:5],
            "save_count": total_learning_saves,
            "suggested_goals": [
                "Acquire new skills or knowledge",
                "Take structured courses or training",
                "Develop expertise in specific area"
            ]
        })
    
    return goal_indicators

def analyze_saving_patterns(timestamps):
    """Analyze temporal patterns in saving behavior."""
    print(f"\\n⏰ SAVING BEHAVIOR PATTERNS:")
    
    # Convert timestamps to datetime objects
    dates = [datetime.fromtimestamp(ts, tz=timezone.utc) for ts in timestamps]
    dates.sort()
    
    # Recent activity (last 30 days)
    now = datetime.now(timezone.utc)
    recent_dates = [d for d in dates if (now - d).days <= 30]
    print(f"   Recent Activity (30 days): {len(recent_dates)} saves")
    
    # Monthly patterns
    monthly_counts = defaultdict(int)
    for date in dates:
        month_key = f"{date.year}-{date.month:02d}"
        monthly_counts[month_key] += 1
    
    print(f"   Most Active Periods:")
    for month, count in sorted(monthly_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"      {month}: {count} saves")
    
    # Consistency indicators
    if len(dates) > 1:
        date_range = (dates[-1] - dates[0]).days
        avg_saves_per_week = len(dates) / (date_range / 7) if date_range > 0 else 0
        print(f"   Average Saves per Week: {avg_saves_per_week:.1f}")
        
        if avg_saves_per_week > 3:
            print("   🎯 Pattern: High engagement - suggests strong motivation for content discovery")
        elif avg_saves_per_week > 1:
            print("   📈 Pattern: Consistent engagement - shows sustained interest")
        else:
            print("   📊 Pattern: Selective saving - indicates focused interests")

def create_feedminer_format(raw_data, user_id="real_user"):
    """Convert real Instagram data to FeedMiner format with enhanced goal insights."""
    print("\\n🔄 Creating Enhanced FeedMiner Format...")
    
    saved_posts = raw_data.get("saved_saved_media", [])
    
    # Transform each saved post
    transformed_posts = []
    for i, post in enumerate(saved_posts):
        try:
            author = post.get("title", f"unknown_author_{i}")
            
            # Extract URL and timestamp
            string_map = post.get("string_map_data", {})
            saved_info = string_map.get("Saved on", {})
            
            url = saved_info.get("href", "")
            timestamp = saved_info.get("timestamp", 0)
            
            # Determine media type and extract post ID
            media_type = "unknown"
            post_id = f"real_post_{i}"
            
            if "/reel/" in url:
                media_type = "reel"
                post_id = url.split("/reel/")[1].split("/")[0] if "/reel/" in url else post_id
            elif "/p/" in url:
                media_type = "post"
                post_id = url.split("/p/")[1].split("/")[0] if "/p/" in url else post_id
            
            # Create meaningful caption based on author and interest category
            interest_category = categorize_author_intent(author)
            caption = f"Content from @{author}"
            if interest_category:
                caption += f" - {interest_category.split(' ', 1)[1] if ' ' in interest_category else interest_category}"
            
            transformed_post = {
                "post_id": post_id,
                "author": author,
                "caption": caption,
                "media_type": media_type,
                "saved_at": datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat() if timestamp else datetime.now(timezone.utc).isoformat(),
                "hashtags": [],  # Real Instagram export doesn't include hashtags
                "location": None,
                "engagement": {},
                "url": url,
                "interest_category": interest_category
            }
            transformed_posts.append(transformed_post)
            
        except Exception as e:
            print(f"⚠️  Error transforming post {i}: {e}")
            continue
    
    # Create comprehensive metadata
    patterns = extract_patterns_from_saved_posts(raw_data)
    
    feedminer_data = {
        "type": "instagram_saved",
        "user_id": user_id,
        "metadata": {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_items": len(transformed_posts),
            "export_version": "real_data_goal_analysis_1.0",
            "source": "instagram_export_saved_posts",
            "analysis_focus": "goal_setting_and_motivation",
            "patterns_discovered": patterns
        },
        "content": {
            "saved_posts": transformed_posts
        }
    }
    
    print(f"✅ Enhanced transformation complete: {len(transformed_posts)} posts with goal insights")
    return feedminer_data

def upload_and_analyze(data):
    """Upload to FeedMiner and get AI analysis."""
    print("\\n🚀 Uploading Enhanced Data to FeedMiner...")
    
    try:
        response = requests.post(
            f"{FEEDMINER_API_BASE}/upload",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content_id = result.get("contentId")
            print(f"✅ Upload successful! Content ID: {content_id}")
            return content_id
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def display_goal_insights(patterns):
    """Display comprehensive goal-setting insights."""
    print("\\n🎯 GOAL-SETTING INSIGHTS FROM YOUR INSTAGRAM PATTERNS")
    print("=" * 70)
    
    goal_indicators = patterns.get("goal_indicators", [])
    
    if goal_indicators:
        print("\\n🏆 IDENTIFIED GOAL AREAS:")
        for indicator in goal_indicators:
            print(f"\\n   📊 {indicator['goal_area']} (Evidence: {indicator['evidence_strength']})")
            print(f"      Saved Content: {indicator['save_count']} related posts")
            print(f"      Key Accounts: {', '.join(indicator['specific_indicators'])}")
            print(f"      Suggested Goals:")
            for goal in indicator['suggested_goals']:
                print(f"         • {goal}")
    
    # Interest distribution
    interests = patterns.get("top_interests", {})
    if interests:
        print(f"\\n📈 INTEREST DISTRIBUTION:")
        total_interest_saves = sum(interests.values())
        for interest, count in sorted(interests.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_interest_saves) * 100
            print(f"   {interest}: {count} saves ({percentage:.1f}%)")
    
    # Content consumption patterns
    content_types = patterns.get("content_types", {})
    print(f"\\n📱 CONTENT CONSUMPTION PATTERNS:")
    for content_type, count in content_types.items():
        print(f"   {content_type.title()}: {count}")
        if content_type == "reels" and count > 50:
            print("      → Prefers dynamic, engaging content - suggests learning through demonstration")
        elif content_type == "posts" and count > 30:
            print("      → Values detailed, thoughtful content - suggests deep-dive learning style")

def main():
    """Main analysis function."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/analyze_real_instagram_patterns.py /path/to/saved_posts.json")
        sys.exit(1)
    
    data_path = sys.argv[1]
    
    print("🎯 FEEDMINER: REAL INSTAGRAM GOAL ANALYSIS")
    print("=" * 50)
    print("🎪 Analyzing your saved content for goal-setting insights...")
    print("🔍 Looking for patterns that reveal interests, motivations, and aspirations")
    
    # Load and analyze data
    with open(data_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Extract patterns first
    patterns = extract_patterns_from_saved_posts(raw_data)
    
    # Display immediate insights
    display_goal_insights(patterns)
    
    # Create enhanced FeedMiner format
    feedminer_data = create_feedminer_format(raw_data)
    
    # Save enhanced data
    output_path = "/home/daddyfristy/real-instagram-data/enhanced_goal_analysis.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feedminer_data, f, indent=2, ensure_ascii=False)
    print(f"\\n💾 Enhanced goal analysis saved to: {output_path}")
    
    # Upload for AI analysis
    content_id = upload_and_analyze(feedminer_data)
    
    if content_id:
        print(f"\\n🤖 Your data is now being processed by our AI system!")
        print(f"Content ID: {content_id}")
        print(f"\\nCheck analysis results with:")
        print(f"curl {FEEDMINER_API_BASE}/content/{content_id}")
    
    print("\\n🎉 Goal-oriented Instagram analysis complete!")
    print("💡 Use these insights to set specific, measurable goals aligned with your interests!")

if __name__ == "__main__":
    main()