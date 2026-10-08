import duckdb
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "ecommerce.duckdb"

if len(sys.argv) != 2:
    print("Usage: python src/run_sql.py <sql_file>")
    sys.exit(1)

sql_file = Path(sys.argv[1])

if not sql_file.exists():
    print(f"SQL file not found: {sql_file}")
    sys.exit(1)

con = duckdb.connect(str(DB_PATH))

print(f"Running: {sql_file}")
print("=" * 70)

sql = sql_file.read_text()

# Split statements and execute individually
statements = [
    statement.strip()
    for statement in sql.split(";")
    if statement.strip()
]

for i, statement in enumerate(statements, start=1):

    print(f"\n--- Query {i} ---")

    try:
        result = con.execute(statement)

        columns = [desc[0] for desc in result.description]
        rows = result.fetchmany(20)

        print(" | ".join(columns))

        for row in rows:
            print(" | ".join(str(value) for value in row))

    except Exception as e:
        print(f"ERROR: {e}")

con.close()
