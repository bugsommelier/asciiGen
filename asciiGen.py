import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
from PIL import Image, ImageTk, ImageEnhance, ImageOps
import cairosvg
import pyperclip


def convert_svg_to_image(svg_path, output_path):
    cairosvg.svg2png(url=svg_path, write_to=output_path)


# Declare image_path as a global variable
image_path = None


def browse_image():
    global image_path

    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp *.gif *.svg")])

    if file_path:
        image_path = file_path

        # Check if the selected file is an SVG
        if image_path.lower().endswith(".svg"):
            # Convert SVG to a temporary PNG file
            temp_image_path = "temp_image.png"
            convert_svg_to_image(image_path, temp_image_path)
            image_path = temp_image_path

        input_image_path.set(image_path)
        display_image(image_path)
        update_ascii()


# Function to remove background using OpenCV
def remove_background(image):
    if remove_background_enabled.get():
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            mask = cv2.drawContours(
                image.copy(), [largest_contour], 0, (0, 0, 0), thickness=cv2.FILLED)
            result = cv2.add(image, mask)
            return result
    return image


def convert_to_ascii(image, width, custom_chars=""):
    try:
        ascii_characters = "@%#*+=-:."

        if custom_chars:
            ascii_characters = custom_chars

        img = image.convert("L")  # Convert the image to grayscale

        ascii_image = ""
        aspect_ratio = img.height / img.width
        new_height = int(aspect_ratio * width)

        img = img.resize((width, new_height))

        for y in range(new_height):
            for x in range(width):
                pixel_color = img.getpixel((x, y))
                if pixel_color == 0 and remove_background_enabled.get():
                    ascii_char = " "
                else:
                    ascii_index = int(pixel_color / 255 *
                                      (len(ascii_characters) - 1))
                    ascii_char = ascii_characters[ascii_index]
                ascii_image += ascii_char
            ascii_image += "\n"

        return ascii_image
    except Exception as e:
        return str(e)


# Function to preprocess and display the selected image
def display_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.resize((canvas_width, canvas_height))
        photo = ImageTk.PhotoImage(img)

        canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        canvas.image = photo

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to update the ASCII art and display it


def update_ascii():
    global image_path  # Declare image_path as a global variable
    if image_path:
        custom_chars = custom_chars_entry.get()
        width = int(size_option.get())

        img = cv2.imread(image_path)  # Use OpenCV to read the image

        # Check if background removal is enabled
        if remove_background_enabled.get():
            img = remove_background(img)  # Remove background

        # Convert back to PIL Image
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        processed_image = preprocess_image(img, grayscale_var.get(),
                                           brightness_scale.get(), contrast_scale.get(), width)

        ascii_text = convert_to_ascii(
            processed_image, width, custom_chars=custom_chars)

        result_text.delete("1.0", tk.END)
        result_text.insert("1.0", ascii_text)

        # Update the canvas
        display_image(image_path)

# Function to apply image preprocessing


def preprocess_image(image, grayscale, brightness, contrast, width):
    processed_image = image.copy()

    if grayscale:
        processed_image = ImageOps.grayscale(processed_image)

    enhancer = ImageEnhance.Brightness(processed_image)
    processed_image = enhancer.enhance(brightness)

    enhancer = ImageEnhance.Contrast(processed_image)
    processed_image = enhancer.enhance(contrast)

    processed_image = processed_image.resize((width, int(
        width * processed_image.height / processed_image.width)), Image.BICUBIC)

    return processed_image

# Function to copy the ASCII art to the clipboard


def copy_to_clipboard():
    ascii_text = result_text.get("1.0", tk.END)
    pyperclip.copy(ascii_text)

# Function to save user preferences


def save_preferences():
    default_custom_chars = custom_chars_entry.get()
    default_image_width = size_option.get()
    default_grayscale = grayscale_var.get()
    default_brightness = brightness_scale.get()
    default_contrast = contrast_scale.get()

    preferences = {
        "custom_chars": default_custom_chars,
        "image_width": default_image_width,
        "grayscale": default_grayscale,
        "brightness": default_brightness,
        "contrast": default_contrast
    }

    with open("preferences.txt", "w") as file:
        for key, value in preferences.items():
            file.write(f"{key}:{value}\n")

# Function to load user preferences


def load_preferences():
    try:
        with open("preferences.txt", "r") as file:
            preferences = {}
            for line in file:
                key, value = line.strip().split(":")
                preferences[key] = value

            if "custom_chars" in preferences:
                custom_chars_entry.set(preferences["custom_chars"])
            if "image_width" in preferences:
                size_option.set(preferences["image_width"])
            if "grayscale" in preferences:
                grayscale_var.set(preferences["grayscale"])
            if "brightness" in preferences:
                brightness_scale.set(float(preferences["brightness"]))
            if "contrast" in preferences:
                contrast_scale.set(float(preferences["contrast"]))

    except FileNotFoundError:
        pass


