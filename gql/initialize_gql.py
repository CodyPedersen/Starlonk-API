from gql.resolvers import *
from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, snake_case_fallback_resolvers, ObjectType
from gql.resolvers import satellite_by_id_resolver



# Define resolvers to query fields
query = ObjectType("Query")
mutation = ObjectType("Mutation")
#user = ObjectType("User")

# Resolvers
query.set_field("satellite_by_id", satellite_by_id_resolver)


# Load schema from schema.graphql
type_defs = load_schema_from_path("gql/schema.graphql")
schema = make_executable_schema(
    type_defs, query, mutation, snake_case_fallback_resolvers
)