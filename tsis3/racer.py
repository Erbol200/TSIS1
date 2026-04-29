import psycopg2
import psycopg2.extras
import csv
import json
import os
from datetime import date, datetime

def get_conn():
    return psycopg2.connect(dbname="phonebook", user="postgres", password="12345678", port=5432, host="localhost")

SCHEMA_SQL = """
-- Groups table
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Seed default groups
INSERT INTO groups (name) VALUES ('Family'),('Work'),('Friend'),('Other')
ON CONFLICT DO NOTHING;

-- Contacts table (extend if columns are missing)
CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL PRIMARY KEY,
    first_name VARCHAR(50)  NOT NULL,
    last_name  VARCHAR(50),
    email      VARCHAR(100),
    birthday   DATE,
    group_id   INTEGER REFERENCES groups(id)
);

-- Add new columns to existing table (idempotent)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='contacts' AND column_name='email') THEN
        ALTER TABLE contacts ADD COLUMN email VARCHAR(100);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='contacts' AND column_name='birthday') THEN
        ALTER TABLE contacts ADD COLUMN birthday DATE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='contacts' AND column_name='group_id') THEN
        ALTER TABLE contacts ADD COLUMN group_id INTEGER REFERENCES groups(id);
    END IF;
END$$;

-- Phones table (1-to-many)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home','work','mobile'))
);

-- ── Stored procedures / functions ─────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM contacts
    WHERE first_name ILIKE p_contact_name OR last_name ILIKE p_contact_name
    LIMIT 1;
    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
    INSERT INTO phones (contact_id, phone, type) VALUES (v_id, p_phone, p_type);
END;
$$;

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    SELECT id INTO v_contact_id FROM contacts
    WHERE first_name ILIKE p_contact_name OR last_name ILIKE p_contact_name
    LIMIT 1;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    SELECT id INTO v_group_id FROM groups WHERE name ILIKE p_group_name;
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT c.id, c.first_name, c.last_name, c.email, c.birthday,
                    g.name AS group_name
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.first_name ILIKE '%' || p_query || '%'
       OR c.last_name  ILIKE '%' || p_query || '%'
       OR c.email      ILIKE '%' || p_query || '%'
       OR p.phone      ILIKE '%' || p_query || '%'
    ORDER BY c.first_name;
END;
$$;

-- Paginated query function (from Practice 8, kept for reuse)
CREATE OR REPLACE FUNCTION get_contacts_page(p_limit INT, p_offset INT)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    ORDER BY c.first_name
    LIMIT p_limit OFFSET p_offset;
END;
$$;
"""

def setup_schema():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        conn.commit()

def print_contacts(rows, phones_map=None):
    if not rows:
        print("  (no contacts)")
        return
    for r in rows:
        cid, fname, lname, email, bday, grp = r
        name = f"{fname} {lname or ''}".strip()
        line = f"  [{cid}] {name}"
        if email:
            line += f" {email}"
        if bday:
            line += f" birthday: {bday}"
        if grp:
            line += f" g:{grp}"
        if phones_map and cid in phones_map:
            nums = ", ".join(f"{p} ({t})" for p, t in phones_map[cid])
            line += f" phones: {nums}"
        print(line)

def fetch_phones_map(conn, contact_ids):
    if not contact_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            "SELECT contact_id, phone, type FROM phones WHERE contact_id = ANY(%s)",
            (list(contact_ids),)
        )
        result = {}
        for cid, phone, ptype in cur.fetchall():
            result.setdefault(cid, []).append((phone, ptype))
    return result


def input_str(prompt, required=True):
    while True:
        val = input(prompt).strip()
        if val or not required:
            return val or None
        print("Error")


def input_date(prompt):
    while True:
        val = input(prompt + " (day-month-year): ").strip()
        if not val:
            return None
        try:
            return datetime.strptime(val, "%Y-%m-%d").date()
        except ValueError:
            print("Error")


def pick_group(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY id")
        groups = cur.fetchall()
    print("  Groups:")
    for gid, gname in groups:
        print(f"    {gid}. {gname}")
    val = input("  Choose group id (or blank to skip): ").strip()
    if not val:
        return None
    try:
        gid = int(val)
        if any(g[0] == gid for g in groups):
            return gid
    except ValueError:
        pass
    print("  Invalid choice, skipping group.")
    return None


def pick_phone_type():
    print("Group: 1=home, 2=work, 3=mobile")
    val = input("Choose type (1-3): ").strip()
    mapping = {"1": "home", "2": "work", "3": "mobile"}
    return mapping.get(val, "mobile")


def add_contact():
    print("\nAddding Contact")
    with get_conn() as conn:
        fname = input_str("First name: ")
        lname = input_str("Last name (or empty): ", required=False)
        email = input_str("Email (or empty): ", required=False)
        bday  = input_date("Birthday")
        gid   = pick_group(conn)

        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                   VALUES (%s,%s,%s,%s,%s) RETURNING id""",
                (fname, lname, email, bday, gid)
            )
            cid = cur.fetchone()[0]

        print(f"Add Number? (y/n)")
        while input("  > ").strip().lower() == "y":
            phone = input_str("Type number: ")
            ptype = pick_phone_type()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                    (cid, phone, ptype)
                )
            print("Add again? (y/n)")
        conn.commit()


def list_all_contacts():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
                FROM contacts c LEFT JOIN groups g ON g.id = c.group_id
                ORDER BY c.first_name
            """)
            rows = cur.fetchall()
        ids = [r[0] for r in rows]
        phones_map = fetch_phones_map(conn, ids)
    print_contacts(rows, phones_map)


