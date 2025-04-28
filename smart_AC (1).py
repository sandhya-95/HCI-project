import tkinter as tk
from tkinter import messagebox
import threading
import speech_recognition as sr
import datetime
import random
from tkinter import ttk
import time
from PIL import Image, ImageTk

# Global variables
power_state =True
temperature = 24  # Default temperature in degrees Celsius
fan_speeds = ["Slow", "Medium", "Fast"]
current_fan_speed_index = 0  # Default fan speed index
modes = ["Cool", "Heat", "Dry", "Fan"]
current_mode_index = 0  # Default mode index
timer_on_remaining = 0
timer_off_remaining = 0
timer_on_active = False
timer_off_active = False
energy_usage = 0
temperature_history = [temperature]
user_profiles = {
    "User1": {"preferred_temp": 22, "preferred_mode": "Cool", "preferred_fan_speed": "Medium"},
    "User2": {"preferred_temp": 24, "preferred_mode": "Fan", "preferred_fan_speed": "Fast"}
}
current_profile = "User1"


# Load images for buttons
def load_image(path, size=(50, 50)):
    img = Image.open(path)
    img = img.resize(size)
    return ImageTk.PhotoImage(img)


# Function to handle button clicks
def button_click(action, value=None):
    global power_state, temperature, current_fan_speed_index, current_mode_index
    global timer_on_remaining, timer_off_remaining, timer_on_active, timer_off_active
    global temperature_history, energy_usage, current_profile

    if action == "Power":
        power_state = not power_state
        update_led()
    elif action == "Temp +":
        if power_state:
            temperature += 1
            temperature_history.append(temperature)
            update_temperature()
            calculate_energy_usage()
        else:
            messagebox.showwarning("Warning", "Turn ON the power first!")
    elif action == "Temp -":
        if power_state:
            temperature -= 1
            temperature_history.append(temperature)
            update_temperature()
            calculate_energy_usage()
        else:
            messagebox.showwarning("Warning", "Turn ON the power first!")
    elif action == "Fan Speed":
        if power_state:
            current_fan_speed_index = (current_fan_speed_index + 1) % len(fan_speeds)
            update_fan_speed()
        else:
            messagebox.showwarning("Warning", "Turn ON the power first!")
    elif action == "Mode":
        if power_state:
            current_mode_index = (current_mode_index + 1) % len(modes)
            update_mode()
        else:
            messagebox.showwarning("Warning", "Turn ON the power first!")
    elif action == "Timer On":
        if power_state:
            if value:
                timer_on_remaining = value
            else:
                timer_on_remaining += 30  # Increment timer by 30 minutes
            timer_on_active = True
            update_timer_display()
            start_timer_thread("on")
        else:
            messagebox.showwarning("Warning", "Turn ON the power first!")
    elif action == "Timer Off":
        if power_state:
            if value:
                timer_off_remaining = value
            else:
                timer_off_remaining += 30  # Increment timer by 30 minutes
            timer_off_active = True
            update_timer_display()
            start_timer_thread("off")
        else:
            messagebox.showwarning("Warning", "Turn ON the power first!")
    elif action == "Cancel Timer On":
        timer_on_remaining = 0  # Reset the timer for ON to 0
        timer_on_active = False
        update_timer_display()
    elif action == "Cancel Timer Off":
        timer_off_remaining = 0  # Reset the timer for OFF to 0
        timer_off_active = False
        update_timer_display()
    elif action == "Switch Profile":
        current_profile = "User2" if current_profile == "User1" else "User1"  # Toggle between profiles
        apply_profile()
    elif action == "Show History":
        show_temperature_history()
    elif action == "Voice Commands":
        threading.Thread(target=process_voice_command, daemon=True).start()
    elif action == "Smart Home":
        connect_to_smart_home()
    elif action == "Push Notifications":
        push_notifications()
    elif action == "Energy Usage":
        show_energy_usage()


# Function to apply the current profile settings
def apply_profile():
    global temperature, current_mode_index, current_fan_speed_index
    profile = user_profiles[current_profile]
    temperature = profile["preferred_temp"]
    current_mode_index = modes.index(profile["preferred_mode"])
    current_fan_speed_index = fan_speeds.index(profile["preferred_fan_speed"])

    update_temperature()
    update_mode()
    update_fan_speed()


