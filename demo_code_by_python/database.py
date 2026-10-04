import sqlite3
from typing import List, Dict, Any, Optional

DB_FILE = "healtrip.db"

# CONNECT DB
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # My Demo Doctor's Data With Out Realtionships
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id TEXT PRIMARY KEY,
            name_en TEXT NOT NULL,
            name_ar TEXT NOT NULL,
            specialty_en TEXT NOT NULL,
            specialty_ar TEXT NOT NULL,
            hospital_en TEXT NOT NULL,
            hospital_ar TEXT NOT NULL,
            city_en TEXT NOT NULL,
            city_ar TEXT NOT NULL,
            rating REAL NOT NULL,
            available_days TEXT NOT NULL,
            consultation_fee REAL NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] == 0:
        sample_doctors = [
            (
                "doc-101",
                "Dr. Ahmed Hassan",
                "د. أحمد حسن",
                "Cardiology",
                "أمراض القلب",
                "Cairo Heart Institute",
                "معهد القلب القومي",
                "Cairo",
                "القاهرة",
                4.9,
                "Sunday, Tuesday, Thursday",
                100.0,
            ),
            (
                "doc-102",
                "Dr. Sarah Al Hamaddy",
                "د. سارة الحمادي",
                "Cardiology",
                "أمراض القلب",
                "International Medical Center",
                "المركز الطبي الدولي",
                "Giza",
                "الجيزة",
                4.8,
                "Monday, Wednesday",
                120.0,
            ),
            (
                "doc-103",
                "Emergency Care Unit",
                "وحدة الطوارئ السريعة",
                "Emergency Medicine",
                "طب الطوارئ",
                "Al-Ahly ER Center",
                "مركز الأهلي للطوارئ",
                "Cairo",
                "القاهرة",
                5.0,
                "Everyday",
                50.0,
            ),
            (
                "doc-104",
                "Dr. Khaled El-Sayed (Orthopedic Specialist)",
                "د. خالد السيد (استشاري العظام والعمود الفقري)",
                "Orthopedics",
                "عظام",
                "Cairo Specialist Hospital",
                "مستشفى القاهرة التخصصي",
                "Cairo",
                "القاهرة",
                4.9,
                "Sunday, Wednesday",
                130.0,
            ),
        ]

        # Add Demo Data
        cursor.executemany(
            """
            INSERT INTO doctors VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            sample_doctors,
        )

        conn.commit()

    conn.close()

# Get Data Specialty en / ar  (Category) - And Filters If Needed - to make llm tool take data by 1 time
def query_doctors_db(
    specialty: Optional[str] = None, city: Optional[str] = None
) -> List[Dict[str, Any]]:
    init_db()

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM doctors WHERE 1=1"
    params = []

    # Search in both specialty_en and specialty_ar
    # البحث في عمودي التخصص الإنجليزي والعربي معًا
    if specialty:
        query += " AND (LOWER(specialty_en) LIKE LOWER(?) OR LOWER(specialty_ar) LIKE LOWER(?))"
        params.extend([f"%{specialty}%", f"%{specialty}%"])

    # Search in both city_en and city_ar
    # البحث في عمودي المدينة الإنجليزي والعربي معًا
    if city:
        query += " AND (LOWER(city_en) LIKE LOWER(?) OR LOWER(city_ar) LIKE LOWER(?))"
        params.extend([f"%{city}%", f"%{city}%"])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()

    return results


# Explicitly execute DB creation upon module load or direct run
# إجبار الكود على إنشاء القاعدة وسجلاتها فور الاستدعاء المباشر
if __name__ == "__main__":
    init_db()
    print("✓ healtrip.db created successfully!")



conn = sqlite3.connect("healtrip.db")
cursor = conn.cursor()


cursor.execute(
    "SELECT id, name_ar, name_en, specialty_ar, specialty_en, hospital_ar, city_ar FROM doctors"
)
rows = cursor.fetchall()

print(f"\n---  {len(rows)} ---\n")
for row in rows:
    print(
        f"ID: {row[0]} | الاسم: {row[1]} | التخصص: {row[3]} ({row[4]}) | المستشفى: {row[5]} | المدينة: {row[6]}"
    )

conn.close()
