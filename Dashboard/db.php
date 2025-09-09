<?php
$servername = "127.0.0.1";
$username   = "root";
$password   = "Alvina@2904";
$dbname     = "serverDBDash";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>