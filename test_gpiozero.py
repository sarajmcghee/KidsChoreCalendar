from gpiozero import Button
import time

BUSY_PIN = 24  # Replace with your actual BUSY_PIN number

try:
    button = Button(BUSY_PIN, pull_up=False)
    print("Monitoring BUSY_PIN state. Press CTRL+C to exit.")
    while True:
        if button.is_pressed:
            print("BUSY_PIN is HIGH")
        else:
            print("BUSY_PIN is LOW")
        time.sleep(1)
except Exception as e:
    print(f"Error: {e}")