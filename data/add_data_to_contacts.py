import sqlite3
from pathlib import Path

def update_images_from_files(db_path: str, image_dir: str):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for i in range(1, 21):
        image_file = Path(image_dir) / f"contact_{i}.jpg"

        if not image_file.exists():
            print(f"⚠️ Image file not found: {image_file}")
            continue

        with open(image_file, 'rb') as f:
            image_blob = f.read()

        # Update the i-th record (assumes id or rowid corresponds to index)
        cursor.execute("""
            UPDATE contacts
            SET image = ?
            WHERE rowid = ?
        """, (image_blob, i))

    conn.commit()
    conn.close()
    print("✅ All images updated in the database.")

if __name__ == "__main__":
    update_images_from_files("contacts", ".")