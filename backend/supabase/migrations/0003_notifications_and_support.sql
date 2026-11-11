-- Closet Loop — Migration 0003: Notifications and Support

-- 1. notifications
CREATE TABLE IF NOT EXISTS public.notifications (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    event_key text NOT NULL,
    type text NOT NULL
        CONSTRAINT notifications_type_check CHECK (
            type IN ('data_export_ready', 'data_export_failed')
        ),
    title text NOT NULL
        CONSTRAINT notifications_title_len CHECK (char_length(title) BETWEEN 1 AND 200),
    body text NOT NULL
        CONSTRAINT notifications_body_len CHECK (char_length(body) BETWEEN 1 AND 500),
    target_type text NOT NULL
        CONSTRAINT notifications_target_type_check CHECK (
            target_type IN ('settings_privacy', 'data_export')
        ),
    target_id uuid NULL,
    read_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (owner_id, event_key)
);

CREATE INDEX IF NOT EXISTS idx_notifications_owner_created
ON public.notifications(owner_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_notifications_owner_unread
ON public.notifications(owner_id, created_at DESC)
WHERE read_at IS NULL;

-- 2. support_requests
CREATE TABLE IF NOT EXISTS public.support_requests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    reference_code text NOT NULL UNIQUE,
    request_key text NOT NULL,
    category text NOT NULL
        CONSTRAINT support_requests_category_check CHECK (
            category IN ('account', 'media_ai', 'wardrobe', 'outfit_planner', 'privacy_data', 'bug', 'feedback')
        ),
    subject text NOT NULL
        CONSTRAINT support_requests_subject_len CHECK (char_length(btrim(subject)) BETWEEN 5 AND 120),
    description text NOT NULL
        CONSTRAINT support_requests_description_len CHECK (char_length(btrim(description)) BETWEEN 20 AND 4000),
    diagnostics jsonb NULL
        CONSTRAINT support_requests_diagnostics_size CHECK (diagnostics IS NULL OR octet_length(diagnostics::text) <= 2048),
    status text NOT NULL DEFAULT 'received'
        CONSTRAINT support_requests_status_check CHECK (status IN ('received', 'in_review', 'closed')),
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    closed_at timestamptz NULL,
    UNIQUE (owner_id, request_key)
);

CREATE INDEX IF NOT EXISTS idx_support_requests_owner_created
ON public.support_requests(owner_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_support_requests_status_created
ON public.support_requests(status, created_at DESC);

CREATE TRIGGER trg_support_requests_updated_at
BEFORE UPDATE ON public.support_requests
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 3. support_audit_events (Operator only, never exposed via Data API)
CREATE TABLE IF NOT EXISTS public.support_audit_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id uuid NULL REFERENCES public.support_requests(id) ON DELETE SET NULL,
    operator_id text NOT NULL,
    action text NOT NULL
        CONSTRAINT support_audit_action_check CHECK (action IN ('viewed', 'status_in_review', 'status_closed', 'redacted_on_account_delete')),
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE INDEX IF NOT EXISTS idx_support_audit_request ON public.support_audit_events(request_id, created_at DESC);

