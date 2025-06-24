"""Parameter validation functions for VFX operations."""

from pathlib import Path


def validate_range(
    value: float,
    min_val: float,
    max_val: float,
    name: str,
) -> None:
    """Validate that a parameter is within the specified range."""
    if not min_val <= value <= max_val:
        raise ValueError(f"{name} must be between {min_val} and {max_val}")


def validate_file_path(file_path: str) -> Path:
    """Validate that a file path exists and is readable."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    return path


def validate_output_path(
    output_path: str,
) -> Path:
    """Validate that an output path is writable."""
    path = Path(output_path)
    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def validate_video_paths(video_paths: list[str], min_count: int = 1) -> list[Path]:
    """Validate a list of video file paths."""
    if len(video_paths) < min_count:
        raise ValueError(f"At least {min_count} video file(s) required")

    validated_paths = []
    for path_str in video_paths:
        path = validate_file_path(path_str)
        validated_paths.append(path)

    return validated_paths


def validate_transition_type(
    transition_type: str,
) -> str:
    """Validate transition type parameter."""
    valid_transitions = [
        "fade",
        "wipe_left",
        "wipe_right",
        "wipe_up",
        "wipe_down",
        "slide_left",
        "slide_right",
        "dissolve",
        "crossfade",
    ]
    if transition_type not in valid_transitions:
        raise ValueError(
            f"Transition type must be one of: {', '.join(valid_transitions)}"
        )
    return transition_type


def validate_filter_name(filter_name: str) -> str:
    """Validate video filter name."""
    common_filters = [
        "blur",
        "sharpen",
        "brightness",
        "contrast",
        "saturation",
        "vintage",
        "sepia",
        "grayscale",
        "hflip",
    ]
    # Allow scale filters with parameters
    if filter_name.startswith("scale="):
        return filter_name
    if filter_name not in common_filters:
        raise ValueError(
            f"Filter must be one of: {', '.join(common_filters)} or scale=WIDTHxHEIGHT"
        )
    return filter_name


def validate_animation_type(
    animation_type: str,
) -> str:
    """Validate text animation type."""
    valid_animations = [
        "fade_in",
        "slide_in_left",
        "slide_in_right",
        "slide_in_top",
        "slide_in_bottom",
        "zoom_in",
        "rotate_in",
        "typewriter",
    ]
    if animation_type not in valid_animations:
        raise ValueError(
            f"Animation type must be one of: {', '.join(valid_animations)}"
        )
    return animation_type
