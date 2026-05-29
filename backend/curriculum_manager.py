import json
from pathlib import Path
from typing import List


def get_repo_root() -> Path:
    """Return the repository root so curriculum files can be stored there."""
    return Path(__file__).resolve().parents[1]


def get_curriculum_root() -> Path:
    """Return the curriculum directory path."""
    return get_repo_root() / "curriculum"


def available_levels() -> List[str]:
    """Return the supported student learning levels."""
    return ["beginner", "intermediate", "advanced"]


def get_level_dir(level: str) -> Path:
    """Return the directory path for a specific curriculum level."""
    level_slug = level.lower()
    return get_curriculum_root() / level_slug


def ensure_curriculum() -> None:
    """Create curriculum folders and placeholder files if they do not exist."""
    root = get_curriculum_root()
    root.mkdir(parents=True, exist_ok=True)

    sample_data = {
        "beginner": {
            "devices": [
                {"name": "LED", "description": "A simple light you can turn on and off."},
                {"name": "Button", "description": "A push button for input and interaction."}
            ],
            "prompts": [
                "Build a blinking light circuit that turns on and off.",
                "Connect a button and make the LED light when the button is pressed."
            ]
        },
        "intermediate": {
            "devices": [
                {"name": "Buzzer", "description": "A sound device for audible feedback."},
                {"name": "Potentiometer", "description": "A knob you can read to adjust values."}
            ],
            "prompts": [
                "Create a volume controller using a potentiometer and buzzer.",
                "Make a two-button game that responds differently to each press."
            ]
        },
        "advanced": {
            "devices": [
                {"name": "OLED Display", "description": "A small screen to show text or graphics."},
                {"name": "Distance Sensor", "description": "A sensor that measures how far objects are."}
            ],
            "prompts": [
                "Build a mini dashboard that displays sensor readings on the screen.",
                "Make a proximity alert that changes behavior when objects move near the sensor."
            ]
        }
    }

    for level, data in sample_data.items():
        level_dir = root / level
        level_dir.mkdir(parents=True, exist_ok=True)
        devices_path = level_dir / "devices.json"
        prompts_path = level_dir / "prompts.json"

        if not devices_path.exists():
            devices_path.write_text(json.dumps(data["devices"], indent=2))

        if not prompts_path.exists():
            prompts_path.write_text(json.dumps(data["prompts"], indent=2))


def load_json_list(path: Path):
    """Load a JSON file that contains a list and return it."""
    if not path.exists():
        return []
    return json.loads(path.read_text())


def load_level_devices(level: str) -> List[dict]:
    """Return the device definitions for a given student level."""
    level_dir = get_level_dir(level)
    return load_json_list(level_dir / "devices.json")


def load_level_prompts(level: str) -> List[str]:
    """Return the suggested project prompts for a given student level."""
    level_dir = get_level_dir(level)
    return load_json_list(level_dir / "prompts.json")
