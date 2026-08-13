"""Stage 14 eval graders.

Self-contained by necessity: apps/ and services/ have no implementation yet
(Stage 20 is deliberately last), so unlike V2's graders (which import real
service modules, e.g. submission.src.services.tool_gateway), these graders
embed the deterministic rule they check directly, sourced from the specific
Stage 09-13 document named in each docstring. The same function signatures
are what Stage 20 wires to real service calls -- the grading logic does not
change, only what produces its input does.
"""
