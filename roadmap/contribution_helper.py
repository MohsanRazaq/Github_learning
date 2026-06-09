def get_contribution_advice(stars):

    if stars < 50:
        return (
            "Beginner-friendly project. "
            "Read the README and try small fixes."
        )

    elif stars < 500:
        return (
            "Look for documentation issues, "
            "bug fixes, and beginner tasks."
        )

    else:
        return (
            "Large project. Search for "
            "'good first issue' or "
            "'help wanted' labels."
        )