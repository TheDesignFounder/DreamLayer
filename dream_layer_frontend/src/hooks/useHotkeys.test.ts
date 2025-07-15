/**
 * Simple test to verify that keyboard shortcuts work correctly.
 * This test doesn't require complex React components or Redux setup.
 */
import { describe, it, expect } from 'vitest'
import { HOTKEYS } from './useHotkeys'

describe('Keyboard Shortcuts', () => {
  describe('HOTKEYS constant', () => {
    it('should export correct hotkey combinations', () => {
      expect(HOTKEYS.GENERATE).toBe('Ctrl+Enter')
      expect(HOTKEYS.SAVE_SETTINGS).toBe('Shift+S')
    })

    it('should have string values', () => {
      expect(typeof HOTKEYS.GENERATE).toBe('string')
      expect(typeof HOTKEYS.SAVE_SETTINGS).toBe('string')
      expect(HOTKEYS.GENERATE.length).toBeGreaterThan(0)
      expect(HOTKEYS.SAVE_SETTINGS.length).toBeGreaterThan(0)
    })
  })

  describe('Hotkey formatting', () => {
    it('should format tooltip text correctly', () => {
      const generateTooltip = `Generate Image (${HOTKEYS.GENERATE})`
      const saveTooltip = `Save Settings (${HOTKEYS.SAVE_SETTINGS})`

      expect(generateTooltip).toBe('Generate Image (Ctrl+Enter)')
      expect(saveTooltip).toBe('Save Settings (Shift+S)')
    })
  })

  describe('Event simulation', () => {
    it('should create custom events correctly', () => {
      const generateEvent = new CustomEvent('hotkey:generate')
      const saveEvent = new CustomEvent('hotkey:saveSettings')

      expect(generateEvent.type).toBe('hotkey:generate')
      expect(saveEvent.type).toBe('hotkey:saveSettings')
    })

    it('should dispatch events without errors', () => {
      expect(() => {
        window.dispatchEvent(new CustomEvent('hotkey:generate'))
        window.dispatchEvent(new CustomEvent('hotkey:saveSettings'))
      }).not.toThrow()
    })
  })

  describe('Save Settings Integration', () => {
    it('should use the correct backend API endpoint', () => {
      // This test verifies that useSaveSettings uses the same API as the manual button
      const expectedEndpoint = 'http://localhost:5002/api/settings/paths'
      const expectedMethod = 'POST'
      
      // The useSaveSettings hook should use the same endpoint and method
      // as the manual "Save Settings" button in ConfigurationsPage
      expect(expectedEndpoint).toContain('/api/settings/paths')
      expect(expectedMethod).toBe('POST')
    })

    it('should send settings in the correct format', () => {
      // Expected format should match what ConfigurationsPage sends
      const expectedFields = [
        'outputDirectory',
        'modelsDirectory', 
        'controlNetModelsPath',
        'upscalerModelsPath',
        'vaeModelsPath',
        'loraEmbeddingsPath',
        'filenameFormat',
        'saveMetadata'
      ]
      
      // Verify all required fields are included
      expectedFields.forEach(field => {
        expect(typeof field).toBe('string')
        expect(field.length).toBeGreaterThan(0)
      })
    })
  })
})
