from typing import Optional

from wexample_helpers.classes.mixin.has_class_dependencies import HasClassDependencies
from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import HasSnakeShortClassNameClassMixin
from wexample_helpers.classes.mixin.has_two_steps_init import HasTwoStepInit
from wexample_prompt.mixins.with_prompt_context import WithPromptContext


class ServiceMixin(
    WithPromptContext,
    HasSnakeShortClassNameClassMixin,
    HasTwoStepInit,
    HasClassDependencies
):
    @classmethod
    def get_class_name_suffix(cls) -> Optional[str]:
        return 'Service'
