import json


def parse_aws_jsons(content: str) -> list:
    """Parse AWS JSON content without delimiters."""
    decoder = json.JSONDecoder()
    content_length = len(content)
    decode_index = 0
    objects = []

    while decode_index < content_length:
        try:
            obj, decode_index = decoder.raw_decode(content, decode_index)
            objects.append(obj)
        except json.JSONDecodeError:
            decode_index += 1

    return objects
