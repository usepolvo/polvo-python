"""
GraphQL examples using Polvo Core.

This example demonstrates how to use the GraphQL client to interact with GraphQL APIs.
"""

import asyncio

import usepolvo_core as pv


def graphql_query_example():
    """Example of making a GraphQL query."""
    # Create a GraphQL client
    client = pv.GraphQLClient(endpoint="https://countries.trevorblades.com/graphql")

    # Define a simple query for country data
    query = """
    query GetCountries {
      countries {
        code
        name
        capital
        currency
      }
    }
    """

    # Execute the query
    response = client.query(query)
    data = response.json()

    print(f"Status: {response.status_code}")
    print(f"Found {len(data['data']['countries'])} countries")

    # Print the first 3 countries
    for country in data["data"]["countries"][:3]:
        print(f"Country: {country['name']} ({country['code']})")
        print(f"  Capital: {country['capital']}")
        print(f"  Currency: {country['currency']}")


def graphql_query_with_variables_example():
    """Example of making a GraphQL query with variables."""
    # Create a GraphQL client
    client = pv.GraphQLClient(endpoint="https://countries.trevorblades.com/graphql")

    # Define a query with variables
    query = """
    query GetCountry($code: ID!) {
      country(code: $code) {
        name
        capital
        currency
        languages {
          name
          native
        }
      }
    }
    """

    # Execute the query with variables
    variables = {"code": "BR"}
    response = client.query(query, variables=variables)
    data = response.json()

    country = data["data"]["country"]
    print(f"Country: {country['name']}")
    print(f"  Capital: {country['capital']}")
    print(f"  Currency: {country['currency']}")
    print("  Languages:")
    for lang in country["languages"]:
        print(f"    - {lang['name']} ({lang['native']})")


async def async_graphql_example():
    """Example of using the async GraphQL client."""
    # Create an async GraphQL client
    client = pv.AsyncGraphQLClient(endpoint="https://countries.trevorblades.com/graphql")

    # Define two queries to run concurrently
    queries = [
        """
        query {
          country(code: "US") {
            name
            capital
          }
        }
        """,
        """
        query {
          country(code: "JP") {
            name
            capital
          }
        }
        """,
    ]

    # Execute queries concurrently
    tasks = [client.query(query) for query in queries]
    responses = await asyncio.gather(*tasks)

    # Process results
    for i, response in enumerate(responses):
        data = response.json()
        country = data["data"]["country"]
        print(f"Async Query {i+1}: {country['name']} - Capital: {country['capital']}")


if __name__ == "__main__":
    print("GraphQL Query Example:")
    graphql_query_example()

    print("\nGraphQL Query with Variables Example:")
    graphql_query_with_variables_example()

    print("\nAsync GraphQL Example:")
    asyncio.run(async_graphql_example())
