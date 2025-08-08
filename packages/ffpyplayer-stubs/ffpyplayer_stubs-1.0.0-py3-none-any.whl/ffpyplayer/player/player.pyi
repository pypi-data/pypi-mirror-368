import typing

class MediaPlayer(object):
    def __init__(
        self,
        filename: str,
        callback=None,
        loglevel: str = "trace",
        ff_opts: dict = {},
        thread_lib: str = "SDL",
        audio_sink: str = "SDL",
        lib_opts: dict = {},
        **kargs
    ):
        pass

    def get_frame(self, force_refresh=False, show=True, *args) -> typing.Any:
        pass

    def close_player(self) -> None:
        pass

    def get_metadata(self) -> dict:
        pass

    def select_video_filter(self, index: int = 0):
        pass

    def set_volume(self, volume: int):
        pass

    def get_volume(self) -> int:
        pass

    def set_mute(self, state: bool):
        pass

    def get_mute(self) -> bool:
        pass

    def toggle_pause(self):
        pass

    def set_pause(self, state: bool):
        pass

    def get_pause(self) -> bool:
        pass

    def get_pts(self) -> int:
        pass

    def set_size(self, width: int = -1, height: int = -1):
        pass

    def get_output_pix_fmt(self) -> str:
        pass

    def set_output_pix_fmt(self, pix_fmt: str):
        pass

    def request_channel(
        self, stream_type: str, action: str = "cycle", requested_stream: int = -1
    ):
        pass

    def get_programs(self) -> list:
        pass

    def request_program(self, requested_program: int):
        pass

    def seek(
        self,
        pts: int,
        relative: bool = True,
        seek_by_bytes: str = "auto",
        accurate: bool = True,
    ):
        pass

    def seek_to_chapter(self, increment: int, accurate: bool = True):
        pass

    def _seek(self, pts: int, relative: int, seek_by_bytes: int, accurate: int):
        pass
