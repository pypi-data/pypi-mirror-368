from typing import Any

import pandas as pd

from tesorotools.offsets.offsets import process_raw_data, trim

from .node import Node


def resolve(
    start: Node,
    resolved: list[Node],
    unresolved: list[str],
    independent: set[str],
    dependencies_cfg: dict[str, Any],
):
    if start.name in dependencies_cfg:
        is_independent: bool = False
        config: dict[str, Any] = dependencies_cfg[start.name]
        start.build_edges(**config)
    else:
        is_independent: bool = True
        independent.add(start.name)

    if not is_independent:
        unresolved.append(start.name)
        for node in start.edges:
            if node.name in unresolved:
                raise ValueError(
                    f"circular dependency: {start.name} <-> {node.name}"
                )
            if node not in resolved:
                resolve(
                    node, resolved, unresolved, independent, dependencies_cfg
                )
        resolved.append(start)
        unresolved.remove(start.name)


def collect_document_series(
    config_dicts: list[dict[str, Any]], find: str = "series"
) -> list[str]:
    series: set[str] = set()
    for config_dict in config_dicts:
        series = series | collect_series(config_dict, find)
    return list(series)


def resolve_series(
    config_dicts: list[dict[str, Any]], dependencies_cfg: dict[str, Any]
):
    series: list[str] = collect_document_series(config_dicts)
    nodes: list[Node] = [Node(name=name) for name in series]
    independent_nodes: set[str] = set()
    resolved: list[Node] = []
    for node in nodes:
        resolve(
            start=node,
            resolved=resolved,
            unresolved=[],
            independent=independent_nodes,
            dependencies_cfg=dependencies_cfg,
        )

    return {
        "independent": independent_nodes,
        "dependent": resolved,
    }


def compute_derivate_series(
    dependent_nodes: list[Node], trimmed_data: pd.DataFrame
):
    inferred_series: list[pd.Series] = []
    for node in dependent_nodes:
        dependencies_names: list[str] = [n.name for n in node.edges]
        dependencies_df = trimmed_data.loc[:, dependencies_names]
        dependencies_dict = dependencies_df.to_dict(orient="series").values()
        inferred: pd.Series = node.resolving_function(*dependencies_dict)
        inferred.name = node.name
        inferred_series.append(inferred)
    inferred_df: pd.DataFrame = pd.concat(inferred_series, axis=1)
    return inferred_df


def concat_derivate_series(
    independent_full_df: pd.DataFrame,
    derivate_trimmed_df: pd.DataFrame,
    offsets_config: dict[str, Any],
    force_trim: bool = False,
) -> pd.DataFrame:

    # useful when adding emergency fixed offsets
    if force_trim:
        independent_full_df: pd.DataFrame = process_raw_data(
            trim(independent_full_df), **offsets_config
        )

    derivate_full_df: pd.DataFrame = process_raw_data(
        derivate_trimmed_df, **offsets_config
    )
    full: pd.DataFrame = pd.concat(
        [independent_full_df, derivate_full_df], axis=1
    )
    return full


def collect_series(
    config_dict: dict[str, Any], find: str = "series"
) -> set[str]:
    series: set[str] = set()
    if find in config_dict:
        config_series: dict[str, str] = config_dict[find]
        series = series | set(config_series.keys())
    for k, v in config_dict.items():
        if k != find and isinstance(v, dict):
            series = series | collect_series(v, find)
    return series
