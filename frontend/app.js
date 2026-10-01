const API = "/api";  // nginx proxies /api to the backend service
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

async function api(path, method = "GET", body) {
  try {
    const res = await fetch(API + path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || res.statusText);
    $("msg").textContent = "";
    return data;
  } catch (e) {
    $("msg").textContent = "Request failed: " + e.message;
    throw e;
  }
}

async function loadEmployees() {
  const emps = await api("/employees");
  $("emp-list").innerHTML = emps.map(e =>
    `<tr><td>${e.id}</td><td>${esc(e.name)}</td><td>${esc(e.email)}</td><td>${esc(e.department)}</td></tr>`).join("");
  $("task-emp").innerHTML = emps.map(e => `<option value="${e.id}">${esc(e.name)}</option>`).join("");
}

async function loadTasks() {
  const tasks = await api("/tasks");
  const opts = ["Pending", "In Progress", "Completed"];
  $("task-list").innerHTML = tasks.map(t => `
    <tr><td>${t.id}</td><td>${esc(t.task_name)}</td><td>${esc(t.employee_name)}</td>
    <td><select onchange="updateStatus(${t.id}, this.value)">
      ${opts.map(o => `<option ${o === t.status ? "selected" : ""}>${o}</option>`).join("")}
    </select></td>
    <td><button class="del" onclick="deleteTask(${t.id})">Delete task</button></td></tr>`).join("");
}

async function addEmployee() {
  await api("/employees", "POST", {
    name: $("emp-name").value, email: $("emp-email").value, department: $("emp-dept").value });
  ["emp-name", "emp-email", "emp-dept"].forEach(i => $(i).value = "");
  await loadEmployees();
}

async function addTask() {
  await api("/tasks", "POST", { employee_id: $("task-emp").value, task_name: $("task-name").value });
  $("task-name").value = "";
  await loadTasks();
}

async function updateStatus(id, status) { await api(`/tasks/${id}`, "PUT", { status }); }
async function deleteTask(id) { await api(`/tasks/${id}`, "DELETE"); await loadTasks(); }

loadEmployees().then(loadTasks).catch(() => {});
