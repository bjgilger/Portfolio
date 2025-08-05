def regex_match(r: str, s: str) -> bool:
    """Matches a single character `r` from a regex to a single character `s` from a string."""
    if r == '.':
        return True
    return r == s


def regex_match_full(regex: str, string: str) -> bool:
    if not regex:
        return not string

    if regex[0] == '\\' and len(regex) >= 2:
        # Handle escaped character as literal
        if string and regex[1] == string[0]:
            return regex_match_full(regex[2:], string[1:])
        return False

    if len(regex) > 1 and regex[1] in '?*+':
        char, meta = regex[0], regex[1]

        if meta in '?*' and regex_match_full(regex[2:], string):
            return True

        if string and regex_match(char, string[0]):
            if regex_match_full(regex[2:], string[1:]):
                return True
            if meta in '*+' and regex_match_full(regex, string[1:]):
                return True

        return False

    if string and regex_match(regex[0], string[0]):
        return regex_match_full(regex[1:], string[1:])

    return False


def regex_match_prefix(regex: str, string: str) -> bool:
    if not regex:
        return True

    if regex[0] == '\\' and len(regex) >= 2:
        if string and regex[1] == string[0]:
            return regex_match_prefix(regex[2:], string[1:])
        return False

    if len(regex) > 1 and regex[1] in '?*+':
        char, meta = regex[0], regex[1]

        if meta in '?*' and regex_match_prefix(regex[2:], string):
            return True

        if string and regex_match(char, string[0]):
            if regex_match_prefix(regex[2:], string[1:]):
                return True
            if meta in '*+' and regex_match_prefix(regex, string[1:]):
                return True

        return False

    if string and regex_match(regex[0], string[0]):
        return regex_match_prefix(regex[1:], string[1:])

    return False


def regex_search(regex: str, string: str) -> bool:
    if not regex:
        return True

    if regex.startswith('^') and regex.endswith('$'):
        return regex_match_full(regex[1:-1], string)

    if regex.startswith('^'):
        return regex_match_prefix(regex[1:], string)

    if regex.endswith('$'):
        core_regex = regex[:-1]
        for i in range(len(string) + 1):
            if regex_match_full(core_regex, string[i:]):
                return True
        return False

    for i in range(len(string) + 1):
        if regex_match_prefix(regex, string[i:]):
            return True
    return False


def main():
    try:
        regex, text = input().split("|")
        result = regex_search(regex, text)
        print(str(result))
    except (ValueError, IndexError):
        print(str(False))


if __name__ == '__main__':
    main()