# Function to calculate energy usage
def calculate_energy_usage():
    global energy_usage
    if power_state:
        energy_usage = (temperature - 20) * 0.1 + (current_fan_speed_index + 1) * 0.2
        update_energy_usage()


# Function to update the LED color
def update_led():
    if power_state:
        led_label.config(bg="green", text="ON")
    else:
        led_label.config(bg="red", text="OFF")


# Function to update the temperature display
def update_temperature():
    temp_display.config(text=f"{temperature} °C")


# Function to update the fan speed display
def update_fan_speed():
    fan_speed_display.config(text=fan_speeds[current_fan_speed_index])


# Function to update the mode display
def update_mode():
    mode_display.config(text=modes[current_mode_index])


# Function to update energy usage display
def update_energy_usage():
    energy_usage_display.config(text=f"Energy Usage: {energy_usage:.2f} kWh")


# Function to update the timer display
def update_timer_display():
    timer_on_label.config(text=f"Timer ON: {timer_on_remaining} min" if timer_on_active else "Timer ON: OFF")
    timer_off_label.config(text=f"Timer OFF: {timer_off_remaining} min" if timer_off_active else "Timer OFF: OFF")


# Function to start the timer thread
def start_timer_thread(timer_type):
    def run_timer():
        global timer_on_remaining, timer_off_remaining, timer_on_active, timer_off_active
        while True:
            if timer_type == "on" and timer_on_active:
                if timer_on_remaining > 0:
                    timer_on_remaining -= 1
                    update_timer_display()
                else:
                    timer_on_active = False
                    update_timer_display()
                    break
            elif timer_type == "off" and timer_off_active:
                if timer_off_remaining > 0:
                    timer_off_remaining -= 1
                    update_timer_display()
                else:
                    timer_off_active = False
                    update_timer_display()
                    break
            threading.Event().wait(60)

    threading.Thread(target=run_timer, daemon=True).start()


# Function to process voice commands
def process_voice_command():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                print("Listening for a command...")
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()

                print(f"Command received: {command}")
                # Process voice commands
                if "start ac" in command:
                    button_click("Power")
                elif "increase temperature" in command:
                    button_click("Temp +")
                elif "decrease temperature" in command:
                    button_click("Temp -")
                elif "switch profile" in command:
                    button_click("Switch Profile")
                elif "fan speed" in command:
                    button_click("Fan Speed")
                elif "change mode" in command:
                    button_click("Mode")
        except sr.UnknownValueError:
            print("Could not understand the command.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")


# Function to simulate connecting to a smart home system
def connect_to_smart_home():
    messagebox.showinfo("Smart Home", "AC connected to Smart Home System!")


# Function to simulate push notifications
def push_notifications():
    messagebox.showinfo("Push Notification", "Timer is about to expire!")


# Function to show temperature history
def show_temperature_history():
    history_str = "\n".join([f"{i + 1}: {temp}°C" for i, temp in enumerate(temperature_history)])
    messagebox.showinfo("Temperature History", history_str)


# Function to show energy usage
def show_energy_usage():
    messagebox.showinfo("Energy Usage", f"Current energy usage: {energy_usage:.2f} kWh")


# Create the main application window
root = tk.Tk()
root.title("Smart AC Remote")
root.geometry("360x700")
root.resizable(False, True)
root.config(bg="#E1F5FE")  # Light Blue background

# Add a scrollbar
canvas = tk.Canvas(root, bg="#E1F5FE")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#E1F5FE")

scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(fill="both", expand=True)

