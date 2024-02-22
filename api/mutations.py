from ariadne import convert_kwargs_to_snake_case, ObjectType


@convert_kwargs_to_snake_case
def create_post_resolver(_, __, title, description):
    print(title, description)
    return {
        "id": "IDDDD",
        "title": title,
        "description": description,
    }


mutation = ObjectType("Mutation")
mutation.set_field("createPost", create_post_resolver)
