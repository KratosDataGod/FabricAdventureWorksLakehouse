"""Check that the repo is internally consistent. Run from the repo root: python scripts/validate_repo.py

Needs only the Python standard library. It checks that:
  1. every data file matches the format and schema declared in NoteBooks/01_Load_Silver.ipynb
     (encoding, delimiter, header, data types, row counts, unique keys, relationships);
  2. every JSON file and notebook parses;
  3. the semantic model's relationships and roles point at tables and columns that exist;
  4. the report uses only tables, columns and measures that exist in the semantic model.

Exits with status 1 and lists the problems if anything is off.
"""
import datetime
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "AdventureWorks")
MODEL = os.path.join(ROOT, "PowerBI", "AdventureWorks.SemanticModel", "definition")
REPORT = os.path.join(ROOT, "PowerBI", "AdventureWorks.Report")
problems = []


def problem(message):
    problems.append(message)


# ---------------------------------------------------------------- 1. data files

def load_table_definitions():
    """Read TABLES and RELATIONSHIPS from the load notebook, so there is one source of truth."""
    with open(os.path.join(ROOT, "NoteBooks", "01_Load_Silver.ipynb"), encoding="utf-8") as handle:
        notebook = json.load(handle)
    scope = {}
    for cell in notebook["cells"]:
        source = "".join(cell["source"])
        if cell["cell_type"] == "code" and re.match(r"\s*(#[^\n]*\n)*\s*(TABLES|RELATIONSHIPS) = ", source):
            exec(source, scope)
    return scope["TABLES"], scope["RELATIONSHIPS"]


def is_date(value):
    try:
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)) and bool(datetime.date.fromisoformat(value))
    except ValueError:
        return False


CHECKS = {
    "INT": lambda v: re.fullmatch(r"-?\d+", v) is not None,
    "BOOLEAN": lambda v: v in ("true", "false"),
    "DECIMAL(19,4)": lambda v: re.fullmatch(r"-?\d+(\.\d{1,4})?", v) is not None,
    "DOUBLE": lambda v: re.fullmatch(r"-?\d+(\.\d+)?", v) is not None,
    "DATE": is_date,
    "STRING": lambda v: v == v.strip(),
}


def check_data():
    tables, relationships = load_table_definitions()
    files = {os.path.basename(path)[:-4] for path in glob.glob(os.path.join(DATA, "*.csv"))}
    for name in sorted(files - set(tables)):
        problem(f"{name}.csv has no table definition in the load notebook")
    for name in sorted(set(tables) - files):
        problem(f"{name}.csv is missing")

    values = {}   # (table, column) -> set of non-empty values, for the key and relationship checks
    for name in sorted(set(tables) & files):
        spec = tables[name]
        columns = [tuple(line.strip().rstrip(",").split(" ", 1)) for line in spec["schema"].strip().splitlines()]
        with open(os.path.join(DATA, name + ".csv"), "rb") as handle:
            raw = handle.read()
        if raw.startswith(b"\xef\xbb\xbf"):
            problem(f"{name}: file starts with a byte order mark")
        if b"\r" in raw:
            problem(f"{name}: file has CR characters; line endings must be LF")
        if not raw.endswith(b"\n"):
            problem(f"{name}: file does not end with a newline")
        try:
            lines = raw.decode("utf-8").split("\n")[:-1]
        except UnicodeDecodeError as error:
            problem(f"{name}: not valid UTF-8 ({error})")
            continue
        if lines[0].split("|") != [column for column, _ in columns]:
            problem(f"{name}: header does not match the schema in the load notebook")
            continue
        if len(lines) - 1 != spec["rows"]:
            problem(f"{name}: expected {spec['rows']} rows, found {len(lines) - 1}")
        seen = {column: set() for column, _ in columns}
        keys = set()
        key_index = [[column for column, _ in columns].index(k) for k in spec["key"]]
        reported = 0
        for number, line in enumerate(lines[1:], 2):
            fields = line.split("|")
            if len(fields) != len(columns):
                if reported < 5:
                    problem(f"{name} line {number}: {len(fields)} fields, expected {len(columns)}")
                reported += 1
                continue
            for (column, kind), value in zip(columns, fields):
                if value == "":
                    continue
                if not CHECKS[kind](value):
                    if reported < 5:
                        problem(f"{name} line {number}: {column} value {value!r} is not a valid {kind}")
                    reported += 1
                seen[column].add(value)
            key = tuple(fields[i] for i in key_index)
            if "" in key:
                problem(f"{name} line {number}: key {spec['key']} is empty")
            keys.add(key)
        if len(keys) != len(lines) - 1 and reported == 0:
            problem(f"{name}: key {spec['key']} is not unique")
        for column in seen:
            values[(name, column)] = seen[column]

    for child, child_column, parent, parent_column in relationships:
        if (child, child_column) not in values or (parent, parent_column) not in values:
            problem(f"relationship {child}.{child_column} -> {parent}.{parent_column} names a table or column that does not exist")
            continue
        orphans = values[(child, child_column)] - values[(parent, parent_column)]
        if orphans:
            problem(f"{child}.{child_column}: {len(orphans)} values not found in {parent}.{parent_column}")
    return len(tables)


