function loadServers(query = "") {
    fetch("fetch.php?q=" + encodeURIComponent(query))
      .then(res => res.json())
      .then(data => {
        const tbody = document.querySelector("#serverTable tbody");
        tbody.innerHTML = "";
  
        data.forEach(row => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${row.id}</td>
            <td>${row.server_name}</td>
            <td>${row.server_ip}</td>
            <td>${row.category}</td>
            <td>${row.sub_category}</td>
            <td>${row.purpose}</td>
            <td>${row.allocated_date}</td>
            <td>${row.server_status}</td>
            <td>${row.surrendered_date}</td>
            <td>${row.owner}</td>
            <td>${row.priority}</td>
            <td>${row.backup}</td>
            <td>${row.commvault_backup}</td>
            <td>${row.backup_status}</td>
            <td>${row.last_backup_date}</td>
            <td>${row.remarks}</td>
          `;
          tbody.appendChild(tr);
        });
      });
  }
  
  function searchServer() {
    let key = document.getElementById("searchKey").value;
    loadServers(key);
  }
  
  function resetSearch() {
    document.getElementById("searchKey").value = "";
    loadServers();
  }
  
  document.addEventListener("DOMContentLoaded", () => loadServers());  