import cv2
import pytesseract
import os

# Specify the Tesseract-OCR executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Class to represent a detected character with its coordinates
class DetectedCharacter:
    def __init__(self, character, x, y, width, height):
        self.character = character
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def to_output_format(self, image_width, image_height):
        # Map character to an index
        if self.character.isdigit():
            class_index = int(self.character)  # '0' -> 0, '1' -> 1, ..., '9' -> 9
        elif self.character.isalpha():
            class_index = ord(self.character) - ord('A') + 10  # 'A' -> 10, 'B' -> 11, ..., 'Z' -> 35
        else:
            return None  # If the character is not valid, return None
        
        # Calculate normalized values ensuring they are within [0, 1]
        normalized_x = max(0, min(1, (self.x + self.width / 2) / image_width))
        normalized_y = max(0, min(1, (self.y + self.height / 2) / image_height))
        normalized_width = max(0, min(1, self.width / image_width))
        normalized_height = max(0, min(1, self.height / image_height))
        
        return f"{class_index} {normalized_x:.6f} {normalized_y:.6f} {normalized_width:.6f} {normalized_height:.6f}"

# Function to process the image
def process_image(image_path, output_folder):
    # Load the image
    image = cv2.imread(image_path)

    # Get image dimensions
    image_height, image_width, _ = image.shape

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Thresholding to get a binary image
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Use pytesseract to do OCR on the image
    boxes = pytesseract.image_to_boxes(thresh)

    detected_characters = []

    # Filter and save detected characters
    for box in boxes.splitlines():
        b = box.split()
        character = b[0]
        if character in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':  # Allowed characters
            x, y, w_box, h_box = int(b[1]), int(b[2]), int(b[3]), int(b[4])
            detected_char = DetectedCharacter(character, x, image_height - y, w_box, h_box)
            detected_characters.append(detected_char)

            # Draw rectangle around the detected character
            cv2.rectangle(image, (x, image_height - y), (w_box, image_height - h_box), (0, 255, 0), 1)

    # Save the annotated image
    annotated_image_path = os.path.join(output_folder, 'annotated_' + os.path.basename(image_path))
    os.makedirs(output_folder, exist_ok=True)  # Create output directory if it doesn't exist
    cv2.imwrite(annotated_image_path, image)

    # Save detected characters to a text file
    text_output_path = os.path.join(output_folder, os.path.splitext(os.path.basename(image_path))[0] + '.txt')
    with open(text_output_path, 'w') as f:
        for char in detected_characters:
            output_line = char.to_output_format(image_width, image_height)
            if output_line:
                f.write(output_line + '\n')

    print(f"Annotations saved in '{text_output_path}' and image saved in '{annotated_image_path}'.")

# Example usage
if __name__ == "__main__":
    input_folder = 'images/test'  # Path to the folder containing the license plate images
    output_folder = 'results/test'  # Output folder for the results

    # Process each image in the input folder
    for image_file in os.listdir(input_folder):
        if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):  # Check for valid image file types
            process_image(os.path.join(input_folder, image_file), output_folder)
