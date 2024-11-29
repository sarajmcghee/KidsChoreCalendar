from PIL import Image
from display.epd7in5_V2 import EPD  # Replace with your display's driver

try:
    # Initialize the e-paper display
    epd = EPD()
    epd.init()
    epd.Clear()
    print("E-paper display initialized successfully.")
    print(f"EPD Width: {epd.width}, EPD Height: {epd.height}")

    # Load the previously created image
    image_path = '/home/pi/MagInkCal/blackimg.png'  # Update to your image's path if different
    image = Image.open(image_path)
    print(f"Loaded image resolution: {image.size}")

    # Rotate the image 90 degrees
    image = image.rotate(90, expand=True)
    print(f"Rotated image resolution: {image.size}")

    # Ensure the image matches the e-paper resolution
    if image.size != (epd.width, epd.height):
        print("Resizing image to match e-paper resolution...")
        image = image.resize((epd.width, epd.height))

    # Convert the image to 1-bit or grayscale mode, depending on the display
    image = image.convert('1')  # Convert to 1-bit black-and-white mode
    # For grayscale displays, use: image = image.convert('L')

    # Display the image
    buffer = epd.getbuffer(image)  # Convert the image to a display buffer
    epd.display(buffer)
    print("Rotated image displayed successfully.")

    # Put the e-paper display to sleep
    epd.sleep()
    print("E-paper display put to sleep.")
except Exception as e:
    print(f"Error: {e}")
