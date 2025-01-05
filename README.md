# RTE Jours Signalés pour Home Assistant

Composant pour exposer les (Jours Signalés RTE)[https://www.services-rte.com/fr/visualisez-les-donnees-publiees-par-rte/jours-signales-de-l-appel-d-offres-effacement.html] en application des dispositions de l’appel d’offres effacement.
Ces jours sont -entre autre- utilisés par certains fournisseurs d'énergie comme (Octopus France)[https://www.octopusenergy.fr] pour récompenser les économies d'énergie réalisé par leurs clients.

![downloads](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.rte_jours_signales.total)

## Installation

Utilisez [hacs](https://hacs.xyz/).
[![Ouvrez votre instance Home Assistant et ouvrez un référentiel dans la boutique communautaire Home Assistant.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=hiteule&repository=rte-jours-signales&category=integration)

### Obtenir un accès API pour les API RTE

- Créer un compte sur [site API RTE](https://data.rte-france.com/web/guest)
- Inscrivez-vous à l'[API Demand Response Signal](https://data.rte-france.com/catalog/-/api/market/Demand-Response-Signal/v2.0) et cliquez sur "Abonnez-vous à l'API", créez un nouvelle application
- Obtenir le `client_id` et `client_secret` (uuid dans les deux cas)
