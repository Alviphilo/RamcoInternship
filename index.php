<?php include __DIR__ . "/db.php"; ?>
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Server Management</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>

<h1>Server Management Dashboard</h1>

<div class="search-bar">
  <input type="text" id="searchKey" placeholder="Search by ID or Name">
  <button id ="search" onclick="searchServer()">Search</button>
  <button id ="reset" onclick="resetSearch()">Reset</button>
</div>

<table id="serverTable">
  <thead>
    <tr>
      <th>ID</th>
      <th>Server Name</th>
      <th>Server IP</th>
      <th>Category</th>
      <th>Sub Category</th>
      <th>Purpose</th>
      <th>Allocated Date</th>
      <th>Server Status</th>
      <th>Surrendered Date</th>
      <th>Owner</th>
      <th>Priority</th>
      <th>Backup</th>
      <th>Commvault Backup</th>
      <th>Backup Status</th>
      <th>Last Backup Date</th>
      <th>Remarks</th>
    </tr>
  </thead>
  <tbody></tbody>
</table>

<script src="script.js"></script>
<script src="highlights.js"></script>
</body>
</html>