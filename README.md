# HA Pilot Live [![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)

Pilot Live Sensor for Home Assistant

<img src="img/preview.png" width="auto" height="auto"/>

# Manual Install
<details>
<summary>Instructions</summary>

1. Download and unzip to your Home Assistant `config/custom_components` folder.
  <details>
  <summary>Screenshot</summary>
  
![image](https://user-images.githubusercontent.com/2578772/164681660-57d56fc4-4713-4be5-9ef1-bf2f7cf96b64.png)
  </details>
  
2. Restart Home Assistant.

</details>

# Example Lovelace Card

Each store's metrics (sales, discounts, payouts, etc.) are exposed as
attributes on a single sensor. See
[`lovelace/example-card.yaml`](lovelace/example-card.yaml) for a card that
gives each attribute its own icon — swap in your store's entity ID.
