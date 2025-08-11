import re

from corptools.models import EveItemType

from incursions.app_settings import (
    EVECATEGORY_CHARGE, EVECATEGORY_DEPLOYABLE, EVECATEGORY_IMPLANTS,
)

ALWAYS_CARGO_CATEGORIES = [EVECATEGORY_IMPLANTS, EVECATEGORY_CHARGE, EVECATEGORY_DEPLOYABLE]


class FitError(Exception):
    pass


class FittingParser:
    def __init__(self, ship: int, modules: dict[int, int] | None = None, cargo: dict[int, int] | None = None):
        self.ship = ship
        self.modules = modules if modules is not None else {}
        self.cargo = cargo if cargo is not None else {}

    @classmethod
    def from_dna(cls, dna: str) -> "FittingParser":
        pieces = dna.split(':')
        if not pieces or pieces[0] == "":
            raise FitError("DNA string is empty or missing ship")
        try:
            ship = int(pieces[0])
        except ValueError:
            raise FitError("Invalid ship type ID")
        cargo: dict[int, int] = {}
        modules: dict[int, int] = {}
        i = 0
        for piece in pieces[1:]:
            if not piece:
                continue
            i += 1
            if i > 1000:
                raise FitError("Too many pieces in DNA")
            mod_split = piece.split(';', 1)
            type_id_str = mod_split[0]
            # If the type id ends with '_' then it is cargo
            if type_id_str.endswith('_'):
                try:
                    type_id = int(type_id_str[:-1])
                except ValueError:
                    raise FitError("Invalid type ID in cargo")
                is_cargo = True
            else:
                try:
                    type_id = int(type_id_str)
                except ValueError:
                    raise FitError("Invalid type ID")
                # Use your database to check if this type is always cargo.
                is_cargo = True if EveItemType.objects.get(type_id=type_id).group.category.category_id in ALWAYS_CARGO_CATEGORIES else False
            # Count defaults to 1 if missing.
            count = 1
            if len(mod_split) == 2 and mod_split[1]:
                try:
                    count = int(mod_split[1])
                except ValueError:
                    raise FitError("Invalid count in DNA")
            # Choose dictionary based on whether this is cargo or module.
            dest = cargo if is_cargo else modules
            dest[type_id] = dest.get(type_id, 0) + count
        return cls(ship, modules, cargo)

    def to_dna(self) -> str:
        # Start with ship followed by a colon
        dna = f"{self.ship}:"
        # Append modules: format "{id};{count}:"
        for type_id, count in self.modules.items():
            dna += f"{type_id};{count}:"
        # Append cargo: if type is not always cargo, add an underscore after the id.
        for type_id, count in self.cargo.items():
            if EveItemType.objects.get(type_id=type_id).group.category.category_id in ALWAYS_CARGO_CATEGORIES:
                dna += f"{type_id};{count}:"
            else:
                dna += f"{type_id}_;{count}:"
        return dna + ":"

    @classmethod
    def from_eft(cls, eft: str) -> "FittingParser":
        fit: FittingParser | None = None
        section = 0

        for line in eft.splitlines():
            line = line.strip()

            # Look for the fitting header.
            if line.startswith('[') and line.endswith(']') and ',' in line:
                if fit is not None:
                    raise FitError("Multiple fitting headers found; expected only one fitting in EFT input.")
                # Remove the brackets and split on the first comma.
                line_inner = line[1:-1]
                pieces = line_inner.split(',', 1)
                ship_name = pieces[0].strip()
                if not pieces[1].strip():
                    raise FitError("Missing ship name in EFT header")
                # Look up the ship ID from the name.
                try:
                    ship = EveItemType.objects.get(name__iexact=ship_name).type_id
                except EveItemType.DoesNotExist:
                    ship = EveItemType.objects.get_or_create_from_esi_name(ship_name)[0].type_id
                fit = cls(ship, modules={}, cargo={})
                section = 0  # Reset section counter for the current fit.
            elif fit is not None:
                # If the line indicates an empty section, increase section counter.
                if line == "":
                    section += 1
                    continue

                # Skip lines that indicate empty modules.
                if line.startswith("[Empty "):
                    continue

                # Remove script/charge after comma (e.g., "Sentient Sensor Booster, ECCM Script")
                line = line.split(',')[0].strip()

                # Parse module line with optional stack count
                m = re.match(r"(.+?)(?:\s*x\s*(\d+))?$", line)
                if not m:
                    raise FitError("Could not parse EFT line: " + line)
                type_name = m.group(1).strip()
                try:
                    type_id = EveItemType.objects.get(name__iexact=type_name).type_id
                except EveItemType.DoesNotExist:
                    type_id = EveItemType.objects.get_or_create_from_esi_name(type_name)[0].type_id
                count = int(m.group(2)) if m.group(2) is not None else 1
                stacked = m.group(2) is not None

                # Determine if this item is cargo:
                # If section >= 7 then treat as cargo; otherwise, query the type info.
                if section >= 7:
                    is_cargo = True
                else:
                    type_obj = EveItemType.objects.get(type_id=type_id)

                    is_cargo = type_obj.group.category.category_id in ALWAYS_CARGO_CATEGORIES or (stacked and type_obj.group.category.name != "Drone")

                # Add to cargo or modules.
                dest = fit.cargo if is_cargo else fit.modules
                dest[type_id] = dest.get(type_id, 0) + count
            else:
                # Skip lines until a header is found.
                continue

        if fit is None:
            raise FitError("Invalid EFT format; no fitting header found")

        return fit

    def to_analysis(self, doctrine: "FittingParser", name: str | None = None) -> dict:
        def diff_modules(ref: dict[int, int], actual: dict[int, int]) -> tuple[dict[int, int], dict[int, int]]:
            missing = {}
            extra = {}
            for type_id, expected in ref.items():
                actual_count = actual.get(type_id, 0)
                if actual_count < expected:
                    missing[type_id] = expected - actual_count
            for type_id, actual_count in actual.items():
                expected = ref.get(type_id, 0)
                if actual_count > expected:
                    extra[type_id] = actual_count - expected
            return missing, extra

        missing, extra = diff_modules(doctrine.modules, self.modules)
        cargo_missing, cargo_extra = diff_modules(doctrine.cargo, self.cargo)

        # Stub downgrade logic (can implement real downgrade/upgrade logic later)
        downgraded: dict[int, dict[int, int]] = {}
        upgraded: dict[int, dict[int, int]] = {}

        return {
            "name": name or "Unnamed Analysis",
            "missing": missing,
            "extra": extra,
            "cargo_missing": cargo_missing,
            "downgraded": downgraded,
            "upgraded": upgraded,
        }
