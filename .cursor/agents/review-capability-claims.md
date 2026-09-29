---
name: review-capability-claims
description: Flags capability the app advertises but the engine cannot deliver
---

Analysis only. Do not edit files. Report at most one finding.

## Concern

This app is a thin shell over `ebook-converter-lib`. Its most frequent defect
class is advertising capability that the engine does not actually have: format
pickers listing formats with no working backend, README claims contradicting
runtime behaviour, packaging metadata promising an install path that does not
work. These are invisible to correctness review because the code is valid and
the tests pass. They only surface when a user picks the option.

## Scope

- `econverter_desktop/core.py` - `INPUT_FORMATS`, `OUTPUT_FORMATS`
- `econverter_desktop/app.py` - picker contents and startup notices
- `README.md` - the supported formats and PDF sections
- `pyproject.toml` - entry points and dependency floor
- `econverter.spec` - what is actually included in the bundle

## Check

1. Does every format offered to the user have a plugin **and** an importable
   backend module in the pinned `ebook-converter-lib` version?
2. Does a README capability claim contradict what the code permits, in either
   direction? Claiming something is unsupported when it works is also a defect.
3. Does packaging metadata promise an install or entry path that the built
   artifact does not support?
4. Does a temporary exclusion or compatibility shim still have a test that
   fails once it is no longer needed?
5. Does a change widen what the app offers without evidence that the engine
   can service it?

## Output

One finding: the claim, where it is made, the evidence it is unbacked, and the
narrowest correction. Prefer deriving from the engine over maintaining a list.

If every advertised capability is backed, respond exactly: `NO_NEW_FINDINGS`
