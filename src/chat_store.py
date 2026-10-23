import json
import sqlite3
import time
import uuid

import config


def _con():
    con = sqlite3.connect(config.CHAT_DB, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY, session_id TEXT, title TEXT, created REAL, updated REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, conv_id TEXT, role TEXT, content TEXT,
        sources_json TEXT, created REAL,
        FOREIGN KEY(conv_id) REFERENCES conversations(id) ON DELETE CASCADE)""")
    return con


def new_conversation(session_id, title="New chat"):
    cid = uuid.uuid4().hex[:12]
    now = time.time()
    with _con() as con:
        con.execute("INSERT INTO conversations VALUES (?,?,?,?,?)", (cid, session_id, title, now, now))
    return cid


def add_message(conv_id, role, content, sources=None):
    now = time.time()
    with _con() as con:
        con.execute("INSERT INTO messages (conv_id, role, content, sources_json, created) VALUES (?,?,?,?,?)",
                    (conv_id, role, content, json.dumps(sources or []), now))
        row = con.execute("SELECT title FROM conversations WHERE id=?", (conv_id,)).fetchone()
        if row and row["title"] == "New chat" and role == "user":
            title = content.strip().replace("\n", " ")
            con.execute("UPDATE conversations SET title=? WHERE id=?",
                        (title[:40] + ("..." if len(title) > 40 else ""), conv_id))
        con.execute("UPDATE conversations SET updated=? WHERE id=?", (now, conv_id))


def get_messages(conv_id):
    with _con() as con:
        rows = con.execute("SELECT role, content, sources_json FROM messages WHERE conv_id=? ORDER BY id",
                           (conv_id,)).fetchall()
    return [{"role": r["role"], "content": r["content"], "sources": json.loads(r["sources_json"] or "[]")}
            for r in rows]


def list_conversations(session_id):
    with _con() as con:
        rows = con.execute("SELECT id, title, updated FROM conversations WHERE session_id=? "
                           "ORDER BY updated DESC", (session_id,)).fetchall()
    return [dict(r) for r in rows]


def delete_conversation(conv_id):
    with _con() as con:
        con.execute("DELETE FROM messages WHERE conv_id=?", (conv_id,))
        con.execute("DELETE FROM conversations WHERE id=?", (conv_id,))


def clear_all(session_id):
    with _con() as con:
        con.execute("DELETE FROM messages WHERE conv_id IN (SELECT id FROM conversations WHERE session_id=?)", (session_id,))
        con.execute("DELETE FROM conversations WHERE session_id=?", (session_id,))
