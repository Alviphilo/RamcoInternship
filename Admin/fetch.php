<?php
include __DIR__ . "/db.php";
$q = $_GET['q'] ?? "";  

if ($q !== "") {
    if (is_numeric($q)) {
        $stmt = $conn->prepare("SELECT * FROM servers WHERE id = ? OR server_name LIKE ?");
        $like = "%$q%";
        $stmt->bind_param("is", $q, $like);
    } else {
        $stmt = $conn->prepare("SELECT * FROM servers WHERE server_name LIKE ?");
        $like = "%$q%";
        $stmt->bind_param("s", $like);
    }
    $stmt->execute();
    $result = $stmt->get_result();
} else {
    $result = $conn->query("SELECT * FROM servers");
}

$data = [];
if ($result && $result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
}

header('Content-Type: application/json');
echo json_encode($data);

$conn->close();
?>