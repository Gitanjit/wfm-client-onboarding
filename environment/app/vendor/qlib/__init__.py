"""qlib: small queueing formulas for contact-centre staffing (Erlang B, Erlang C, Erlang A).

Vendored copy; see README.md for the version and CHANGELOG.md for what changed between releases.
"""
from .models import erlang_b, erlang_c, service_level, abandon_probability  # noqa: F401
from .staffing import required_agents, achieved  # noqa: F401

__version__ = "1.3.0"
