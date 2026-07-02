from wcbet.data.sources import SampleDataSource
from wcbet.pipeline import analyze_fixture
from wcbet.report import render_text


def test_pipeline_runs_end_to_end_on_all_sample_fixtures():
    source = SampleDataSource()
    for fixture_id in source.list_fixtures():
        fixture = source.get_fixture(fixture_id)
        home = source.get_team(fixture.home_team)
        away = source.get_team(fixture.away_team)

        report = analyze_fixture(fixture, home, away, n_sims=100_000, seed=123)

        h, d, a = report.ensemble_probabilities
        assert h + d + a - 1.0 < 1e-6
        assert 0 <= h <= 1 and 0 <= d <= 1 and 0 <= a <= 1
        assert "1x2" in report.markets and len(report.markets["1x2"]) == 3
        assert "totals_2.5" in report.markets
        assert "btts" in report.markets
        assert report.sensitivity["baseline"] is not None

        text = render_text(report)
        assert fixture.home_team in text
        assert fixture.away_team in text


def test_recommendation_never_fires_below_min_edge_regardless_of_favorite():
    """Even the heavy favorite in a lopsided sample fixture should not be
    recommended purely because it's favored -- only a real edge should."""
    source = SampleDataSource()
    fixture = source.get_fixture("WC2026-FINAL-ARG-FRA")
    home = source.get_team(fixture.home_team)
    away = source.get_team(fixture.away_team)
    report = analyze_fixture(fixture, home, away, n_sims=100_000, seed=999, min_edge=0.05)

    for rec in report.markets["1x2"]:
        if rec.edge <= 0.05:
            assert not rec.recommended
