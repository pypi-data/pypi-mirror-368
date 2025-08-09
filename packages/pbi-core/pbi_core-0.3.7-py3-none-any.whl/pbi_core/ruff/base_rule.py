import enum
from collections.abc import Iterable
from typing import Any

from colorama import Fore, Style
from pbi_parsers.dax.utils import Context


class Fixable(enum.Enum):
    NOT_FIXABLE = "Not Automatically Fixable"
    UNSAFE_FIXABLE = "Unsafe Fixable"
    SAFE_FIXABLE = "Safe Fixable"


class RuleGroup:
    name: str
    rules: Iterable[type["BaseRule"]]


class RuleResult:
    rule: type["BaseRule"]
    message: str
    context: Context | None = None
    context_vars: dict[str, Any]
    trace: tuple[str | int, ...] | None

    def __init__(
        self,
        rule: type["BaseRule"],
        message: str,
        context: Context | None = None,
        context_vars: dict[str, Any] | None = None,
        trace: tuple[str | int, ...] | None = None,
    ) -> None:
        self.rule = rule
        self.message = message
        self.context = context
        self.context_vars = context_vars or {}
        self.trace = trace

    def render_html(self) -> str:
        """Render the rule result as an HTML string."""
        context = ""
        if self.context:
            context = f"<div>{self.context}</div>"

        return f"""
<div class="rule-result">
    <span class="rule-id">{self.rule.id} - {self.rule.name}: </span>
    <p class="rule-message">{self.message}</p>
    {context}
</div>
        """

    def render_console(self) -> str:
        context = ""
        if self.context:
            context = f"""
            -----
            {self.context}
            -----"""
        return f"""
{Fore.RED}{self.rule.id}{Style.RESET_ALL} - {self.rule.name}: {self.message}
{context}
Trace: {self.trace_string()}
"""

    def __repr__(self) -> str:
        return self.render_console()

    def fix(self) -> None:
        """Attempt to fix the issue described by this rule result."""
        msg = "Subclasses may implement the fix method."
        raise NotImplementedError(msg)

    def trace_string(self) -> str:
        """Return a string representation of the trace."""
        if self.trace is None:
            return ""
        return ".".join(str(t) for t in self.trace)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of the RuleResult."""
        return {
            "rule": self.rule.to_dict(),
            "message": self.message,
            "context": self.context.to_dict() if self.context else None,
            "context_vars": self.context_vars,
            "trace": self.trace_string(),
        }


class BaseRule:
    id: str
    name: str
    description: str
    fixable: Fixable = Fixable.NOT_FIXABLE

    @classmethod
    def check(cls, *args: Any, **kwargs: Any) -> list[RuleResult]:
        """Check the provided arguments and return a list of RuleResults."""
        msg = "Subclasses must implement the check method."
        raise NotImplementedError(msg)

    @classmethod
    def to_dict(cls) -> dict[str, str]:
        """Return a dictionary representation of the rule."""
        return {
            "id": cls.id,
            "name": cls.name,
            "description": cls.description,
        }
