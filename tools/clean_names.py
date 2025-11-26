def clean_name(line):
    line = line.strip()
    parts = line.split()
    parts = [p.capitalize() for p in parts]
    return " ".join(parts)
