# phscrap
PH scraper

- [x] Make it virtualenv friendly
- [x] Add config
- [x] Daemon should know it's list of scrappers
- [ ] There should be one scrapper per service (argenprop, zonaprop), not one for URL.
- [x] Improve self.soup logic
- [ ] Add a "page index", since for now it only scraps one page of results.
- [x] Daemon shouldn't know about csv headers
- [x] Add Zonaprop scraper
- [x] Add the possibility of a single run
- [x] Clean repeated houses from self.houses
- [x] Make daemon inform of diffs in csv between runs
- [x] Make daemon send mail with diff?
- [x] Logging
- [x] Make it loop forever and sleep between interval defined in config
- [x] Debianize service
