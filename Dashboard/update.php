<?php
include __DIR__ . "/db.php";

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $id     = $_POST['id'] ?? null;
    $name   = trim($_POST['server_name'] ?? '');
    $ip     = trim($_POST['server_ip'] ?? '');
    $category = $_POST['category'] ?? '';
    $sub_category = $_POST['sub_category'] ?? '';
    $purpose = $_POST['purpose'] ?? '';
    $allocated_date = $_POST['allocated_date'] ?? null;
    $status = $_POST['server_status'] ?? 'active';
    $surrendered_date = $_POST['surrendered_date'] ?? null;
    $owner = $_POST['owner'] ?? '';
    $priority = (int)($_POST['priority'] ?? 0);
    $backup = $_POST['backup'] ?? 'No';
    $commvault = $_POST['commvault_backup'] ?? '';
    $backup_status = $_POST['backup_status'] ?? '';
    $last_backup = $_POST['last_backup_date'] ?? null;
    $rdp_user = $_POST['rdp_user'] ?? '';
    $rdp_password = $_POST['rdp_password'] ?? '';
    $backend_server = $_POST['backend_server'] ?? '';
    $backend_user = $_POST['backend_user'] ?? '';
    $backend_password = $_POST['backend_password'] ?? '';
    $vpn = $_POST['vpn'] ?? '';
    $connection_method = $_POST['connection_method'] ?? '';
    $remarks = $_POST['remarks'] ?? '';

    if (!$id) {
        http_response_code(400);
        echo "Missing server ID.";
        exit;
    }

    if (!filter_var($ip, FILTER_VALIDATE_IP) && $ip !== "") {
        http_response_code(400);
        echo "Invalid IP address.";
        exit;
    }

    try {
        $stmt = $conn->prepare("UPDATE servers 
            SET server_name=?, server_ip=?, category=?, sub_category=?, purpose=?, allocated_date=?, server_status=?, surrendered_date=?, owner=?, priority=?, backup=?, commvault_backup=?, backup_status=?, last_backup_date=?, rdp_user=?, rdp_password=?, backend_server=?, backend_user=?, backend_password=?, vpn=?, connection_method=?, remarks=? 
            WHERE id=?");
        $stmt->bind_param("ssssssssisssssssssssssi", $name, $ip, $category, $sub_category, $purpose, $allocated_date, $status, $surrendered_date, $owner, $priority, $backup, $commvault, $backup_status, $last_backup, $rdp_user, $rdp_password, $backend_server, $backend_user, $backend_password, $vpn, $connection_method, $remarks, $id);
        $stmt->execute();

        if ($stmt->affected_rows > 0) {
            echo "Server updated successfully";
        } else {
            echo "No changes made or server not found.";
        }
    } catch (mysqli_sql_exception $e) {
        if (strpos($e->getMessage(), 'Duplicate entry') !== false) {
            echo "Error: Server name must be unique.";
        } else {
            echo "Database error: " . $e->getMessage();
        }
    }
}
?>