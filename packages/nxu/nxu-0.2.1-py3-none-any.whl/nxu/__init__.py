import typer
from .init_project import setup_project
from .builder import build as build_strategy
from typing_extensions import Annotated
from pathlib import Path
from .expression import Expr

from .strategy_config import (
    StrategyConfig,
    Factor,
    OrderEnum,
    Timing,
    TimingFactor,
    Filter,
    StrategyList,
)

__all__ = [
    "StrategyConfig",
    "Factor",
    "OrderEnum",
    "Timing",
    "TimingFactor",
    "Filter",
    "StrategyList",
    "Expr",
]

app = typer.Typer()


@app.command(help="初始化项目")
def init():
    setup_project()


@app.command(help="编译策略")
def build(path: Annotated[Path, typer.Argument(help="配置文件路径")]):
    build_strategy(path)


def main() -> None:
    app()
