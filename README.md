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

Each store is exposed as its own device with a sensor per metric (sales,
discounts, payouts, etc.), each with its own icon. See
[`lovelace/example-card.yaml`](lovelace/example-card.yaml) for ready-to-use
card examples (entities list and tile grid) — swap in your store's entity
IDs from its device page.
