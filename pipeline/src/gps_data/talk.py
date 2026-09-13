"""The 25-field Talk record: the data layer's output and the engine's input.
Shape is fixed by packages/contracts (talk.schema.json). Engines may read
only id, title, abstract, units, topics."""
from dataclasses import asdict, dataclass, fields


@dataclass(frozen=True)
class Talk:
    id: int
    external_id: str | None
    title: str
    abstract: str
    units: tuple[str, ...]
    topics: tuple[str, ...]
    type: str | None
    is_invited: bool
    is_withdrawn: bool
    start: str | None
    end: str | None
    sort_order: int | None
    presentation_location: str | None
    author_ids: tuple[int, ...]
    presenter_ids: tuple[int, ...]
    publication_reference: str | None
    funding_acknowledgement: str | None
    team_acknowledgement: str | None
    session_id: int | None
    session_title: str | None
    session_code: str | None
    session_type: str | None
    session_topics: tuple[str, ...]
    building: str | None
    room: str | None


_LIST_FIELDS = {"units", "topics", "author_ids", "presenter_ids", "session_topics"}


def to_row(t: Talk) -> dict:
    row = asdict(t)
    for k in _LIST_FIELDS:
        row[k] = list(row[k])
    return row


def from_row(row: dict) -> Talk:
    kw = {f.name: row[f.name] for f in fields(Talk)}
    for k in _LIST_FIELDS:
        kw[k] = tuple(kw[k])
    return Talk(**kw)


def external_anchor(title: str, abstract: str, units: list[str]) -> Talk:
    """A paper that is not in the programme: id 0, text and units only."""
    return Talk(
        id=0, external_id=None, title=title, abstract=abstract,
        units=tuple(units), topics=(), type=None, is_invited=False,
        is_withdrawn=False, start=None, end=None, sort_order=None,
        presentation_location=None, author_ids=(), presenter_ids=(),
        publication_reference=None, funding_acknowledgement=None,
        team_acknowledgement=None, session_id=None, session_title=None,
        session_code=None, session_type=None, session_topics=(),
        building=None, room=None,
    )
