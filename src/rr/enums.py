"""Closed vocabularies shared across the pipeline.

Defined at step 1.0 even where nothing implements them yet. These are seams: the enum is the
contract, and the code behind it is replaceable. A value added here later is a migration, so they
are worth getting right before data exists.
"""

from enum import StrEnum


class CareersOutcome(StrEnum):
    """Result of checking one employer for a hiring path.

    Every check produces exactly one of these, persisted as an append-only row rather than a
    column. The absence of a posting otherwise collapses three different facts into one: not
    checked yet, checked and nothing open, checked and unreachable.

    Nothing implements this until stage 4. See docs/planning/13-discovery-notes.md.
    """

    PORTAL_FOUND = "portal_found"
    """Careers page or hiring platform identified. Postings get extracted."""

    INSTRUCTIONS_ONLY = "instructions_only"
    """Site says to email or apply in person. Produces no Posting - destination undecided."""

    NONE_FOUND = "none_found"
    """Site loaded normally with no hiring signals. Included in periodic spot checks."""

    UNCERTAIN = "uncertain"
    """Hiring language without a usable link, or the page rendered empty. Routes to review."""

    BLOCKED = "blocked"
    """Refused request, challenge page, or robots.txt disallow. Routes to review."""

    UNREACHABLE = "unreachable"
    """Timeout, server error, or missing domain. Retried twice, then listed."""


class Channel(StrEnum):
    """How an application was actually submitted.

    This column is what later decides whether any browser-prefill adapter is worth building, and
    it turns the hiring-platform census into a byproduct of use rather than a scheduled study.
    See docs/adr/0010-defer-browser-prefill.md.
    """

    EMAIL = "email"
    FORM = "form"
    PORTAL = "portal"
    """Named platform. The specific one goes in `Application.channel_detail`."""
    INDEED = "indeed"


class ApplicationMode(StrEnum):
    """How much effort a document got.

    Quick-apply is the deep path with the curator call replaced by a copy of the profile's
    standard fields - a null curator behind one seam, not a second pipeline. The *resolved* mode
    persists on the application row, or effort reporting can never compare the two.
    """

    QUICK = "quick"
    DEEP = "deep"


class PostingStatus(StrEnum):
    """Where a posting sits in its lifecycle. Stage 2 drives most of these."""

    NEW = "new"
    DRAFTED = "drafted"
    APPLIED = "applied"
    SKIPPED = "skipped"
    CLOSED = "closed"
    """Observed to no longer be open."""
    STALE = "stale"
    """Not re-observed within the configured window."""
