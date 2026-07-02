"""Data-source adapter interfaces.

The modeling and value-detection layers only ever talk to these interfaces,
never to a concrete provider. That is what makes "continuously updating"
data feeds a deployment concern rather than a rewrite: implement one of
these against a real provider (an odds API, a paid Elo/SPI feed, a
scraper, a warehouse table) and hand it to the pipeline instead of
``SampleDataSource``.

No live implementations ship here because this environment has no
credentials for paid sports-data or odds providers. ``SampleDataSource``
is the reference implementation backed by the hand-authored sample
datasets, useful for development, testing, and demonstrating the pipeline
end-to-end.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from wcbet.data.models import Fixture, Player, TeamStats


class TeamDataSource(ABC):
    """Provides team-level Elo/FIFA/SPI/xG/form data."""

    @abstractmethod
    def get_team(self, name: str) -> TeamStats: ...

    @abstractmethod
    def list_teams(self) -> list[str]: ...


class PlayerDataSource(ABC):
    """Provides projected-lineup player data for a fixture."""

    @abstractmethod
    def get_roster(self, team: str, fixture_id: str) -> list[Player]: ...


class OddsDataSource(ABC):
    """Provides current/opening/closing market odds and line-movement data.

    A real implementation should poll the provider on a schedule and persist
    snapshots so ``opening_*``/``closing_*``/current odds and public betting
    percentages can be populated; this interface intentionally only exposes
    the read side that the pipeline needs per fixture.
    """

    @abstractmethod
    def get_fixture(self, fixture_id: str) -> Fixture: ...

    @abstractmethod
    def list_fixtures(self) -> list[str]: ...


class SampleDataSource(TeamDataSource, PlayerDataSource, OddsDataSource):
    """Reference implementation backed by the sample datasets in this package."""

    def __init__(self) -> None:
        from wcbet.data.sample_fixtures import SAMPLE_FIXTURES
        from wcbet.data.sample_teams import SAMPLE_TEAMS

        self._teams = SAMPLE_TEAMS
        self._fixtures = {f.fixture_id: f for f in SAMPLE_FIXTURES}

    def get_team(self, name: str) -> TeamStats:
        try:
            return self._teams[name]
        except KeyError as exc:
            raise KeyError(f"No sample data for team {name!r}") from exc

    def list_teams(self) -> list[str]:
        return sorted(self._teams)

    def get_roster(self, team: str, fixture_id: str) -> list[Player]:
        fixture = self.get_fixture(fixture_id)
        if fixture.home_team == team:
            return fixture.home_players
        if fixture.away_team == team:
            return fixture.away_players
        return []

    def get_fixture(self, fixture_id: str) -> Fixture:
        try:
            return self._fixtures[fixture_id]
        except KeyError as exc:
            raise KeyError(f"No sample fixture {fixture_id!r}") from exc

    def list_fixtures(self) -> list[str]:
        return list(self._fixtures)
