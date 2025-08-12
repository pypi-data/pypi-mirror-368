from collections.abc import Collection
from pathlib import Path

import pandas as pd
import xarray


def classes_to_templates() -> dict[str, str | None]:
    """Return a mapping of class names to a default column in various tables:

    - $martial for martial classes
    - $spellcaster for spellcasting classes
    - None for classes that are too nuanced and must always be listed
    """
    fname = Path(__file__).parent / "_templates.csv"
    d = pd.read_csv(fname, index_col=0).template.to_dict()
    return {k: None if pd.isna(v) else v for k, v in d.items()}


def postproc_classes(
    ds: xarray.Dataset,
    *,
    extra_columns: Collection[str] = (),
    only_spellcasters: bool = False,
) -> None:
    """Post-process a table that contains exactly one column per class:

    - Merge class/subclass columns into single variables with an extra dimension
    - Expand $martial and $spellcaster templates to omitted classes
    - Sort alphabetically
    - Test for missing classes
    """
    to_delete = set()

    # Merge class/subclass columns into single variables with an extra dimension
    for class_name, dim, subclasses in (
        ("cleric", "doctrine", ["battle creed", "cloistered cleric", "warpriest"]),
        ("fighter", "mastery", ["mastery", "other"]),
        ("gunslinger", "mastery", ["mastery", "other"]),
    ):
        if f"{class_name}/{subclasses[0]}" in ds:
            ds[class_name] = xarray.concat(
                [ds[f"{class_name}/{subclass}"] for subclass in subclasses],
                dim=dim,
            ).T
            to_delete |= {f"{class_name}/{subclass}" for subclass in subclasses}
            ds[dim] = subclasses

    if "mastery" in ds:
        ds["mastery"] = [True, False]

    classes_tpls = classes_to_templates()

    # Expand $martial and $spellcaster templates to omitted classes
    for class_name, tpl in classes_tpls.items():
        if class_name not in ds and tpl is not None and tpl in ds:
            ds[class_name] = ds[tpl]
            to_delete.add(tpl)

    for col_name in to_delete:
        del ds[col_name]

    # Sort alphabetically and test for missing classes
    vars = {}
    for class_name, tpl in classes_tpls.items():
        if class_name in ds:
            vars[class_name] = ds[class_name]
            del ds[class_name]
        elif not only_spellcasters or tpl == "$spellcaster":
            raise KeyError(class_name)  # pragma: no cover

    # Move extra columns to the end
    for col_name in extra_columns:
        vars[col_name] = ds[col_name]
        del ds[col_name]

    # Test for unexpected columns
    assert not ds.data_vars, f"Unexpected columns: {list(ds.data_vars)}"

    ds.update(vars)
