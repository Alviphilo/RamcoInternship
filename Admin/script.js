function loadServers(query="") {
    fetch("fetch.php?q=" + query)
      .then(res => res.json())
      .then(data => {
        let tbody = document.querySelector("#serverTable tbody");
        tbody.innerHTML = "";
        data.forEach(row => {
          tbody.innerHTML += `
            <tr>
              <td>${row.id}</td>
              <td contenteditable data-field="server_name">${row.server_name}</td>
              <td contenteditable data-field="server_ip">${row.server_ip}</td>
              <td contenteditable data-field="category">${row.category}</td>
              <td contenteditable data-field="sub_category">${row.sub_category}</td>
              <td contenteditable data-field="purpose">${row.purpose}</td>
              <td contenteditable data-field="allocated_date">${row.allocated_date ?? ""}</td>
              <td contenteditable data-field="server_status">${row.server_status}</td>
              <td contenteditable data-field="surrendered_date">${row.surrendered_date ?? ""}</td>
              <td contenteditable data-field="owner">${row.owner}</td>
              <td contenteditable data-field="priority">${row.priority}</td>
              <td contenteditable data-field="backup">${row.backup}</td>
              <td contenteditable data-field="commvault_backup">${row.commvault_backup}</td>
              <td contenteditable data-field="backup_status">${row.backup_status}</td>
              <td contenteditable data-field="last_backup_date">${row.last_backup_date ?? ""}</td>
              <td contenteditable data-field="remarks">${row.remarks}</td>
              <td>
                <button onclick="saveRow(${row.id}, this)">Save</button>
              </td>
            </tr>`;
        });
      });
  }
  
  function addServer() {
    let form = document.getElementById("addForm");
    fetch("insert.php", { method: "POST", body: new FormData(form) })
      .then(res => res.text())
      .then(msg => {
        alert(msg);
        form.reset();
        loadServers();
      });
  }
  
  function saveRow(id, btn) {
    let row = btn.closest("tr");
    let data = new FormData();
    data.append("id", id);
    row.querySelectorAll("[contenteditable]").forEach(cell => {
      data.append(cell.dataset.field, cell.innerText.trim());
    });
    fetch("update.php", { method: "POST", body: data })
      .then(res => res.text())
      .then(msg => {
        alert(msg);
        loadServers();
      });
  }
  
  function searchServer() {
    let key = document.getElementById("searchKey").value;
    loadServers(key);
  }
  
  document.addEventListener("DOMContentLoaded", () => loadServers());