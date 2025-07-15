import { describe, it, expect } from 'vitest'
import { realAnalysisResults, sampleInstagramData } from '../../data/analysisResults'

describe('Analysis Results Data', () => {
  describe('realAnalysisResults', () => {
    it('has the correct structure and required fields', () => {
      expect(realAnalysisResults).toBeDefined()
      expect(realAnalysisResults.totalPosts).toBe(177)
      expect(realAnalysisResults.analysisDate).toBe('2025-07-14')
      expect(realAnalysisResults.contentId).toBe('27d6ca17-eea8-404a-a05c-d53bdbdda10f')
    })

    it('contains the expected number of goal areas', () => {
      expect(realAnalysisResults.goalAreas).toHaveLength(3)
      expect(realAnalysisResults.goalAreas[0].name).toBe('🏋️ Physical Fitness')
      expect(realAnalysisResults.goalAreas[1].name).toBe('📚 Continuous Learning')
      expect(realAnalysisResults.goalAreas[2].name).toBe('💼 Business & Personal Brand')
    })

    it('has correct fitness goal data', () => {
      const fitnessGoal = realAnalysisResults.goalAreas[0]
      
      expect(fitnessGoal.id).toBe('fitness')
      expect(fitnessGoal.evidence).toBe('HIGH')
      expect(fitnessGoal.percentage).toBe(38.2)
      expect(fitnessGoal.saveCount).toBe(12)
      expect(fitnessGoal.keyAccounts).toContain('rishfits')
      expect(fitnessGoal.keyAccounts).toContain('fitfight_')
      expect(fitnessGoal.goals).toHaveLength(3)
      
      // Check goal timeframes
      const timeframes = fitnessGoal.goals.map(g => g.term)
      expect(timeframes).toContain('30-day')
      expect(timeframes).toContain('90-day')
      expect(timeframes).toContain('1-year')
    })

    it('has correct learning goal data', () => {
      const learningGoal = realAnalysisResults.goalAreas[1]
      
      expect(learningGoal.id).toBe('learning')
      expect(learningGoal.evidence).toBe('HIGH')
      expect(learningGoal.percentage).toBe(20.6)
      expect(learningGoal.saveCount).toBe(7)
      expect(learningGoal.keyAccounts).toContain('shuffleacademy')
      expect(learningGoal.keyAccounts).toContain('brilliantorg')
    })

    it('has correct business goal data', () => {
      const businessGoal = realAnalysisResults.goalAreas[2]
      
      expect(businessGoal.id).toBe('business')
      expect(businessGoal.evidence).toBe('MEDIUM')
      expect(businessGoal.percentage).toBe(5.9)
      expect(businessGoal.saveCount).toBe(2)
      expect(businessGoal.keyAccounts).toContain('personalbrandlaunch')
    })

    it('contains behavioral patterns', () => {
      expect(realAnalysisResults.behavioralPatterns).toHaveLength(4)
      
      const patternTypes = realAnalysisResults.behavioralPatterns.map(p => p.type)
      expect(patternTypes).toContain('content_preference')
      expect(patternTypes).toContain('quality_focus')
      expect(patternTypes).toContain('temporal')
      expect(patternTypes).toContain('learning_style')
    })

    it('has content preference pattern with correct data', () => {
      const contentPattern = realAnalysisResults.behavioralPatterns.find(
        p => p.type === 'content_preference'
      )
      
      expect(contentPattern).toBeDefined()
      expect(contentPattern!.title).toBe('Visual Learning Preference')
      expect(contentPattern!.data.reels).toBe(143)
      expect(contentPattern!.data.posts).toBe(34)
      expect(contentPattern!.data.reelsPercentage).toBe(80.8)
    })

    it('has interest distribution data', () => {
      expect(realAnalysisResults.interestDistribution).toHaveLength(5)
      
      const fitnessInterest = realAnalysisResults.interestDistribution.find(
        i => i.category === 'Fitness & Health Goals'
      )
      expect(fitnessInterest).toBeDefined()
      expect(fitnessInterest!.percentage).toBe(38.2)
      expect(fitnessInterest!.goalPotential).toBe('High')
    })

    it('has percentages that add up to 100%', () => {
      const totalPercentage = realAnalysisResults.interestDistribution
        .reduce((sum, item) => sum + item.percentage, 0)
      
      expect(totalPercentage).toBe(100)
    })

    it('validates all goal areas have required goal timeframes', () => {
      realAnalysisResults.goalAreas.forEach(goalArea => {
        expect(goalArea.goals).toHaveLength(3)
        
        const terms = goalArea.goals.map(g => g.term)
        expect(terms).toContain('30-day')
        expect(terms).toContain('90-day')
        expect(terms).toContain('1-year')
        
        goalArea.goals.forEach(goal => {
          expect(goal.title).toBeTruthy()
          expect(goal.description).toBeTruthy()
        })
      })
    })

    it('validates behavioral patterns have required fields', () => {
      realAnalysisResults.behavioralPatterns.forEach(pattern => {
        expect(pattern.type).toBeTruthy()
        expect(pattern.title).toBeTruthy()
        expect(pattern.description).toBeTruthy()
        expect(pattern.data).toBeTruthy()
        expect(pattern.insight).toBeTruthy()
      })
    })
  })

  describe('sampleInstagramData', () => {
    it('has correct Instagram export format', () => {
      expect(sampleInstagramData).toBeDefined()
      expect(sampleInstagramData.saved_saved_media).toBeDefined()
      expect(Array.isArray(sampleInstagramData.saved_saved_media)).toBe(true)
    })

    it('contains sample posts with correct structure', () => {
      const posts = sampleInstagramData.saved_saved_media
      expect(posts.length).toBeGreaterThan(0)
      
      posts.forEach(post => {
        expect(post.title).toBeTruthy()
        expect(post.string_map_data).toBeDefined()
        expect(post.string_map_data['Saved on']).toBeDefined()
        expect(post.string_map_data['Saved on'].href).toBeTruthy()
        expect(post.string_map_data['Saved on'].timestamp).toBeTruthy()
      })
    })

    it('matches real Instagram export format', () => {
      const firstPost = sampleInstagramData.saved_saved_media[0]
      
      expect(firstPost.title).toBe('rishfits')
      expect(firstPost.string_map_data['Saved on'].href).toMatch(/instagram\.com\/reel\//)
      expect(typeof firstPost.string_map_data['Saved on'].timestamp).toBe('number')
    })
  })

  describe('Data consistency', () => {
    it('maintains consistency between goal areas and interest distribution', () => {
      const fitnessGoal = realAnalysisResults.goalAreas.find(g => g.id === 'fitness')
      const fitnessInterest = realAnalysisResults.interestDistribution.find(
        i => i.category === 'Fitness & Health Goals'
      )
      
      expect(fitnessGoal!.percentage).toBe(fitnessInterest!.percentage)
    })

    it('has realistic save counts relative to percentages', () => {
      realAnalysisResults.goalAreas.forEach(goal => {
        // Save count should be reasonable relative to total posts and percentage
        const expectedSaves = Math.round((goal.percentage / 100) * realAnalysisResults.totalPosts)
        const tolerance = Math.max(2, expectedSaves * 0.3) // Allow 30% tolerance
        
        expect(Math.abs(goal.saveCount - expectedSaves)).toBeLessThanOrEqual(tolerance)
      })
    })

    it('has evidence levels matching save counts', () => {
      const highEvidenceGoals = realAnalysisResults.goalAreas.filter(g => g.evidence === 'HIGH')
      const mediumEvidenceGoals = realAnalysisResults.goalAreas.filter(g => g.evidence === 'MEDIUM')
      
      // High evidence goals should have more saves than medium evidence goals
      if (highEvidenceGoals.length > 0 && mediumEvidenceGoals.length > 0) {
        const minHighSaves = Math.min(...highEvidenceGoals.map(g => g.saveCount))
        const maxMediumSaves = Math.max(...mediumEvidenceGoals.map(g => g.saveCount))
        
        expect(minHighSaves).toBeGreaterThan(maxMediumSaves)
      }
    })
  })
})