# phscrap
PH scraper

- [x] Make it virtualenv friendly
- [x] Add config
- [x] Daemon should know it's list of scrappers
- [ ] There should be one scrapper per service (argenprop, zonaprop), not one for URL.
- [ ] Improve self.soup logic
- [ ] Add a "page index", since for now it only scraps one page of results.
- [x] Daemon shouldn't know about csv headers
- [ ] Add Zonaprop scraper
- [ ] Add the possibility of a single run
- [ ] Clean repeated houses from self.houses
- [ ] Make daemon inform of diffs in csv between runs
- [ ] Logging
- [ ] Make it loop forever and sleep between interval defined in config
- [x] Debianize service
