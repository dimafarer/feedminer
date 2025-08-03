"""
Response Normalizer for Multi-Model AI Integration

Transforms different model outputs into a standardized format that works
consistently with the React frontend components.

Based on MODEL_OUTPUT_ANALYSIS.md findings:
- All models return stringified Python dicts that need parsing
- Content varies in structure between model families
- Frontend expects specific AnalysisResult interface
"""

import ast
import json
import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback for environments without pydantic
    BaseModel = object
    Field = lambda **kwargs: None


class EvidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class GoalPotential(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class CostTier(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Goal:
    term: str  # '30-day', '90-day', '1-year'
    title: str
    description: str


@dataclass
class GoalArea:
    id: str
    name: str
    icon: str
    evidence: EvidenceLevel
    percentage: float
    save_count: int
    key_accounts: List[str]
    description: str
    goals: List[Goal]


@dataclass
class BehavioralPattern:
    type: str
    title: str
    description: str
    data: Dict[str, Any]
    insight: str


@dataclass
class InterestDistribution:
    category: str
    percentage: float
    goal_potential: GoalPotential


@dataclass
class ModelInfo:
    provider: str
    model: str
    latency_ms: int
    cost_tier: CostTier
    capabilities: List[str]


@dataclass
class AnalysisResult:
    total_posts: int
    analysis_date: str
    content_id: str
    model_info: ModelInfo
    goal_areas: List[GoalArea]
    behavioral_patterns: List[BehavioralPattern]
    interest_distribution: List[InterestDistribution]
    raw_model_output: str


class ResponseNormalizer:
    """
    Transforms raw model responses into standardized AnalysisResult format.
    
    Handles the critical parsing challenges identified in Phase 1:
    1. Stringified Python dict format from all models
    2. Model-specific content structure variations
    3. Frontend compatibility requirements
    """
    
    # Goal category mappings with icons
    GOAL_CATEGORIES = {
        'fitness': {'name': 'Physical Fitness', 'icon': '💪'},
        'health': {'name': 'Health & Wellness', 'icon': '🏥'},
        'learning': {'name': 'Learning & Education', 'icon': '📚'},
        'education': {'name': 'Learning & Education', 'icon': '📚'},
        'business': {'name': 'Business & Career', 'icon': '💼'},
        'career': {'name': 'Business & Career', 'icon': '💼'},
        'technology': {'name': 'Technology', 'icon': '💻'},
        'tech': {'name': 'Technology', 'icon': '💻'},
        'creativity': {'name': 'Creative Arts', 'icon': '🎨'},
        'art': {'name': 'Creative Arts', 'icon': '🎨'},
        'travel': {'name': 'Travel & Adventure', 'icon': '✈️'},
        'food': {'name': 'Food & Cooking', 'icon': '🍳'},
        'cooking': {'name': 'Food & Cooking', 'icon': '🍳'},
        'relationships': {'name': 'Relationships', 'icon': '❤️'},
        'social': {'name': 'Social Life', 'icon': '👥'},
        'finance': {'name': 'Financial Planning', 'icon': '💰'},
        'money': {'name': 'Financial Planning', 'icon': '💰'},
        'mindfulness': {'name': 'Mental Wellness', 'icon': '🧘'},
        'mental': {'name': 'Mental Wellness', 'icon': '🧘'},
    }
    
    # Term mappings for goal timeframes
    TERM_PATTERNS = {
        '30-day': [r'30[\s\-]?day', r'one month', r'next month', r'short[\s\-]?term'],
        '90-day': [r'90[\s\-]?day', r'three month', r'quarter', r'medium[\s\-]?term'],
        '1-year': [r'1[\s\-]?year', r'one year', r'annual', r'long[\s\-]?term', r'yearly']
    }

    def __init__(self):
        """Initialize with model-specific parsing strategies."""
        self.model_parsers = {
            'claude': self._parse_claude_content,
            'nova': self._parse_nova_content,
            'llama': self._parse_llama_content
        }

    def normalize_response(self, raw_response: Dict[str, Any], 
                         original_data: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """
        Main entry point: Transform raw model response to AnalysisResult.
        
        Args:
            raw_response: Raw response from any of the 6 models
            original_data: Original Instagram data for context
            
        Returns:
            AnalysisResult: Standardized structure for frontend
        """
        try:
            # Extract and parse the stringified Python dict content
            content_text = self._extract_content_text(raw_response)
            
            # Determine model family and use appropriate parser
            model_family = raw_response.get('model_family', 'unknown')
            parser_func = self.model_parsers.get(model_family, self._parse_generic_content)
            
            # Parse content using model-specific strategy
            parsed_content = parser_func(content_text)
            
            # Build standardized response
            return self._build_analysis_result(
                raw_response=raw_response,
                parsed_content=parsed_content,
                original_data=original_data
            )
            
        except Exception as e:
            # Fallback: Return minimal valid structure
            return self._create_fallback_result(raw_response, str(e))

    def _extract_content_text(self, raw_response: Dict[str, Any]) -> str:
        """
        Extract actual text content from stringified Python dict.
        
        All models return: "{'role': 'assistant', 'content': [{'text': '...'}]}"
        Need to parse this and extract the inner text content.
        """
        content_str = raw_response.get('content', '')
        
        if not content_str:
            raise ValueError("No content found in response")
        
        try:
            # Parse the stringified Python dict
            content_dict = ast.literal_eval(content_str)
            
            # Extract text from nested structure
            if isinstance(content_dict, dict):
                content_list = content_dict.get('content', [])
                if isinstance(content_list, list) and len(content_list) > 0:
                    text_obj = content_list[0]
                    if isinstance(text_obj, dict):
                        return text_obj.get('text', '')
            
            # Fallback: return original string if parsing fails
            return content_str
            
        except (ValueError, SyntaxError) as e:
            # If literal_eval fails, return original content
            return content_str

    def _parse_claude_content(self, content: str) -> Dict[str, Any]:
        """
        Parse Claude model responses.
        
        Claude characteristics:
        - Concise, actionable recommendations
        - Clear bullet point structure
        - Business-like tone
        """
        parsed = {
            'goal_areas': [],
            'behavioral_patterns': [],
            'insights': []
        }
        
        # Claude typically uses clear section headers
        sections = self._split_by_headers(content)
        
        for section_title, section_content in sections.items():
            if any(term in section_title.lower() for term in ['goal', 'recommendation', 'objective']):
                # Extract percentage from section title if present (e.g., "Fitness Goals (50%)")
                title_percentage_match = re.search(r'\((\d+)%\)', section_title)
                section_percentage = float(title_percentage_match.group(1)) if title_percentage_match else None
                
                goals = self._extract_goals_from_text(section_content, override_percentage=section_percentage)
                parsed['goal_areas'].extend(goals)
            elif any(term in section_title.lower() for term in ['pattern', 'behavior', 'habit']):
                parsed['behavioral_patterns'].extend(self._extract_patterns_from_text(section_content))
            elif any(term in section_title.lower() for term in ['insight', 'analysis', 'finding']):
                parsed['insights'].extend(self._extract_insights_from_text(section_content))
        
        # If no clear sections, parse the entire content
        if not parsed['goal_areas'] and not parsed['behavioral_patterns']:
            parsed['goal_areas'] = self._extract_goals_from_text(content)
            parsed['behavioral_patterns'] = self._extract_patterns_from_text(content)
        
        return parsed

    def _parse_nova_content(self, content: str) -> Dict[str, Any]:
        """
        Parse Nova model responses.
        
        Nova characteristics:
        - Very verbose and academic
        - Formal presentation style
        - Detailed explanations with markdown headers
        """
        parsed = {
            'goal_areas': [],
            'behavioral_patterns': [],
            'insights': []
        }
        
        # Nova uses markdown-style headers
        sections = self._split_by_markdown_headers(content)
        
        for section_title, section_content in sections.items():
            # Nova is more verbose, look for specific patterns
            if any(term in section_title.lower() for term in ['goal', 'recommendation', 'action', 'plan']):
                parsed['goal_areas'].extend(self._extract_goals_from_text(section_content))
            elif any(term in section_title.lower() for term in ['pattern', 'behavior', 'trend', 'analysis']):
                parsed['behavioral_patterns'].extend(self._extract_patterns_from_text(section_content))
            elif any(term in section_title.lower() for term in ['insight', 'conclusion', 'summary']):
                parsed['insights'].extend(self._extract_insights_from_text(section_content))
        
        # Fallback parsing for verbose content
        if not parsed['goal_areas']:
            parsed['goal_areas'] = self._extract_goals_from_text(content)
        if not parsed['behavioral_patterns']:
            parsed['behavioral_patterns'] = self._extract_patterns_from_text(content)
        
        return parsed

    def _parse_llama_content(self, content: str) -> Dict[str, Any]:
        """
        Parse Llama model responses.
        
        Llama characteristics:
        - Good balance of detail and action
        - Clear bullet point structure  
        - Practical recommendations
        """
        parsed = {
            'goal_areas': [],
            'behavioral_patterns': [],
            'insights': []
        }
        
        # Llama often uses numbered lists and clear structure
        sections = self._split_by_numbered_sections(content)
        
        for section_title, section_content in sections.items():
            if any(term in section_title.lower() for term in ['goal', 'action', 'plan', 'step']):
                parsed['goal_areas'].extend(self._extract_goals_from_text(section_content))
            elif any(term in section_title.lower() for term in ['pattern', 'behavior', 'habit', 'trend']):
                parsed['behavioral_patterns'].extend(self._extract_patterns_from_text(section_content))
            elif any(term in section_title.lower() for term in ['insight', 'observation', 'analysis']):
                parsed['insights'].extend(self._extract_insights_from_text(section_content))
        
        # Fallback: extract from bullet points
        if not parsed['goal_areas']:
            parsed['goal_areas'] = self._extract_goals_from_bullets(content)
        if not parsed['behavioral_patterns']:
            parsed['behavioral_patterns'] = self._extract_patterns_from_text(content)
        
        return parsed

    def _parse_generic_content(self, content: str) -> Dict[str, Any]:
        """
        Generic fallback parser for unknown model families.
        Uses pattern matching to extract structured data.
        """
        return {
            'goal_areas': self._extract_goals_from_text(content),
            'behavioral_patterns': self._extract_patterns_from_text(content),
            'insights': self._extract_insights_from_text(content)
        }

    def _split_by_headers(self, content: str) -> Dict[str, str]:
        """Split content by section headers (**, ##, etc.)"""
        sections = {}
        current_section = "introduction"
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for header patterns
            if (line.startswith('**') and line.endswith('**')) or \
               line.startswith('##') or \
               (line.isupper() and len(line.split()) <= 5):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                # Start new section
                current_section = line.strip('*# ').lower()
                current_content = []
            else:
                current_content.append(line)
        
        # Save final section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

    def _split_by_markdown_headers(self, content: str) -> Dict[str, str]:
        """Split content by markdown headers (#, ##, ###)"""
        sections = {}
        current_section = "introduction"
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                # Start new section
                current_section = line.lstrip('# ').lower()
                current_content = []
            else:
                current_content.append(line)
        
        # Save final section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

    def _split_by_numbered_sections(self, content: str) -> Dict[str, str]:
        """Split content by numbered sections (1., 2., etc.)"""
        sections = {}
        current_section = "introduction"
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for numbered list pattern
            if re.match(r'^\d+\.', line):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                # Start new section
                current_section = re.sub(r'^\d+\.\s*', '', line).lower()
                current_content = []
            else:
                current_content.append(line)
        
        # Save final section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

    def _extract_goals_from_text(self, text: str, override_percentage: Optional[float] = None) -> List[Dict[str, Any]]:
        """Extract goal areas from text content."""
        goals = []
        
        # Look for goal categories in text (use word boundaries to avoid false matches)
        for category_key, category_info in self.GOAL_CATEGORIES.items():
            if re.search(rf'\b{category_key}\b', text.lower()):
                # Extract percentage if mentioned - look for patterns like "Fitness Goals (50%)" or "fitness.*50%"
                percentage_patterns = [
                    rf'{category_key}.*?\((\d+)%\)',  # "Fitness Goals (50%)"
                    rf'{category_key}.*?(\d+)%',      # "fitness 50%"
                    rf'(\d+)%.*{category_key}',       # "50% fitness"
                ]
                
                # Use override percentage if provided, otherwise extract from text
                if override_percentage is not None:
                    percentage = override_percentage
                else:
                    percentage = 30.0  # Default
                    for pattern in percentage_patterns:
                        match = re.search(pattern, text.lower())
                        if match:
                            percentage = float(match.group(1))
                            break
                
                # Calculate save count based on percentage
                save_count = int(percentage)  # Simplified calculation
                
                # Extract description
                description = self._extract_goal_description(text, category_key)
                
                # Extract specific goals
                goal_list = self._extract_specific_goals(text, category_key)
                
                goals.append({
                    'category': category_key,
                    'name': category_info['name'],
                    'icon': category_info['icon'],
                    'percentage': percentage,
                    'save_count': save_count,
                    'description': description,
                    'goals': goal_list
                })
        
        # If no specific categories found, create generic goals
        if not goals:
            goals = self._create_generic_goals(text)
        
        return goals

    def _extract_goal_description(self, text: str, category: str) -> str:
        """Extract description for a specific goal category."""
        # Look for sentences containing the category
        sentences = text.split('.')
        for sentence in sentences:
            if category in sentence.lower():
                return sentence.strip()
        
        return f"Focus on {category} based on your saved content patterns."

    def _extract_specific_goals(self, text: str, category: str) -> List[Dict[str, str]]:
        """Extract specific goals with timeframes."""
        goals = []
        
        # Look for timeframe patterns in text
        for term, patterns in self.TERM_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Extract surrounding context
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end]
                    
                    # Find sentence containing the match
                    sentences = context.split('.')
                    for sentence in sentences:
                        if pattern in sentence.lower():
                            goals.append({
                                'term': term,
                                'title': f"{category.title()} {term} Goal",
                                'description': sentence.strip()
                            })
                            break
        
        # Ensure we have goals for each timeframe
        existing_terms = {goal['term'] for goal in goals}
        for term in ['30-day', '90-day', '1-year']:
            if term not in existing_terms:
                goals.append({
                    'term': term,
                    'title': f"{category.title()} {term} Goal",
                    'description': f"Develop {category} skills and habits over {term}."
                })
        
        return goals[:3]  # Limit to 3 goals per area

    def _extract_patterns_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract behavioral patterns from text."""
        patterns = []
        
        # Common pattern types to look for
        pattern_types = [
            'content_preference',
            'posting_frequency',
            'engagement_style',
            'learning_style',
            'motivation_cycle'
        ]
        
        for pattern_type in pattern_types:
            # Look for relevant sentences
            if any(word in text.lower() for word in [pattern_type.replace('_', ' '), 'pattern', 'behavior', 'habit']):
                patterns.append({
                    'type': pattern_type,
                    'title': pattern_type.replace('_', ' ').title(),
                    'description': self._extract_pattern_description(text, pattern_type),
                    'data': {},
                    'insight': f"Analysis reveals {pattern_type.replace('_', ' ')} patterns in your saved content."
                })
        
        return patterns[:3]  # Limit to top 3 patterns

    def _extract_pattern_description(self, text: str, pattern_type: str) -> str:
        """Extract description for a behavioral pattern."""
        # Look for sentences mentioning patterns or behaviors
        sentences = text.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['pattern', 'behavior', 'prefer', 'tend']):
                return sentence.strip()
        
        return f"Your {pattern_type.replace('_', ' ')} shows interesting trends."

    def _extract_insights_from_text(self, text: str) -> List[str]:
        """Extract key insights from text."""
        insights = []
        
        # Look for insight markers
        insight_markers = ['insight:', 'key finding:', 'important:', 'notice:', 'observe:']
        
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(marker in sentence.lower() for marker in insight_markers):
                insights.append(sentence)
            elif len(sentence) > 50 and any(word in sentence.lower() for word in ['recommend', 'suggest', 'should', 'could']):
                insights.append(sentence)
        
        return insights[:5]  # Limit to top 5 insights

    def _extract_goals_from_bullets(self, text: str) -> List[Dict[str, Any]]:
        """Extract goals from bullet point structure."""
        goals = []
        
        # Find bullet points
        bullet_patterns = [r'•\s+(.+)', r'\*\s+(.+)', r'-\s+(.+)', r'\d+\.\s+(.+)']
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                # Determine if this bullet point describes a goal
                if any(word in match.lower() for word in ['goal', 'aim', 'target', 'achieve', 'improve']):
                    category = self._determine_goal_category(match)
                    if category:
                        category_info = self.GOAL_CATEGORIES[category]
                        goals.append({
                            'category': category,
                            'name': category_info['name'],
                            'icon': category_info['icon'],
                            'percentage': 25.0,  # Default percentage
                            'save_count': 25,
                            'description': match,
                            'goals': self._create_default_goals(category)
                        })
        
        return goals

    def _determine_goal_category(self, text: str) -> Optional[str]:
        """Determine goal category from text content."""
        text_lower = text.lower()
        
        for category in self.GOAL_CATEGORIES.keys():
            if category in text_lower:
                return category
        
        # Check for related terms
        category_terms = {
            'fitness': ['workout', 'exercise', 'gym', 'sport', 'training'],
            'learning': ['learn', 'study', 'education', 'course', 'skill'],
            'business': ['work', 'career', 'professional', 'job', 'business'],
            'technology': ['tech', 'coding', 'programming', 'software', 'digital'],
            'creativity': ['creative', 'art', 'design', 'music', 'writing'],
        }
        
        for category, terms in category_terms.items():
            if any(term in text_lower for term in terms):
                return category
        
        return None

    def _create_generic_goals(self, text: str) -> List[Dict[str, Any]]:
        """Create generic goals when specific categories aren't found."""
        return [{
            'category': 'general',
            'name': 'Personal Development',
            'icon': '🎯',
            'percentage': 100.0,
            'save_count': 100,
            'description': 'Based on your saved content, focus on personal growth and development.',
            'goals': [
                {
                    'term': '30-day',
                    'title': 'Short-term Focus',
                    'description': 'Identify and work on immediate improvement areas.'
                },
                {
                    'term': '90-day',
                    'title': 'Medium-term Development',
                    'description': 'Build consistent habits and skills over three months.'
                },
                {
                    'term': '1-year',
                    'title': 'Long-term Growth',
                    'description': 'Achieve significant personal and professional milestones.'
                }
            ]
        }]

    def _create_default_goals(self, category: str) -> List[Dict[str, str]]:
        """Create default goals for a category."""
        return [
            {
                'term': '30-day',
                'title': f"{category.title()} Quick Start",
                'description': f"Begin focusing on {category} with immediate actions."
            },
            {
                'term': '90-day',
                'title': f"{category.title()} Skill Building",
                'description': f"Develop solid {category} habits and skills."
            },
            {
                'term': '1-year',
                'title': f"{category.title()} Mastery",
                'description': f"Achieve significant progress in {category}."
            }
        ]

    def _build_analysis_result(self, raw_response: Dict[str, Any], 
                             parsed_content: Dict[str, Any],
                             original_data: Optional[Dict[str, Any]]) -> AnalysisResult:
        """Build the final AnalysisResult from parsed content."""
        
        # Extract model information
        model_info = ModelInfo(
            provider=raw_response.get('provider', 'unknown'),
            model=raw_response.get('model', 'unknown'),
            latency_ms=raw_response.get('latency_ms', 0),
            cost_tier=CostTier(raw_response.get('cost_tier', 'medium')),
            capabilities=raw_response.get('capabilities', [])
        )
        
        # Convert parsed goals to GoalArea objects
        goal_areas = []
        for goal_data in parsed_content.get('goal_areas', []):
            goals = [
                Goal(
                    term=g['term'],
                    title=g['title'],
                    description=g['description']
                ) for g in goal_data.get('goals', [])
            ]
            
            goal_areas.append(GoalArea(
                id=goal_data.get('category', str(uuid.uuid4())),
                name=goal_data.get('name', 'Unknown Goal'),
                icon=goal_data.get('icon', '🎯'),
                evidence=self._determine_evidence_level(goal_data.get('percentage', 0)),
                percentage=goal_data.get('percentage', 0.0),
                save_count=goal_data.get('save_count', 0),
                key_accounts=goal_data.get('key_accounts', []),
                description=goal_data.get('description', ''),
                goals=goals
            ))
        
        # Convert parsed patterns to BehavioralPattern objects
        behavioral_patterns = [
            BehavioralPattern(
                type=pattern.get('type', 'general'),
                title=pattern.get('title', 'Behavioral Pattern'),
                description=pattern.get('description', ''),
                data=pattern.get('data', {}),
                insight=pattern.get('insight', '')
            ) for pattern in parsed_content.get('behavioral_patterns', [])
        ]
        
        # Generate interest distribution from goal areas
        interest_distribution = [
            InterestDistribution(
                category=goal.name,
                percentage=goal.percentage,
                goal_potential=self._determine_goal_potential(goal.percentage)
            ) for goal in goal_areas
        ]
        
        return AnalysisResult(
            total_posts=self._extract_total_posts(original_data),
            analysis_date=datetime.now().isoformat(),
            content_id=str(uuid.uuid4()),
            model_info=model_info,
            goal_areas=goal_areas,
            behavioral_patterns=behavioral_patterns,
            interest_distribution=interest_distribution,
            raw_model_output=raw_response.get('content', '')
        )

    def _determine_evidence_level(self, percentage: float) -> EvidenceLevel:
        """Determine evidence level based on percentage."""
        if percentage >= 40:
            return EvidenceLevel.HIGH
        elif percentage >= 20:
            return EvidenceLevel.MEDIUM
        else:
            return EvidenceLevel.LOW

    def _determine_goal_potential(self, percentage: float) -> GoalPotential:
        """Determine goal potential based on percentage."""
        if percentage >= 30:
            return GoalPotential.HIGH
        elif percentage >= 15:
            return GoalPotential.MEDIUM
        else:
            return GoalPotential.LOW

    def _extract_total_posts(self, original_data: Optional[Dict[str, Any]]) -> int:
        """Extract total posts from original data."""
        if not original_data:
            return 100  # Default fallback
        
        # Try to extract from various data structures
        if isinstance(original_data, dict):
            return original_data.get('total_posts', 100)
        
        return 100

    def _create_fallback_result(self, raw_response: Dict[str, Any], error: str) -> AnalysisResult:
        """Create a minimal valid result when parsing fails."""
        model_info = ModelInfo(
            provider=raw_response.get('provider', 'unknown'),
            model=raw_response.get('model', 'unknown'),
            latency_ms=raw_response.get('latency_ms', 0),
            cost_tier=CostTier(raw_response.get('cost_tier', 'medium')),
            capabilities=raw_response.get('capabilities', [])
        )
        
        # Create minimal goal area
        fallback_goal = GoalArea(
            id='fallback',
            name='General Development',
            icon='🎯',
            evidence=EvidenceLevel.MEDIUM,
            percentage=50.0,
            save_count=50,
            key_accounts=[],
            description='Unable to parse specific goals from model response.',
            goals=[
                Goal(
                    term='30-day',
                    title='Short-term Focus',
                    description='Review and plan immediate actions.'
                )
            ]
        )
        
        return AnalysisResult(
            total_posts=100,
            analysis_date=datetime.now().isoformat(),
            content_id=str(uuid.uuid4()),
            model_info=model_info,
            goal_areas=[fallback_goal],
            behavioral_patterns=[],
            interest_distribution=[
                InterestDistribution(
                    category='General',
                    percentage=100.0,
                    goal_potential=GoalPotential.MEDIUM
                )
            ],
            raw_model_output=f"Parsing error: {error}"
        )


def normalize_model_response(raw_response: Dict[str, Any], 
                           original_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function for normalizing model responses.
    
    Args:
        raw_response: Raw response from any model
        original_data: Optional original Instagram data
        
    Returns:
        Dict: Normalized response in frontend-expected format
    """
    normalizer = ResponseNormalizer()
    result = normalizer.normalize_response(raw_response, original_data)
    
    # Convert to dict for JSON serialization
    return {
        'success': True,
        'analysisResult': {
            'totalPosts': result.total_posts,
            'analysisDate': result.analysis_date,
            'contentId': result.content_id,
            'modelInfo': {
                'provider': result.model_info.provider,
                'model': result.model_info.model,
                'latency_ms': result.model_info.latency_ms,
                'cost_tier': result.model_info.cost_tier.value,
                'capabilities': result.model_info.capabilities
            },
            'goalAreas': [
                {
                    'id': goal.id,
                    'name': goal.name,
                    'icon': goal.icon,
                    'evidence': goal.evidence.value,
                    'percentage': goal.percentage,
                    'saveCount': goal.save_count,
                    'keyAccounts': goal.key_accounts,
                    'description': goal.description,
                    'goals': [
                        {
                            'term': g.term,
                            'title': g.title,
                            'description': g.description
                        } for g in goal.goals
                    ]
                } for goal in result.goal_areas
            ],
            'behavioralPatterns': [
                {
                    'type': pattern.type,
                    'title': pattern.title,
                    'description': pattern.description,
                    'data': pattern.data,
                    'insight': pattern.insight
                } for pattern in result.behavioral_patterns
            ],
            'interestDistribution': [
                {
                    'category': dist.category,
                    'percentage': dist.percentage,
                    'goalPotential': dist.goal_potential.value
                } for dist in result.interest_distribution
            ],
            'rawModelOutput': result.raw_model_output
        }
    }


if __name__ == "__main__":
    # Test the normalizer with sample data
    sample_response = {
        'content': "{'role': 'assistant', 'content': [{'text': 'Based on your Instagram analysis, I recommend focusing on fitness goals (50%), learning goals (30%), and business goals (20%). For fitness, start with 30-day workout routines.'}]}",
        'latency_ms': 5000,
        'model_family': 'claude',
        'cost_tier': 'high',
        'provider': 'anthropic',
        'model': 'claude-3-5-sonnet',
        'capabilities': ['text', 'vision'],
        'success': True
    }
    
    normalized = normalize_model_response(sample_response)
    print(json.dumps(normalized, indent=2))