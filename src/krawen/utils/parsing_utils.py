def parse_urls_from_tag_attr(key: str, value: str) -> list[str]:
    if isinstance(value, list):
        return value
    else:
        if key.lower() == 'srcset':
            return [part.split()[0] for part in value.split(", ")]
        else:
            return [value]