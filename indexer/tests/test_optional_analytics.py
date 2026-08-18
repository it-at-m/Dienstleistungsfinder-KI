from src import site_visits


def test_analytics_is_skipped_without_configuration(monkeypatch):
    monkeypatch.setattr(site_visits, "ETRACKER_BASE_URL", None)
    monkeypatch.setattr(site_visits, "ETRACKER_TOKEN", None)
    monkeypatch.setattr(site_visits, "process_etracker_data", lambda: (_ for _ in ()).throw(AssertionError()))
    site_visits.add_site_visits_main()
