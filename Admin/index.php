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
    <input type="text" name="server_name" placeholder="Server Name" required>
    <input type="text" name="server_ip" placeholder="Server IP">
    
    <select name="category" required>
      <option value="">--Select Category--</option>
      <option value="Product">Product</option>
      <option value="Development">Development</option>
      <option value="Testing">Testing</option>
      <option value="Common RM">Common RM</option>
    </select>

    <select name="sub_category" required>
      <option value="">--Select Sub Category--</option>
      <option value="Frontend">Frontend</option>
      <option value="Backend">Backend</option>
      <option value="Database">Database</option>
      <option value="Infrastructure">Infrastructure</option>
    </select>

    <input type="text" name="purpose" placeholder="Purpose">
    <input type="text" placeholder="Allocated Date" name="allocated_date" onfocus="(this.type='date')" onblur="(this.type='text')"/>


    <select name="server_status">
    <option value="">--Select Server Status--</option>
      <option value="active">Active</option>
      <option value="inactive">Inactive</option>
      <option value="maintenance">Maintenance</option>
    </select>

    <input type="text" placeholder="Surrendered Date" name="surrendered_date" onfocus="(this.type='date')" onblur="(this.type='text')"/>
    <input type="text" name="owner" placeholder="Owner">
    <input type="number" name="priority" placeholder="Priority">

    <select name="backup">
    <option value="">--Backup--</option>
      <option value="Yes">Yes</option>
      <option value="No">No</option>
    </select>
    
    <input type="text" name="commvault_backup" placeholder="CommVault Backup">
    <input type="text" name="backup_status" placeholder="Backup Status">
    <input type="text" placeholder="Last Backup Date" name="last_backup_date" onfocus="(this.type='date')" onblur="(this.type='text')"/>
    <input type="text" name="remarks" placeholder="Remarks">
    
    <button type="submit">Add Server</button>
  </form>

  <div>
    <input type="text" id="searchKey" placeholder="Search by ID or Name">
    <button id="search" onclick="searchServer()">Search</button>
    <button id= "show" onclick="loadServers()">Show All</button>
  </div>

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
        <th>Remarks</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>

  <script src="highlights.js"></script>
  <script src="script.js"></script>
</body>
</html>