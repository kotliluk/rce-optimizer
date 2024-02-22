from ariadne import load_schema_from_path, make_executable_schema, graphql_sync, snake_case_fallback_resolvers
from ariadne.explorer import ExplorerGraphiQL
from flask import Flask, request, jsonify

from api.mutations import mutation
from api.queries import query

app = Flask(__name__)


@app.route('/')
def api_root():
    return 'Use GraphQL API'


type_defs = load_schema_from_path("api/schema.graphql")
schema = make_executable_schema(
    type_defs, query, mutation, snake_case_fallback_resolvers
)
explorer_html = ExplorerGraphiQL().html(None)


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return explorer_html, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code