# ---------------------------------------------------------------- 2. JSON files

def check_json():
    count = 0
    for directory, _, names in os.walk(ROOT):
        if ".git" in directory.split(os.sep):
            continue
        for name in names:
            if name.endswith((".json", ".ipynb", ".pbir", ".pbism", ".pbip", ".platform")):
                count += 1
                try:
                    with open(os.path.join(directory, name), encoding="utf-8-sig") as handle:
                        json.load(handle)
                except ValueError as error:
                    problem(f"{os.path.relpath(os.path.join(directory, name), ROOT)}: invalid JSON ({error})")
    return count


# ---------------------------------------------------------------- 3 and 4. semantic model and report

def unquote(name):
    name = name.strip()
    return name[1:-1].replace("''", "'") if name.startswith("'") else name


def split_reference(reference):
    """Split a TMDL column reference such as Sales.'Order Date' into table and column."""
    match = re.fullmatch(r"\s*('(?:[^']|'')*'|[^.']+)\.('(?:[^']|'')*'|.+?)\s*", reference)
    return unquote(match.group(1)), unquote(match.group(2))


def read_model():
    """Return {table: {"columns": set, "measures": set}} from the TMDL table files."""
    model = {}
    for path in glob.glob(os.path.join(MODEL, "tables", "*.tmdl")):
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        table = unquote(re.search(r"(?m)^table (.+)$", text).group(1))
        model[table] = {
            "columns": {unquote(m) for m in re.findall(r"(?m)^\tcolumn (.+)$", text)},
            "measures": {unquote(m) for m in re.findall(r"(?m)^\tmeasure ('(?:[^']|'')*'|[^ =]+) =", text)},
        }
    return model


def check_model(model):
    with open(os.path.join(MODEL, "model.tmdl"), encoding="utf-8") as handle:
        declared = {unquote(m) for m in re.findall(r"(?m)^ref table (.+)$", handle.read())}
    if declared != set(model):
        problem(f"model.tmdl and the tables folder disagree: {sorted(declared ^ set(model))}")
    with open(os.path.join(MODEL, "relationships.tmdl"), encoding="utf-8") as handle:
        for reference in re.findall(r"(?m)^\t(?:from|to)Column: (.+)$", handle.read()):
            table, column = split_reference(reference)
            if column not in model.get(table, {}).get("columns", ()):
                problem(f"relationships.tmdl: {reference} does not exist in the model")
    for path in glob.glob(os.path.join(MODEL, "roles", "*.tmdl")):
        with open(path, encoding="utf-8") as handle:
            for table in re.findall(r"(?m)^\ttablePermission ('(?:[^']|'')*'|[^ =]+) =", handle.read()):
                if unquote(table) not in model:
                    problem(f"{os.path.basename(path)}: table {table} does not exist in the model")


def fields_used(node, found):
    """Collect every (kind, table, name) field reference in a report visual."""
    if isinstance(node, dict):
        for kind in ("Column", "Measure"):
            reference = node.get(kind)
            if isinstance(reference, dict) and "Property" in reference:
                entity = reference.get("Expression", {}).get("SourceRef", {}).get("Entity")
                if entity:
                    found.add((kind, entity, reference["Property"]))
        for value in node.values():
            fields_used(value, found)
    elif isinstance(node, list):
        for value in node:
            fields_used(value, found)


def check_report(model):
    used = set()
    for path in glob.glob(os.path.join(REPORT, "definition", "pages", "*", "visuals", "*", "visual.json")):
        with open(path, encoding="utf-8") as handle:
            fields_used(json.load(handle), used)
    for kind, table, name in sorted(used):
        group = "columns" if kind == "Column" else "measures"
        if name not in model.get(table, {}).get(group, ()):
            problem(f"report uses {kind.lower()} {table}[{name}], which is not in the semantic model")
    return len(used)


if __name__ == "__main__":
    table_count = check_data()
    json_count = check_json()
    model = read_model()
    check_model(model)
    field_count = check_report(model)
    if problems:
        print(f"{len(problems)} problem(s) found:")
        for message in problems:
            print("  - " + message)
        sys.exit(1)
    print(f"OK: {table_count} data files, {json_count} JSON files, {len(model)} model tables, {field_count} report fields checked.")
