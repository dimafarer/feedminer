import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ModelSelector, { AVAILABLE_MODELS, type ModelInfo } from '../../components/ModelSelector'

describe('ModelSelector', () => {
  const mockOnModelChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders model selector with available models', () => {
    render(
      <ModelSelector
        selectedModel={AVAILABLE_MODELS[0]}
        onModelChange={mockOnModelChange}
        showDetails={true}
      />
    )
    
    // Check if Claude models are available (Phase 1)
    expect(screen.getAllByText(/Claude 3.5 Sonnet/)).toHaveLength(2) // Both API and Bedrock versions
    expect(screen.getByText(/Anthropic Claude/)).toBeInTheDocument()
  })

  it('displays model details correctly', () => {
    render(
      <ModelSelector
        selectedModel={AVAILABLE_MODELS[0]}
        onModelChange={mockOnModelChange}
        showDetails={true}
      />
    )
    
    // Check for cost tier information (multiple models may have High Cost)
    expect(screen.getAllByText(/High Cost/)).toHaveLength(2) // Claude API and Bedrock
    
    // Check for capability information
    expect(screen.getByText(/Advanced reasoning/)).toBeInTheDocument()
    expect(screen.getByText(/multimodal capabilities/)).toBeInTheDocument()
  })

  it('shows current model as selected', () => {
    const selectedModel = AVAILABLE_MODELS[0] // Claude Sonnet
    
    render(
      <ModelSelector
        selectedModel={selectedModel}
        onModelChange={mockOnModelChange}
        showDetails={true}
      />
    )
    
    // Selected model should show as active in the interface
    expect(screen.getByText(selectedModel.name)).toBeInTheDocument()
    expect(screen.getByText(selectedModel.family)).toBeInTheDocument()
  })

  it('renders compact mode correctly', () => {
    render(
      <ModelSelector
        selectedModel={AVAILABLE_MODELS[0]}
        onModelChange={mockOnModelChange}
        compact={true}
      />
    )
    
    // In compact mode, should render as a select dropdown
    expect(screen.getByRole('combobox')).toBeInTheDocument()
    expect(screen.getByText('AI Model')).toBeInTheDocument()
  })

  it('displays available models correctly', () => {
    render(
      <ModelSelector
        selectedModel={AVAILABLE_MODELS[0]}
        onModelChange={mockOnModelChange}
        showDetails={true}
      />
    )
    
    // Should show model family information
    expect(screen.getByText(/Anthropic Claude/)).toBeInTheDocument()
    expect(screen.getByText(/Amazon Nova/)).toBeInTheDocument()
    expect(screen.getByText(/Meta Llama/)).toBeInTheDocument()
    
    // Should show model capabilities
    expect(screen.getByText(/Advanced reasoning/)).toBeInTheDocument()
  })

  it('shows cost tier information', () => {
    render(
      <ModelSelector
        selectedModel={AVAILABLE_MODELS[0]}
        onModelChange={mockOnModelChange}
        showDetails={true}
      />
    )
    
    // Should show cost tier badges - check that they exist
    const highCostElements = screen.getAllByText(/High Cost/)
    expect(highCostElements.length).toBeGreaterThanOrEqual(2) // At least Claude API and Bedrock
    
    const veryLowCostElements = screen.getAllByText(/Very Low Cost/)
    expect(veryLowCostElements.length).toBeGreaterThanOrEqual(2) // At least Nova models
    
    const lowCostElements = screen.getAllByText(/Low Cost/)
    expect(lowCostElements.length).toBeGreaterThanOrEqual(2) // At least Llama models
    
    // Should show timing information for selected model
    expect(screen.getByText(/7\.5s/)).toBeInTheDocument()
  })

  it('handles dropdown selection in compact mode', () => {
    render(
      <ModelSelector
        selectedModel={AVAILABLE_MODELS[0]}
        onModelChange={mockOnModelChange}
        compact={true}
      />
    )
    
    const dropdown = screen.getByRole('combobox')
    expect(dropdown).toBeInTheDocument()
    
    // Should have the selected model's value
    expect(dropdown).toHaveValue(AVAILABLE_MODELS[0].id)
    
    // Test dropdown change
    fireEvent.change(dropdown, { target: { value: AVAILABLE_MODELS[1]?.id || 'claude-bedrock' } })
    
    // Should call onModelChange when selection changes
    expect(mockOnModelChange).toHaveBeenCalled()
  })

  it('renders model capabilities and benefits', () => {
    render(
      <ModelSelector
        selectedModel={AVAILABLE_MODELS[0]}
        onModelChange={mockOnModelChange}
        showDetails={true}
      />
    )
    
    // Should show benefits from the first model (Claude Sonnet)
    expect(screen.getByText(/Excellent reasoning and analysis/)).toBeInTheDocument()
    // Benefits are only shown first 2 items, and "Strong goal-setting insights" is the 3rd item
    // Let's test the actual second benefit instead
    expect(screen.getByText(/Concise, actionable recommendations/)).toBeInTheDocument()
  })
})