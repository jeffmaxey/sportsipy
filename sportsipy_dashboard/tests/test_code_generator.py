"""Tests for code_generator module."""
import pytest
from sportsipy_dashboard.utils.code_generator import CodeGenerator, CodeAction


def test_code_generator_init():
    gen = CodeGenerator()
    assert gen.actions == []


def test_add_action():
    gen = CodeGenerator()
    action = CodeAction(action_type="load_teams", params={"sport": "mlb", "season": 2023})
    gen.add_action(action)
    assert len(gen.actions) == 1


def test_generate_script_load_teams():
    gen = CodeGenerator()
    action = CodeAction(action_type="load_teams", params={"sport": "mlb", "season": 2023})
    gen.add_action(action)
    script = gen.generate_script()
    assert "from sportsipy.mlb.teams import Teams" in script
    assert "Teams(2023)" in script


def test_generate_script_with_filter():
    gen = CodeGenerator()
    gen.add_action(CodeAction("load_teams", {"sport": "nba", "season": 2023}))
    gen.add_action(CodeAction("filter", {"column": "wins", "operator": ">", "value": "40"}))
    script = gen.generate_script()
    assert "wins" in script


def test_generate_notebook():
    gen = CodeGenerator()
    gen.add_action(CodeAction("load_teams", {"sport": "mlb", "season": 2023}))
    nb = gen.generate_notebook()
    assert nb["nbformat"] == 4
    assert len(nb["cells"]) > 0


def test_clear():
    gen = CodeGenerator()
    gen.add_action(CodeAction("load_teams", {"sport": "mlb", "season": 2023}))
    gen.clear()
    assert gen.actions == []


def test_to_dict_from_dict():
    gen = CodeGenerator()
    gen.add_action(CodeAction("load_teams", {"sport": "mlb", "season": 2023}))
    d = gen.to_dict()
    gen2 = CodeGenerator.from_dict(d)
    assert len(gen2.actions) == 1
    assert gen2.actions[0].action_type == "load_teams"
