# NetGuard

### Intelligent Network Security Monitoring System

NetGuard is a Java-based computer networking and security monitoring project designed to monitor connected clients, track their connection status, receive periodic heartbeats, detect suspicious connection behavior, and display network activity through a graphical monitoring dashboard.

The current version is an **in-development desktop prototype**. The core client-server communication, heartbeat monitoring, security monitoring, activity logging, and dashboard interface have been implemented, while several dashboard controls and the planned web-based deployment architecture are still under development.

---

## Overview

NetGuard uses a client-server architecture based on Java TCP sockets.

A NetGuard client connects to the server, provides its client name, and periodically sends heartbeat messages. The server receives these messages, maintains client information, monitors connection status, and updates the graphical dashboard.

The system also includes a basic security monitoring layer that tracks repeated connection attempts and frequent client disconnections. Suspicious behavior can generate security alerts and activity logs.

The project currently runs as a **Java desktop application using Swing**.

---

## Current Features

### Client-Server Communication

* TCP socket-based client-server communication
* Server listens on port `5000`
* Client connects using the configured server IP
* Client name is sent to the server after connection
* Multiple clients can be handled using separate threads
* Server maintains connected client information

The current client configuration uses:

```text
Server IP: 127.0.0.1
Port: 5000
```

---

### Heartbeat Monitoring

NetGuard uses heartbeat messages to determine whether a connected client is still active.

The client sends:

```text
HEARTBEAT
```

every 5 seconds.

The server records the latest heartbeat time and updates the client's status.

The heartbeat manager checks client activity periodically and considers a client offline when the heartbeat timeout exceeds the configured threshold.

Current values:

```text
Heartbeat interval: 5 seconds
Offline timeout: 10 seconds
```

---

### Client Monitoring

The dashboard maintains information about connected clients, including:

* Client number
* Client name
* IP address
* Connection time
* Connection status
* Last heartbeat

The GUI updates client information when connections, heartbeats, and disconnections occur.

---

### Security Monitoring

NetGuard contains a basic security monitoring mechanism.

The current security monitor tracks:

* Connection attempts
* Client disconnections
* Repeated connection behavior
* Frequent connect/disconnect behavior
* Unknown or empty client names

A warning threshold of **3 events** is currently used for repeated connection and disconnection detection.

When suspicious behavior reaches the threshold, NetGuard generates a security alert.

---

### Security Alerts

Security alerts are displayed through the dashboard and are also written to the activity log.

Examples of current detection messages include:

```text
Multiple connection attempts detected.
```

and:

```text
Frequent connect/disconnect behavior detected.
```

---

### Activity Logging

NetGuard maintains an activity log containing events such as:

* Client connections
* Client disconnections
* Heartbeat events
* Network events
* Security warnings
* Security alerts
* System events

The current log file is:

```text
resources/logs/activity.log
```

Each entry includes a timestamp.

Example format:

```text
[2026-09-22 21:30:00] CLIENT CONNECTED | Name: Client1 | IP: 127.0.0.1
```

---

## Dashboard

NetGuard includes a dark-themed Swing dashboard designed to provide a Security Operations Center-style monitoring interface.

The dashboard currently contains:

### System Status

Displays:

* Server status
* Server IP
* Port
* Uptime

Current default configuration:

```text
Server IP: 127.0.0.1
Port: 5000
```

---

### Statistics

The dashboard contains monitoring statistics for:

* Total clients
* Online clients
* Security alerts
* Heartbeat activity

---

### Connected Clients

A table displays currently registered clients and their network information.

The table contains:

| Field           | Description                      |
| --------------- | -------------------------------- |
| #               | Client number                    |
| Client Name     | Name provided by the client      |
| IP Address      | Client IP address                |
| Connection Time | Time the client connected        |
| Status          | Online/offline state             |
| Last Heartbeat  | Most recently received heartbeat |

---

### Network Monitoring

The dashboard includes a network monitoring section designed to visually represent network activity.

The current GUI contains a custom network visualization component and monitoring interface.

---

### Security Alerts Panel

The dashboard contains a dedicated area for displaying security-related events and alerts.

---

### Activity Logs

A live activity area displays system and network events with timestamps.

Example:

```text
21:30:15 [SYSTEM] NetGuard dashboard initialized successfully.
21:30:20 [CONNECTED] Client Client1 connected from 127.0.0.1
21:30:25 [HEARTBEAT] Heartbeat received from Client1
```

---

### Server Controls

The current dashboard contains:

```text
START SERVER
STOP SERVER
CLEAR LOGS
```

The **Clear Logs** button currently clears the displayed activity area and resets the visible alert message.

The Start/Stop controls currently update the dashboard's displayed server monitoring status and activity messages. They are not yet connected to complete server lifecycle control.

This functionality is planned for a future implementation.

---

## Architecture

The current project follows a basic client-server architecture.

