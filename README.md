# poznajmypolske.pl
- application promoting different type of knowledge related to Poland (Polish language)
- idea is to do this by delivering simple web functionalities
- it is actually deployed here: https://poznajmypolske.pl/
- core assumption is to implement things leveraging Polish "Open Data" sources
- used Polish "Open Data" sources:
  - Geographical registry from Head Office of Geodesy and Cartography,
  - Polish Central Statistical Office API,
  - monuments databases from National Heritage Institute
- other assumption was to utilize different type of modern APIs
- those were used:
   - Google Custom Search API,
   - Open AI API
   - various RSS channels

## poznajmypolske.pl features
- "Polska w liczbach" - simplified web interface for Polish Central Statistical Office Database API
- "Prasówka" - current day press review (RSS channels of six popular polish portals/medium)
- "Przyroda" - unique search engine for polish geographical objects
  - there are additional functionalities like link to Google maps and possibility to ask AI about the object
- "Zabytki" - search engine for monuments (also archeological)
  - it includes also additional functions like links to Zabytek.pl and Google maps, possibility to ask AI about the monument and searching photos related to
- "Kontakt" - simple contact form

### Other notes:
- the project developed in MVP style
- [Configuration notes](https://github.com/DanielPalacz/DjangoPolishnessApp/tree/master/configuration)
- [Development, deployment notes](https://github.com/DanielPalacz/DjangoPolishnessApp/tree/master/configuration/README_Development_Deployment_notes.md)

### Possible Improvements/Activities:
- [Comprehensive test activities](https://github.com/DanielPalacz/DjangoPolishnessApp/tree/master/README_TESTS.md)
- General refactoring (mainly tools module and views)
- Usage of external CDN for Cracow Main Square video from main page
