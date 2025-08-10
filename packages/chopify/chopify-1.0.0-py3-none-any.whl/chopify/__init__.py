def chopify(word: str) -> str:
    """
    Converts a word to its "chopped" version by replacing the initial consonant(s) with "ch".

    Examples:
    - poop -> choop
    - unc -> chunc
    - hamster -> chamster

    Parameters:
        word (str): The word to chopify

    Returns:
        str: The chopified word
    """
    if not word:
        return word

    word = word.lower()
    vowels = "aeiou"

    if word[0] in vowels:
        return "ch" + word

    for i, char in enumerate(word):
        if char in vowels:
            return "ch" + word[i:]

    return "ch" + word
