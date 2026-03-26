import sqlite3


def init_db():
    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    # 🧾 Tasks table (UPDATED)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        owner TEXT,
        deadline TEXT,
        status TEXT,
        confidence REAL,
        project TEXT,
        jira_issue_key TEXT,
        automated INTEGER DEFAULT 0,   -- 🔥 NEW COLUMN
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 🔥 Add automated column if not exists (for old DB)
    try:
        cur.execute("SELECT automated FROM tasks LIMIT 1")
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE tasks ADD COLUMN automated INTEGER DEFAULT 0")

    # Existing Jira column fix
    try:
        cur.execute("SELECT jira_issue_key FROM tasks LIMIT 1")
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE tasks ADD COLUMN jira_issue_key TEXT")

    # ⚠️ Clarifications
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clarifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        status TEXT,
        project TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 📝 Processed Transcripts
    cur.execute("""
    CREATE TABLE IF NOT EXISTS processed_transcripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project TEXT,
        transcript_hash INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# ===============================
# 🔥 INSERT TASK (UPDATED)
# ===============================
def insert_task(t, project_name):

    task_name = t.get("task", "Unknown Task")

    if task_exists_case_insensitive(task_name, project_name):
        return False

    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO tasks (
        task, owner, deadline, status, confidence, project, automated, last_updated
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        task_name,
        t.get("owner", "Unassigned"),
        t.get("deadline", ""),
        t.get("status", "Pending"),
        t.get("confidence", 0.0),
        project_name,
        int(t.get("automated", False))  # 🔥 IMPORTANT
    ))

    conn.commit()
    conn.close()
    return True


# ===============================
# 🔥 CONFIRM TASK (FIXED)
# ===============================
def update_task_owner(task_name, owner, project_name):
    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    cur.execute("""
    UPDATE tasks
    SET owner = ?, status = 'CONFIRMED', last_updated = CURRENT_TIMESTAMP
    WHERE task = ? AND project = ?
    """, (owner, task_name, project_name))

    conn.commit()
    conn.close()


# ===============================
# 🔥 FETCH TASKS (UPDATED)
# ===============================
def get_tasks_by_project(project_name):
    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT task, owner, deadline, status, confidence, project, last_updated, automated
    FROM tasks
    WHERE project = ?
    """, (project_name,))

    rows = cur.fetchall()
    conn.close()
    return rows


# ===============================
# 🔥 OTHER FUNCTIONS (UNCHANGED)
# ===============================
def insert_clarification(t, project_name):
    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO clarifications (task, status, project)
    VALUES (?, ?, ?)
    """, (
        t.get("task", "Unknown Task"),
        "Pending",
        project_name
    ))

    conn.commit()
    conn.close()


def get_all_projects():
    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT DISTINCT project FROM tasks
    WHERE project IS NOT NULL AND project != ''
    ORDER BY project
    """)

    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]


def delete_project(project_name):
    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM tasks WHERE project = ?", (project_name,))
    cur.execute("DELETE FROM clarifications WHERE project = ?", (project_name,))

    conn.commit()
    conn.close()


def get_all_tasks():
    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT id, task, owner, deadline, status, confidence, created_at, last_updated
    FROM tasks
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def get_owner_history(project_name):
    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT task, owner FROM tasks
    WHERE project = ? AND owner != 'Unassigned'
    """, (project_name,))

    rows = cur.fetchall()
    conn.close()
    return rows


# ===============================
# 🔥 DUPLICATE HANDLING
# ===============================
def task_exists_case_insensitive(task_name, project_name):
    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT COUNT(*) FROM tasks 
    WHERE LOWER(task) = LOWER(?) AND project = ?
    """, (task_name, project_name))

    count = cur.fetchone()[0]
    conn.close()
    return count > 0


def cleanup_case_insensitive_duplicates(project_name):
    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM tasks 
    WHERE id NOT IN (
        SELECT MIN(id) 
        FROM tasks 
        WHERE project = ?
        GROUP BY LOWER(task)
    ) AND project = ?
    """, (project_name, project_name))

    deleted_count = cur.rowcount
    conn.commit()
    conn.close()

    return deleted_count