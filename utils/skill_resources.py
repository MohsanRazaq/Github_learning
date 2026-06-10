# Skill Resources utility
# Maps skill names to curated resource links (books, courses, tutorials).
# This can be extended or sourced from an external service.

from typing import List, Tuple

_SKILL_RESOURCES = {
    "AI Engineer": [
        ("Deep Learning Book", "https://www.deeplearningbook.org/"),
        ("Fast.ai Course", "https://www.fast.ai/"),
        ("Stanford CS229", "http://cs229.stanford.edu/"),
    ],
    "Data Scientist": [
        ("Python Data Science Handbook", "https://jakevdp.github.io/PythonDataScienceHandbook/"),
        ("Kaggle Courses", "https://www.kaggle.com/learn"),
        ("Statistical Learning", "https://web.stanford.edu/~hastie/ElemStatLearn/"),
    ],
    "Web Developer": [
        ("MDN Web Docs", "https://developer.mozilla.org/"),
        ("FreeCodeCamp Curriculum", "https://www.freecodecamp.org/learn"),
        ("The Odin Project", "https://www.theodinproject.com/"),
    ],
    # Add more skills as needed
}

def get_skill_resources(skill: str) -> List[Tuple[str, str]]:
    """Return a list of (title, URL) tuples for the given skill.
    Matching is case‑insensitive; unknown skills return an empty list.
    """
    return _SKILL_RESOURCES.get(skill.title(), [])
