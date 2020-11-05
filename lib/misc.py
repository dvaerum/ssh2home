# ex: set tabstop=8 softtabstop=0 expandtab shiftwidth=4 smarttab:

import re


def insert_text_block(path: str, insert_text: str, identity: str = "TEXT BLOCK"):
    _beginning = f"### BEGINNING OF {identity} ###"
    _ending    = f"### ENDING OF {identity} ###"
    beginning = re.escape(_beginning)
    ending    = re.escape(_ending)

    with open(path, 'r') as f:
        context = f.read()

    match_beginning = re.search(f"^{beginning}$", context, re.MULTILINE)
    match_ending    = re.search(f"^{ending}$", context, re.MULTILINE)

    update = False
    if match_beginning and match_ending:
        begin_first, begin_last = match_beginning.span()
        end_first, end_last     = match_ending.span()

        if begin_first < end_first:
            update = True

    if update:
        before = context[0:begin_last]
        after  = context[end_first:]
        new_context = f"{before}\n{insert_text}\n{after}"
    else:
        new_context = f"{_beginning}\n{insert_text}\n{_ending}\n{context}"

    if context != new_context:
        with open(path, 'w') as f:
            f.write(new_context)


