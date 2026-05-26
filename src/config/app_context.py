from dataclasses import dataclass

@dataclass
class AppContext:
    page: any
    data_manager: any
    auth_manager: any
    screen_manager: any
    theme: dict