def search_contacts_menu():
    query = input_str("Enter words like name / phone / email: ")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()
        ids = [r[0] for r in rows]
        phones_map = fetch_phones_map(conn, ids)
    print_contacts(rows, phones_map)


def filter_by_group():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM groups ORDER BY id")
            groups = cur.fetchall()
        print("Groups:")
        for gid, gname in groups:
            print(f"    {gid}. {gname}")
        val = input("Group id: ").strip()
        try:
            gid = int(val)
        except ValueError:
            print("Error")
            return
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
                FROM contacts c LEFT JOIN groups g ON g.id = c.group_id
                WHERE c.group_id = %s ORDER BY c.first_name
            """, (gid,))
            rows = cur.fetchall()
        ids = [r[0] for r in rows]
        phones_map = fetch_phones_map(conn, ids)
    print_contacts(rows, phones_map)


def search_by_email():
    pattern = input_str("Type fragment of an req email: ")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
                FROM contacts c LEFT JOIN groups g ON g.id = c.group_id
                WHERE c.email ILIKE %s ORDER BY c.first_name
            """, (f"%{pattern}%",))
            rows = cur.fetchall()
        ids = [r[0] for r in rows]
        phones_map = fetch_phones_map(conn, ids)
    print_contacts(rows, phones_map)


def sorted_contacts():
    print("Sort: 1=name  2=birthday  3=date added")
    choice = input("  > ").strip()
    order = {"1": "c.first_name", "2": "c.birthday", "3": "c.id"}.get(choice, "c.first_name")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
                FROM contacts c LEFT JOIN groups g ON g.id = c.group_id
                ORDER BY {order}
            """)
            rows = cur.fetchall()
        ids = [r[0] for r in rows]
        phones_map = fetch_phones_map(conn, ids)
    print_contacts(rows, phones_map)


def paginated_browse():
    page_size = 5
    page = 0
    with get_conn() as conn:
        while True:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_contacts_page(%s,%s)", (page_size, page * page_size))
                rows = cur.fetchall()
            ids = [r[0] for r in rows]
            phones_map = fetch_phones_map(conn, ids)
            print(f"\nPage {page + 1}:")
            print_contacts(rows, phones_map)
            print("n - next  p - prev  q - quit")
            cmd = input("  > ").strip().lower()
            if cmd == "n":
                if len(rows) < page_size:
                    print("Already on last page.")
                else:
                    page += 1
            elif cmd == "p":
                if page == 0:
                    print("Already on first page.")
                else:
                    page -= 1
            elif cmd == "q":
                break


def update_contact():
    cid = input_str("Type contact id to update: ")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id,first_name,last_name,email,birthday FROM contacts WHERE id=%s", (cid,))
            row = cur.fetchone()
        if not row:
            print("Error")
            return
        cid, fname, lname, email, bday = row
        print(f"Current: {fname} {lname or ''} | {email} | {bday}")
        new_fname = input(f"First name [{fname}]: ").strip() or fname
        new_lname = input(f"Last name [{lname or ''}]: ").strip() or lname
        new_email = input(f"Email [{email or ''}]: ").strip() or email
        new_bday_str = input(f"Birthday [{bday or ''}] (day-month-yead): ").strip()
        new_bday = datetime.strptime(new_bday_str, "%Y-%m-%d").date() if new_bday_str else bday
        gid = pick_group(conn)
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE contacts SET first_name=%s, last_name=%s, email=%s, birthday=%s,
                group_id=COALESCE(%s, group_id) WHERE id=%s
            """, (new_fname, new_lname, new_email, new_bday, gid, cid))
        conn.commit()


def delete_contact():
    cid = input_str("Contact id to delete: ")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM contacts WHERE id=%s", (cid,))
            if cur.rowcount:
                print("Deleted.")
            else:
                print("error")
        conn.commit()


def add_phone_menu():
    name  = input_str("Contact name: ")
    phone = input_str("Phone number: ")
    ptype = pick_phone_type()
    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("CALL add_phone(%s,%s,%s)", (name, phone, ptype))
                conn.commit()
                print("Phone added")
            except Exception as e:
                conn.rollback()
                print(f"Error: {e}")


def move_to_group_menu():
    name  = input_str("Contact name: ")
    group = input_str("Group name: ")
    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("CALL move_to_group(%s,%s)", (name, group))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Error: {e}")


