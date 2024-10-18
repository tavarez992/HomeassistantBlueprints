# HomeassistantBlueprints

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/shadala)

## Blueprints list

### Sonoff Ultimate TX blueprint for "two fingers double click" gesture and "two fingers + slide action"

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Ftavarez992%2FHomeassistantBlueprints%2Fblob%2Fmain%2Fblueprints%2Fautomation%2FSonoffUltimateTX.yaml)

You need to define 3 entities in Blueprint config:
- entity with ambient light
- entity with slide actions
- text helper (*need to manualy create text helper*) as a support string used in Blueprint. It will contain JSON string for getting last event and last event time.

Blueprint create extra 3 actions for Sonoff Ultimate TX Wall Switch. In one automation you can define 5 actions:
- slide left
- slide right
- double two finger click
- two finger click -> slide left
- two finger click -> slide right

Blueprint use entities provided by Sonoff LAN HACS integration - https://github.com/AlexxIT/SonoffLAN

This is how Blueprint looks:

<img src="https://github.com/user-attachments/assets/8b7b3186-b76f-423f-97b4-e5338f278d7f" alt="image" width="200" />

