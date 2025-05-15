"""
REST Resource Pattern examples using Polvo Core.

This example demonstrates how to use the ResourceClient for RESTful APIs.
"""

import asyncio
import json

import usepolvo_core as pv


def rest_client_example():
    """Example using the RestClient."""
    # Create a REST client
    client = pv.RestClient(base_url="https://jsonplaceholder.typicode.com")

    # Make a simple request using the base client
    response = client.get("/posts/1")
    print(f"Simple GET Status: {response.status_code}")
    print(f"Post Data: {json.dumps(response.json(), indent=2)}")

    # Create a resource for posts
    posts = client.resource("posts")

    # Get all posts
    response = posts.get()
    print(f"All Posts Count: {len(response.json())}")

    # Get a specific post using the resource call syntax
    post = posts(1)
    response = post.get()
    print(f"Single Post Title: {response.json()['title']}")

    # Create a new post
    response = posts.post(
        json={
            "title": "Polvo REST Client",
            "body": "This post was created with Polvo REST Client",
            "userId": 1,
        }
    )
    print(f"Create Post Status: {response.status_code}")
    print(f"Created Post: {json.dumps(response.json(), indent=2)}")

    # Update a post
    response = post.put(
        json={
            "id": 1,
            "title": "Updated with Polvo",
            "body": "This post was updated with Polvo REST Client",
            "userId": 1,
        }
    )
    print(f"Update Post Status: {response.status_code}")
    print(f"Updated Post: {json.dumps(response.json(), indent=2)}")

    # Delete a post
    response = post.delete()
    print(f"Delete Post Status: {response.status_code}")


def nested_resource_example():
    """Example using nested resources."""
    client = pv.RestClient(base_url="https://jsonplaceholder.typicode.com")

    # Create resources for users and their posts
    users = client.resource("users")
    user_1 = users(1)
    user_1_posts = user_1("posts")

    # Get all posts for user 1
    response = user_1_posts.get()
    print(f"User 1 Posts Count: {len(response.json())}")

    # Alternative way using path in get()
    response = users(1).get("posts")
    print(f"User 1 Posts Count (alt): {len(response.json())}")

    # Get comments for a specific post from user 1
    post_1 = user_1_posts(1)
    response = post_1.get("comments")
    print(f"Post 1 Comments Count: {len(response.json())}")


async def async_rest_client_example():
    """Example using the AsyncRestClient."""
    # Create an async REST client
    async with pv.AsyncRestClient(base_url="https://jsonplaceholder.typicode.com") as client:
        # Create a resource for todos
        todos = client.resource("todos")

        # Get a specific todo
        todo_1 = todos(1)
        response = await todo_1.get()
        print(f"Async Todo 1 Title: {response.json()['title']}")

        # Get multiple todos concurrently
        tasks = [todos(i).get() for i in range(1, 6)]
        responses = await asyncio.gather(*tasks)

        print("Async Todos Titles:")
        for i, response in enumerate(responses):
            print(f"  {i+1}: {response.json()['title']}")


if __name__ == "__main__":
    print("REST Client Example:")
    rest_client_example()

    print("\nNested Resource Example:")
    nested_resource_example()

    print("\nAsync REST Client Example:")
    asyncio.run(async_rest_client_example())
