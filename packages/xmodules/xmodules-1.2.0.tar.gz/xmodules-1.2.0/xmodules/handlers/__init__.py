from .help import register_help_handler
from .save import register_save_handler
from .type import register_type_handler
from .countdown import register_countdown_handler
from .flood import register_flood_handler
from .calculator import register_calculator_handler
from .mention import register_mention_handler
from .clear import register_clear_handler
from .online import register_online_handler

handlers = [
    register_save_handler,
    register_help_handler,
    register_type_handler,
    register_countdown_handler,
    register_flood_handler,
    register_calculator_handler,
    register_mention_handler,
    register_clear_handler,
    register_online_handler,
]
