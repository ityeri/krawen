from yarl import URL


def to_absolute_url(origin_url: URL, target_url: URL) -> URL:
    if target_url.is_absolute():
        return target_url
    else:
        origin_url = origin_url.origin()
        return origin_url.join(target_url)


def parse_elements_from_tag_attr(key: str, value: str) -> list[str]:
    if isinstance(value, list):
        return value
    else:
        if key.lower() == 'srcset':
            return [part.strip() for part in value.split(",")]
        else:
            return [value]

def is_valid_url(url: URL) -> bool:
    if url.port is None:
        return False
    return True


__all__ = [
    'to_absolute_url',
    'parse_elements_from_tag_attr'
]