# ── Export / Import ────────────────────────────────────────────────────────────
def export_json():
    path = input("File path: ").strip() or "contacts.json"
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email,
                       c.birthday::text AS birthday, g.name AS group_name
                FROM contacts c LEFT JOIN groups g ON g.id = c.group_id
                ORDER BY c.first_name
            """)
            contacts = [dict(r) for r in cur.fetchall()]
            for c in contacts:
                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id=%s", (c["id"],)
                )
                c["phones"] = [dict(p) for p in cur.fetchall()]
                del c["id"]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(contacts)} contacts to {path}")


def _get_or_create_group(cur, group_name):
    if not group_name:
        return None
    cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
    return cur.fetchone()[0]


def import_json():
    path = input("File path : ").strip() or "contacts.json"
    if not os.path.exists(path):
        print("File not found.")
        return
    with open(path, encoding="utf-8") as f:
        contacts = json.load(f)

    inserted = skipped = overwritten = 0
    with get_conn() as conn:
        for c in contacts:
            fname = c.get("first_name", "")
            lname = c.get("last_name")
            email = c.get("email")
            bday  = c.get("birthday")
            grp   = c.get("group_name")
            phones = c.get("phones", [])

            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM contacts WHERE first_name ILIKE %s AND (last_name ILIKE %s OR (last_name IS NULL AND %s IS NULL))",
                    (fname, lname, lname)
                )
                existing = cur.fetchone()

            if existing:
                print(f"  Duplicate: {fname} {lname or ''}")
                choice = input("s - skip / o - overwrite? ").strip().lower()
                if choice == "o":
                    with conn.cursor() as cur:
                        gid = _get_or_create_group(cur, grp)
                        cur.execute("""
                            UPDATE contacts SET email=%s, birthday=%s, group_id=%s
                            WHERE id=%s
                        """, (email, bday, gid, existing[0]))
                        cur.execute("DELETE FROM phones WHERE contact_id=%s", (existing[0],))
                        for p in phones:
                            cur.execute(
                                "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                                (existing[0], p.get("phone"), p.get("type", "mobile"))
                            )
                    overwritten += 1
                else:
                    skipped += 1
            else:
                with conn.cursor() as cur:
                    gid = _get_or_create_group(cur, grp)
                    cur.execute("""
                        INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                        VALUES (%s,%s,%s,%s,%s) RETURNING id
                    """, (fname, lname, email, bday, gid))
                    cid = cur.fetchone()[0]
                    for p in phones:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, p.get("phone"), p.get("type", "mobile"))
                        )
                inserted += 1
        conn.commit()
    print(f"  Done. Inserted={inserted} Overwritten={overwritten} Skipped={skipped}")


def import_csv():
    path = input("File path : ").strip() or "contacts.csv"
    if not os.path.exists(path):
        print("File not found")
        return
    inserted = 0
    with get_conn() as conn, open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = row.get("first_name", "").strip()
            if not fname:
                continue
            lname = row.get("last_name", "").strip() or None
            email = row.get("email", "").strip() or None
            bday_str = row.get("birthday", "").strip()
            bday = None
            if bday_str:
                try:
                    bday = datetime.strptime(bday_str, "%Y-%m-%d").date()
                except ValueError:
                    pass
            grp   = row.get("group", "").strip() or None
            phone = row.get("phone", "").strip() or None
            ptype = row.get("phone_type", "mobile").strip() or "mobile"

            with conn.cursor() as cur:
                gid = _get_or_create_group(cur, grp)
                cur.execute("""
                    INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                    VALUES (%s,%s,%s,%s,%s) RETURNING id
                """, (fname, lname, email, bday, gid))
                cid = cur.fetchone()[0]
                if phone:
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                        (cid, phone, ptype)
                    )
            inserted += 1
        conn.commit()
    print(f"  Imported {inserted} contacts from CSV.")


# ── Main menu ──────────────────────────────────────────────────────────────────
MENU = """
1. Add contact                  2. List all contacts            
3. Search (name/phone/email)    4. Filter by group              
5. Search by email              6. Sort contacts                
7. Browse pages (next/prev)     8. Update contact               
9. Delete contact               10. Add phone to contact         
11. Move contact to group       12. Export to JSON               
13. Import from JSON            14. Import from CSV              
                       0. Exit                         
"""

ACTIONS = {
    "1":  add_contact,
    "2":  list_all_contacts,
    "3":  search_contacts_menu,
    "4":  filter_by_group,
    "5":  sorted_contacts,
    "6":  paginated_browse,
    "7":  update_contact,
    "8":  delete_contact,
    "9": add_phone_menu,
    "10": move_to_group_menu,
    "11": export_json,
    "12": import_json,
    "13": import_csv,
}

def main():
    print("Connecting")
    setup_schema()
    while True:
        print(MENU)
        choice = input("Choose option: ").strip()
        if choice == "0":
            break
        action = ACTIONS.get(choice)
        if action:
            try:
                action()
            except Exception as e:
                print(f"Error {e}")
        else:
            print("Error ")

if __name__ == "__main__":
    main()