CREATE DATABASE IF NOT EXISTS serverDBDash;
USE serverDBDash;

CREATE TABLE IF NOT EXISTS servers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_name VARCHAR(50) NOT NULL UNIQUE,
    server_ip VARCHAR(50),
    category VARCHAR(50),
    sub_category VARCHAR(50),
    purpose VARCHAR(100),
    allocated_date VARCHAR(50),
    server_status VARCHAR(50),
    surrendered_date VARCHAR(50),
    owner VARCHAR(50),
    priority INT,
    backup VARCHAR(10),
    commvault_backup VARCHAR(50),
    backup_status VARCHAR(50),
    last_backup_date VARCHAR(50),
    remarks VARCHAR(255),
    rdp_user VARCHAR(50),
    rdp_password VARCHAR(50),
    backend_server VARCHAR(50),
    backend_user VARCHAR(50),
    backend_password VARCHAR(50),
    vpn VARCHAR(50),
    connection_method VARCHAR(50)
);


INSERT INTO servers (
    server_name, server_ip, category, sub_category, purpose, allocated_date,
    server_status, surrendered_date, owner, priority, backup, commvault_backup,
    backup_status, last_backup_date, rdp_user, rdp_password, backend_server,
    backend_user, backend_password, vpn, connection_method, remarks
) VALUES
(
    'SBURMSCNPO1','172.27.4.233','1-Product','Common RM','Common RM',
    'Aug 9, 2022','','','Vinoth',1,'Yes','SBURMSCNPO1','Completed',
    'Aug 9, 2022, 06:28:06 PM','','','','','','','',''
),
(
    'SBURMSCNV09','172.27.7.160','1-Product','Common RM','Common RM',
    'Jun 19, 2022','','','Vinoth',1,'Yes','SBURMSCNV09','Completed',
    'Jun 19, 2022, 10:15:42 PM','','','','','','','',''
)
ON DUPLICATE KEY UPDATE
    server_ip=VALUES(server_ip),
    owner=VALUES(owner);
