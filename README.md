# BCRS Availability for Home Assistant

See at a glance whether your nearest **BCRS machine** (the Return Right reverse vending machines for Singapore's Beverage Container Return Scheme) is available, full or closed, right on your Home Assistant dashboard.

It uses the same live information as the map on [recycle.gov.sg](https://www.recycle.gov.sg/materials/beverage).

## What you'll need

- Home Assistant 2025.2 or newer
- [HACS](https://hacs.xyz/docs/use/download/download/) installed

## Install

You only do this once.

### 1. Add this repository to HACS

1. In Home Assistant, click **HACS** in the sidebar.
2. Click the **⋮** menu in the top-right corner and choose **Custom repositories**.
3. In **Repository**, paste:
   ```
   https://github.com/kalestarler/bcrs-availability-for-home-assistant
   ```
4. In **Type**, choose **Integration**.
5. Click **Add**, then close the dialog.

### 2. Download it

1. In HACS, search for **BCRS Availability** and click it.
2. Click **Download** (bottom right), then **Download** again to confirm.

### 3. Restart Home Assistant

1. Go to **Settings → System**.
2. Click the **power icon** in the top-right corner.
3. Choose **Restart Home Assistant**.

Wait a minute or two for it to come back.

## Add a BCRS machine

Do this for each machine you want to track.

1. Go to **Settings → Devices & services**.
2. Click **+ Add integration** (bottom right).
3. Search for **BCRS Availability** and click it.
4. Type either:
   - part of the machine's name, such as `Tampines Mall`, or
   - a **postal code**, such as `529510`, to list the 10 nearest machines.
5. Click **Submit**.
6. Pick your machine from the list, then click **Submit**.
7. Optionally choose an area, then click **Finish**.

The machine now shows up under **Settings → Devices & services → BCRS Availability**, with two sensors such as *FairPrice Tampines Mall Status* and *FairPrice Tampines Mall Hours today*.

## Put it on your dashboard

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

## Switching or removing a machine

To switch to a different machine, first add the new one using the steps in [Add a BCRS machine](#add-a-bcrs-machine).

Then remove the old one:

1. Go to **Settings → Devices & services → BCRS Availability**.
2. Next to the machine you no longer want, click **⋮** and choose **Delete**.
3. Update any dashboard card that used it.

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

Postal code search uses [OneMap](https://www.onemap.gov.sg/). The icon uses the recycle symbol from [Material Design Icons](https://pictogrammers.com/library/mdi/) (Apache 2.0).

It's only listed in HACS for Home Assistant instances set to Singapore, since BCRS machines only exist there.

[MIT licence](LICENSE).

### For developers

The status logic is in [`status.py`](custom_components/bcrs_availability/status.py), with tests you can run using `python3 -m unittest discover tests` (no Home Assistant needed). Machines are found by their saved coordinates plus exact name, not by the site's internal IDs, because recycle.gov.sg reissues those IDs.
