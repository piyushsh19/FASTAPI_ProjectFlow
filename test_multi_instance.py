
# test_multi_instance.py

import asyncio
import uuid

import httpx
import websockets


INSTANCE_A = "http://127.0.0.1:8000"
INSTANCE_B_WS = "ws://127.0.0.1:8001"


async def main():
    email = f"redis-test-{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPassword123!"

    async with httpx.AsyncClient(timeout=10) as client:

        # 1. Register a user through Instance A.
        register_response = await client.post(
            f"{INSTANCE_A}/auth/register",
            json={
                "name": "Redis Integration Tester",
                "email": email,
                "password": password,
            },
        )

        assert register_response.status_code == 201

        # 2. Login through Instance A.
        login_response = await client.post(
            f"{INSTANCE_A}/auth/login",
            data={
                "username": email,
                "password": password,
            },
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # 3. Create a project through Instance A.
        project_response = await client.post(
            f"{INSTANCE_A}/projects/",
            headers=headers,
            json={
                "name": "Redis Multi Instance Test",
                "description": "Testing cross-instance events",
            },
        )

        assert project_response.status_code == 201

        project_id = project_response.json()["id"]

        print(f"Project created: {project_id}")

        # 4. Connect WebSocket to Instance B.
        websocket_url = (
            f"{INSTANCE_B_WS}/ws/projects/"
            f"{project_id}?token={token}"
        )

        async with websockets.connect(websocket_url) as websocket:

            print("Connected to Instance B WebSocket")

            # 5. Create task through Instance A.
            task_response = await client.post(
                f"{INSTANCE_A}/projects/{project_id}/tasks",
                headers=headers,
                json={
                    "title": "Cross-instance Redis task",
                    "description": "Testing Redis Pub/Sub",
                    "status": "todo",
                    "priority": "high",
                },
            )

            assert task_response.status_code == 201

            print("Task created through Instance A")

            # 6. Wait for event on Instance B.
            event = await asyncio.wait_for(
                websocket.recv(),
                timeout=10,
            )

            import json

            event = json.loads(event)

            print("Received event:", event)

            assert event["type"] == "task.created"
            assert event["project_id"] == project_id
            assert event["task"]["title"] == (
                "Cross-instance Redis task"
            )

            print("\nSUCCESS: Redis delivered the event across instances!")


if __name__ == "__main__":
    asyncio.run(main())
