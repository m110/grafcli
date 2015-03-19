ROOT_PATH = "/"
SEPARATOR = "/"


def format_path(current_path, path):
    path = path.strip()

    absolute = path.startswith(ROOT_PATH)
    if not absolute:
        path = SEPARATOR.join((current_path, path))

    parts = [part for part in path.split(SEPARATOR)
             if part]

    result = []
    for part in parts:
        if part == ".":
            continue
        elif part == "..":
            # Up one level
            result = result[:-1]
        else:
            result.append(part)

    new_path = ROOT_PATH + SEPARATOR.join(result)

    return new_path
