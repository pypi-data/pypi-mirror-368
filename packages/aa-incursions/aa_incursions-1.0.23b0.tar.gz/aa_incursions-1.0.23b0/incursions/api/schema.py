from ninja import Schema


class CharacterSchema(Schema):
    character_id: int
    character_name: str
    corporation_id: int | None = None
    alliance_id: int | None = None


class CorporationSchema(Schema):
    corporation_id: int
    corporation_name: str
    alliance_id: int | None = None


class AllianceSchema(Schema):
    alliance_id: int
    alliance_name: str


class HullSchema(Schema):
    id: int
    name: str
