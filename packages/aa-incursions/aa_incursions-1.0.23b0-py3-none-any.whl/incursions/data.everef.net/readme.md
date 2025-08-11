# <https://data.everef.net/>

Staging directory for <https://data.everef.net/>

Unless you need all possible incursion data, Load the existing django Fixture for a best effort copy of historical incursion data.

## Pulling in all Incursion Data

```shell
cd aa-incursions
rclone sync -v --checkers 2 --transfers 2 --http-url https://data.everef.net :http:/incursions incursions/data.everef.net/incursions/
```

## Updating Fixture

```shell
pyhon manage.py shell
```

```python
from incursions.everef import import_staging_history, import_staging_backfill
import_staging_backfill()
import_staging_history()
```

```shell
python manage.py dumpdata incursions.Incursion  -o /home/ozira/aa_dev/working/aa-incursions/incursions/fixtures/Incursion.json.xz
python manage.py dumpdata incursions.IncursionInfluence  -o /home/ozira/aa_dev/working/aa-incursions/incursions/fixtures/IncursionInfluence.json.xz
```
