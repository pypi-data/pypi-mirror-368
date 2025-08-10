from typing import Any
from msgspec import Struct, field

from ._additional import Author


__all__ = ["CommentGlyph", "CommentList"]

class CommentGlyph(Struct):
    votes_sum:          int | None            = field(name="votesSum")
    voted_value:        int | None            = field(name="votedValue")
    media_list:         list[Any] | None      = field(name="mediaList")
    parent_ndc_id:      int | None            = field(name="parentNdcId")
    parent_id:          str | None            = field(name="parentId")
    parent_type:        int | None            = field(name="parentType")
    content:            str | None            = field(name="content")
    extensions:         dict[str, Any] | None = field(name="extensions")
    ndc_id:             int | None            = field(name="ndcId")
    modified_time:      str | None            = field(name="modifiedTime")
    created_time:       str | None            = field(name="createdTime")
    comment_id:         str | None            = field(name="commentId")
    subcomments_count:  int | None            = field(name="subcommentsCount")
    type:               int | None            = field(name="type")
    author:             Author                = field(name="author")


class CommentList(Struct):
    comment_list:      list[CommentGlyph]    = field(name="commentList")