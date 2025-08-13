## Overview

UAI is a Unified Agent Interface that provides a unified way to interact with Agents or AI Applications made with different frameworks and technologies (Framework Agnostic).
It provides a set of endpoints to create, manage, and interact with chat sessions and long-running tasks, allowing users to send messages, retrieve artifacts, and manage the lifecycle of these sessions.
Session and Run Management will be handled by the UAI backend using PostgreSQL and Redis for data storage and caching (For the initial implementation we are using in-memory storage).
for runs we can use procrastinate library (pure-Python task queue that uses Postgres as the broker, supports retries, scheduling, locks, Django/ASGI integration, and comes with a nice CLI. Solid fit for FastAPI + Postgres without extra infra).


## Endpoints

- /chat
    - POST / # Create a new chat session, returns session_id
    - POST /{session_id} # Send a message to a chat session (can include images, text, files)
    - DELETE /{session_id} # Cancel or terminate a chat session including all its resources
    - GET /{session_id}/messages # Retrieve all messages in a chat session
    - GET /{session_id}/artifacts # Retrieve all artifacts produced by a chat session
    - GET /{session_id}/artifacts/{artifact_id} # Retrieve a specific artifact produced by a chat session
    - POST /next # Endpoint to perform sessionless chats
        - Request
            - user_input - text images, files
            - state - usually messages or some context format the agent supports (JSON)
        - Response
            - state - updated context or messages (JSON)
            - artifacts - any new artifacts produced (JSON)

- /run (Long running tasks)
    - POST / # Create a new long-running task, returns task_id, estimated_completion_time
    - GET /{task_id} # Retrieve the status of a long-running task (includes the output text if the task is complete)
    - DELETE /{task_id} # Cancel or terminate a long-running task including all its resources
    - POST /{task_id}/input # Provide input to a long-running task (If applicable) (can include images, text, files)
    - GET /{task_id}/artifacts # Retrieve list of artifacts produced by a long-running task
    - GET /{task_id}/artifacts/{artifact_id} # Retrieve a specific artifact produced by a long-running task
    - POST /{task_id}/logs # Send logs to a long-running task
