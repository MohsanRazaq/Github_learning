"""
Contribution advice module.
Generates context-aware contribution suggestions based on
multiple repository signals, not just star count.
"""


def get_contribution_advice(stars, forks=0, open_issues=0,
                            has_wiki=False, license_type="None",
                            topics=None):
    """
    Generate contribution advice based on multiple repo signals.
    Returns a list of advice strings.
    """
    advice = []

    # --- Beginner-friendliness assessment ---
    if stars < 50:
        advice.append(
            " Small, beginner-friendly project — perfect for your first contribution!"
        )
        advice.append(
            " Read the README carefully and try fixing typos or improving docs."
        )
    elif stars < 500:
        advice.append(
            " Mid-sized project — look for 'good first issue' labels."
        )
        advice.append(
            " Check open issues for bug reports you can help reproduce or fix."
        )
    elif stars < 5000:
        advice.append(
            " Popular project — contributions here carry serious weight!"
        )
        advice.append(
            " Study the CONTRIBUTING.md before submitting anything."
        )
    else:
        advice.append(
            " Major open-source project — follow their contribution guide strictly."
        )
        advice.append(
            " Search for 'help wanted' or 'good first issue' labels to get started."
        )

    # --- Open issues guidance ---
    if open_issues > 100:
        advice.append(
            f" This repo has {open_issues} open issues — plenty of opportunities!"
        )
    elif open_issues > 10:
        advice.append(
            f" There are {open_issues} open issues to explore."
        )
    else:
        advice.append(
            " Few open issues — consider proposing new features or improvements."
        )

    # --- License check ---
    if license_type and license_type not in ("None", "NOASSERTION"):
        advice.append(
            f" Licensed under {license_type} — you're free to contribute!"
        )
    else:
        advice.append(
            " No clear license detected — check with the maintainer before contributing."
        )

    # --- Wiki ---
    if has_wiki:
        advice.append(
            " This project has a wiki — read it for deeper context."
        )

    # --- Fork strategy ---
    if forks > 500:
        advice.append(
            "🍴 Highly forked — fork the repo, create a feature branch, and submit a PR."
        )

    # --- Topics-based tips ---
    if topics:
        topic_set = set(t.lower() for t in topics)
        if "hacktoberfest" in topic_set:
            advice.append(
                " Hacktoberfest project! Great for earning event contributions."
            )
        if "machine-learning" in topic_set or "ai" in topic_set:
            advice.append(
                " ML/AI project — consider contributing datasets, notebooks, or documentation."
            )
        if "web" in topic_set or "frontend" in topic_set:
            advice.append(
                "Web project — look for UI/UX improvements or accessibility fixes."
            )

    return advice