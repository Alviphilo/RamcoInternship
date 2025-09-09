<?php ?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Server Management Dashboard</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h2>Server Management Dashboard</h2>

  <form id="addForm" onsubmit="event.preventDefault(); addServer();">
    <div class="form-group">
      <label>Server Name</label>
      <input type="text" name="server_name" required>
    </div>

    <div class="form-group">
      <label>Server IP</label>
      <input type="text" name="server_ip">
    </div>

    <div class="form-group">
      <label>Category</label>
      <select name="category" required>
        <option value="">--Select Category--</option>
        <option value="Product">Product</option>
        <option value="Development">Development</option>
        <option value="Testing">Testing</option>
        <option value="Common RM">Common RM</option>
      </select>
    </div>

    <div class="form-group">
      <label>Sub Category</label>
      <select name="sub_category" required>
        <option value="">--Select Sub Category--</option>
        <option value="Frontend">Frontend</option>
        <option value="Backend">Backend</option>
        <option value="Database">Database</option>
        <option value="Infrastructure">Infrastructure</option>
      </select>
    </div>

    <div class="form-group">
      <label>Purpose</label>
      <input type="text" name="purpose">
    </div>

    <div class="form-group">
      <label>Allocated Date</label>
      <input type="date" name="allocated_date">
    </div>

    <div class="form-group">
      <label>Server Status</label>
      <select name="server_status">
        <option value="">--Select Server Status--</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
        <option value="maintenance">Maintenance</option>
      </select>
    </div>

    <div class="form-group">
      <label>Surrendered Date</label>
      <input type="date" name="surrendered_date">
    </div>

    <div class="form-group">
      <label>Owner</label>
      <input type="text" name="owner">
    </div>

    <div class="form-group">
      <label>Priority</label>
      <input type="number" name="priority">
    </div>

    <div class="form-group">
      <label>Backup</label>
      <select name="backup">
        <option value="">--Backup--</option>
        <option value="Yes">Yes</option>
        <option value="No">No</option>
      </select>
    </div>

    <div class="form-group">
      <label>CommVault Backup</label>
      <input type="text" name="commvault_backup">
    </div>

    <div class="form-group">
      <label>Backup Status</label>
      <input type="text" name="backup_status">
    </div>

    <div class="form-group">
      <label>Last Backup Date</label>
      <input type="date" name="last_backup_date">
    </div>

    <div class="form-group">
      <label>RDP Username</label>
      <input type="text" name="rdp_user">
    </div>

    <div class="form-group">
      <label>RDP Password</label>
      <input type="password" name="rdp_password">
    </div>

    <div class="form-group">
      <label>Backend Server</label>
      <input type="text" name="backend_server">
    </div>

    <div class="form-group">
      <label>Backend Username</label>
      <input type="text" name="backend_user">
    </div>

    <div class="form-group">
      <label>Backend Password</label>
      <input type="password" name="backend_password">
    </div>

    <div class="form-group">
      <label>VPN</label>
      <input type="text" name="vpn">
    </div>

    <div class="form-group">
      <label>Connection Method</label>
      <select name="connection_method">
        <option value="">--Connection Method--</option>
        <option value="Type1">Type 1</option>
        <option value="Type2">Type 2</option>
        <option value="Type3">Type 3</option>
      </select>
    </div>

    <div class="form-group">
      <label>Remarks</label>
      <input type="text" name="remarks">
    </div>

    <button type="submit" class="btn">Add Server</button>
  </form>


  <div class="search-bar">
    <input type="text" id="searchKey" placeholder="Search by ID or Name">
    <button id="search" onclick="searchServer()">Search</button>
    <button id="show" onclick="loadServers()">Show All</button>
  </div>

  <div class="table-container">
  <table id="serverTable">
    <thead>
      <tr>
        <th>ID</th>
        <th>Server Name</th>
        <th>IP</th>
        <th>Category</th>
        <th>Sub Category</th>
        <th>Purpose</th>
        <th>Allocated Date</th>
        <th>Status</th>
        <th>Surrendered Date</th>
        <th>Owner</th>
        <th>Priority</th>
        <th>Backup</th>
        <th>CommVault Backup</th>
        <th>Backup Status</th>
        <th>Last Backup Date</th>
        <th>RDP Username</th>
        <th>RDP Password</th>
        <th>Backend Server</th>
        <th>Backend Username</th>
        <th>Backend Password</th>
        <th>VPN</th>
        <th>Connection Method</th>
        <th>Remarks</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>
</div>

  <script src="highlights.js"></script>
  <script src="script.js"></script>
</body>
</html>