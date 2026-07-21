@disagreement-and-calibration.md
@i-have-adhd.md

# Code comments

- Avoid comments as much as possible
- When necessary, comments should only state the "why" of the code, never what it is or what it is doing (the "what").
- If you feel the need to write a comment, try renaming variables with more descriptive names and/or extracting parts of the code to functions with descriptive names.
- If even so the "why" is not clear, you may write a terse, direct comment explaining it.


# Naming

- Function names state the intent with standard verbs: if the functions create an object, name it `create_...`. If it filters, `filter_...` and so on.
    - List of verbs: get, create, list, delete, filter, parse;

# Misc

Be terse in commit messages.
When writing guides or plan docs, write them to .claude/plans/{org}/{repo}/ (org: posthog or personal).
When I tell you to test it yourself or test in browser, you should use Claude in Chrome MCP to open the app in the browser.
