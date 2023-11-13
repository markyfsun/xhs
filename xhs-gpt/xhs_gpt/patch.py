from typing import Union, Dict, Tuple


def monkey_patch():
    """Allow multi-input tools."""
    import langchain.tools.base

    def new_to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        """Convert tool input to pydantic model."""
        args, kwargs = super(langchain.tools.base.Tool, self)._to_args_and_kwargs(tool_input)
        # Remove backwards compatibility.
        all_args = list(args) + list(kwargs.values())
        return tuple(all_args), {}

    # Monkey patch the Tool class
    langchain.tools.base.Tool._to_args_and_kwargs = new_to_args_and_kwargs
