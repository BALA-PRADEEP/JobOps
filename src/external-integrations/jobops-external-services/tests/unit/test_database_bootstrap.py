from scripts.bootstrap_database import EXPECTED_TABLES, classify_existing_tables


def test_fresh_database_is_safe():
    safe, foreign = classify_existing_tables(set())
    assert safe is True
    assert foreign == set()


def test_existing_jobops_schema_is_safe():
    safe, foreign = classify_existing_tables(EXPECTED_TABLES)
    assert safe is True
    assert foreign == set()


def test_foreign_tables_fail_isolation_check():
    safe, foreign = classify_existing_tables({"customers", "invoices"})
    assert safe is False
    assert foreign == {"customers", "invoices"}
