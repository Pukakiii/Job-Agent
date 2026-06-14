from app.integrations.sources.apify_indeed import ApifyIndeedSource


class _FakeApify:
    def __init__(self, items): self.items = items; self.called_with = None
    async def run_indeed(self, query, location, country=None):
        self.called_with = (query, location, country)
        return self.items


async def test_apify_indeed_maps_items_to_rawjobs():
    items = [{
        "id": "ind-1", "positionName": "Python Dev", "company": "ACME",
        "location": "Berlin", "url": "http://indeed/1", "description": "py",
    }]
    apify = _FakeApify(items)
    src = ApifyIndeedSource(apify)
    jobs = await src.fetch("python", "berlin")
    assert src.name == "indeed" and src.is_scraped is True
    assert jobs[0].source_job_id == "ind-1" and jobs[0].url == "http://indeed/1"
    assert jobs[0].company == "ACME"
    assert apify.called_with == ("python", "berlin", None)  # no country in "berlin"


async def test_apify_indeed_passes_country_and_city_from_location():
    apify = _FakeApify([])
    src = ApifyIndeedSource(apify)
    await src.fetch("software engineer", "Warszawa, PL")
    # city goes to Indeed's location field; the ISO code selects the domain (pl.indeed.com)
    assert apify.called_with == ("software engineer", "Warszawa", "pl")
