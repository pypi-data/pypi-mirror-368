from typing import Any, Optional, Type

from pydantic import BaseModel

from wexample_helpers.helpers.string import string_to_kebab_case


class Option(BaseModel):
    name: str
    kebab_name: Optional[str] = None
    short_name: Optional[str] = None
    type: Type
    description: Optional[str] = None
    required: bool = False
    default: Any = None
    is_flag: bool = False
    # The computed value using input argument or default value.
    value: Any = None

    def __init__(self, **kwargs):
        from wexample_wex_core.helpers.option import option_build_short_name

        super().__init__(**kwargs)

        self.kebab_name = string_to_kebab_case(self.name)
        self.short_name = option_build_short_name(self.name)
