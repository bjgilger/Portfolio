def get_valid_int(prompt, min_value=None, max_value=None, error_msg=None):
    """Prompt the user for an integer value, validating optional min/max bounds."""
    while True:
        try:
            value = int(input(prompt))
            if (min_value is not None and value < min_value) or \
               (max_value is not None and value > max_value):
                print(error_msg or f"Value must be between {min_value} and {max_value}.")
            else:
                return value
        except ValueError:
            print("Please enter a valid integer.")

def get_positive_int(prompt):
    """Prompt the user for a positive integer."""
    return get_valid_int(prompt, min_value=1, error_msg="The number of rows should be greater than zero")

FORMATTERS = [
    'plain', 'bold', 'italic', 'header', 'link',
    'inline-code', 'new-line', 'ordered-list', 'unordered-list'
]

def format_plain():
    """Prompt for and return plain text (no formatting)."""
    return input("Text: ")

def format_bold():
    """Prompt for and return text formatted as bold in Markdown."""
    return f"**{input('Text: ')}**"

def format_italic():
    """Prompt for and return text formatted as italic in Markdown."""
    return f"*{input('Text: ')}*"

def format_inline_code():
    """Prompt for and return text formatted as inline code in Markdown."""
    return f"`{input('Text: ')}`"

def format_new_line():
    """Return a Markdown line break."""
    return '\n'

def format_link():
    """Prompt for label and URL, and return Markdown-formatted link."""
    label = input("Label: ")
    url = input("URL: ")
    return f"[{label}]({url})"

def format_header():
    """Prompt for header level and text, and return Markdown header."""
    level = get_valid_int("Level: ", 1, 6, "The level should be within the range of 1 to 6")
    text = input("Text: ")
    return f"{'#' * level} {text}\n"

def format_ordered_list():
    """Prompt for number of rows and each list item. Return Markdown-formatted ordered list."""
    n = get_positive_int("Number of rows: ")
    result = ""
    for i in range(1, n + 1):
        item = input(f"Row #{i}: ")
        result += f"{i}. {item}\n"
    return result

def format_unordered_list():
    """Prompt for number of rows and each list item. Return Markdown-formatted unordered list."""
    n = get_positive_int("Number of rows: ")
    result = ""
    for i in range(1, n + 1):
        item = input(f"Row #{i}: ")
        result += f"* {item}\n"
    return result

FORMATTER_FUNCTIONS = {
    "plain": format_plain,
    "bold": format_bold,
    "italic": format_italic,
    "header": format_header,
    "link": format_link,
    "inline-code": format_inline_code,
    "new-line": format_new_line,
    "ordered-list": format_ordered_list,
    "unordered-list": format_unordered_list,
}

def show_help():
    """Display available formatters and special commands."""
    print("Available formatters: " + " ".join(FORMATTERS))
    print("Special commands: !help !done")

def finish_session(document):
    """
    Write the final document to 'output.md' and display a Markdown preview.
    Overwrites any existing file.
    """
    with open('output.md', 'w', encoding='utf-8') as f:
        f.write(document)
    print("\n--- Markdown preview ---")
    print(document)
    print("--- File saved as output.md ---")

def main():
    """
    Main loop for the Markdown editor.
    Handles user commands and accumulates document content.
    """
    document = ""
    while True:
        user_choice = input("Choose a formatter: ")
        if user_choice == "!help":
            show_help()
        elif user_choice == "!done":
            finish_session(document)
            break
        elif user_choice in FORMATTER_FUNCTIONS:
            document += FORMATTER_FUNCTIONS[user_choice]()
            print(document)
        else:
            print("Unknown formatting type or command")

if __name__ == "__main__":
    main()
