import { describe, it, expect } from 'vitest';
import { validatePikaFrameRequest, PIKA_API_CONFIG } from '../pika';
import { VALIDATION_LIMITS, PIKA_CONSTANTS } from '@/constants/validation';
import { API_ENDPOINTS, API_TIMEOUTS } from '@/constants/api';

describe('Pika API Types and Validation', () => {
  describe('validatePikaFrameRequest', () => {
    const validRequest = {
      prompt_text: 'A beautiful landscape',
      negative_prompt: 'blurry, low quality',
      seed: 12345,
      resolution: '1080p' as const,
      duration: '5s' as const,
      aspect_ratio: 1.7778,
      motion_strength: 0.7,
    };

    it('validates a correct request', () => {
      expect(validatePikaFrameRequest(validRequest)).toBe(true);
    });

    it('rejects empty prompt text', () => {
      const request = { ...validRequest, prompt_text: '' };
      expect(validatePikaFrameRequest(request)).toBe(false);
    });

    it('rejects whitespace-only prompt text', () => {
      const request = { ...validRequest, prompt_text: '   ' };
      expect(validatePikaFrameRequest(request)).toBe(false);
    });

    it('validates resolution enum values', () => {
      // Valid resolutions
      PIKA_CONSTANTS.VALID_RESOLUTIONS.forEach(resolution => {
        const request = { ...validRequest, resolution };
        expect(validatePikaFrameRequest(request)).toBe(true);
      });

      // Invalid resolution
      const request = { ...validRequest, resolution: 'invalid' as any };
      expect(validatePikaFrameRequest(request)).toBe(false);
    });

    it('validates duration enum values', () => {
      // Valid durations
      PIKA_CONSTANTS.VALID_DURATIONS.forEach(duration => {
        const request = { ...validRequest, duration };
        expect(validatePikaFrameRequest(request)).toBe(true);
      });

      // Invalid duration
      const request = { ...validRequest, duration: 'invalid' as any };
      expect(validatePikaFrameRequest(request)).toBe(false);
    });

    it('validates aspect ratio range', () => {
      // Valid aspect ratios
      const validRatios = [
        VALIDATION_LIMITS.ASPECT_RATIO.MIN,
        VALIDATION_LIMITS.ASPECT_RATIO.DEFAULT,
        VALIDATION_LIMITS.ASPECT_RATIO.MAX,
        1.0, // square
        1.333, // 4:3
      ];

      validRatios.forEach(aspect_ratio => {
        const request = { ...validRequest, aspect_ratio };
        expect(validatePikaFrameRequest(request)).toBe(true);
      });

      // Invalid aspect ratios
      const invalidRatios = [
        VALIDATION_LIMITS.ASPECT_RATIO.MIN - 0.1,
        VALIDATION_LIMITS.ASPECT_RATIO.MAX + 0.1,
        0,
        -1,
      ];

      invalidRatios.forEach(aspect_ratio => {
        const request = { ...validRequest, aspect_ratio };
        expect(validatePikaFrameRequest(request)).toBe(false);
      });
    });

    it('validates motion strength range', () => {
      // Valid motion strengths
      const validStrengths = [
        VALIDATION_LIMITS.MOTION_STRENGTH.MIN,
        VALIDATION_LIMITS.MOTION_STRENGTH.DEFAULT,
        VALIDATION_LIMITS.MOTION_STRENGTH.MAX,
        0.5,
      ];

      validStrengths.forEach(motion_strength => {
        const request = { ...validRequest, motion_strength };
        expect(validatePikaFrameRequest(request)).toBe(true);
      });

      // Invalid motion strengths
      const invalidStrengths = [
        VALIDATION_LIMITS.MOTION_STRENGTH.MIN - 0.1,
        VALIDATION_LIMITS.MOTION_STRENGTH.MAX + 0.1,
        -1,
        2,
      ];

      invalidStrengths.forEach(motion_strength => {
        const request = { ...validRequest, motion_strength };
        expect(validatePikaFrameRequest(request)).toBe(false);
      });
    });

    it('validates with undefined optional fields', () => {
      const minimalRequest = {
        prompt_text: 'A beautiful landscape',
        negative_prompt: 'blurry, low quality',
      };
      
      expect(validatePikaFrameRequest(minimalRequest)).toBe(true);
    });
  });

  describe('PIKA_API_CONFIG', () => {
    it('uses correct endpoint from constants', () => {
      expect(PIKA_API_CONFIG.ENDPOINT).toBe(API_ENDPOINTS.PIKA_SERVICE.BASE);
    });

    it('uses correct timeout from constants', () => {
      expect(PIKA_API_CONFIG.TIMEOUT).toBe(API_TIMEOUTS.DEFAULT);
    });

    it('has correct method and content type', () => {
      expect(PIKA_API_CONFIG.METHOD).toBe('POST');
      expect(PIKA_API_CONFIG.CONTENT_TYPE).toBe('application/json');
    });
  });

  describe('Constants validation', () => {
    it('has valid resolution constants', () => {
      expect(PIKA_CONSTANTS.VALID_RESOLUTIONS).toEqual(['720p', '1080p', '1440p', '4K']);
      expect(PIKA_CONSTANTS.VALID_RESOLUTIONS.length).toBeGreaterThan(0);
    });

    it('has valid duration constants', () => {
      expect(PIKA_CONSTANTS.VALID_DURATIONS).toEqual(['3s', '5s', '10s', '15s']);
      expect(PIKA_CONSTANTS.VALID_DURATIONS.length).toBeGreaterThan(0);
    });

    it('has reasonable timeout value', () => {
      expect(PIKA_CONSTANTS.TIMEOUT_MS).toBe(30000);
      expect(PIKA_CONSTANTS.TIMEOUT_MS).toBeGreaterThan(0);
    });

    it('has valid aspect ratio limits', () => {
      expect(VALIDATION_LIMITS.ASPECT_RATIO.MIN).toBe(0.4);
      expect(VALIDATION_LIMITS.ASPECT_RATIO.MAX).toBe(2.5);
      expect(VALIDATION_LIMITS.ASPECT_RATIO.DEFAULT).toBe(1.7778);
      expect(VALIDATION_LIMITS.ASPECT_RATIO.MIN).toBeLessThan(VALIDATION_LIMITS.ASPECT_RATIO.MAX);
    });

    it('has valid motion strength limits', () => {
      expect(VALIDATION_LIMITS.MOTION_STRENGTH.MIN).toBe(0);
      expect(VALIDATION_LIMITS.MOTION_STRENGTH.MAX).toBe(1);
      expect(VALIDATION_LIMITS.MOTION_STRENGTH.DEFAULT).toBe(0.7);
      expect(VALIDATION_LIMITS.MOTION_STRENGTH.MIN).toBeLessThan(VALIDATION_LIMITS.MOTION_STRENGTH.MAX);
    });
  });
});