"""In-memory settings shared across screens."""

from dataclasses import dataclass


@dataclass
class AppSettings:
    background_mode: bool = False
