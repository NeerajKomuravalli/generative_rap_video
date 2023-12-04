def split_srt_chunk(chunk):
    # Split the chunk into lines
    lines = chunk.split("\n")

    # NOTE: May be this is a not a great check but works for a POC. Come back to it later when it's needed
    if len(lines) < 3:
        raise Exception("Corrupted file")

    # The first line is the index
    index = lines[0]

    # The second line is the time range
    time_range = lines[1]

    # The remaining lines are the subtitle text
    subtitle_text = "\n".join(lines[2:])

    return index, time_range, subtitle_text
