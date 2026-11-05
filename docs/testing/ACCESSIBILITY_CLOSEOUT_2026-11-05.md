# Exam-interface accessibility closeout — 5 November 2026

## Scope and observed defects

The submitted SRS OEP-NF-005 requires responsive exam screens and WCAG 2.1 AA
basics, specifically contrast and keyboard navigation, with a manual audit and
Lighthouse score at least 90. This record addresses that scope; it does not claim
formal certification of every WCAG success criterion or a live screen-reader
listening session.

Live native-zoom inspection reproduced two issues: opening the submission
confirmation left focus on the removed button/body, and cancelling could restore
focus partly behind the sticky timer at a short viewport. The correction moves
focus to **Keep working**, supports Escape, restores focus on cancellation and
scrolls focused exam controls clear of the pinned timer. The confirmation has a
linked description and remains inline/nonmodal. Submission, pending-save guards,
timer accounting and grading rules are unchanged.

Initial focus uses the reversible action; see [W3C dialog guidance](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/).
The existing browser integration regression now checks keyboard entry, cancellation,
Escape, focus restoration and visibility at 320 × 255 CSS pixels before actual submission.

## Executed audit

[Text/JSON evidence](accessibility/2026-11-05/audit.json) records a fresh synthetic
SQLite fixture and the compiled application on Windows/full Chromium. Both the
original dated baseline and all private failed harness runs are retained separately.
No screenshot is added to this report or published evidence.

| Native page zoom | CSS viewport | Result |
| --- | --- | --- |
| 100% | 1280 × 1020 | No horizontal overflow; readable controls; timer visible; corrected focus flow passes |
| 200% | 640 × 510 | Same checks pass without removing functionality |
| 400% | 320 × 255 | Vertical scrolling retained; no horizontal overflow; timer and focused control remain visible |

This is real browser page zoom, not a CSS transform or device-DPI substitution:
an isolated Chromium profile uses its [partition zoom preference](https://chromium.googlesource.com/chromium/src/+/lkgr/chrome/browser/ui/zoom/chrome_zoom_level_prefs.cc),
and observed devicePixelRatio is 1/2/4 while physical outer width stays 1306 and
visualViewport.scale stays 1. The normal page and forced-colors renderings were
visually inspected using unclipped browser captures; the default screenshot clip
was unsuitable at native zoom and was not used as proof.

Radio names and checked states were inspected in Chromium's accessibility tree.
The full keyboard sign-in/save/cancel/submit/results flow is also recorded in the
[3 November audit](closeout/2026-11-03/browser-results.json). Existing authenticated
Lighthouse checks cover desktop/mobile contrast, skip-link, labels, overflow and
sticky-timer placement; fresh PR CI must pass before this patch is accepted.

Forced-colors emulation renders control labels and focus rings visibly, including
the restored Submit exam control at 400%. It is identified as browser emulation,
not a claim that the operator changed Windows high-contrast settings. Live
Narrator/NVDA audio and broader assistive-technology certification are not claimed.

The source JSON identifies the inspected base plus local focus patch and the
exact frontend-file hash. Subsequent CI/merge metadata supplies the committed head.
