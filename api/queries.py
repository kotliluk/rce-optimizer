from ariadne import convert_kwargs_to_snake_case, ObjectType


def list_posts_resolver(_, __):
    return [
        {
            "id": "id01",
            "title": "Post 01",
            "description": "dddd",
        },
        {
            "id": "id02",
            "title": "Post 02",
            "description": "dddd",
        },
    ]


@convert_kwargs_to_snake_case
def get_post_resolver(_, __, id):
    return {
        "id": id,
        "title": "Post 01",
        "description": "dddd",
    }


query = ObjectType("Query")
query.set_field("listPosts", list_posts_resolver)
query.set_field("getPost", get_post_resolver)
