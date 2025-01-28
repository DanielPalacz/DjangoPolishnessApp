# poznajmypolske.pl
- application promoting different type of knowledge related to Poland
- idea is to do this by delivering simple web functionalities
- it is actually deployed here: https://poznajmypolske.pl/

### poznajmypolske.pl functionalities
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

### Notes:
- the project developed in MVP style
- [Configuration notes](https://github.com/DanielPalacz/DjangoPolishnessApp/tree/master/configuration)
- [Development, deployment notes](https://github.com/DanielPalacz/DjangoPolishnessApp/tree/master/configuration/README_Development_Deployment_notes.md)

### Improvements:
- [Comprehensive test activities](https://github.com/DanielPalacz/DjangoPolishnessApp/tree/master/README_TESTS.md)
- General refactoring (mainly tools module and views)
- Usage of external CDN for Cracow Main Square video from main page
