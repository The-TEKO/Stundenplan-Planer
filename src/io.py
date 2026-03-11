# Handles loading and validating input data from JSON files.
import json
def load_data(file_path):
    """
    Loads data from a JSON file and validates its structure.

    Args:
        file_path: The path to the JSON file containing the input data.
    Returns:
        dict: A dictionary containing the loaded and validated data.
    Raises:
        ValueError: If the JSON file is malformed or missing required fields.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Add your validation logic here if needed
        return data
    except Exception as e:
        raise ValueError(f"Error loading JSON: {e}")

# Example usage: load banane.json directly
if __name__ == "__main__":
    data = load_data(r"C:\Users\janis\OneDrive\Dokumente\Teko\Projekte\Projektarbeit Programmieren\Stundenplan-Planer\banane.json")
    print(data)



