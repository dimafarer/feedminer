"""
Unit tests for Response Normalizer

Tests the standardization layer that transforms different model outputs
into consistent frontend-compatible format.
"""

import pytest
import json
from unittest.mock import patch
from src.ai.response_normalizer import (
    ResponseNormalizer,
    normalize_model_response,
    EvidenceLevel,
    GoalPotential,
    CostTier
)


class TestResponseNormalizer:
    """Test suite for ResponseNormalizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.normalizer = ResponseNormalizer()
        
        # Sample responses from different model families
        self.claude_response = {
            'content': "{'role': 'assistant', 'content': [{'text': 'Based on your saved content analysis:\\n\\n**Fitness Goals (50%)**\\n- You saved 50 fitness posts\\n- 30-day goal: Start daily workouts\\n- 90-day goal: Build consistent routine\\n- 1-year goal: Complete fitness transformation\\n\\n**Learning Goals (30%)**\\n- 30 learning-related saves\\n- Focus on skill development\\n\\n**Business Goals (20%)**\\n- 20 business posts saved\\n- Career advancement opportunities'}]}",
            'latency_ms': 7470,
            'model_family': 'claude',
            'cost_tier': 'high',
            'provider': 'anthropic',
            'model': 'claude-3-5-sonnet-20241022',
            'capabilities': ['text', 'vision', 'reasoning'],
            'success': True,
            'usage': {'input_tokens': 93, 'output_tokens': 323}
        }
        
        self.nova_response = {
            'content': "{'role': 'assistant', 'content': [{'text': '# Instagram Content Analysis\\n\\n## Goal Recommendations\\n\\n### Fitness and Health (50%)\\nBased on your 50 fitness-related saves, I recommend:\\n- Short-term (30-day): Establish daily movement habit\\n- Medium-term (90-day): Build structured workout routine\\n- Long-term (1-year): Achieve significant fitness milestones\\n\\n### Learning and Education (30%)\\nYour 30 learning posts indicate:\\n- Focus on skill development\\n- Continuous education priorities\\n\\n### Business and Career (20%)\\n20 business-related saves suggest professional growth focus.'}]}",
            'latency_ms': 2781,
            'model_family': 'nova',
            'cost_tier': 'very_low',
            'provider': 'nova',
            'model': 'us.amazon.nova-micro-v1:0',
            'capabilities': ['text', 'multimodal'],
            'success': True,
            'usage': {'input_tokens': 81, 'output_tokens': 640}
        }
        
        self.llama_response = {
            'content': "{'role': 'assistant', 'content': [{'text': 'Instagram Analysis Results:\\n\\n1. Fitness Goals (50% of saves)\\n   - You show strong interest in fitness content\\n   - 30-day action: Start with 3 weekly workouts\\n   - 90-day plan: Build consistent exercise habits\\n   - 1-year vision: Complete fitness transformation\\n\\n2. Learning Goals (30% of saves)\\n   - Educational content preferences\\n   - Skill development focus\\n\\n3. Business Goals (20% of saves)\\n   - Career-oriented content\\n   - Professional development interest'}]}",
            'latency_ms': 2400,
            'model_family': 'llama',
            'cost_tier': 'low',
            'provider': 'llama',
            'model': 'meta.llama3-1-8b-instruct-v1:0',
            'capabilities': ['text'],
            'success': True,
            'usage': {'input_tokens': 93, 'output_tokens': 645}
        }

    def test_extract_content_text_claude(self):
        """Test content extraction from Claude's stringified dict."""
        content_text = self.normalizer._extract_content_text(self.claude_response)
        
        assert "Fitness Goals (50%)" in content_text
        assert "30-day goal:" in content_text
        assert "Business Goals (20%)" in content_text

    def test_extract_content_text_nova(self):
        """Test content extraction from Nova's stringified dict."""
        content_text = self.normalizer._extract_content_text(self.nova_response)
        
        assert "# Instagram Content Analysis" in content_text
        assert "### Fitness and Health (50%)" in content_text
        assert "Short-term (30-day)" in content_text

    def test_extract_content_text_llama(self):
        """Test content extraction from Llama's stringified dict."""
        content_text = self.normalizer._extract_content_text(self.llama_response)
        
        assert "1. Fitness Goals (50% of saves)" in content_text
        assert "30-day action:" in content_text
        assert "3. Business Goals (20% of saves)" in content_text

    def test_extract_content_text_fallback(self):
        """Test content extraction fallback for malformed content."""
        malformed_response = {'content': 'plain text without dict format'}
        content_text = self.normalizer._extract_content_text(malformed_response)
        assert content_text == 'plain text without dict format'

    def test_parse_claude_content(self):
        """Test Claude-specific content parsing."""
        content_text = self.normalizer._extract_content_text(self.claude_response)
        parsed = self.normalizer._parse_claude_content(content_text)
        
        assert 'goal_areas' in parsed
        assert len(parsed['goal_areas']) >= 1
        
        # Check fitness goal extraction
        fitness_goals = [g for g in parsed['goal_areas'] if 'fitness' in g.get('category', '').lower()]
        assert len(fitness_goals) >= 1
        
        fitness_goal = fitness_goals[0]
        assert fitness_goal['percentage'] == 50.0
        assert len(fitness_goal['goals']) >= 1

    def test_parse_nova_content(self):
        """Test Nova-specific content parsing."""
        content_text = self.normalizer._extract_content_text(self.nova_response)
        parsed = self.normalizer._parse_nova_content(content_text)
        
        assert 'goal_areas' in parsed
        assert len(parsed['goal_areas']) >= 1
        
        # Nova should extract fitness goal with proper percentage
        fitness_goals = [g for g in parsed['goal_areas'] if 'fitness' in g.get('category', '').lower()]
        assert len(fitness_goals) >= 1

    def test_parse_llama_content(self):
        """Test Llama-specific content parsing."""
        content_text = self.normalizer._extract_content_text(self.llama_response)
        parsed = self.normalizer._parse_llama_content(content_text)
        
        assert 'goal_areas' in parsed
        assert len(parsed['goal_areas']) >= 1
        
        # Llama uses numbered lists
        fitness_goals = [g for g in parsed['goal_areas'] if 'fitness' in g.get('category', '').lower()]
        assert len(fitness_goals) >= 1

    def test_extract_goals_from_text(self):
        """Test goal extraction from generic text."""
        text = "Your fitness saves (50%) show high interest. Learning content (30%) indicates education focus. Business posts (20%) suggest career goals."
        goals = self.normalizer._extract_goals_from_text(text)
        
        assert len(goals) >= 2
        
        # Check that fitness goal is extracted correctly
        fitness_goal = next((g for g in goals if g['category'] == 'fitness'), None)
        assert fitness_goal is not None
        assert fitness_goal['percentage'] == 50.0
        assert fitness_goal['icon'] == '💪'

    def test_extract_specific_goals_with_timeframes(self):
        """Test extraction of goals with specific timeframes."""
        text = "30-day goal: Start daily workouts. 90-day plan: Build routine. 1-year vision: Complete transformation."
        goals = self.normalizer._extract_specific_goals(text, 'fitness')
        
        # Should extract goals for multiple timeframes
        terms = {goal['term'] for goal in goals}
        assert '30-day' in terms
        assert '90-day' in terms or '1-year' in terms

    def test_determine_evidence_level(self):
        """Test evidence level determination logic."""
        assert self.normalizer._determine_evidence_level(50.0) == EvidenceLevel.HIGH
        assert self.normalizer._determine_evidence_level(25.0) == EvidenceLevel.MEDIUM
        assert self.normalizer._determine_evidence_level(10.0) == EvidenceLevel.LOW

    def test_determine_goal_potential(self):
        """Test goal potential determination logic."""
        assert self.normalizer._determine_goal_potential(40.0) == GoalPotential.HIGH
        assert self.normalizer._determine_goal_potential(20.0) == GoalPotential.MEDIUM
        assert self.normalizer._determine_goal_potential(5.0) == GoalPotential.LOW

    def test_normalize_response_claude(self):
        """Test full normalization of Claude response."""
        result = self.normalizer.normalize_response(self.claude_response)
        
        # Verify basic structure
        assert result.model_info.provider == 'anthropic'
        assert result.model_info.model == 'claude-3-5-sonnet-20241022'
        assert result.model_info.cost_tier == CostTier.HIGH
        assert result.model_info.latency_ms == 7470
        
        # Verify goal areas
        assert len(result.goal_areas) >= 1
        assert result.goal_areas[0].evidence in [EvidenceLevel.HIGH, EvidenceLevel.MEDIUM, EvidenceLevel.LOW]
        
        # Verify interest distribution
        assert len(result.interest_distribution) >= 1
        total_percentage = sum(dist.percentage for dist in result.interest_distribution)
        assert total_percentage > 0

    def test_normalize_response_nova(self):
        """Test full normalization of Nova response."""
        result = self.normalizer.normalize_response(self.nova_response)
        
        assert result.model_info.provider == 'nova'
        assert result.model_info.cost_tier == CostTier.VERY_LOW
        assert len(result.goal_areas) >= 1

    def test_normalize_response_llama(self):
        """Test full normalization of Llama response."""
        result = self.normalizer.normalize_response(self.llama_response)
        
        assert result.model_info.provider == 'llama'
        assert result.model_info.cost_tier == CostTier.LOW
        assert len(result.goal_areas) >= 1

    def test_normalize_model_response_function(self):
        """Test the convenience function normalize_model_response."""
        normalized = normalize_model_response(self.claude_response)
        
        # Verify structure matches frontend expectations
        assert 'success' in normalized
        assert 'analysisResult' in normalized
        assert normalized['success'] is True
        
        analysis = normalized['analysisResult']
        assert 'totalPosts' in analysis
        assert 'analysisDate' in analysis
        assert 'contentId' in analysis
        assert 'modelInfo' in analysis
        assert 'goalAreas' in analysis
        assert 'behavioralPatterns' in analysis
        assert 'interestDistribution' in analysis
        assert 'rawModelOutput' in analysis
        
        # Verify model info structure
        model_info = analysis['modelInfo']
        assert model_info['provider'] == 'anthropic'
        assert model_info['cost_tier'] == 'high'
        assert model_info['latency_ms'] == 7470

    def test_fallback_result_creation(self):
        """Test fallback result when parsing fails."""
        invalid_response = {
            'content': 'completely invalid format',
            'provider': 'test',
            'model': 'test-model',
            'cost_tier': 'medium'
        }
        
        with patch.object(self.normalizer, '_extract_content_text', side_effect=Exception("Parse error")):
            result = self.normalizer.normalize_response(invalid_response)
            
            # Should create valid fallback result
            assert result.model_info.provider == 'test'
            assert len(result.goal_areas) == 1
            assert result.goal_areas[0].id == 'fallback'
            assert 'error' in result.raw_model_output.lower()

    def test_goal_category_mapping(self):
        """Test that goal categories are properly mapped with icons."""
        categories = self.normalizer.GOAL_CATEGORIES
        
        assert 'fitness' in categories
        assert categories['fitness']['icon'] == '💪'
        assert 'learning' in categories
        assert categories['learning']['icon'] == '📚'
        assert 'business' in categories
        assert categories['business']['icon'] == '💼'

    def test_term_pattern_matching(self):
        """Test that timeframe patterns are correctly identified."""
        patterns = self.normalizer.TERM_PATTERNS
        
        assert '30-day' in patterns
        assert '90-day' in patterns
        assert '1-year' in patterns
        
        # Test pattern matching
        text = "For the next 30 days, focus on building habits."
        import re
        matches = any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns['30-day'])
        assert matches

    def test_json_serialization(self):
        """Test that normalized response can be JSON serialized."""
        normalized = normalize_model_response(self.claude_response)
        
        # Should be able to serialize to JSON without errors
        json_str = json.dumps(normalized)
        assert len(json_str) > 0
        
        # Should be able to deserialize back
        parsed = json.loads(json_str)
        assert parsed['success'] is True

    def test_large_response_handling(self):
        """Test handling of very large model responses."""
        large_content = "{'role': 'assistant', 'content': [{'text': '" + "Very long content. " * 1000 + "'}]}"
        large_response = {
            'content': large_content,
            'latency_ms': 10000,
            'model_family': 'claude',
            'cost_tier': 'high',
            'provider': 'anthropic',
            'model': 'claude-3-5-sonnet',
            'success': True
        }
        
        # Should handle large responses without errors
        result = self.normalizer.normalize_response(large_response)
        assert result.model_info.provider == 'anthropic'
        assert len(result.goal_areas) >= 1

    def test_empty_content_handling(self):
        """Test handling of empty or minimal content."""
        empty_response = {
            'content': "{'role': 'assistant', 'content': [{'text': ''}]}",
            'latency_ms': 1000,
            'model_family': 'claude',
            'cost_tier': 'high',
            'provider': 'anthropic',
            'model': 'claude-3-5-sonnet',
            'success': True
        }
        
        # Should create fallback result for empty content
        result = self.normalizer.normalize_response(empty_response)
        assert len(result.goal_areas) >= 1  # Should have fallback goals

    def test_model_specific_parsing_strategy_selection(self):
        """Test that correct parsing strategy is selected for each model family."""
        # Test Claude parser selection
        with patch.object(self.normalizer, '_parse_claude_content') as mock_claude:
            mock_claude.return_value = {'goal_areas': [], 'behavioral_patterns': [], 'insights': []}
            # Update parser dictionary to use mocked method
            self.normalizer.model_parsers['claude'] = mock_claude
            self.normalizer.normalize_response(self.claude_response)
            mock_claude.assert_called_once()
        
        # Test Nova parser selection
        with patch.object(self.normalizer, '_parse_nova_content') as mock_nova:
            mock_nova.return_value = {'goal_areas': [], 'behavioral_patterns': [], 'insights': []}
            # Update parser dictionary to use mocked method
            self.normalizer.model_parsers['nova'] = mock_nova
            self.normalizer.normalize_response(self.nova_response)
            mock_nova.assert_called_once()
        
        # Test Llama parser selection
        with patch.object(self.normalizer, '_parse_llama_content') as mock_llama:
            mock_llama.return_value = {'goal_areas': [], 'behavioral_patterns': [], 'insights': []}
            # Update parser dictionary to use mocked method
            self.normalizer.model_parsers['llama'] = mock_llama
            self.normalizer.normalize_response(self.llama_response)
            mock_llama.assert_called_once()


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])