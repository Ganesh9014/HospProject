# 🏥 HOSPITAL APP - PRODUCTION DEPLOYMENT GUIDE

This guide walks you through setting up and running your compiled hospital application on the server computer. Because the application has been pre-compiled to Python bytecode (`.pyc`), your source code is completely secure and cannot be viewed or modified.

---

## 📌 Prerequisites for the Server Computer

Before starting, ensure the server computer has the following software installed:

1. **Python (version 3.10, 3.11, or 3.12)**
   - Download the installer from the official website (e.g., Python 3.11).
   - ⚠️ **IMPORTANT:** When running the installer, you **MUST** check the box that says **"Add Python to PATH"** at the bottom of the first screen. If you skip this, python commands will not work in Command Prompt.

2. **Microsoft SQL Server (2019, 2022, or SQL Server Express)**
   - Ensure the SQL Server database engine is installed and running.
   - Make sure you know your SQL Server instance name (e.g., `LAPTOP-DCKF2NF6\SQLEXPRESS` or `LOCALHOST\SQLEXPRESS`).

3. **SQL Server Management Studio (SSMS)**
   - Highly recommended for creating and managing the database.

4. **Microsoft ODBC Driver for SQL Server (Driver 17 or 18)**
   - Python requires this driver to communicate with SQL Server.
   - [Download ODBC Driver for SQL Server (MSDN)](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
   - *Tip:* The "ODBC Driver 17 for SQL Server" is fully supported and recommended.

---

## 🚀 Step-by-Step Deployment Instructions

### Step 1: Copy files to the Server
1. Copy the entire `hospital_build` folder from your USB drive to the server computer (for example, paste it into `C:\hospital_build`).

---

### Step 2: Create the Empty Database
1. Open **SQL Server Management Studio (SSMS)** and connect to your SQL Server instance.
2. Right-click on **Databases** and select **New Database...**.
3. Enter the Database name exactly as: `hospitalDatabase` and click **OK**.
   *(Note: The database is now empty. We will create the tables in Step 5 and import data in Step 6).*

---

### Step 3: Configure the Environment (`.env`)
Inside the `C:\hospital_build` directory, you will find a file named `.env.template`.
1. **Rename** the file from `.env.template` to `.env`.
2. Open `.env` in Notepad and update the values:
   - **`SECRET_KEY`**: Set this to a long random sequence of characters.
   - **`DEBUG`**: Keep this as `False` (for production safety and speed).
   - **`ALLOWED_HOSTS`**: Add the server's local IP address and names (separated by commas).
     - *Example:* `localhost,127.0.0.1,192.168.1.100` (replace `192.168.1.100` with the actual server IP). Set to `*` to allow all secure local IPs.
   - **`DB_HOST`**: Set this to your SQL Server instance name.
     - *Example:* `YOUR-SERVER-NAME\SQLEXPRESS` (use a single backslash). If SQL Server is on the same computer, you can use `localhost\SQLEXPRESS`.

---

### Step 4: Install Python Dependencies
1. Open **Command Prompt** (cmd) on the server.
2. Navigate to your build directory:
   ```cmd
   cd C:\hospital_build
   ```
3. Install the pre-packaged python libraries by running:
   ```cmd
   pip install -r requirements.txt
   ```

---

### Step 5: Create Database Tables (Run Migrations)
To automatically create all 57 database tables in your empty `hospitalDatabase`:
1. In the Command Prompt window (at `C:\hospital_build`), run the Django migration command:
   ```cmd
   python manage.py migrate
   ```
   *Note: This command connects to your database instance and builds the empty database schema.*

---

### Step 6: Import Initial Data (Seed Data)
Once the tables have been created, import the default roles, menus, districts, and configurations:
1. Go back to **SQL Server Management Studio (SSMS)**.
2. Click **File** > **Open** > **File...** and select the `hospital_db.sql` file located inside your `C:\hospital_build` folder.
3. In the toolbar, ensure `hospitalDatabase` is selected in the database dropdown, then click the **Execute** button (or press `F5`). This will import your configuration data into the newly created tables.

---

### Step 7: Configure Automatic Startup (Auto-Run)
To configure the application to start automatically when the computer boots up or when a user logs in, run the autorun utility:
1. In the Command Prompt window, run:
   ```cmd
   setup_autorun.bat
   ```
   *Note: This registers the server startup script directly into the Windows Startup folder. The application will start automatically in a visible window whenever the server boots or restarts.*

---

### Step 8: Start the Server manually
If you did not set up automatic startup, or want to test the server immediately:
1. In the Command Prompt window, run:
   ```cmd
   run_on_startup.bat
   ```
2. You will see a terminal window output stating:
   ```text
   ==================================================
     🏥 HOSPITAL MANAGEMENT SYSTEM
   ==================================================
     ✅ Server is starting...
     🌐 Open browser: http://localhost:8000
     🌐 Network access: http://YOUR-IP:8000
     ⛔ To stop: Close this window
   ==================================================
   ```
3. Open your web browser on the server and go to `http://localhost:8000` to verify it works!

---

## 💻 Connecting other computers in the Hospital Network

To allow other computers (reception, doctors, pharmacy) to access the application:

1. **Find the Server's Local IP Address**:
   - Open a new Command Prompt on the server.
   - Run the command: `ipconfig`
   - Look for **IPv4 Address** (usually starts with `192.168.x.x` or `10.x.x.x`). Let's assume it is `192.168.1.50`.

2. **Open the Windows Firewall Port**:
   - The server needs to allow incoming traffic on Port **8000**.
   - Go to **Windows Defender Firewall** > **Advanced Settings** > **Inbound Rules** > **New Rule...**
   - Choose **Port** > **TCP** > Specific local ports: **8000** > **Allow the connection** > Click Next and name it `Hospital App Port 8000`.

3. **Access from clients**:
   - Make sure the client computers are connected to the same local network (Wi-Fi or LAN cable).
   - Open a web browser on any client computer and go to:
     `http://192.168.1.50:8000` (replace `192.168.1.50` with your actual server IP).
