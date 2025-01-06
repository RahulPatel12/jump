from PIL import Image, ImageDraw

def create_crosshair():
    # Create a new image with a transparent background
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Crosshair settings
    color = (255, 255, 255, 255)  # White
    thickness = 2
    length = 16
    gap = 4
    
    # Draw horizontal line
    draw.rectangle([
        (size//2 - length - gap, size//2 - thickness//2),
        (size//2 - gap, size//2 + thickness//2)
    ], fill=color)
    draw.rectangle([
        (size//2 + gap, size//2 - thickness//2),
        (size//2 + length + gap, size//2 + thickness//2)
    ], fill=color)
    
    # Draw vertical line
    draw.rectangle([
        (size//2 - thickness//2, size//2 - length - gap),
        (size//2 + thickness//2, size//2 - gap)
    ], fill=color)
    draw.rectangle([
        (size//2 - thickness//2, size//2 + gap),
        (size//2 + thickness//2, size//2 + length + gap)
    ], fill=color)
    
    # Draw center dot
    dot_size = 2
    draw.ellipse([
        (size//2 - dot_size, size//2 - dot_size),
        (size//2 + dot_size, size//2 + dot_size)
    ], fill=color)
    
    # Save the image
    image.save('assets/textures/crosshair.png')

if __name__ == '__main__':
    create_crosshair() 