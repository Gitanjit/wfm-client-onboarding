"""Weekly notifications rendered to text files under out/<client>/notify/<week>/: a digest for the
account team, a shift notice per agent and a sheet per local day for team leads. Nothing is sent
from here; the team distributes those files (docs/OPERATIONS.md)."""
from __future__ import annotations

from pathlib import Path

from wfm.export.base import Segment
from wfm.notify.agents import notices
from wfm.notify.digest import digest
from wfm.notify.sheets import sheets


def notify_dir(out_dir: Path, client: str, week: str) -> Path:
    return out_dir / client / "notify" / week


def _fresh(d: Path) -> Path:
    """Create `d` and remove text files left by an earlier run of the same week."""
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.txt"):
        old.unlink()
    return d


def write_notifications(out_dir: Path, cfg: dict, week: str, ev: dict, segments: list[Segment], agents,
                        account_manager: str | None = None, previous: dict | None = None) -> list[Path]:
    """Write digest.txt, agents/<agent_id>.txt and days/<date>.txt so that the folder matches this
    run. `previous`: the eval of an earlier archived week, for the digest's comparison lines.
    Returns the files written, in order."""
    root = notify_dir(out_dir, cfg["client"], week)
    agent_dir, day_dir = _fresh(root / "agents"), _fresh(root / "days")
    written = [root / "digest.txt"]
    written[0].write_text(digest(ev, segments, cfg, week, account_manager, agents, previous))
    for aid, text in notices(segments, cfg, week, agents).items():
        written.append(agent_dir / f"{aid}.txt")
        written[-1].write_text(text)
    for day, text in sheets(segments, cfg, week).items():
        written.append(day_dir / f"{day:%Y-%m-%d}.txt")
        written[-1].write_text(text)
    return written
