"""Type stubs for ffmpeg-python library."""

from typing import TypedDict, Literal, Union, overload
from collections.abc import Mapping, Sequence

class StreamSpec(TypedDict, total=False):
    """Type definition for a stream specification."""
    index: int
    codec_type: Literal["video", "audio", "subtitle", "data"]
    codec_name: str
    codec_long_name: str
    profile: str
    codec_time_base: str
    codec_tag_string: str
    codec_tag: str
    width: int
    height: int
    coded_width: int
    coded_height: int
    closed_captions: int
    has_b_frames: int
    sample_aspect_ratio: str
    display_aspect_ratio: str
    pix_fmt: str
    level: int
    color_range: str
    color_space: str
    color_transfer: str
    color_primaries: str
    chroma_location: str
    field_order: str
    timecode: str
    refs: int
    is_avc: str
    nal_length_size: str
    r_frame_rate: str
    avg_frame_rate: str
    time_base: str
    start_pts: int
    start_time: str
    duration_ts: int
    duration: str
    bit_rate: str
    max_bit_rate: str
    bits_per_raw_sample: int
    nb_frames: str
    nb_read_frames: str
    nb_read_packets: str
    sample_rate: str
    channels: int
    channel_layout: str
    bits_per_sample: int
    disposition: Mapping[str, int]
    tags: Mapping[str, str]

class FormatSpec(TypedDict, total=False):
    """Type definition for format specification."""
    filename: str
    nb_streams: int
    nb_programs: int
    format_name: str
    format_long_name: str
    start_time: str
    duration: str
    size: str
    bit_rate: str
    probe_score: int
    tags: Mapping[str, str]

class ProbeResult(TypedDict):
    """Type definition for ffprobe result."""
    streams: Sequence[StreamSpec]
    format: FormatSpec
    chapters: Sequence[Mapping[str, Union[str, int]]]

class Stream:
    """Represents an ffmpeg stream object."""
    def __init__(self) -> None: ...
    
    def __getitem__(self, key: str) -> Stream: ...
    
    def filter(self, filter_name: str, *args: str, **kwargs: Union[str, int, float]) -> Stream: ...
    def trim(self, start: Union[int, float, str] | None = None, 
             end: Union[int, float, str] | None = None, 
             duration: Union[int, float, str] | None = None) -> Stream: ...
    def setpts(self, expr: str) -> Stream: ...
    def split(self) -> tuple[Stream, ...]: ...
    def overlay(self, overlay: Stream, x: Union[int, str] = 0, 
                y: Union[int, str] = 0, **kwargs: Union[str, int, float]) -> Stream: ...
    def hflip(self) -> Stream: ...
    def vflip(self) -> Stream: ...
    def crop(self, width: int, height: int, x: int = 0, y: int = 0) -> Stream: ...
    def scale(self, width: Union[int, str], height: Union[int, str], **kwargs: Union[str, int]) -> Stream: ...
    def concat(self, *streams: Stream, v: int = 1, a: int = 1, n: int | None = None) -> Stream: ...
    def filter_multi_output(self, filter_name: str, *args: str, **kwargs: Union[str, int, float]) -> tuple[Stream, ...]: ...

class Error(Exception):
    """FFmpeg error with stderr and stdout information."""
    cmd: str
    stderr: bytes | None
    stdout: bytes | None
    
    def __init__(self, cmd: str, stdout: bytes | None = None, stderr: bytes | None = None) -> None: ...

@overload
def input(filename: str, **kwargs: Union[str, int, float]) -> Stream: ...

@overload
def input(*args: Union[str, Stream], **kwargs: Union[str, int, float]) -> Stream: ...

def filter(stream_spec: Union[Stream, Sequence[Stream]], filter_name: str, 
           *args: str, **kwargs: Union[str, int, float]) -> Stream: ...

def filter_multi_output(stream_spec: Union[Stream, Sequence[Stream]], filter_name: str,
                       *args: str, **kwargs: Union[str, int, float]) -> tuple[Stream, ...]: ...

def concat(*streams: Stream, v: int = 1, a: int = 1, n: int | None = None) -> Stream: ...

def output(*streams_and_filename: Union[Stream, str], **kwargs: Union[str, int, float]) -> Stream: ...

def run(stream_spec: Stream, 
        cmd: str | Sequence[str] | None = None,
        capture_stdout: bool = False,
        capture_stderr: bool = False,
        input: bytes | None = None,
        quiet: bool = False,
        overwrite_output: bool = False) -> tuple[bytes, bytes]: ...

def run_async(stream_spec: Stream, 
              cmd: str | Sequence[str] | None = None,
              pipe_stdin: bool = False,
              pipe_stdout: bool = False,
              pipe_stderr: bool = False,
              quiet: bool = False,
              overwrite_output: bool = False) -> None: ...

def compile(stream_spec: Stream, 
            cmd: str | Sequence[str] = "ffmpeg",
            overwrite_output: bool = False) -> Sequence[str]: ...

def probe(filename: str, cmd: str = "ffprobe", **kwargs: str) -> ProbeResult: ...

def get_args(stream_spec: Stream) -> Sequence[str]: ...

# Re-export commonly used items
__all__ = [
    "Error",
    "Stream", 
    "input",
    "output",
    "filter",
    "filter_multi_output",
    "concat",
    "run",
    "run_async",
    "compile",
    "probe",
    "get_args",
]