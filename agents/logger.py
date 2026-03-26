import sqlite3

def log(agent, decision, confidence):
    conn = sqlite3.connect("agent.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO logs (agent, decision, confidence)
    VALUES (?, ?, ?)
    """, (agent, decision, confidence))

    conn.commit()
    conn.close()