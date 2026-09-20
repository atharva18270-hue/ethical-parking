from datetime import datetime
import sqlite3
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# Initialize SQLite Database automatically
def init_db():
  conn = sqlite3.connect("parking.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            txn TEXT,
            slotId TEXT,
            vehicle TEXT,
            duration TEXT,
            total INTEGER,
            date TEXT,
            time TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()


@app.route("/")
def index():
  return render_template("index.html")


# API: Store a parking record when a car is booked
@app.route("/api/park", methods=["POST"])
def park_vehicle():
  data = request.json
  now = datetime.now()
  txn = f"TXN-{int(now.timestamp())}"
  date_str = now.strftime("%Y-%m-%d")
  time_str = now.strftime("%H:%M:%S")

  conn = sqlite3.connect("parking.db")
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT INTO ledger (txn, slotId, vehicle, duration, total, date, time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
      (
          txn,
          data.get("slotId"),
          data.get("vehicle"),
          data.get("duration"),
          data.get("total"),
          date_str,
          time_str,
      ),
  )
  conn.commit()
  conn.close()

  return jsonify({
      "success": True,
      "record": {
          "txn": txn,
          "slotId": data.get("slotId"),
          "vehicle": data.get("vehicle"),
          "duration": data.get("duration"),
          "total": data.get("total"),
          "date": f"{date_str} {time_str}",
      },
  })


# API: Fetch all past parking records for the Ledger view
@app.route("/api/ledger", methods=["GET"])
def get_ledger():
  conn = sqlite3.connect("parking.db")
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM ledger ORDER BY id DESC")
  rows = cursor.fetchall()
  conn.close()

  ledger_list = []
  for row in rows:
    ledger_list.append({
        "txn": row["txn"],
        "slotId": row["slotId"],
        "vehicle": row["vehicle"],
        "duration": row["duration"],
        "total": row["total"],
        "date": f"{row['date']} at {row['time']}",
    })
  return jsonify(ledger_list)


if __name__ == "__main__":
  app.run(debug=True, port=3000)