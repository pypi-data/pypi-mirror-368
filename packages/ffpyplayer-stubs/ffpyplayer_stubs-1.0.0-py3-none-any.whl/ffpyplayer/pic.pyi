import typing

def get_image_size(pix_fmt: str, width: int, height: int):
    return typing.Tuple[int]

class SWScale(object):
    def __init__(
        self,
        iw: int,
        ih: int,
        ifmt: str,
        ow: int = -1,
        oh: int = -1,
        ofmt: str = "",
        **kargs
    ):
        pass

    def scale(self, src: Image, dst: Image = None, _flip: int = False) -> Image:
        pass

def raise_exec(ecls: object):
    pass

class Image(object):
    def __init__(
        self,
        plane_buffers: list = [],
        pix_fmt: str = "",
        size: tuple = (),
        linesize: list = [],
        **kwargs
    ):
        pass

    def is_ref(self) -> bool:
        pass

    def is_key_frame(self) -> bool:
        pass

    def get_linesizes(self, keep_align: bool = False) -> typing.Tuple[int]:
        pass

    def get_size(self) -> typing.Tuple[int]:
        pass

    def get_pixel_format(self) -> str:
        pass

    def get_buffer_size(self, keep_align: bool = False) -> typing.Tuple[int]:
        pass

    def get_required_buffers(self) -> typing.Tuple[bool]:
        pass

    def to_bytearray(self, keep_align: bool = False) -> typing.Tuple[bytearray]:
        pass

    def to_memoryview(self, keep_align: bool = False) -> typing.Tuple[typing.Iterable]:
        pass

class ImageLoader(object):
    def __init__(self, filename: str, **kwargs):
        pass

    def next_frame(self) -> typing.Tuple[Image]:
        pass

    def eof_frame(self) -> typing.Tuple[Image, int]:
        pass
