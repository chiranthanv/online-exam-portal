from django.db import migrations


def install(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == 'postgresql':
        schema_editor.execute("""CREATE FUNCTION reject_audit_mutation() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION 'Audit records are append-only'; END; $$ LANGUAGE plpgsql""")
        schema_editor.execute('CREATE TRIGGER audit_immutable BEFORE UPDATE OR DELETE ON audit_logs FOR EACH ROW EXECUTE FUNCTION reject_audit_mutation()')
    elif vendor == 'sqlite':
        for operation in ('UPDATE', 'DELETE'):
            schema_editor.execute(f"CREATE TRIGGER audit_no_{operation.lower()} BEFORE {operation} ON audit_logs BEGIN SELECT RAISE(ABORT, 'Audit records are append-only'); END")


def uninstall(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('DROP TRIGGER IF EXISTS audit_immutable ON audit_logs')
        schema_editor.execute('DROP FUNCTION IF EXISTS reject_audit_mutation()')
    elif schema_editor.connection.vendor == 'sqlite':
        schema_editor.execute('DROP TRIGGER IF EXISTS audit_no_update')
        schema_editor.execute('DROP TRIGGER IF EXISTS audit_no_delete')


class Migration(migrations.Migration):
    dependencies = [('portal', '0001_initial')]
    operations = [migrations.RunPython(install, uninstall)]
