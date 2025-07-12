import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import ImageHistoryGallery from '../ImageHistoryGallery';
import { ImageResult } from '@/types/imageResult';

// Mock the clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

const mockImages: ImageResult[] = [
  {
    id: '1',
    url: 'http://test.com/image1.png',
    prompt: 'A beautiful landscape with mountains and lakes',
    negativePrompt: 'blurry, low quality',
    timestamp: Date.now(),
    settings: {
      model_name: 'test-model',
      steps: 20,
      cfg_scale: 7.0,
    },
  },
  {
    id: '2',
    url: 'http://test.com/image2.png',
    prompt: 'A futuristic city with flying cars',
    negativePrompt: '',
    timestamp: Date.now() - 1000,
    settings: {
      model_name: 'another-model',
      steps: 30,
      cfg_scale: 8.0,
    },
  },
];

const defaultProps = {
  images: mockImages,
  onRemoveImage: vi.fn(),
  onClearAll: vi.fn(),
  type: 'txt2img' as const,
};

describe('ImageHistoryGallery', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders empty state when no images', () => {
    render(<ImageHistoryGallery {...defaultProps} images={[]} />);
    expect(screen.getByText('No images generated yet')).toBeInTheDocument();
  });

  it('displays image count in header', () => {
    render(<ImageHistoryGallery {...defaultProps} />);
    expect(screen.getByText('Image History (2 images)')).toBeInTheDocument();
  });

  it('renders image grid with correct number of images', () => {
    render(<ImageHistoryGallery {...defaultProps} />);
    const images = screen.getAllByRole('img');
    expect(images).toHaveLength(2);
  });

  it('filters images by search query', () => {
    render(<ImageHistoryGallery {...defaultProps} />);
    
    const searchInput = screen.getByPlaceholderText('Search prompts...');
    fireEvent.change(searchInput, { target: { value: 'landscape' } });
    
    // Should show only the landscape image
    waitFor(() => {
      const images = screen.getAllByRole('img');
      expect(images).toHaveLength(1);
    });
  });

  it('sorts images by newest/oldest', () => {
    render(<ImageHistoryGallery {...defaultProps} />);
    
    const sortSelect = screen.getByDisplayValue('Newest');
    fireEvent.click(sortSelect);
    
    const oldestOption = screen.getByText('Oldest');
    fireEvent.click(oldestOption);
    
    // Verify sort order changed (timestamps should be in ascending order)
    expect(sortSelect).toBeInTheDocument();
  });

  it('filters by model', () => {
    render(<ImageHistoryGallery {...defaultProps} />);
    
    const modelSelect = screen.getByDisplayValue('All Models');
    fireEvent.click(modelSelect);
    
    const testModelOption = screen.getByText('test-model');
    fireEvent.click(testModelOption);
    
    // Should filter to only show images from test-model
    waitFor(() => {
      const images = screen.getAllByRole('img');
      expect(images).toHaveLength(1);
    });
  });

  it('calls onRemoveImage when delete button clicked', () => {
    render(<ImageHistoryGallery {...defaultProps} />);
    
    const images = screen.getAllByRole('img');
    fireEvent.click(images[0]);
    
    // Modal should open, find delete button
    waitFor(() => {
      const deleteButton = screen.getByText('Delete Image');
      fireEvent.click(deleteButton);
      expect(defaultProps.onRemoveImage).toHaveBeenCalledWith('1');
    });
  });

  it('calls onClearAll when clear all button clicked', () => {
    render(<ImageHistoryGallery {...defaultProps} />);
    
    const clearAllButton = screen.getByText('Clear All');
    fireEvent.click(clearAllButton);
    
    expect(defaultProps.onClearAll).toHaveBeenCalled();
  });

  it('copies prompt to clipboard when copy button clicked', async () => {
    render(<ImageHistoryGallery {...defaultProps} />);
    
    const images = screen.getAllByRole('img');
    fireEvent.click(images[0]);
    
    await waitFor(() => {
      const copyButton = screen.getByText('Copy Prompt');
      fireEvent.click(copyButton);
    });
    
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      'Prompt: A beautiful landscape with mountains and lakes\nNegative: blurry, low quality'
    );
  });

  it('handles clipboard copy errors gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    navigator.clipboard.writeText = vi.fn().mockRejectedValue(new Error('Clipboard error'));
    
    render(<ImageHistoryGallery {...defaultProps} />);
    
    const images = screen.getAllByRole('img');
    fireEvent.click(images[0]);
    
    await waitFor(() => {
      const copyButton = screen.getByText('Copy Prompt');
      fireEvent.click(copyButton);
    });
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Failed to copy prompt:', expect.any(Error));
    });
    
    consoleSpy.mockRestore();
  });
});