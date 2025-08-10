from olivattam import analyze_image, rgb_to_hex
result = analyze_image("C:/Users/Dheena Krishna/Pictures/Screenshots/Screenshot 2025-07-10 132531.png", num_colors=9,rgb=True)
for color in result:
    print(color)
    print(rgb_to_hex(color))
    # print(rgb_to_hsl(color))
    # print(rgb_to_hex(color))
print(type(result))