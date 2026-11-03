ALLOWED: dict[str, set[str]] = {
    "idle": {"running", "maintenance", "error", "off"},
    "running": {"idle", "error"},
    "off": {"idle", "error"},
    "error": {"idle", "maintenance"},
    "maintenance": {"idle", "error"},
}

COMMANDS: dict[str, list[str]] = {
    "idle": ["start_pump"],
    "running": ["stop_pump"],
    "off": ["turn_on"],
    "error": ["reset"],
    "maintenance": ["finish_maintenance"],
}


class IllegalTransitionError(ValueError):
    pass
