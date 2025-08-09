"""Formatter to process ruff output and yield GitHub annotations."""

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from github_checks.formatters.utils import filter_for_checksignore, get_conclusion
from github_checks.models import (
    AnnotationLevel,
    CheckAnnotation,
    CheckRunConclusion,
    CheckRunOutput,
)


class _CodePosition(BaseModel):
    column: int
    row: int


class _RuffEditSuggestion(BaseModel):
    content: str
    location: _CodePosition
    end_location: _CodePosition


class _RuffFixSuggestion(BaseModel):
    applicability: str
    edits: list[_RuffEditSuggestion]
    message: str | None


class _RuffJSONError(BaseModel):
    cell: Any | None  # not sure of its type, but fairly sure it's irrelevant for us
    code: str
    location: _CodePosition
    end_location: _CodePosition
    filename: Path
    fix: _RuffFixSuggestion | None
    message: str
    noqa_row: int
    url: str


def _format_annotations_for_ruff_json_output(
    json_output_fp: Path,
    local_repo_base: Path,
    annotation_level: AnnotationLevel,
) -> Iterable[CheckAnnotation]:
    """Generate annotations for the ruff's output when run with output-format=json.

    :param json_output_fp: filepath to the full json output from ruff
    :param local_repo_base: local repository base path, for deriving repo-relative paths
    """
    with json_output_fp.open("r", encoding="utf-8") as json_file:
        json_content = json.load(json_file)

    for error_dict in json_content:
        ruff_err: _RuffJSONError = _RuffJSONError.model_validate(error_dict)
        err_is_on_one_line: bool = ruff_err.location.row == ruff_err.end_location.row
        # Note: github annotations have markdown support -> let's hyperlink the err code
        # this will look like "D100: undocumented public module" with the D100 clickable
        title: str = f"[{ruff_err.code}] {ruff_err.url.split('/')[-1]}"
        raw_details: str | None = None
        if ruff_err.fix:
            msg = ruff_err.fix.message or ""
            raw_details = f"Ruff suggests the following fix: {msg}\n" + "\n".join(
                f"Replace line {edit.location.row}, column {edit.location.column} "
                f"to line {edit.end_location.row}, column "
                f"{edit.end_location.column} with:\n{edit.content}"
                for edit in ruff_err.fix.edits
            )
        message = (
            ruff_err.message + "\n\n" + "See " + ruff_err.url + " for more information."
        )
        yield CheckAnnotation(
            annotation_level=annotation_level,
            start_line=ruff_err.location.row,
            start_column=ruff_err.location.column if err_is_on_one_line else None,
            end_line=ruff_err.end_location.row,
            end_column=ruff_err.end_location.column if err_is_on_one_line else None,
            path=str(ruff_err.filename.relative_to(local_repo_base)),
            message=message,
            raw_details=raw_details,
            title=title,
        )


def format_ruff_check_run_output(
    json_output_fp: Path,
    local_repo_base: Path,
    ignore_globs: list[str] | None = None,
    ignore_verdict_only: bool = False,
) -> tuple[CheckRunOutput, CheckRunConclusion]:
    """Generate high level results, to be shown on the "Checks" tab."""
    with json_output_fp.open("r", encoding="utf-8") as json_file:
        json_content = json.load(json_file)

    issues: set[str] = set()
    issue_codes: set[str] = set()
    for ruff_err_json in json_content:
        ruff_err = _RuffJSONError.model_validate(ruff_err_json)
        if ruff_err.code in issue_codes:
            continue
        issue_codes.add(ruff_err.code)
        # Note: github annotations have markdown support -> let's hyperlink the err code
        # this will look like "D100: undocumented public module" with the D100 clickable
        issues.add(
            f"> **[[{ruff_err.code}]({ruff_err.url})] {ruff_err.url.split('/')[-1]}**",
        )

    # Use warning level for annotations (since nothing broke, but still needs fixing)
    annotations: list[CheckAnnotation] = list(
        _format_annotations_for_ruff_json_output(
            json_output_fp,
            local_repo_base,
            AnnotationLevel.WARNING,
        ),
    )

    # Filter out ignored files from the verdict / annotations (depending on settings)
    if ignore_globs:
        filtered_annotations: list[CheckAnnotation] = list(
            filter_for_checksignore(
                annotations,
                ignore_globs,
                local_repo_base,
            )
        )
        conclusion = get_conclusion(filtered_annotations)
        if not ignore_verdict_only:
            annotations = filtered_annotations
    else:
        conclusion = get_conclusion(annotations)

    if annotations:
        if conclusion == CheckRunConclusion.ACTION_REQUIRED:
            title = f"Ruff found issues with {len(issue_codes)} rules."
        else:
            title = "Ruff only found issues in ignored files."
        summary: str = (
            "\n".join(issues) + "\n\n"
            "Click the error codes to read ruff's documentation for these rules, or "
            "navigate to the source files via the annotations below to see the "
            "offending code."
        )
    else:
        title = "Ruff found no issues."
        summary = "Nice work!"

    return (
        CheckRunOutput(title=title, summary=summary, annotations=annotations),
        conclusion,
    )
