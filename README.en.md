# RTE Jours Signalés for Home Assistant

![downloads](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.rte_jours_signales.total)

Component to expose [RTE Jours Signalés](https://www.services-rte.com/fr/visualisez-les-donnees-publiees-par-rte/jours-signales-de-l-appel-d-offres-effacement.html).
These days are used - among other things - by certain energy suppliers such as [Octopus France](https://www.octopusenergy.fr) to reward energy savings made by their customers on busy days on the electricity grid.

Two entity are exposed:
- `sensor.rte_jours_signales_signal_current`: The current day's signal
- `sensor.rte_jours_signales_signal_next`: The next day's signal

The status of the entities is refreshed every day at midnight and 10.45am.

## Installation

Use [hacs](https://hacs.xyz/).
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=hiteule&repository=rte-jours-signales&category=integration)

### Get api access for RTE APIs

- Create an account on [RTE API website](https://data.rte-france.com/web/guest)
- Register to the [Demand Response Signal API](https://data.rte-france.com/catalog/-/api/market/Demand-Response-Signal/v2.0) and click on "Abonnez-vous à l'API", create a new application
- Get the `client_id` and `client_secret` (uuid in both cases)
