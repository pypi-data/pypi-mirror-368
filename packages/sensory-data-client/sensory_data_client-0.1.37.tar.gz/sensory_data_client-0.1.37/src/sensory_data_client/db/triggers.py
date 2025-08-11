# Файл: sensory_data_client/db/triggers.py
from sqlalchemy import DDL, event
from .document_orm import DocumentORM

# 1. Определяем DDL для триггера обновления 'edited'
update_edited_trigger_ddl = DDL("""
    CREATE OR REPLACE FUNCTION update_edited_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.edited = now();
        RETURN NEW;
    END;
    $$ language 'plpgsql';

    DROP TRIGGER IF EXISTS trg_documents_update_edited ON documents;
    CREATE TRIGGER trg_documents_update_edited
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_edited_column();
""")

# 2. Определяем DDL для триггера, который запускает парсинг
notify_new_doc_trigger_ddl = DDL("""
    CREATE OR REPLACE FUNCTION notify_new_document()
    RETURNS trigger AS $$
    DECLARE
        payload JSON;
    BEGIN
        payload = json_build_object('doc_id', NEW.id::text, 'file_name', NEW.name);
        PERFORM pg_notify('docparser_new_doc', payload::text);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_documents_after_insert ON documents;
    CREATE TRIGGER trg_documents_after_insert
    AFTER INSERT ON documents
    FOR EACH ROW
    EXECUTE FUNCTION notify_new_document();
""")

# 3. "Привязываем" DDL-команды к событию "after_create" для таблицы DocumentORM
# Это "сердце" всего механизма.
event.listen(
    DocumentORM.__table__,
    "after_create",
    update_edited_trigger_ddl.execute_if(dialect="postgresql")
)
event.listen(
    DocumentORM.__table__,
    "after_create",
    notify_new_doc_trigger_ddl.execute_if(dialect="postgresql")
)

print("[sensory-data-client] Database triggers registered for DocumentORM.")