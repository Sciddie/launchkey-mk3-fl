def ColorToRGB(color):
    return (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