# Create a Tkinter window
root = tk.Tk()
root.title("asciiGen")

# Declare a variable to track whether background removal is enabled
remove_background_enabled = tk.BooleanVar()
remove_background_enabled.set(False)  # Default is disabled

input_image_path = tk.StringVar()

# Create a Frame for the controls
control_frame = ttk.Frame(root)
control_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Create a Frame for the canvas and ASCII art
canvas_frame = ttk.Frame(root)
canvas_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Create Canvas to display the image
canvas_width = 400
canvas_height = 400
canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height)
canvas.pack()

# Create Scrollbars for the Canvas
x_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
y_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Link the canvas and scrollbars
canvas.config(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
x_scrollbar.config(command=canvas.xview)
y_scrollbar.config(command=canvas.yview)

# Create a Text widget for displaying ASCII art
result_text = tk.Text(canvas_frame, wrap="none",  # Set wrap to "none"
                      width=canvas_width // 10, height=canvas_height // 20)
result_text.pack(fill=tk.BOTH, expand=True)

# Create horizontal scrollbar for the Text widget
x_scrollbar_text = ttk.Scrollbar(
    canvas_frame, orient=tk.HORIZONTAL, command=result_text.xview)
x_scrollbar_text.pack(side=tk.BOTTOM, fill=tk.X)
result_text.configure(xscrollcommand=x_scrollbar_text.set)

# Create vertical scrollbar for the Text widget
y_scrollbar_text = ttk.Scrollbar(
    canvas_frame, orient=tk.VERTICAL, command=result_text.yview)
y_scrollbar_text.pack(side=tk.RIGHT, fill=tk.Y)
result_text.configure(yscrollcommand=y_scrollbar_text.set)


# Create a Label and Entry for custom characters
custom_chars_label = ttk.Label(control_frame, text="Custom Characters:")
custom_chars_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))

custom_chars_entry = tk.StringVar()
custom_chars_entry_value = ttk.Entry(
    control_frame, textvariable=custom_chars_entry)
custom_chars_entry_value.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)

# Create a Label and Entry for image width
size_label = ttk.Label(control_frame, text="Image Width:")
size_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 5))

size_option = tk.StringVar()
size_option.set("100")
size_entry = ttk.Combobox(
    control_frame, textvariable=size_option, values=("50", "100", "200", "400"))
size_entry.grid(row=1, column=1, padx=(0, 10), sticky=tk.W)

# Create a Grayscale checkbox
grayscale_var = tk.IntVar()
grayscale_checkbox = ttk.Checkbutton(
    control_frame, text="Grayscale", variable=grayscale_var)
grayscale_checkbox.grid(row=2, column=0, columnspan=2,
                        padx=(0, 10), sticky=tk.W)

# Create Brightness scale
brightness_label = ttk.Label(control_frame, text="Brightness:")
brightness_label.grid(row=3, column=0, sticky=tk.W, padx=(0, 5))

brightness_scale = tk.DoubleVar()
brightness_scale.set(1.0)
brightness_slider = ttk.Scale(
    control_frame, from_=0.1, to=2.0, variable=brightness_scale, orient=tk.HORIZONTAL)
brightness_slider.grid(row=3, column=1, padx=(0, 10), sticky=tk.W)

# Create Contrast scale
contrast_label = ttk.Label(control_frame, text="Contrast:")
contrast_label.grid(row=4, column=0, sticky=tk.W, padx=(0, 5))

contrast_scale = tk.DoubleVar()
contrast_scale.set(1.0)
contrast_slider = ttk.Scale(
    control_frame, from_=0.1, to=2.0, variable=contrast_scale, orient=tk.HORIZONTAL)
contrast_slider.grid(row=4, column=1, padx=(0, 10), sticky=tk.W)

# Create buttons
browse_button = ttk.Button(control_frame, text="Browse", command=browse_image)
browse_button.grid(row=5, column=0, columnspan=2, pady=(10, 0))

convert_button = ttk.Button(
    control_frame, text="Convert", command=update_ascii)
convert_button.grid(row=6, column=0, columnspan=2, pady=(10, 0))

copy_button = ttk.Button(
    control_frame, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.grid(row=7, column=0, columnspan=2, pady=(10, 0))

# Create a checkbox for enabling/disabling background removal
remove_background_checkbox = ttk.Checkbutton(
    control_frame, text="Remove Background", variable=remove_background_enabled)
remove_background_checkbox.grid(row=8, column=0, columnspan=2, pady=(10, 0))

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create a File menu
file_menu = tk.Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Save Preferences", command=save_preferences)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Load user preferences
load_preferences()

# Initialize custom chars history
custom_chars_history = []
undone_chars_history = []

# Start the Tkinter main loop
root.mainloop()