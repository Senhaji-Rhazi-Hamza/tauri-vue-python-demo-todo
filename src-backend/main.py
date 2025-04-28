from sanic import Sanic
from sanic.response import json
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    Integer,
    String,
    MetaData,
)
from sqlalchemy import insert, delete, select
from datetime import datetime
from platformdirs import user_data_dir
import os 

APP_NAME = "TauriTodoPythonBackend"
DATA_APP_DIR = user_data_dir(APP_NAME)
os.makedirs(DATA_APP_DIR, exist_ok=True)

engine = create_engine(f"sqlite:///{DATA_APP_DIR}/tasks.db", future=True)
metadata = MetaData()

task_table = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column(
        "created_at", String
    ),  ## we keep it as a string to avoid serialization pbs for demo purposes
)

metadata.create_all(engine)

app = Sanic(APP_NAME)


@app.route("/")
async def index(request):
    return json({"status": "running"})


@app.get("/greet")
async def greet_get(request):
    return json({"message": "Hello from GET"})


@app.post("/greet")
async def greet_post(request):
    name = request.json.get("name", "World")
    return json({"message": f"Hello, {name} from POST"})


@app.get("/tasks")
async def tasks_get(request):
    with engine.begin() as conn:
        tasks_result = [dict(el) for el in conn.execute(select(task_table)).mappings()]
        return json(
            {
                "message": "Getting tasks for client",
                "data": tasks_result,
            }
        )


@app.post("/tasks")
async def tasks_post(request):
    data = {
        "name": request.json.get("taskName", "no-name"),
        "created_at": request.json.get("createdAt"),
        "id": request.json.get("taskId"),
    }
    with engine.begin() as conn:
        conn.execute(insert(task_table).values(**data))
        print(f"Added task: {data['name']}")
    return json({"message": f"Created task name {data.get('name')}"})


@app.delete("/tasks")
async def tasks_delete(request):
    task_id = request.json.get("taskId", "no-id")
    with engine.begin() as conn:
        conn.execute(delete(task_table).where(task_table.c.id == task_id))
    return json({"message": f"Deleted task of id {task_id}"})


if __name__ == "__main__":

    from sanic.server import serve
    import asyncio

    async def start():
        await serve(
            app,
            host="127.0.0.1",
            port=8000,
            single_process=True,   # no forking at all
            workers=1,             # exactly one process
            access_log=False,      # optional, quiet STDOUT clutter
        )

    asyncio.run(start)