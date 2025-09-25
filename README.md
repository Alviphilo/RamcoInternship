# Internal SQL Deployment Tool

A simple web-based tool that enables team members to deploy SQL scripts to various database environments with one click.

## Features

- **Multi-Database Support**: Works with SQL Server, MySQL, and PostgreSQL
- **Security Features**: Scans for dangerous SQL operations and blocks them
- **MySQL to MSSQL Conversion**: Automatically converts MySQL syntax to MSSQL when needed
- **Batch Processing**: Handles GO statements and batch execution for SQL Server
- **Detailed Logging**: Logs all deployment attempts with batch-level results
- **User-Friendly Interface**: Modern, responsive web interface
- **File Validation**: Validates file types, sizes, and content
- **Error Handling**: Graceful handling of connection timeouts, duplicate keys, etc.

## Prerequisites

- Python 3.8+
- SQL Server with ODBC Driver 17+ (for MSSQL connections)
- Access to target database servers
- Required Python packages (see requirements.txt)

## Installation

1. Clone or download the project files
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your database servers in `servers.json` (see configuration section below)

4. Create necessary directories:
   ```bash
   mkdir uploads templates static
   ```

5. Place the HTML file in the `templates/` directory

## Configuration

### Server Configuration (`servers.json`)

Configure your database environments in the `servers.json` file:

```json
{
  "RM-DEV": {
    "type": "mssql",
    "host": "localhost,1433",
    "username": "sa",
    "password": "YourPassword",
    "database": "YourDatabase",
    "description": "Development Environment"
  }
}
```

**Supported Database Types:**
- `mssql` - Microsoft SQL Server
- `mysql` - MySQL Server  
- `postgres` - PostgreSQL

**Security Note**: Store this file securely and never expose it to the frontend. Consider using environment variables for sensitive credentials in production.

### Environment Variables (Optional)

You can override database credentials using environment variables:
```bash
export RM_DEV_PASSWORD="YourSecurePassword"
export RM_QA_PASSWORD="YourQAPassword"
```

## Usage

1. **Start the Application**:
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:5000`

2. **Deploy SQL Scripts**:
   - Enter your Employee ID
   - Select a `.sql` file (max 5MB)
   - Choose target server environment
   - Click "Deploy Script"

3. **View Results**:
   - Success/error messages are displayed immediately
   - Detailed batch execution results show individual statement outcomes
   - All deployments are logged in `deployments.log.json`

## File Structure

```
sql-deployment-tool/
├── app.py                 # Main Flask application
├── servers.json          # Database server configurations
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── uploads/              # Uploaded SQL files (auto-created)
├── deployments.log.json  # Deployment logs (auto-created)
└── README.md            # This file
```

## Security Features

- **SQL Injection Protection**: Scans for dangerous SQL patterns
- **File Validation**: Only accepts `.sql` files under 5MB
- **Input Sanitization**: Validates employee IDs and server selections  
- **Credential Security**: Database credentials never exposed to frontend
- **Operation Blocking**: Prevents dangerous operations like `DROP DATABASE`, `xp_cmdshell`

## API Endpoints

### POST `/deploy-sql`
Deploy a SQL script to specified server.

**Request**: Multipart form data
- `employeeId`: Employee identification
- `sqlFile`: SQL script file (.sql)
- `serverKey`: Target server key from servers.json

**Response**: JSON with deployment results
```json
{
  "status": "success|warning|error",
  "message": "Deployment result message",
  "batch_results": [...],
  "timestamp": "2025-09-25T10:30:00Z"
}
```

### GET `/health`
Health check endpoint.

### GET `/logs`
View recent deployment logs (last 50 entries).

## Troubleshooting

### Common Issues

1. **Connection Timeouts**:
   - Check database server connectivity
   - Verify firewall settings
   - Ensure correct host/port configuration

2. **Authentication Failures**:
   - Verify username/password in servers.json
   - Check database user permissions
   - For SQL Server: ensure SQL Server authentication is enabled

3. **ODBC Driver Issues**:
   - Install Microsoft ODBC Driver 17 for SQL Server
   - Update connection string if using different driver version

4. **File Upload Errors**:
   - Ensure uploads directory exists and is writable
   - Check file size limits (5MB max)
   - Verify file encoding (UTF-8 recommended)

### Error Codes

- **400**: Validation error (invalid input)
- **403**: Security violation (dangerous SQL detected)
- **500**: Server error (connection issues, SQL errors)

## Logging

All deployment attempts are logged in `deployments.log.json` with:
- Timestamp and employee ID
- Target server and filename
- Execution status and batch results
- Error messages and warnings
- Database type and normalization info

## Production Deployment

For production use:

1. **Security**:
   - Use environment variables for database passwords
   - Enable HTTPS/TLS
   - Implement proper authentication
   - Restrict file upload directory permissions

2. **Performance**:
   - Set `debug=False` in Flask app
   - Use production WSGI server (gunicorn, uWSGI)
   - Implement connection pooling for high volume

3. **Monitoring**:
   - Set up log rotation for deployment logs
   - Monitor disk space in uploads directory
   - Implement health checks and alerting

## License

Internal use only. Not for distribution.
