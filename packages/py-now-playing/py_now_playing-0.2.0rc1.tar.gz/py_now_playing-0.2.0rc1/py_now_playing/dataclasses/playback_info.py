"""Playback Information Module
This module defines the PlaybackInfo class, which holds information about the current media playback session.
It includes details such as playback type, status, rate, auto-repeat mode, and shuffle state."""
from dataclasses import dataclass
import enum
from .enabled_controls import EnabledControls


class MediaPlaybackStatus(enum.IntEnum):
  """Playback status of the media"""
  CLOSED = 0
  OPENED = 1
  CHANGING = 2
  STOPPED = 3
  PLAYING = 4
  PAUSED = 5

class MediaPlaybackType(enum.IntEnum):
  """Type of media playback."""
  UNKNOWN = 0
  MUSIC = 1
  VIDEO = 2
  IMAGE = 3

class MediaPlaybackAutoRepeatMode(enum.IntEnum):
  """Auto-repeat enum mode for media playback."""
  NONE = 0
  TRACK = 1
  LIST = 2
  

@dataclass
class PlaybackInfo:
  """Playback information for the current media session.
  This class hold details such as the playback type, status, rate, auto-repeat mode, and shuffle state.
  Attributes:
    playback_type: Type of media playback (e.g., music, video, image)
    playback_status: Current status of the media playback
    playback_rate: Rate at which the media is being played (1.0 for normal speed)
    auto_repeat_mode: Auto-repeat mode for the media playback
    is_shuffle_active: Whether shuffle mode is active
  """
  playback_type: MediaPlaybackType | None = None
  playback_status: MediaPlaybackStatus | None = None
  playback_rate: float | None = None
  auto_repeat_mode: MediaPlaybackAutoRepeatMode | None = None
  is_shuffle_active: bool | None = None
  controls: EnabledControls | None = None