```text
                 ┌─────────────────────────┐
                 │       NetGuard GUI       │
                 │      ServerGUI.java     │
                 └────────────┬────────────┘
                              │
                              │
                 ┌────────────▼────────────┐
                 │       NetGuard Server   │
                 │        Server.java      │
                 └────────────┬────────────┘
                              │
                         TCP Socket
                         Port 5000
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │ Client 1 │    │ Client 2 │    │ Client N │
        └──────────┘    └──────────┘    └──────────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                         HEARTBEAT
                         Monitoring
```

---

## Project Structure

The current source code is organized into several packages.

```text
NetGuard_Computer_Networking_Project/
│
├── pom.xml
│
└── src/
    └── main/
        └── java/
            └── com/
                └── netguard/
                    │
                    ├── client/
                    │   ├── Client.java
                    │   ├── ClientMain.java
                    │   └── HeartbeatSender.java
                    │
                    ├── model/
                    │   └── ClientInfo.java
                    │
                    ├── server/
                    │   ├── ClientHandler.java
                    │   ├── HeartbeatManager.java
                    │   ├── LogManager.java
                    │   ├── SecurityMonitor.java
                    │   ├── Server.java
                    │   ├── ServerGUI.java
                    │   └── ServerMain.java
                    │
                    └── utils/
                        ├── Constants.java
                        └── Logger.java
```

The current `Constants` and `Logger` utility classes are placeholders and are not yet used as the main configuration/logging implementation.

---

## Technologies Used

| Technology       | Purpose                                             |
| ---------------- | --------------------------------------------------- |
| Java             | Main programming language                           |
| Java Swing       | Desktop graphical interface                         |
| Java TCP Sockets | Client-server communication                         |
| Multithreading   | Concurrent client handling and heartbeat monitoring |
| Maven            | Project and dependency/build management             |
| Java I/O         | Network communication and log file handling         |
| Java Collections | Client and security event tracking                  |

The Maven configuration currently targets **Java 21**.

---

## How NetGuard Works

### 1. Start the Server

The NetGuard server starts a TCP server socket on:

```text
Port 5000
```

It then waits for incoming client connections.

### 2. Start a Client

A client asks for a client name:

```text
Enter Client Name:
```

The client then attempts to connect to:

```text
127.0.0.1:5000
```

### 3. Client Registration

After connecting, the client sends its name to the server.

The server obtains:

* Client name
* Client IP address
* Connection time
* Initial connection status

The client is then added to the server's client list.

### 4. Heartbeat Communication

The client starts a background heartbeat thread.

Every 5 seconds it sends:

```text
HEARTBEAT
```

The server receives the heartbeat and updates:

```text
Last Heartbeat
Status = ONLINE
```

### 5. Connection Monitoring

The heartbeat manager periodically checks the last heartbeat received from every client.

If the heartbeat is not received within the timeout period, the client can be marked:

```text
OFFLINE
```

### 6. Security Monitoring

When a client connects, the security monitor checks the client's connection behavior.

Repeated connection attempts can trigger a security alert.

Repeated disconnections can also trigger a security alert.

### 7. Dashboard Update

The server communicates monitoring events to the Swing dashboard.

The dashboard updates:

* Client table
* Online/offline status
* Heartbeat information
* Activity log
* Security alerts
* Statistics

---

## Current Project Status

> **NetGuard is currently under active development.**

### Implemented

* [x] Java client-server architecture
* [x] TCP socket communication
* [x] Client registration
* [x] Client IP detection
* [x] Client connection tracking
* [x] Heartbeat sender
* [x] Heartbeat receiver
* [x] Heartbeat timeout monitoring
* [x] Online/offline client status
* [x] Multi-threaded client handling
* [x] Security monitoring
* [x] Repeated connection detection
* [x] Frequent disconnection detection
* [x] Security alert generation
* [x] Activity logging
* [x] Swing monitoring dashboard
* [x] Connected-client table
* [x] Network monitoring visualization
* [x] Server status display
* [x] Uptime monitoring
* [x] Activity log display
* [x] Clear logs control

### In Development

* [ ] Fully functional Start Server button
* [ ] Fully functional Stop Server button
* [ ] Proper server lifecycle management from the GUI
* [ ] Functional sidebar navigation
* [ ] Functional client management actions
* [ ] Client assignment logic
* [ ] Backend implementation for dashboard controls
* [ ] Persistent backend data management
* [ ] Improved security detection
* [ ] Better network event analysis
* [ ] Web-based frontend
* [ ] Web backend/API
* [ ] Remote client monitoring
* [ ] Live web deployment

---

## Planned Web-Based Version

The current application is a Java Swing desktop prototype.

The long-term plan is to evolve NetGuard into a **web-based network security monitoring platform**.

The planned architecture will separate the frontend, backend, and monitoring services.

```text
                    ┌──────────────────────┐
                    │      Web Browser     │
                    │   Security Dashboard │
                    └──────────┬───────────┘
                               │
                              API
                               │
                    ┌──────────▼───────────┐
                    │      Web Backend     │
                    │ Authentication / API │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
        Client Data       Security Engine    Event System
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                       Network Monitoring
```

