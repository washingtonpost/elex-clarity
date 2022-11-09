# Changelog

## [0.0.7] - 2022-11-08

- [#46] feat: add candidate mapping

## [0.0.6] - 2022-11-08

- [#41] feat: add candidate mapping

## [0.0.5] - 2022-11-04

- [#39] Remove locality from race ID, add it back to subunit ID

## [0.0.4] - 2022-11-04

- [#36] Remove county ID from precinct ID

## [0.0.3] - 2022-11-01

- [#16] Add ability to get xml for county pages
- [#21] Try two methods to get counties
- [#18] Lookup race types, including for GA partisan primaries
- [#17] Add GA primaries office names
- [#19] Get current version for each county when requesting precinct files
- [#23] Add more exception handling for client
- [#20] Add `county_id` to precinct IDs, use dash to slugify precinct names
- [#22] Update README.rst
- [#24] Add more offices to GA 2022 primaries
- [#25] Remove extraneous slash from Clarity base URL
- [#27] Fake the user agent
- [#28] Partially match office IDs for AR, GA, IA
- [#29] Add district number to U.S. house office ID
- [#30] Change client args to work with importer
- [#31] Fall back when looking up county
- [#32] Correctly handle non-EST timezones

## [0.0.2] - 2021-01-04

- [#6] Adds a timestamp to the race settings JSON output
- [#7] Adds an option for a map to convert race names
- [#8] Changes to election settings handling
- [#9] Allow filtering by officeID in formatting step
- [#10] Include county name in the race settings JSON output
- [#11] README updates and CLI cleanup
- [#12] Adds a new `voteCompletionMode` CLI option
- [#13] Updates to use `race_type=G` for runoffs

## [0.0.1-beta.2]

- Adds a `voteCompletionMode` parameter to switch between using the `percentReporting` field vs vote counts by type to determine whether a precinct is fully reporting

## [0.0.1-beta.1]

- Initial beta release with county-level settings formatting and precinct, county, and state-level results formatting

## [0.0.1] - (Not yet published)

- Initial release!
