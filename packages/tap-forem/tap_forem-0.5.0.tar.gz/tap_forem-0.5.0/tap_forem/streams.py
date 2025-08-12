"""Stream type classes for tap-forem."""

from __future__ import annotations

import typing as t

from singer_sdk import typing as th

from tap_forem.client import ForemStream, PaginatedForemStream

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

USER_TYPE = th.ObjectType(
    th.Property("name", th.StringType),
    th.Property("username", th.StringType),
    th.Property("twitter_username", th.StringType),
    th.Property("github_username", th.StringType),
    th.Property("website_url", th.StringType),
    th.Property("profile_image", th.StringType),
    th.Property("profile_image_90", th.StringType),
    th.Property("user_id", th.IntegerType),
)

ORG_TYPE = th.ObjectType(
    th.Property("name", th.StringType),
    th.Property("username", th.StringType),
    th.Property("slug", th.StringType),
    th.Property("profile_image", th.StringType),
    th.Property("profile_image_90", th.StringType),
)

FLARE_TAG_TYPE = th.ObjectType(
    th.Property("name", th.StringType),
    th.Property("bg_color_hex", th.StringType),
    th.Property("text_color_hex", th.StringType),
)


class Articles(PaginatedForemStream):
    """Articles stream."""

    name = "articles"
    path = "/articles"
    primary_keys = ("id",)

    schema = th.PropertiesList(
        th.Property(
            "id",
            th.IntegerType,
            description="The article's system ID",
            required=True,
        ),
        th.Property("type_of", th.StringType),
        th.Property("title", th.StringType),
        th.Property("description", th.StringType),
        th.Property("cover_image", th.StringType),
        th.Property("social_image", th.StringType),
        th.Property("city", th.StringType),
        th.Property("slug", th.StringType),
        th.Property("path", th.StringType),
        th.Property("url", th.StringType),
        th.Property("canonical_url", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("edited_at", th.DateTimeType),
        th.Property("crossposted_at", th.DateTimeType),
        th.Property("published_at", th.DateTimeType),
        th.Property("last_comment_at", th.DateTimeType),
        th.Property("tag_list", th.ArrayType(th.StringType)),
        th.Property("tags", th.StringType),
        th.Property("collection_id", th.IntegerType),
        th.Property("reading_time_minutes", th.IntegerType),
        th.Property("comments_count", th.IntegerType),
        th.Property("positive_reactions_count", th.IntegerType),
        th.Property("public_reactions_count", th.IntegerType),
        th.Property("page_views_count", th.IntegerType),
        th.Property("user", USER_TYPE),
        th.Property("organization", ORG_TYPE),
        th.Property("flare_tag", FLARE_TAG_TYPE),
        th.Property("readable_publish_date", th.StringType),
        th.Property("published_timestamp", th.DateTimeType),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Get query parameters."""
        params = super().get_url_params(context, next_page_token)
        params["tag"] = self.config.get("tag")
        return params

    def get_child_context(
        self,
        record: dict[str, t.Any],
        context: Context | None,  # noqa: ARG002
    ) -> dict[str, t.Any]:
        """Get context for article children."""
        return {"article_id": record["id"], "comments_count": record["comments_count"]}


class Comments(ForemStream):
    """Comments stream."""

    name = "comments"
    path = "/comments"
    primary_keys = ("id_code",)
    parent_stream_type = Articles

    schema = th.PropertiesList(
        th.Property(
            "id_code",
            th.StringType,
            description="The comment's system ID",
            required=True,
        ),
        th.Property("type_of", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("article_id", th.IntegerType),
        th.Property("body_html", th.StringType),
        th.Property("children", th.ArrayType(th.ObjectType())),
        th.Property("user", USER_TYPE),
    ).to_dict()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any] | str:
        """Get query parameters."""
        params = super().get_url_params(context, next_page_token)
        if context:
            params["a_id"] = context["article_id"]  # type: ignore[index]
        return params

    def should_sync(self, context: Context | None) -> bool:
        """Sync comments only if article has any."""
        return bool(context and context["comments_count"] > 0)
