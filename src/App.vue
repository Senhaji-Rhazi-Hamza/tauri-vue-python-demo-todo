<script setup>
import { ref, onMounted } from "vue";

// import { callPython } from "./utils";
import { invoke } from "@tauri-apps/api/core";

function callPython(method, endpoint, payload = null) {

return invoke('py_api', {
  method,
  endpoint,
  payload
})}

const greetMsg = ref("");
const taskName = ref("");

const tasks = ref([]);

onMounted(async () => {
  tasks.value = await callPython("GET", "tasks").then(response => response.data)
  console.log("task value values")
  console.log(tasks.value)
})

async function greet() {
  // Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
  console.log("calling log cosnole");
  // greetMsg.value = await callPython("GET" , "greet" , {}) || 'Failed to call backend';
}

async function deleteTask(taskId) {
  console.log("deleting task :" + `${taskId}`);
  tasks.value = tasks.value.filter((task) => task.id !== taskId);
  const response_data = await callPython("DELETE", "tasks", {taskId: taskId})
    .then(() => {
      tasks.value = tasks.value.filter((task) => task.id !== taskId);
    })
    .catch((error) => {
      console.error("Python call failed:", error);
    });
  console.log(response_data)
}
async function addTask() {
  const task = {
    id: tasks.value.length + 1,
    createdAt: new Date().toISOString(),
    taskName: taskName.value,
  }
  const response_data = await callPython("POST", "tasks", task)
    .then(() => {
      tasks.value.push({...task, name: task.taskName })
    })
    .catch((error) => {
      console.error("Python call failed:", error);
    });
  // console.log(greetMsg.value)
  console.log(response_data)

  // callPython("POST" , "tasks" , task)
}
</script>

<template>
  <main class="container">
    <h1>Todo list demo</h1>
    <h2>Tauri + Vue + Python</h2>

    <form class="row" @submit.prevent="addTask">
      <input
        id="add-task-input"
        v-model="taskName"
        placeholder="Add task name..."
      />
      <button type="submit">Add task</button>
    </form>

    <div class="task-list">
      <div v-for="task in tasks" :key="task.id">
        <div class="task-row">
          <div class="task-name">
            {{ task.name }}
          </div>

          <button @click="deleteTask(task.id)">Delete</button>
        </div>
      </div>
    </div>
  </main>
</template>

<style>
html,
body {
  height: 100%;
  margin: 0;
  color: #f6f6f6;
  background-color: #2f2f2f;
}
#app {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>


<style scoped>
.task-list {
  padding: 1rem;
  margin-top: 2rem;
  width: 100%;
  border: white dotted 1px;
  border-radius: 5px;
  box-shadow: #0f0f0f;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.task-row > button {
  background: red;
  padding: 0;
  margin: 0;
  width: 20%;
  padding: 4px 0;
  margin-right: 1rem;
}
.task-row > .task-name {
  display: flex;
  justify-content: center;
  align-items: center;
  /* border: #0f0f0f solid 1px; */
  flex: 1;
  padding: 1px;
  color: black;
  text-transform: uppercase;
  font-size: 130%;
}
.task-row {
  background: white;
  padding: 4px 0;
  display: flex;
  border-radius: 5px;
  /* justify-content: space-between; */
  align-items: center;
}
.container {
  padding-top: 10vh;
  display: flex;
  flex-direction: column;
  /* justify-content: center; */
  align-items: center;
  height: 40vh;
  /* min-height: 60vh; */
  /* margin: auto; */
  height: 400px;
  width: 600px;
  /* color: #f6f6f6;
  background-color: #2f2f2f; */
  margin-top: 10vh;
}
.container h1 {
  font-size: 2.5em;
}

input,
button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
  color: #0f0f0f;
  background-color: #ffffff;
  transition: border-color 0.25s;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.2);
  margin-top: 2rem;
}
input {
  margin-right: 1rem;
}
button {
  background-color: green;
  color: #ffffff;
  cursor: pointer;
}

/* form {
  padding: 3rem;
  border: solid 1px;
} */
button:hover {
  outline: solid white 1px;
  box-sizing: border-box;
}
button:active {
  border-color: #396cd8;
  background-color: #e8e8e8;
  color: black;
}
</style>

