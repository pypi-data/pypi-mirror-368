# Incursions for Alliance Auth

Incursion Tools for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth/).

## Features

- AA-Discordbot Cogs for information about active incursions, their status and any set Focus
- Webhook notifications for new incursions and them changing state (Mobilizing/Withdrawing)

- Waitlist forked from TLA and _heavily_ updated

## Planned Features

- Waitlist
- AA Fittings Integration
- Secure Groups Integration

## Installation

### Step 1 - Pre_Requisites

Incursions is an App for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth/), Please make sure you have this installed. Incursions is not a standalone Django Application

Incursions needs the App [AA Routing](https://gitlab.com/tactical-supremacy/aa-routing/-/tree/main/routing?ref_type=heads) in order to give the spawn bot context

Incursions needs the App [AA Discord Bot](https://github.com/Solar-Helix-Independent-Transport/allianceauth-discordbot) for safe integration with the discord service and discord multiverse, it also delivers some future features

Incursions needs the App [Corp Tools](https://github.com/Solar-Helix-Independent-Transport/allianceauth-corp-tools/tree/master/corptools) to feed the Waitlist and its Map Data. You can opt out of using the Waitlist and any of corp-tools auditing

### Step 2 - Install app

```shell
pip install aa-incursions
```

### Step 3 - Configure Auth settings

Configure your Auth settings (`local.py`) as follows:

- Add the following `INSTALLED_APPS` in `local.py`

```python
'incursions',
'corptools',
```

- Add below lines to your settings file:

```python
## Settings for AA-Incursions ##
# Route is Cached for 300 Seconds, if you aren't riding the Kundalini Manifest to the last minute
# Feel free to adjust this to minute='*/5'
CELERYBEAT_SCHEDULE['incursions_update_incursions'] = {
    'task': 'incursions.tasks.update_incursions',
    'schedule': crontab(minute='*/1', hour='*'),
}
# Routes are Cached for 5 Seconds
CELERYBEAT_SCHEDULE['incursions_update_all_fleets'] = {
    'task': 'incursions.tasks.update_all_fleets',
    'schedule': crontab(minute='*/1', hour='*'),
}
```

### Step 4 - Maintain Alliance Auth

- Run migrations `python manage.py migrate`
- Gather your staticfiles `python manage.py collectstatic`
- Restart your project `supervisorctl restart myauth:`

### Step 5 - Pre-Load

Preload some expected incursion data. The frontend _should_ adapt to any custom values But it is tested with these.

```shell
python manage.py loaddata waitlist_badges.json
python manage.py loaddata waitlist_category.json
python manage.py loaddata waitlist_category_rule.json
python manage.py loaddata waitlist_roles.json
```

### Step 6 - Setup Waitlist Dependencies

The Waitlist was built to require a Server-Sent Event backend that i have not yet replaced.

#### Bare Metal

Generate a Secret with `openssl rand -hex 32`, use this later in secret=

```shell
git clone https://github.com/luna-duclos/waitlist-sse
docker buildx build . -t tla/sse --load
docker run -d -p 8001:8000 --env SSE_SECRET="0000000000000000000000000000000000000000000000000000000000000000" tla/sse
```

route sse.domain to localhost:8001 in Nginx

#### Docker

git clone <https://github.com/luna-duclos/waitlist-sse>

in NPM route sse.domain route to `sse-server` `8000`
Generate a Secret with `openssl rand -hex 32`, use this in your docker compose
Add the following to your `Docker-Compose.yml`

```docker
  sse-server:
    image: "tla/sse:latest"
    pull_policy: never
    build: ./waitlist-sse
    expose:
      - 8000
    environment:
      SSE_SECRET: "0000000000000000000000000000000000000000000000000000000000000000"
```

## Waitlist Features Detail

### Waitlist

### Categories / Category Rules

For easy filtering of ships into basic categories for prioritization and fleet composition.
Some functions of the waitlist expect at minimum Marauder Logi Vindi and Other, this is a work in progress
The Sponge category is for anything that lowers the isk/hr of the fleet, like Ishtars

### Badges

Badges are both medals of Merit and a sign of recognition that you have met a series of requirements at a glance.
You may use Logi to dictate known quality Logistics pilots to prioritise
Or use DPS / Alt to highlight a player has met a series of DPS / Skills / Fitting Requirements
Badges are fully dynamic and you can assign as many or as

### ~~Roles~~

You May be familiar with Roles or Commanders from other HS waitlists. This feature has been intentionally stripped. Use AA Groups instead.

### Approved Fittings / Approved Implants

the /fits page and the fits that ships are compared to are fully dynamic from the DB.
The implants are _not_ yet, that frontend page is still hardcoded, but they are used for backend comparison

## Permissions

| Codename                                | Perm                                 | Description                         |
| --------------------------------------- | ------------------------------------ | ----------------------------------- |
| `basic_waitlist`                        | Waitlist Access                      | Can Access the Waitlist Application |
| `waitlist_alts_view`                    | View - all of a users Alts ! Danger? |                                     |
| `waitlist_announcements_manage`         | Announcements - Manage               |                                     |
| `waitlist_badges_view`                  | Badges - View                        |                                     |
| `waitlist_badges_manage`                | Badges - Manage                      |                                     |
| `waitlist_bans_view`                    | Bans - View                          |                                     |
| `waitlist_bans_manage`                  | Bans - Manage                        |                                     |
| `waitlist_documentation_view`           | Documentation - View                 |                                     |
| `waitlist_fleet_view`                   | Fleet Composition                    |                                     |
| `waitlist_history_view`                 | Fleet History                        |                                     |
| `waitlist_notes_view`                   | Notes - View                         |                                     |
| `waitlist_notes_manage`                 | Notes - Manage                       |                                     |
| `waitlist_search`                       | Search                               |                                     |
| `waitlist_stats_view`                   | Fleet Stats                          |                                     |
| `waitlist_skills_view`                  | Skills                               |                                     |
| `waitlist_pilot_view`                   | Pilot Information                    |                                     |
| # Waitlist Context Permissions          |                                      |                                     |
| `waitlist_context_a`                    | Context: Number of Pilots            |                                     |
| `waitlist_context_b`                    | Context: Ship Types                  |                                     |
| `waitlist_context_c`                    | Context: Time in Waitlist            |                                     |
| `waitlist_context_d`                    | Context: Pilot Names                 |                                     |
| `waitlist_implants_view`                | Context: Implants                    |                                     |
| `waitlist_manage_waitlist`              | Waitlist Manage                      |                                     |
| `waitlist_manage_waitlist_approve_fits` | Waitlist Manage Fits                 |                                     |
| # ESI Permissions                       |                                      |                                     |
| `waitlist_esi_show_info`                | Show Info                            |                                     |
| `waitlist_esi_search`                   | Search - ESI                         |                                     |

## Settings

| Name                            | Description                                                                  | Default                                                                                                               |
| ------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `SSE_SITE_URL`                  | The Site URL for the SSE server, usually sse.example.com                     | GENERATED FROM CODE                                                                                                   |
| `SSE_SECRET`                    | Must Match in `local.py` and the SSE Docker Container                        | "0000000000000000000000000000000000000000000000000000000000000000"                                                    |
| `INCURSIONS_AUTO_HIGHSEC_FOCUS` | Whether or not to set the current Focus to a new HS spawn automatically      | True                                                                                                                  |
| `INCURSIONS_SCOPES_BASE`        | Not really used, Corp-Tools controls auditing                                | ["publicData", "esi-skills.read_skills.v1", "esi-clones.read_implants.v1"]                                            |
| `INCURSIONS_SCOPES_FC`          | Not really optional, R/W Fleet, Open Window and Search (yes its named badly) | ["esi-fleets.read_fleet.v1", "esi-fleets.write_fleet.v1", "esi-ui.open_window.v1", "esi-search.search_structures.v1"] |

## Contributing

Make sure you have signed the [License Agreement](https://developers.eveonline.com/resource/license-agreement) by logging in at <https://developers.eveonline.com> before submitting any pull requests. All bug fixes or features must not include extra superfluous formatting changes.
