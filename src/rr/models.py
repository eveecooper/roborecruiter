"""Database tables.

Carries the data items that are cheap now and unretrofittable later. Each is a column that cannot
be backfilled once records exist, which is why they land at step 1.0 even though nothing reads
most of them until stages 4 and 5. See docs/planning/10-build-plan.md.

Facts deliberately have no table: `config/profile.yaml` is their one home and the tool never
writes it. See docs/adr/0009-one-owner-per-file.md.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel

from rr.enums import ApplicationMode, CareersOutcome, Channel, PostingStatus


def _now() -> datetime:
    return datetime.now(UTC)


class VersionStamped(SQLModel):
    """Provenance for anything a generator produced.

    Without these, a 0.72 recorded in March and a 0.72 recorded in October are different
    measurements wearing one label, and a response cache silently reuses a stale schema shape.
    All four are nullable because stage 1 produces none of them - the columns exist so later
    stages have somewhere to write.
    """

    profile_version: int | None = None
    prompt_version: str | None = None
    model_alias: str | None = None
    output_schema_version: int | None = None


class Employer(SQLModel, table=True):
    """An employer. Location is an attribute, not identity."""

    __tablename__ = "employers"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    website: str | None = None
    city: str | None = None
    region: str | None = None
    #: Where this record came from, kept source-neutral so no provider's schema leaks in.
    source: str | None = None
    source_ref: str | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class CareersCheck(SQLModel, table=True):
    """One check of one employer for a hiring path. Append-only.

    A `latest_outcome` column on the employer would collapse three different facts into one: not
    checked yet, checked and nothing open, checked and unreachable. Rows also make churn visible -
    an employer that opens a role every six weeks is a different lead from one that never has -
    and give Investigation A its denominator.
    """

    __tablename__ = "careers_checks"

    id: int | None = Field(default=None, primary_key=True)
    employer_id: int = Field(foreign_key="employers.id", index=True)
    checked_at: datetime = Field(default_factory=_now)
    url: str | None = None
    outcome: CareersOutcome
    #: Which detector produced this, so a result can be attributed after the detector changes.
    detector_version: str | None = None
    note: str | None = None


class Posting(SQLModel, table=True):
    """A job posting. The full text is persisted, not just a hash and a URL."""

    __tablename__ = "postings"

    id: int | None = Field(default=None, primary_key=True)
    employer_id: int | None = Field(default=None, foreign_key="employers.id", index=True)
    employer_name: str
    #: `employer_name` reduced to letters and digits. The duplicate key is scoped by employer and
    #: the name is a correctable guess, so the key cannot depend on how it was spelled.
    employer_key: str = Field(index=True)
    title: str
    url: str | None = Field(default=None, index=True)

    #: The employer's own identifier for this opening - IBM's 132846, Greenhouse's `gh_jid`. The
    #: one duplicate key that survives a rewritten URL and an edited body, so it is captured at
    #: intake even though nothing enforces it until stage 3. Unique only within one employer.
    source_posting_id: str | None = Field(default=None, index=True)

    #: The whole posting, verbatim. This is stage 5's corpus; a URL rots and a hash says nothing.
    text: str
    #: Content hash of `text`, so re-adding the same posting is detectable.
    text_hash: str = Field(index=True)

    source: str = "manual"
    status: PostingStatus = PostingStatus.NEW
    #: Which persona and mode this posting is being approached with.
    persona: str | None = None
    mode_override: ApplicationMode | None = None

    first_seen: datetime = Field(default_factory=_now)
    last_seen: datetime = Field(default_factory=_now)
    closed_at: datetime | None = None
    updated_at: datetime = Field(default_factory=_now)


class FamilyAssignment(SQLModel, table=True):
    """Which job family a posting was assigned to, and under which version of the family list.

    Stable family IDs are necessary and not sufficient. Without this history there is no held-out
    set to measure a later clusterer against - it would be scored on its own earlier output.
    """

    __tablename__ = "family_assignments"

    id: int | None = Field(default=None, primary_key=True)
    posting_id: int = Field(foreign_key="postings.id", index=True)
    family_id: str
    #: Version of `config/families.yaml` in force when the assignment was made.
    families_version: int | None = None
    #: "human" or the name of whatever assigned it.
    assigned_by: str = "human"
    assigned_at: datetime = Field(default_factory=_now)


class Application(SQLModel, table=True):
    """One application actually sent.

    The row holding a sent file's hash is the one record in this project that cannot be
    regenerated, which is why migrations ship at step 1.0.
    """

    __tablename__ = "applications"

    id: int | None = Field(default=None, primary_key=True)
    posting_id: int = Field(foreign_key="postings.id", index=True)

    #: Resolved at send time, not read back from config - config changes, history does not.
    persona: str
    mode: ApplicationMode

    channel: Channel | None = None
    #: The specific portal when `channel` is PORTAL.
    channel_detail: str | None = None
    submit_seconds: int | None = None

    sent_at: datetime | None = None
    #: What came back. Marked by hand until email reading exists, if it ever does.
    response: str | None = None
    response_at: datetime | None = None

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class SentFile(SQLModel, table=True):
    """A file that went out with an application, by content hash.

    Stage 1's only exit criterion that matters is that this row can name the exact file an
    employer received, months later, after the local copy has been edited five more times.
    """

    __tablename__ = "sent_files"

    id: int | None = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="applications.id", index=True)
    kind: str
    """resume, cover_letter, or anything else attached."""
    filename: str
    content_hash: str
    sent_at: datetime = Field(default_factory=_now)


class GeneratedDocument(VersionStamped, table=True):
    """A rendered document and the hash it had when written.

    A changed hash means the applicant edited it, and an edited file is never overwritten - a
    re-render writes `.v2` instead. See docs/adr/0002-hand-editing-allowed.md.
    """

    __tablename__ = "generated_documents"

    id: int | None = Field(default=None, primary_key=True)
    posting_id: int = Field(foreign_key="postings.id", index=True)
    kind: str
    path: str
    #: Hash at the moment the tool wrote it. Compared before any re-render.
    content_hash: str
    style_id: str | None = None
    mode: ApplicationMode = ApplicationMode.QUICK
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
