from bottle import Bottle, json_dumps, request

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

app = Bottle()



@app.get("/")
def index():
    return json_dumps({"status": "running"})



@app.get("/tasks")
def tasks_get():
    with engine.begin() as conn:
        tasks_result = [dict(el) for el in conn.execute(select(task_table)).mappings()]
        return json_dumps(
            {
                "message": "Getting tasks for client",
                "data": tasks_result,
            }
        )


@app.post("/tasks")
def tasks_post():
    data = {
        "name": request.json.get("taskName", "no-name"),
        "created_at": request.json.get("createdAt"),
        "id": request.json.get("taskId"),
    }
    with engine.begin() as conn:
        conn.execute(insert(task_table).values(**data))
        print(f"Added task: {data['name']}")
    return json_dumps({"message": f"Created task name {data.get('name')}"})


@app.delete("/tasks")
def tasks_delete():
    task_id = request.json.get("taskId", "no-id")
    with engine.begin() as conn:
        conn.execute(delete(task_table).where(task_table.c.id == task_id))
    return json_dumps({"message": f"Deleted task of id {task_id}"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)