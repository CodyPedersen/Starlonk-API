from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, snake_case_fallback_resolvers, ObjectType
from gql.resolvers import satellite_by_id_resolver, satellites_resolver, process_by_id_resolver, processes_resolver


''' Initialize resolvers '''
# Define schema objects
query = ObjectType("Query")
mutation = ObjectType("Mutation")

# Resolvers
query.set_field("satellite_by_id", satellite_by_id_resolver)
query.set_field("satellites", satellites_resolver)
query.set_field("process_by_id", process_by_id_resolver)
query.set_field("processes", processes_resolver)


''' Initialize ariadne '''
# Get defined schema
type_defs = load_schema_from_path("gql/schema.graphql")

# Associate schema with resolvers (make executable)
schema = make_executable_schema(
    type_defs, query, mutation, snake_case_fallback_resolvers
)