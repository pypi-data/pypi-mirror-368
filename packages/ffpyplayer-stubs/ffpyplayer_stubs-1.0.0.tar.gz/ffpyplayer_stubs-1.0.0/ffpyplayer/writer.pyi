from pic import Image

class MediaWriter(object):
    def __init__(
        self,
        filename: str,
        streams,
        fmt: str = "",
        lib_opts: dict = {},
        metadata: dict = {},
        overwrite: bool = False,
        **kwargs
    ):
        pass

    def close(self):
        pass

    def write_frame(self, img: Image, pts: int, stream: int = 0):
        pass

    def get_configuration(self) -> list:
        pass

    def clean_up(self):
        pass
