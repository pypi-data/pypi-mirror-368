from typing import Any, Dict, Mapping

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kognitos.bdk.cli.config import configs

from .authentication import (build_authentication_description,
                             build_authentications, prompt_authentications)
from .books import build_books
from .common import (bdkctl_choose, build_simple_message,
                     get_from_context_or_prompt, prompt_for_value)
from .configs import build_book_configs
from .describe import build_book_description
from .environment import build_environment, build_environment_display
from .procedure import (build_procedure, build_procedure_error,
                        build_procedure_result, prompt_inputs,
                        prompt_procedure_data)

console = Console()
