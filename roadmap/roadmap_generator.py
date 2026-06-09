def get_roadmap(language):

    roadmaps = {
        "Python": [
            "Learn Python Basics",
            "Learn Object Oriented Programming",
            "Learn Git & GitHub",
            "Study Repository Structure"
        ],

        "JavaScript": [
            "Learn JavaScript Basics",
            "Learn ES6",
            "Learn HTML/CSS",
            "Study Repository Structure"
        ],

        "Java": [
            "Learn Java Fundamentals",
            "Learn OOP",
            "Learn Maven/Gradle",
            "Study Repository Structure"
        ],

        "C++": [
            "Learn C++ Basics",
            "Learn STL",
            "Learn OOP",
            "Study Repository Structure"
        ]
    }

    return roadmaps.get(
        language,
        [
            "Learn Basics",
            "Learn Git & GitHub",
            "Study Repository Structure"
        ]
    )


def get_difficulty(stars):

    if stars < 50:
        return "Beginner"

    elif stars < 500:
        return "Intermediate"

    return "Advanced"