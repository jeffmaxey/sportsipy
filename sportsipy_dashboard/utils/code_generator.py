"""Auto-generate Python code from user data exploration actions."""
import logging
from dataclasses import asdict, dataclass, field

import nbformat

logger = logging.getLogger(__name__)

SPORT_IMPORT_MAP = {
    "mlb": "sportsipy.mlb.teams",
    "nba": "sportsipy.nba.teams",
    "nfl": "sportsipy.nfl.teams",
    "nhl": "sportsipy.nhl.teams",
    "ncaab": "sportsipy.ncaab.teams",
    "ncaaf": "sportsipy.ncaaf.teams",
    "fb": "sportsipy.fb.teams",
}


@dataclass
class CodeAction:
    """Represents a single user action that maps to Python code."""
    action_type: str
    params: dict = field(default_factory=dict)
    description: str = ""


class CodeGenerator:
    """Generates Python code from a sequence of data exploration actions."""

    def __init__(self) -> None:
        """Initialize with an empty action list."""
        self.actions: list[CodeAction] = []
        self._imports: set[str] = set()

    def add_action(self, action: CodeAction) -> None:
        """Add an action to the code generation sequence.

        Args:
            action: The CodeAction to record.
        """
        self.actions.append(action)
        logger.debug("Added action: %s", action.action_type)

    def _render_action(self, action: CodeAction) -> tuple[list[str], list[str]]:
        """Render a single action into import lines and code lines.

        Args:
            action: The action to render.

        Returns:
            Tuple of (import_lines, code_lines).
        """
        imports: list[str] = []
        lines: list[str] = []

        if action.action_type == "load_teams":
            sport = action.params.get("sport", "mlb").lower()
            season = action.params.get("season")
            module = SPORT_IMPORT_MAP.get(sport, f"sportsipy.{sport}.teams")
            imports.append(f"from {module} import Teams")
            imports.append("import pandas as pd")
            if action.description:
                lines.append(f"# {action.description}")
            if season:
                lines.append(f"teams = Teams({season})")
            else:
                lines.append("teams = Teams()")
            lines.append("df = pd.concat([t.dataframe for t in teams], ignore_index=True)")

        elif action.action_type == "load_players":
            sport = action.params.get("sport", "mlb").lower()
            team = action.params.get("team_abbr", "")
            season = action.params.get("season")
            module = f"sportsipy.{sport}.roster"
            imports.append(f"from {module} import Roster")
            imports.append("import pandas as pd")
            if season:
                lines.append(f"roster = Roster('{team}', year={season})")
            else:
                lines.append(f"roster = Roster('{team}')")
            lines.append("df = pd.concat([p.dataframe for p in roster.players], ignore_index=True)")

        elif action.action_type == "filter":
            col = action.params.get("column", "")
            op = action.params.get("operator", "==")
            val = action.params.get("value", "")
            if action.description:
                lines.append(f"# {action.description}")
            try:
                float(val)
                lines.append(f"df = df[df['{col}'] {op} {val}]")
            except (ValueError, TypeError):
                lines.append(f"df = df[df['{col}'] {op} '{val}']")

        elif action.action_type == "select_columns":
            cols = action.params.get("columns", [])
            cols_repr = repr(cols)
            if action.description:
                lines.append(f"# {action.description}")
            lines.append(f"df = df[{cols_repr}]")

        elif action.action_type == "sort":
            col = action.params.get("column", "")
            ascending = action.params.get("ascending", False)
            if action.description:
                lines.append(f"# {action.description}")
            lines.append(f"df = df.sort_values('{col}', ascending={ascending})")

        elif action.action_type == "groupby":
            by = action.params.get("by", [])
            agg = action.params.get("agg", "mean")
            by_repr = repr(by)
            if action.description:
                lines.append(f"# {action.description}")
            lines.append(f"df = df.groupby({by_repr}).agg('{agg}').reset_index()")

        elif action.action_type == "rename_columns":
            mapping = action.params.get("mapping", {})
            if action.description:
                lines.append(f"# {action.description}")
            lines.append(f"df = df.rename(columns={mapping!r})")

        elif action.action_type == "drop_na":
            if action.description:
                lines.append(f"# {action.description}")
            lines.append("df = df.dropna()")

        elif action.action_type == "reset_index":
            lines.append("df = df.reset_index(drop=True)")

        else:
            lines.append(f"# Unsupported action: {action.action_type}")

        return imports, lines

    def generate_script(self) -> str:
        """Generate a complete Python script from recorded actions.

        Returns:
            String of Python source code.
        """
        all_imports: list[str] = []
        all_code_lines: list[str] = []

        for action in self.actions:
            imports, lines = self._render_action(action)
            all_imports.extend(imports)
            all_code_lines.extend(lines)
            all_code_lines.append("")

        seen: set[str] = set()
        unique_imports: list[str] = []
        for imp in all_imports:
            if imp not in seen:
                seen.add(imp)
                unique_imports.append(imp)

        header = [
            "# Generated by Sportsipy Dashboard",
            "# https://github.com/roclark/sportsipy",
            "",
        ]
        sections = header + unique_imports + ["", ""] + all_code_lines
        return "\n".join(sections).rstrip() + "\n"

    def generate_notebook(self) -> dict:
        """Generate a Jupyter notebook as a dict (nbformat).

        Returns:
            nbformat notebook dict with one code cell per action.
        """
        nb = nbformat.v4.new_notebook()

        nb.cells.append(
            nbformat.v4.new_markdown_cell(
                "# Sportsipy Data Exploration\n\nGenerated by [Sportsipy Dashboard](https://github.com/roclark/sportsipy)."
            )
        )

        all_imports: list[str] = []
        for action in self.actions:
            imports, _ = self._render_action(action)
            all_imports.extend(imports)

        seen: set[str] = set()
        unique_imports: list[str] = []
        for imp in all_imports:
            if imp not in seen:
                seen.add(imp)
                unique_imports.append(imp)

        if unique_imports:
            nb.cells.append(nbformat.v4.new_code_cell("\n".join(unique_imports)))

        for action in self.actions:
            _, lines = self._render_action(action)
            if lines:
                if action.description:
                    source = f"# {action.description}\n" + "\n".join(
                        l for l in lines if not l.startswith("#")
                    )
                else:
                    source = "\n".join(lines)
                nb.cells.append(nbformat.v4.new_code_cell(source.strip()))

        logger.debug("Generated notebook with %d cells", len(nb.cells))
        return dict(nb)

    def clear(self) -> None:
        """Clear all recorded actions."""
        self.actions = []
        self._imports = set()
        logger.debug("Cleared all actions")

    def to_dict(self) -> dict:
        """Serialize to dict for storage.

        Returns:
            Dict representation of the generator state.
        """
        return {"actions": [asdict(a) for a in self.actions]}

    @classmethod
    def from_dict(cls, data: dict) -> "CodeGenerator":
        """Deserialize from dict.

        Args:
            data: Dict previously produced by to_dict().

        Returns:
            New CodeGenerator instance.
        """
        gen = cls()
        for a in data.get("actions", []):
            gen.add_action(CodeAction(**a))
        return gen
