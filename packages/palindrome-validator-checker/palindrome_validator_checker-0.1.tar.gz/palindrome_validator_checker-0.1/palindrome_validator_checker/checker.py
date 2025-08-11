
def is_palindrome(text):
    """Returns True if text is a palindrome, False otherwise."""
    normalized = ''.join(filter(str.isalnum, text.lower()))
    return normalized == normalized[::-1]
