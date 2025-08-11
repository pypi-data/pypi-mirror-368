from datetime import datetime

from ninja import NinjaAPI, Schema

from django.db import transaction
from django.utils.timezone import now

from allianceauth.eveonline.models import EveCharacter
from allianceauth.framework.api.user import get_main_character_from_user
from allianceauth.services.hooks import get_extension_logger

from incursions.api.schema import CharacterSchema
from incursions.models.waitlist import CharacterNote


class NoteSchema(Schema):
    character: CharacterSchema
    note: str
    author: CharacterSchema | None
    logged_at: datetime


class NotesSchema(Schema):
    notes: list[NoteSchema] | None


class AddNoteSchema(Schema):
    character_id: int
    note: str


logger = get_extension_logger(__name__)
api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    NotesAPIEndpoints(api)


class NotesAPIEndpoints:

    tags = ["Notes"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/notes", response={200: NotesSchema, 403: dict}, tags=self.tags)
        def list_notes(request, character_id: int):
            if not (request.user.has_perm("incursions.waitlist_notes_view") or request.user.has_perm("incursions.waitlist_notes_manage")):
                logger.warning(f"User {request.user} denied viewing notes for character {character_id}")
                return 403, {"error": "Permission denied"}

            if not EveCharacter.objects.filter(character_id=character_id).exists():
                logger.info(f"Character {character_id} not found, returning empty note list")
                return NotesSchema(notes=[])

            notes = list(CharacterNote.objects.filter(character__character_id=character_id).select_related("character", "author"))
            logger.info(f"Returned {len(notes)} notes for character {character_id} to user {request.user}")
            return NotesSchema(notes=notes)

        @api.post("/notes/add", tags=self.tags)
        def add_note(request, payload: AddNoteSchema):
            if not request.user.has_perm("incursions.waitlist_notes_manage"):
                logger.warning(f"User {request.user} denied adding note to character {payload.character_id}")
                return 403, {"error": "Permission denied"}

            try:
                character = EveCharacter.objects.only("pk").get(character_id=payload.character_id)
            except EveCharacter.DoesNotExist:
                logger.error(f"Character {payload.character_id} not found")
                return {"status": "Character not found"}

            with transaction.atomic():
                CharacterNote.objects.create(
                    character=character,
                    note=payload.note,
                    author=get_main_character_from_user(request.user),
                    logged_at=now()
                )

            logger.info(f"Note added to character {payload.character_id} by user {request.user}")
            return {"status": "OK"}
