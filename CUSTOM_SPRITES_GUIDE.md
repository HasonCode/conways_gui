# Custom Cell Sprites Guide

This guide explains how to insert your own custom cell sprites into the Conway's Game of Life GUI.

## Method 1: Using Image Files (Recommended)

### Step 1: Create Sprite Directory
Create a `sprites` folder in your project directory:
```
conways/python_implementation/
├── conway_gui.py
├── sprites/
│   ├── dead_sprite.png
│   ├── alive_sprite.png
│   ├── cancer_sprite.png
│   └── cure_sprite.png
```

### Step 2: Prepare Your Sprite Images
- **Format**: PNG files (supports transparency)
- **Size**: Any size (will be automatically resized)
- **Naming Convention**:
  - `dead_sprite.png` - Dead cells
  - `alive_sprite.png` - Alive cells
  - `cancer_sprite.png` - Cancer cells
  - `cure_sprite.png` - Cure cells

### Step 3: The GUI Will Automatically Load Them
The modified `create_cell_sprites()` method will automatically:
1. Look for sprite files in the `sprites/` directory
2. Load and resize them to match the current cell size
3. Fall back to generated sprites if files aren't found

## Method 2: Modify the Generated Sprites

You can customize the `create_generated_sprite()` method to create your own programmatic sprites:

```python
def create_generated_sprite(self, cell_type, color):
    """Create a generated sprite for a cell type"""
    img = Image.new('RGB', (self.cell_size-1, self.cell_size-1), color)
    draw = ImageDraw.Draw(img)
    
    if cell_type == "Cancer":
        # Your custom cancer cell design
        # Example: Skull pattern
        size = self.cell_size
        # Draw skull outline
        draw.ellipse([2, 2, size-3, size//2+2], outline="white", width=1)
        # Draw eye sockets
        draw.ellipse([size//4, size//4, size//4+2, size//4+2], fill="white")
        draw.ellipse([3*size//4-2, size//4, 3*size//4, size//4+2], fill="white")
        
    elif cell_type == "Cure":
        # Your custom cure cell design
        # Example: Heart pattern
        mid = self.cell_size // 2
        # Simple heart shape using circles and triangle
        draw.ellipse([mid-3, mid-2, mid-1, mid], fill="white")
        draw.ellipse([mid+1, mid-2, mid+3, mid], fill="white")
        draw.polygon([(mid-2, mid), (mid+2, mid), (mid, mid+3)], fill="white")
        
    elif cell_type == "Alive":
        # Your custom alive cell design
        # Example: Star pattern
        mid = self.cell_size // 2
        points = []
        for i in range(5):
            angle = i * 2 * 3.14159 / 5
            x = mid + int(3 * cos(angle))
            y = mid + int(3 * sin(angle))
            points.append((x, y))
        draw.polygon(points, fill="white")
    
    return img
```

## Method 3: Using Custom Colors and Patterns

You can also modify the cell types and colors in the `__init__` method:

```python
# In the __init__ method, modify this section:
self.cell_types = {
    "Dead": (DeadCell, "#1a1a1a"),      # Dark gray
    "Alive": (AliveCell, "#00ff41"),    # Bright green
    "Cancer": (CancerCell, "#ff0040"),  # Bright red
    "Cure": (CureCell, "#4080ff")       # Bright blue
}
```

## Method 4: Adding New Cell Types

To add completely new cell types:

### Step 1: Define the Cell Class
Add your new cell class to the imports section:

```python
class CustomCell(ImplCell):
    def __init__(self, row, col, grid):
        super().__init__(Location(row, col), grid)
    
    def process(self):
        # Your custom cell behavior
        return CustomCell(self.location.i, self.location.j, self.grid)
    
    def clone(self, grid):
        return CustomCell(self.location.i, self.location.j, grid)
    
    def __str__(self):
        return "🟨"  # Your emoji representation
```

### Step 2: Add to Cell Types Dictionary
```python
self.cell_types = {
    "Dead": (DeadCell, "#000000"),
    "Alive": (AliveCell, "#00FF00"),
    "Cancer": (CancerCell, "#FF0000"),
    "Cure": (CureCell, "#0000FF"),
    "Custom": (CustomCell, "#FFFF00")  # Add your new type
}
```

### Step 3: Create Sprite
Add handling in `create_generated_sprite()`:
```python
elif cell_type == "Custom":
    # Your custom sprite design
    draw.rectangle([2, 2, self.cell_size-3, self.cell_size-3], outline="white", width=2)
```

## Advanced Sprite Techniques

### Animated Sprites
For animated effects, you can create multiple frames:

```python
def create_animated_sprite(self, cell_type, frame=0):
    """Create animated sprites with multiple frames"""
    img = Image.new('RGB', (self.cell_size-1, self.cell_size-1), color)
    draw = ImageDraw.Draw(img)
    
    if cell_type == "Alive":
        # Pulsing effect
        radius = 2 + int(sin(frame * 0.5))
        mid = self.cell_size // 2
        draw.ellipse([mid-radius, mid-radius, mid+radius, mid+radius], fill="white")
    
    return img
```

### High-Resolution Sprites
For better quality at different sizes:

```python
def create_hires_sprite(self, cell_type, color):
    """Create high-resolution sprites that scale well"""
    # Create at 2x resolution
    hires_size = self.cell_size * 2
    img = Image.new('RGB', (hires_size, hires_size), color)
    draw = ImageDraw.Draw(img)
    
    # Draw at high resolution
    if cell_type == "Cancer":
        # High-res cross pattern
        draw.line([(0, 0), (hires_size, hires_size)], fill="white", width=3)
        draw.line([(0, hires_size), (hires_size, 0)], fill="white", width=3)
    
    # Scale down with anti-aliasing
    img = img.resize((self.cell_size-1, self.cell_size-1), Image.Resampling.LANCZOS)
    return img
```

## Testing Your Sprites

1. **Start Small**: Test with a small grid size first
2. **Check All Sizes**: Test different grid sizes to see how sprites scale
3. **Performance**: Monitor performance with custom sprites
4. **Fallbacks**: Ensure fallback sprites work if custom files fail to load

## Sprite File Specifications

### Recommended Specifications
- **Format**: PNG (supports transparency)
- **Size**: 16x16 to 64x64 pixels
- **Color Depth**: 24-bit or 32-bit (with alpha)
- **Background**: Transparent or solid color

### Example Sprite Creation Tools
- **GIMP**: Free, powerful image editor
- **Aseprite**: Specialized for pixel art
- **Photoshop**: Professional image editor
- **Paint.NET**: Free Windows image editor

## Troubleshooting

### Common Issues
1. **Sprites Not Loading**: Check file paths and naming
2. **Poor Quality**: Use higher resolution source images
3. **Performance Issues**: Optimize sprite complexity
4. **Size Mismatch**: Sprites are automatically resized

### Debug Tips
```python
# Add debug prints to see what's happening
print(f"Loading sprite for {cell_type} from {sprite_path}")
print(f"Sprite exists: {os.path.exists(sprite_path)}")
```

Your custom sprites will now automatically integrate with the GUI's adaptive scaling, drag optimization, and all other features!
