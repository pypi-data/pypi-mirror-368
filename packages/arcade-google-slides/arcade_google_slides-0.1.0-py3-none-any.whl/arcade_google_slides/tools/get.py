from typing import Annotated, cast

from arcade_tdk import ToolContext, ToolMetadataKey, tool
from arcade_tdk.auth import Google

from arcade_google_slides.decorators import with_filepicker_fallback
from arcade_google_slides.types import Presentation
from arcade_google_slides.utils import build_slides_service, convert_presentation_to_markdown


@tool(
    requires_auth=Google(
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
        ],
    ),
    requires_metadata=[ToolMetadataKey.CLIENT_ID, ToolMetadataKey.COORDINATOR_URL],
)
@with_filepicker_fallback
async def get_presentation_as_markdown(
    context: ToolContext,
    presentation_id: Annotated[str, "The ID of the presentation to retrieve."],
) -> Annotated[str, "The presentation textual content as markdown"]:
    """
    Get the specified Google Slides presentation and convert it to markdown.

    Only retrieves the text content of the presentation and formats it as markdown.
    """
    service = build_slides_service(context.get_auth_token_or_empty())

    response = service.presentations().get(presentationId=presentation_id).execute()

    return convert_presentation_to_markdown(cast(Presentation, response))
