# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
from __future__ import absolute_import, division, unicode_literals
    " ": lambda c: (c[0] + 1, c[1] + 1),
    "\\": lambda c: c,  # FOR "\ no newline at end of file
    "+": lambda c: (c[0] + 1, c[1]),
    "-": lambda c: (c[0], c[1] + 1),
no_change = MOVE[" "]
        old_file_path = old_file_header[
            1:
        ]  # eg old_file_header == "a/testing/marionette/harness/marionette_harness/tests/unit/unit-tests.ini"
        new_file_path = new_file_header[
            5:
        ]  # eg new_file_header == "+++ b/tests/resources/example_file.py"
            old_start, old_length, new_start, new_length = HUNK_HEADER.match(
                line_diffs[0]
            ).groups()
            next_c = max(0, int(new_start) - 1), max(0, int(old_start) - 1)
                    line.startswith("new file mode")
                    or line.startswith("deleted file mode")
                    or line.startswith("index ")
                    or line.startswith("diff --git")
                if d == "+":
                    changes.append(
                        {
                            "new": {
                                "line": int(c[0]),
                                "content": strings.limit(line[1:], MAX_CONTENT_LENGTH),
                            }
                        }
                    )
                elif d == "-":
                    changes.append(
                        {
                            "old": {
                                "line": int(c[1]),
                                "content": strings.limit(line[1:], MAX_CONTENT_LENGTH),
                            }
                        }
                    )
        output.append(
            {"new": {"name": new_file_path}, "old": {"name": old_file_path}, "changes": changes}
        )
        old_file_path = old_file_header[
            1:
        ]  # eg old_file_header == "a/testing/marionette/harness/marionette_harness/tests/unit/unit-tests.ini"
        new_file_path = new_file_header[
            5:
        ]  # eg new_file_header == "+++ b/tests/resources/example_file.py"
            old_start, old_length, new_start, new_length = HUNK_HEADER.match(
                line_diffs[0]
            ).groups()
            next_c = max(0, int(new_start) - 1), max(0, int(old_start) - 1)
                    line.startswith("new file mode")
                    or line.startswith("deleted file mode")
                    or line.startswith("index ")
                    or line.startswith("diff --git")
                if d != " ":
        output.append(
            {"new": {"name": new_file_path}, "old": {"name": old_file_path}, "changes": changes}
        )
    constraint=True,  # TODO: remove when constrain=None is the same as True