# Learning Resources utility
# Maps programming languages to curated learning resources (tutorials, docs, courses).
# This module can be extended with more entries or fetched from an external API.

from typing import List, Tuple

_RESOURCES = {
    "Python": [
        ("Official Python Docs", "https://docs.python.org/3/"),
        ("Real Python Tutorials", "https://realpython.com/"),
        ("Python Crash Course (book)", "https://nostarch.com/pythoncrashcourse2e"),
    ],
    "JavaScript": [
        ("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"),
        ("Eloquent JavaScript", "https://eloquentjavascript.net/"),
        ("JavaScript.info", "https://javascript.info/"),
    ],
    "Java": [
        ("Official Java Documentation", "https://docs.oracle.com/en/java/"),
        ("Codecademy Java Course", "https://www.codecademy.com/learn/learn-java"),
    ],
    "C++": [
        ("C++ Reference", "https://en.cppreference.com/w/"),
        ("LearnCpp.com", "https://www.learncpp.com/"),
    ],
    "Go": [
        ("Go Tour", "https://tour.golang.org/"),
        ("Effective Go", "https://golang.org/doc/effective_go.html"),
    ],
    "Rust": [
        ("The Rust Book", "https://doc.rust-lang.org/book/"),
        ("Rustlings Exercises", "https://github.com/rust-lang/rustlings"),
    ],
    # Add more languages as needed
}

def get_resources(language: str) -> List[Tuple[str, str]]:
    """Return a list of (title, URL) tuples for the given language.
    If the language is not recognized, returns an empty list.
    """
    return _RESOURCES.get(language, [])
