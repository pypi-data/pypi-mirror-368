# Файл: sensory_data_client/db/triggers.py
from sqlalchemy import DDL, event
from .document_orm import DocumentORM
from .documentLine_orm import DocumentLineORM

# --- Триггер для обновления поля 'edited' ---

# ✅ РЕШЕНИЕ: Разделяем КАЖДУЮ команду на свой собственный DDL объект.

# 1. DDL для создания функции (это одна команда, все в порядке)
create_update_function_ddl = DDL("""
    CREATE OR REPLACE FUNCTION update_edited_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.edited = now();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
""")

# 2. DDL для УДАЛЕНИЯ старого триггера (отдельная команда)
drop_update_trigger_ddl = DDL("""
    DROP TRIGGER IF EXISTS trg_documents_update_edited ON documents;
""")

# 3. DDL для СОЗДАНИЯ нового триггера (отдельная команда)
create_update_trigger_ddl = DDL("""
    CREATE TRIGGER trg_documents_update_edited
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_edited_column();
""")


# --- Триггер для pg_notify ---

# 4. DDL для создания функции уведомления (одна команда)
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

# 5. DDL для УДАЛЕНИЯ старого триггера уведомления
drop_notify_trigger_ddl = DDL("""
    DROP TRIGGER IF EXISTS trg_documents_after_insert ON documents;
""")

# 6. DDL для СОЗДАНИЯ нового триггера уведомления
create_notify_trigger_ddl = DDL("""
    CREATE TRIGGER trg_documents_after_insert
    AFTER INSERT ON documents
    FOR EACH ROW
    EXECUTE FUNCTION notify_new_document();
""")


# --- "Привязываем" все DDL к событию "after_create" для таблицы DocumentORM ---
# SQLAlchemy выполнит их последовательно, один за другим.

# Слушатели для триггера 'edited'
event.listen(DocumentORM.__table__, "after_create", create_update_function_ddl.execute_if(dialect="postgresql"))
event.listen(DocumentORM.__table__, "after_create", drop_update_trigger_ddl.execute_if(dialect="postgresql"))
event.listen(DocumentORM.__table__, "after_create", create_update_trigger_ddl.execute_if(dialect="postgresql"))

# Слушатели для триггера 'notify'
event.listen(DocumentORM.__table__, "after_create", create_notify_function_ddl.execute_if(dialect="postgresql"))
event.listen(DocumentORM.__table__, "after_create", drop_notify_trigger_ddl.execute_if(dialect="postgresql"))
event.listen(DocumentORM.__table__, "after_create", create_notify_trigger_ddl.execute_if(dialect="postgresql"))


# 1. DDL для создания функции, которая парсит строку и создает задачу
create_image_upsert_function_ddl = DDL("""
CREATE OR REPLACE FUNCTION upsert_document_image_from_line()
RETURNS trigger AS $$
DECLARE
    v_full_path text;
    v_image_hash text;
    v_image_id uuid;
BEGIN
    -- Работаем только если это строка с типом 'image_placeholder'
    IF NEW.block_type IS NULL OR NEW.block_type <> 'image_placeholder' THEN
        RETURN NEW;
    END IF;

    -- Извлекаем ПОЛНЫЙ ПУТЬ к файлу из markdown-разметки: ![...](path/to/file.png)
    SELECT (regexp_matches(NEW.content, '!\\[[^\\]]*\\]\\(([^)]+)\\)'))[1]
    INTO v_full_path;

    -- Если путь не найден, выходим
    IF v_full_path IS NULL OR length(v_full_path) = 0 THEN
        RETURN NEW;
    END IF;

    -- --- ИЗМЕНЕНИЕ: Логика сборки object_key удалена ---
    -- Путь уже полностью сформирован парсером.

    -- Извлекаем хеш изображения из полного пути (это имя файла без расширения)
    -- Пример: из 'pdf/doc_id/images/hash123.png' получаем 'hash123'
    SELECT (regexp_matches(v_full_path, '.*/([^/]+)\\.[^.]+$'))[1]
    INTO v_image_hash;
    
    IF v_image_hash IS NULL THEN
        -- Фоллбэк для случаев, если путь не содержит слешей (маловероятно, но надежно)
        v_image_hash := regexp_replace(v_full_path, '\\.[^.]+$', '', 'g');
    END IF;

    INSERT INTO document_images (document_id, source_line_id, filename, image_hash, status, attempts)
    VALUES (NEW.document_id, NEW.id, v_full_path, v_image_hash, 'pending', 0)
    ON CONFLICT (document_id, image_hash)
    DO UPDATE SET
        source_line_id = EXCLUDED.source_line_id,
        filename = EXCLUDED.filename
        updated_at = now(),
        status = CASE WHEN document_images.status = 'failed' THEN 'pending' ELSE document_images.status END
    RETURNING id INTO v_image_id;

    -- Отправляем уведомление диспетчеру с ID созданной/обновленной задачи
    PERFORM pg_notify('image_jobs', json_build_object('image_id', v_image_id::text)::text);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""")

# 2. DDL для удаления старого триггера (для идемпотентности)
drop_image_upsert_trigger_ddl = DDL("""
    DROP TRIGGER IF EXISTS trg_document_lines_image_upsert ON document_lines;
""")

# 3. DDL для создания нового триггера
create_image_upsert_trigger_ddl = DDL("""
    CREATE TRIGGER trg_document_lines_image_upsert
    AFTER INSERT OR UPDATE OF block_type, content ON document_lines
    FOR EACH ROW
    EXECUTE FUNCTION upsert_document_image_from_line();
""")
# --- "Привязываем" все DDL к событию "after_create" для таблицы DocumentLineORM ---
# SQLAlchemy выполнит их последовательно, один за другим.

event.listen(DocumentLineORM.__table__, "after_create", create_image_upsert_function_ddl.execute_if(dialect="postgresql"))
event.listen(DocumentLineORM.__table__, "after_create", drop_image_upsert_trigger_ddl.execute_if(dialect="postgresql"))
event.listen(DocumentLineORM.__table__, "after_create", create_image_upsert_trigger_ddl.execute_if(dialect="postgresql"))



print("[sensory-data-client] Database triggers registered for DocumentORM.")