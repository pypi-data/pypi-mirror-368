#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["twat-coding"]
# ///
# this_file: d361api/stuby.py

from twat_coding.pystubnik import (
    generate_stub,
    StubGenConfig,
    PathConfig,
    SmartStubGenerator,
    ProcessingConfig,
    TruncationConfig,
)


config = StubGenConfig(
    paths=PathConfig(
        output_dir="path/to/output",
        doc_dir="path/to/docs",
        search_paths=[],
        modules=[],
        packages=[],
        files=[],
    ),
    processing=ProcessingConfig(
        include_docstrings=True,
        include_private=False,
        include_type_comments=True,
        infer_property_types=True,
        export_less=False,
        importance_patterns={
            r"^test_": 0.5,  # Lower importance for test functions
            r"^main$": 1.0,  # High importance for main functions
        },
    ),
    truncation=TruncationConfig(
        max_sequence_length=4,
        max_string_length=17,
        max_docstring_length=150,
        max_file_size=3_000,
        truncation_marker="...",
    ),
)


generator = SmartStubGenerator(
    output_dir="path/to/output",
    include_docstrings=True,
    include_private=False,
    verbose=True,
)

generator.generate()  # Process all configured files
