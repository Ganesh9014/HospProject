# 🏥 Hospital App - Live Server Update Guide

This guide describes how to update the hospital application running on the live hospital server. Following these steps ensures your updates are deployed correctly and **prevents loss of live hospital data or uploaded files.**

---

## ⚠️ CRITICAL WARNINGS - READ BEFORE STARTING

> [!CAUTION]
> **DO NOT** run or import the `hospital_db.sql` file on a live production server. Doing so will completely overwrite the existing database and delete all real-time hospital records and patient data!
>
> **DO NOT** delete the existing `media` directory. It contains active file uploads (doctor prescriptions, lab reports, patient scans, etc.).

---

## 🛠️ Step-by-Step Update Process

### Step 1: Generate the Build on your Development Computer
Run the compiler script on your local development computer to generate the updated codebase:
```cmd
python build_for_hospital.py
```
*This updates the `hospital_build` directory. Copy this entire folder to your USB drive.*

---

### Step 2: Stop the Live Server at the Hospital
On the server computer, stop the running server.
* Find the Command Prompt window running the server and press **`Ctrl + C`** (or close the window).

---

### Step 3: Backup the Current Live Folder
Create a backup of the current installation so you can rollback if anything fails.
1. Open **Command Prompt** (cmd) on the server.
2. Rename the directory to create a backup:
   ```cmd
   rename C:\hospital_build hospital_build_backup
   ```
   *(Alternatively, rename it in Windows File Explorer to something like `hospital_build_backup_2026_06_08`).*

---

### Step 4: Deploy the New Build
1. Insert your USB drive into the server computer.
2. Copy the new `hospital_build` folder from the USB drive to **`C:\`** (resulting in a new `C:\hospital_build` folder).

---

### Step 5: Restore Database Configuration & Media Files
You must copy your live server's settings and uploaded patient files from the backup directory to the new directory.

Run these commands in Command Prompt:
1. **Restore `.env` configuration file:**
   ```cmd
   copy C:\hospital_build_backup\.env C:\hospital_build\.env
   ```
2. **Restore patient upload files (`media/` directory):**
   ```cmd
   xcopy C:\hospital_build_backup\media C:\hospital_build\media /E /I /H /Y
   ```

---

### Step 6: Install New Dependencies (If Any)
If you installed new Python packages on your development computer, you must install them on the server too.
1. Open Command Prompt on the server and navigate to the directory:
   ```cmd
   cd C:\hospital_build
   ```
2. Run the dependency installation command:
   ```cmd
   pip install -r requirements.txt
   ```

---

### Step 7: Apply Database Schema Updates (Only if database columns/tables changed)
*If you did not modify the database tables, database columns, or database keys, skip this step.*

If you made schema changes, run your custom update queries directly in **SQL Server Management Studio (SSMS)**:
1. Open **SSMS** and connect to the database.
2. Click **New Query**.
3. Run your `ALTER TABLE` or structural SQL scripts against the `hospitalDatabase` database.

---

### Step 8: Configure Auto-Run (Optional)
If you want the application to automatically start when the computer turns on or when a user logs in:
1. Open Command Prompt in the build folder:
   ```cmd
   cd C:\hospital_build
   ```
2. Run the configuration tool:
   ```cmd
   setup_autorun.bat
   ```
   *Note: This script runs without administrator privileges and directly registers the startup action in the Windows Startup folder.*

---

### Step 9: Start the Server
Start the production web server again:
* Run the startup script:
  ```cmd
  run_on_startup.bat
  ```
* Open your browser and navigate to `http://localhost:8000` to verify everything is working perfectly!





C:\Users\Administrator>taskkill /PID 9956 /F
SUCCESS: The process with PID 9956 has been terminated.

C:\Users\Administrator>taskkill /PID 10160 /F
SUCCESS: The process with PID 10160 has been terminated.

C:\Users\Administrator>

