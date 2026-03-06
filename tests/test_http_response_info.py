from krawen import HTTPResponseInfo

info = HTTPResponseInfo(
    http_version='1.0',
    status_code=400,
    reason='OK',
    headers=[
        ('1', b'a'),
        ('2', b'b'),
        ('2', b'bb'),
        ('3', b'c'),
        ('3', b'd'),
        ('3', b'e'),
    ]
)

print(info.get_headers('2'))