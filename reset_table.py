from sqlmodel import create_engine, text
from backend.db import DATABASE_URL

# Database se connect karo
engine = create_engine(DATABASE_URL)

def delete_old_table():
    print("🗑️  Purani table delete ho rahi hai...")
    
    with engine.connect() as conn:
        # Ye command purani 'tasks' table ko delete kar degi
        conn.execute(text("DROP TABLE IF EXISTS tasks CASCADE;"))
        conn.commit()
        
    print("✅ Table delete ho gayi!")
    print("🔁 Ab apna Server restart karein, nayi table khud ban jayegi.")

if __name__ == "__main__":
    delete_old_table()