# Load icon images
power_icon = load_image("C:/Users/dubey/Desktop/MP/icons 2/icons/power-button.png")
temp_up_icon = load_image("C:/Users/dubey/Desktop/MP/icons 2/icons/temperature-up.png")
temp_down_icon = load_image("C:/Users/dubey/Desktop/MP/icons 2/icons/arrow-down.png")
fan_icon = load_image("C:/Users/dubey/Desktop/MP/icons 2/icons/fan.png")
mode_icon = load_image("C:/Users/dubey/Desktop/MP/icons 2/icons/brightness-and-contrast.png")
timer_icon = load_image("C:/Users/dubey/Desktop/MP/icons 2/icons/timer.png")
profile_icon = load_image("C:/Users/dubey/Desktop/MP/icons 2/icons/account.png")
history_icon = load_image("C:/Users/dubey/Desktop/MP/icons 2/icons/history.png")
voice_icon = load_image("C:/Users/dubey/Desktop/MP/icons 2/icons/microphone.png")
smart_home_icon = load_image("C:/Users/dubey/Desktop/MP/icons 2/icons/smart-home.png")
energy_icon = load_image("C:/Users/dubey/Desktop/MP/icons 2/icons/lighting.png")

# Top section for displays
top_frame = tk.Frame(scrollable_frame, pady=10, bg="#0288D1")
top_frame.pack()

# Power LED
led_label = tk.Label(top_frame, text="OFF", bg="red", fg="white", font=("Arial", 12), width=10, height=2,
                     relief="solid", borderwidth=2)
led_label.grid(row=0, column=0, padx=10)

# Temperature Display
temp_display = tk.Label(top_frame, text=f"{temperature} °C", font=("Arial", 14), width=12, height=2, fg="#0288D1")
temp_display.grid(row=0, column=1, padx=10)

# Fan Speed Display
fan_speed_display = tk.Label(top_frame, text=fan_speeds[current_fan_speed_index], font=("Arial", 12), width=10,
                             height=2)
fan_speed_display.grid(row=1, column=0, padx=10)

# Mode Display
mode_display = tk.Label(top_frame, text=modes[current_mode_index], font=("Arial", 12), width=12, height=2)
mode_display.grid(row=1, column=1, padx=10)

# Energy Usage Display
energy_usage_display = tk.Label(scrollable_frame, text=f"Energy Usage: {energy_usage:.2f} kWh", font=("Arial", 12), pady=5,
                                bg="#E1F5FE")
energy_usage_display.pack()

# Timer Displays
timer_frame = tk.Frame(scrollable_frame, pady=10, bg="#0288D1")
timer_frame.pack()

# Timer On Display
timer_on_label = tk.Label(timer_frame, text="Timer ON: OFF", font=("Arial", 12), width=20, height=2)
timer_on_label.grid(row=0, column=0, padx=10)

# Timer Off Display
timer_off_label = tk.Label(timer_frame, text="Timer OFF: OFF", font=("Arial", 12), width=20, height=2)
timer_off_label.grid(row=1, column=0, padx=10)

# Main button frame
frame = tk.Frame(scrollable_frame, pady=10, bg="#0288D1")
frame.pack()

# Buttons and their icons with labels
buttons = [
    {"text": "Power", "icon": power_icon, "row": 0, "col":    0},
    {"text": "Temp +", "icon": temp_up_icon, "row": 0, "col": 1},
    {"text": "Temp -", "icon": temp_down_icon, "row": 0, "col": 2},
    {"text": "Fan Speed", "icon": fan_icon, "row": 1, "col": 0},
    {"text": "Mode", "icon": mode_icon, "row": 1, "col": 1},
    {"text": "Timer On", "icon": timer_icon, "row": 1, "col": 2},
    {"text": "Switch Profile", "icon": profile_icon, "row": 2, "col": 0},
    {"text": "Show History", "icon": history_icon, "row": 2, "col": 1},
    {"text": "Voice Commands", "icon": voice_icon, "row": 2, "col": 2},
    {"text": "Smart Home", "icon": smart_home_icon, "row": 3, "col": 0},
    {"text": "Energy Usage", "icon": energy_icon, "row": 3, "col": 1},
    {"text": "Cancel Timer On", "icon": None, "row": 3, "col": 2},
    {"text": "Cancel Timer Off", "icon": None, "row": 4, "col": 0},
]

for button in buttons:
    icon = button["icon"]
    btn = tk.Button(
        frame,
        text=button["text"],
        image=icon,
        compound="top",
        font=("Arial", 10),
        bg="#E1F5FE",
        relief="raised",
        command=lambda action=button["text"]: button_click(action),
    )
    btn.grid(row=button["row"], column=button["col"], padx=10, pady=10)

# Run the application
root.mainloop()

