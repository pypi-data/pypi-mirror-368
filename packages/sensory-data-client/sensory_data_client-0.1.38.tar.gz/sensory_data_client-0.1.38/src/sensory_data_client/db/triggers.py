# Файл: sensory_data_client/db/triggers.py
from sqlalchemy import DDL, event
from .document_orm import DocumentORM

# --- Триггер для обновления поля 'edited' ---

# ✅ РЕШЕНИЕ: Каждая команда - это отдельный DDL объект.

# 1. DDL для создания функции
create_update_function_ddl = DDL("""
    CREATE OR REPLACE FUNCTION update_edited_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.edited = now();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
""")

# 2. DDL для создания самого триггера (включает DROP IF EXISTS для идемпотентности)
create_update_trigger_ddl = DDL("""
    DROP TRIGGER IF EXISTS trg_documents_update_edited ON documents;
    CREATE TRIGGER trg_documents_update_edited
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_edited_column();
""")


# --- Триггер для pg_notify ---

# 3. DDL для создания функции уведомления
create_notify_function_ddl = DDL("""
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
""")

# 4. DDL для создания триггера уведомления
create_notify_trigger_ddl = DDL("""
    DROP TRIGGER IF EXISTS trg_documents_after_insert ON documents;
    CREATE TRIGGER trg_documents_after_insert
    AFTER INSERT ON documents
    FOR EACH ROW
    EXECUTE FUNCTION notify_new_document();
""")


# --- "Привязываем" все DDL к событию "after_create" для таблицы DocumentORM ---
# SQLAlchemy выполнит их в том порядке, в котором они зарегистрированы.

# Слушатели для триггера 'edited'
event.listen(
    DocumentORM.__table__,
    "after_create",
    create_update_function_ddl.execute_if(dialect="postgresql")
)
event.listen(
    DocumentORM.__table__,
    "after_create",
    create_update_trigger_ddl.execute_if(dialect="postgresql")
)

# Слушатели для триггера 'notify'
event.listen(
    DocumentORM.__table__,
    "after_create",
    create_notify_function_ddl.execute_if(dialect="postgresql")
)
event.listen(
    DocumentORM.__table__,
    "after_create",
    create_notify_trigger_ddl.execute_if(dialect="postgresql")
)

print("[sensory-data-client] Database triggers registered for DocumentORM.")