The exact web technologies and backend architecture will be decided during the next development phase.

---

## Planned Improvements

Future development will focus on turning the current prototype into a more complete monitoring platform.

### Dashboard Controls

The existing dashboard controls will eventually perform real backend operations rather than only changing the visual state.

Planned functionality includes:

* Start monitoring service
* Stop monitoring service
* Restart monitoring service
* Clear stored logs
* Refresh monitoring data
* Manage monitored clients

### Client Assignment

A client assignment system is planned.

This will allow the monitoring system to associate clients with specific monitoring rules, groups, or assignments.

The assignment logic is not yet implemented in the current version.

### Backend

A proper backend layer will be introduced to support the future web application.

Possible responsibilities include:

* Client management
* Monitoring data
* Security events
* Authentication
* API endpoints
* Log management
* Dashboard communication

### Web Interface

The current Swing dashboard is planned to become a web-based monitoring interface.

The web version will aim to provide:

* Real-time client monitoring
* Security alerts
* Network activity
* Client management
* Monitoring controls
* Activity logs
* Dashboard statistics

### Free Deployment

The final web version is planned to be deployed using free-tier hosting services where practical.

The deployment strategy will be decided after the web architecture and backend are completed.

---

## Limitations of the Current Version

The current implementation should be considered a **prototype**, not a production-ready network security platform.

Current limitations include:

* Server IP is currently hard-coded.
* Port `5000` is currently hard-coded.
* The client currently connects to `127.0.0.1`.
* The system is primarily designed for local testing.
* Communication is not currently protected with TLS.
* Authentication is not implemented.
* Persistent database storage is not implemented.
* Dashboard navigation is currently mainly visual.
* Some controls do not yet perform their intended backend operations.
* Client assignment functionality is not implemented.
* The web version does not yet exist.
* Production deployment has not yet been completed.

These limitations are part of the current development stage and are intended to be addressed in later versions.

---

## Running the Current Project

### Requirements

* Java Development Kit (JDK) 21 or compatible Java environment
* Maven
* Git
* A Java-compatible IDE such as IntelliJ IDEA or VS Code

### Clone the Repository

```bash
git clone https://github.com/zihammahmud/NetGuard_Computer_Networking_Project.git
cd NetGuard_Computer_Networking_Project
```

### Build the Project

```bash
mvn clean package
```

### Start the Server

Run the GUI server through:

```text
ServerGUI.java
```

The GUI starts first and the server is started in a separate thread.

### Start a Client

Run:

```text
ClientMain.java
```

Enter a client name when prompted.

The client will attempt to connect to:

```text
127.0.0.1:5000
```

After a successful connection, heartbeat messages will begin automatically.

---

## Example Monitoring Flow

```text
Client starts
      │
      ▼
Enter client name
      │
      ▼
Connect to NetGuard Server
      │
      ▼
Server receives client information
      │
      ▼
Security Monitor checks connection
      │
      ▼
Client added to monitoring table
      │
      ▼
Heartbeat starts
      │
      ▼
Server receives HEARTBEAT
      │
      ▼
Client status = ONLINE
      │
      ▼
Dashboard updated
      │
      ▼
Heartbeat stops / connection closes
      │
      ▼
Client status = OFFLINE
      │
      ▼
Security Monitor records disconnect
```

---

## Development Roadmap

### Phase 1 — Core Networking

* Client-server communication
* Client registration
* Heartbeat monitoring
* Connection status

**Status: Completed**

### Phase 2 — Security Monitoring

* Connection monitoring
* Repeated connection detection
* Disconnect monitoring
* Security alerts
* Activity logging

**Status: Implemented / Under Improvement**

### Phase 3 — Dashboard Backend Integration

* Functional Start button
* Functional Stop button
* Real server lifecycle control
* Client assignment
* Backend actions
* Functional dashboard navigation

**Status: Planned**

### Phase 4 — Web Application

* Web frontend
* Backend/API
* Real-time dashboard
* Remote monitoring
* Authentication
* Database integration

**Status: Planned**

### Phase 5 — Deployment

* Production configuration
* Free-tier deployment
* Web accessibility
* Remote testing
* Security hardening

**Status: Planned**

---

## Project Goal

The goal of NetGuard is to develop a network security monitoring platform that can observe connected clients, track their availability, identify suspicious connection behavior, record security events, and present the information through an accessible monitoring dashboard.

The current Java/Swing implementation serves as the foundation for the project's future web-based version.

---

## Author

**Ziham Mahmud**

Computer Science & Engineering

Green University of Bangladesh

---

## Project Status

```text
Development Status: In Progress
Current Platform: Java Desktop
Architecture: Client-Server
Communication: TCP Socket
Monitoring: Real-Time Heartbeat
Security Monitoring: Implemented
Web Version: Planned
Deployment: Planned
```

---

## License

This project is currently developed as an academic and personal software project.

A formal open-source license will be added when the project reaches its intended release stage.
