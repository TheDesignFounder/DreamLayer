# Enhanced Grid Exporter

A powerful image grid creation tool with advanced features for organizing and labeling image collections.

## 🚀 Features

### Core Features
- **Drag & Drop Interface** - Simply drag images into the interface for instant processing
- **Real-time Preview** - See how your grid will look before generating
- **Multiple Export Formats** - PNG, JPEG, WebP, TIFF with quality optimization
- **Custom Font Support** - Upload and use custom fonts for labels
- **Batch Processing** - Process multiple directories at once
- **Image Preprocessing** - Resize, crop, apply filters and adjustments
- **Grid Templates** - Save and load custom grid layouts
- **Metadata Editor** - Edit CSV data directly in the UI
- **Background Options** - Custom background colors and images
- **Animation Support** - Create animated GIF grids (coming soon)

### Advanced Features
- **Smart Grid Layout** - Automatic grid dimension calculation
- **CSV Metadata Integration** - Add labels from CSV files
- **Progress Tracking** - Real-time progress updates
- **Error Handling** - Robust error recovery and validation
- **Cross-platform Support** - Works on Windows, macOS, and Linux
- **High Performance** - Optimized for large image collections

## 📖 Usage

### Basic Usage

1. **Select Images**
   - Drag & drop images into the interface, or
   - Browse and select image files, or
   - Provide a directory path containing images

2. **Configure Settings**
   - Choose a preset or customize grid layout
   - Set output path and format
   - Configure labels and metadata

3. **Generate Grid**
   - Click "Create Grid" to generate
   - Download the result when complete

### Advanced Usage

#### Drag & Drop
- Simply drag image files into the designated area
- Supports all major image formats (PNG, JPEG, GIF, WebP, TIFF, BMP)
- Files are automatically processed and organized

#### Real-time Preview
- Use the Preview tab to see how your grid will look
- Adjust settings and see changes instantly
- Perfect for fine-tuning layouts

#### Batch Processing
- Process multiple directories at once
- Each directory gets its own output file
- Ideal for organizing large image collections

#### Image Preprocessing
- **Resize**: Fit, fill, or stretch images to specific dimensions
- **Adjustments**: Brightness, contrast, and saturation controls
- **Filters**: Blur, sharpen, emboss, and edge enhancement
- **Crop**: Define custom crop areas

#### Grid Templates
- Save frequently used settings as templates
- Load templates for quick setup
- Share templates with team members

#### Export Options
- **PNG**: Lossless quality, perfect for graphics
- **JPEG**: Compressed format, good for photos
- **WebP**: Modern format, excellent compression
- **TIFF**: High quality, suitable for printing

## 🎨 Presets

### Basic Presets
- **Default**: Standard 3x3 grid
- **Compact**: Tight spacing for more images
- **Large**: Bigger images with more spacing
- **Presentation**: Perfect for slideshows
- **Comparison**: Side-by-side comparisons
- **Gallery**: Showcase multiple images
- **Wide**: Landscape format
- **Tall**: Portrait format

### Advanced Presets
- **Web Optimized**: JPEG format for web
- **Print Ready**: High resolution TIFF
- **Dark Theme**: Dark background
- **Minimal**: Clean minimal design

### Specialized Presets
- **Social Media**: Optimized for sharing
- **Portfolio**: Professional layout
- **Thumbnail**: Small preview images
- **Hero**: Large hero-style layout

## 📁 File Structure

```
dream_layer_frontend/src/features/GridExporter/
├── index.tsx              # Main component
├── presets.ts             # Grid presets
└── README.md              # This file
```

## 🔧 API Endpoints

### Create Grid
```
POST /api/create-labeled-grid
```

**Request Body:**
```json
{
  "input_dir": "path/to/images",
  "output_path": "path/to/output.png",
  "csv_path": "path/to/metadata.csv",
  "label_columns": ["prompt", "model"],
  "rows": 3,
  "cols": 3,
  "font_size": 16,
  "margin": 10,
  "export_format": "png",
  "background_color": [255, 255, 255],
  "cell_size": [256, 256],
  "preprocessing": {
    "resize": {
      "size": [256, 256],
      "mode": "fit"
    },
    "brightness": 1.0,
    "contrast": 1.0,
    "saturation": 1.0,
    "filters": [
      {
        "type": "sharpen",
        "strength": 1.0
      }
    ]
  },
  "batch_dirs": ["dir1", "dir2", "dir3"]
}
```

### Get Templates
```
GET /api/grid-templates
```

### Save Template
```
POST /api/save-grid-template
```

### Load Template
```
POST /api/load-grid-template
```

### Preview Grid
```
POST /api/preview-grid
```

## 📋 CSV Format

The CSV file should have a `filename` column that matches your image filenames:

```csv
filename,prompt,model,seed,steps
image1.png,"a beautiful landscape",stable-diffusion,12345,50
image2.png,"a portrait of a cat",midjourney,67890,30
image3.png,"abstract art",dalle,11111,25
```

## 🎯 Use Cases

### AI Art Collections
- Organize Stable Diffusion outputs
- Compare different models and prompts
- Create presentation slideshows
- Build portfolio showcases

### Research & Analysis
- Compare experimental results
- Document research findings
- Create visual reports
- Organize data visualizations

### Content Creation
- Social media content grids
- Blog post illustrations
- Marketing materials
- Educational resources

### Personal Projects
- Photo collections
- Art portfolios
- Memory books
- Creative projects

## 🛠️ Technical Details

### Supported Image Formats
- PNG (Portable Network Graphics)
- JPEG (Joint Photographic Experts Group)
- WebP (Web Picture format)
- TIFF (Tagged Image File Format)
- GIF (Graphics Interchange Format)
- BMP (Bitmap)

### Performance Optimizations
- Lazy loading of images
- Efficient memory management
- Parallel processing for batch operations
- Optimized image compression

### Error Handling
- Graceful fallbacks for missing files
- Validation of input parameters
- Detailed error messages
- Recovery from processing failures

## 🔮 Future Enhancements

- **Animation Support**: Create animated GIF grids
- **Custom Fonts**: Upload and use custom fonts
- **Advanced Filters**: More image processing options
- **Cloud Integration**: Direct upload to cloud storage
- **Collaboration**: Share and collaborate on grids
- **AI Enhancement**: Automatic image enhancement
- **Mobile Support**: Responsive mobile interface

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is part of DreamLayer AI and follows the same licensing terms. 