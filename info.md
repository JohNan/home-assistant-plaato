# Plaato
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

This integration sets up integration with [Plaato](https://www.plaato.io/) Airlock and Keg.

## Configuration

This integration can be configured via the Home Assistant frontend.

- Go to **Configuration** -> **Integrations**.
- Click on the `+` in the bottom right corner to add a new integration.
- Search and select the **Plaato** integration form the list.
- Follow the instruction on screen to add the devices. 

You have two options to choose from: webhook and `auth_token.` The webhook is only available for the Airlock at the moment.

### Auth Token

To be able to query the API an `auth_token` is required which can be obtained by following [these](https://plaato.zendesk.com/hc/en-us/articles/360003234717-Auth-token) instructions.

### Webhook (Airlock only)

The configuration step will give you the webhook URL to use in the PLAATO mobile app. It should be pasted in configuration on the tab "Webhook". 
More information can be found [here](https://plaato.io/apps/help-center#!hc-general).