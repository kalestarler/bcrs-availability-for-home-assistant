# BCRS Availability for Home Assistant

See at a glance whether your nearest **BCRS machine** (the Return Right reverse vending machines for Singapore's Beverage Container Return Scheme) is available, full or closed, right on your Home Assistant dashboard.

It uses the same live information as the map on [recycle.gov.sg](https://www.recycle.gov.sg/materials/beverage).

## What you'll need

- Home Assistant 2025.2 or newer
- [HACS](https://hacs.xyz/docs/use/download/download/) installed

## Install

### 1. Add this to HACS

Click this button and follow the prompts:

[![Open your Home Assistant instance and open this repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kalestarler&repository=bcrs-availability-for-home-assistant&category=integration)

<details>
<summary>If the button doesn't work, add it by hand</summary>

1. In Home Assistant, open **HACS**.
2. Click the **⋮** menu (top right) and choose **Custom repositories**.
3. Paste `https://github.com/kalestarler/bcrs-availability-for-home-assistant`, set **Type** to **Integration**, and click **Add**.
4. Search HACS for **BCRS Availability** and open it.

</details>

Then click **Download**.

### 2. Restart Home Assistant

Go to **Settings → System**, then click the power icon (top right) and choose **Restart Home Assistant**.

### 3. Choose your machine

Click this button:

[![Open your Home Assistant instance and start setting up BCRS Availability.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=bcrs_availability)

Or go to **Settings → Devices & services → Add integration** and search for **BCRS Availability**.

Then type either:

- part of the machine's name, such as `Tampines Mall`, or
- your **postal code**, to list the 10 nearest machines.

Pick your machine from the list. That's it.

### 4. Put it on your dashboard

1. Open your dashboard and click the **pencil** (edit) icon.
2. Click **Add card**, then choose **Tile**.
3. For the entity, pick your machine's **Status**, e.g. *FairPrice Tampines Mall Status*.
4. Click **Save**.

Want a nicer-looking card? See [Fancier cards](#fancier-cards) below.

## What you get

Each machine you add shows up as a device with two sensors:

| Sensor | Example |
|---|---|
| **Status** | Available |
| **Hours today** | 10 am - 10 pm |

The status can be:

| Status | Meaning |
|---|---|
| **Available** | Working, and the shop is open |
| **Filling fast** | Over 75% full (only some machines report this) |
| **Closed** | Outside the shop's opening hours |
| **Maintenance** | Being cleaned or serviced |
| **Full** | Machine is full |
| **Out of service** | Broken or offline |
| **Removed** | No longer in service |
| **Not launched** | Not open yet |

It checks for updates every 5 minutes.

## Tracking more machines, or switching machines

- **Add another machine:** go to **Settings → Devices & services → BCRS Availability** and click the **Add** button on that page. Or use the setup button in step 3 again.
- **Switch to a different machine:** add the new one the same way, then delete the old one from that page with its **⋮** menu → **Delete**. Remember to update your dashboard card.

## Fancier cards

If you use these popular HACS card collections, you can copy a ready-made card:

- [Bubble Card version](cards/bubble-card.yaml): green, amber or red status pill plus today's hours
- [Mushroom version](cards/mushroom-card.yaml): coloured icon with status and today's hours

To use one:

1. Open the file above and copy everything in it.
2. On your dashboard, click the pencil icon, then **Add card**, and scroll down to **Manual**.
3. Paste it in.
4. Replace `fairprice_tampines_mall` with your machine. To find the right name, go to **Settings → Devices & services → BCRS Availability**, open your machine, and click its Status sensor. The entity ID is shown in its settings (cog icon).

## Something not working?

**Status shows "Unavailable".** Either recycle.gov.sg is down (wait a few minutes), or the machine has been renamed or removed on the site. Go to **Settings → Devices & services → BCRS Availability**. If it says the machine is "no longer listed", delete it and add it again.

**Hours today shows "Not listed".** The site doesn't publish opening hours for that machine. Its status still works.

**Can't find your machine.** Try fewer words (e.g. `Tampines` instead of `FairPrice Tampines Mall Level 1`), or search by postal code instead.

## About

This is a personal project. It's not affiliated with or endorsed by NEA, BCRS Ltd or recycle.gov.sg. It reads the public website's map data, which isn't an official API, so it may break if the website changes. To keep it polite, it checks each machine at most every 5 minutes.

Postal code search uses [OneMap](https://www.onemap.gov.sg/).

[MIT licence](LICENSE).

### For developers

The status logic is in [`status.py`](custom_components/bcrs_availability/status.py), with tests you can run using `python3 -m unittest discover tests` (no Home Assistant needed). Machines are found by their saved coordinates plus exact name, not by the site's internal IDs, because recycle.gov.sg reissues those IDs.
