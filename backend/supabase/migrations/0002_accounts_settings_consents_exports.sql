-- Closet Loop — Migration 0002: Accounts, Settings, Consents, Data Exports, Account Deletion

-- 1. user_settings
CREATE TABLE IF NOT EXISTS public.user_settings (
    owner_id uuid PRIMARY KEY REFERENCES public.profiles(id) ON DELETE RESTRICT,
    planner_default_view text NOT NULL DEFAULT 'week'
        CONSTRAINT user_settings_view_check CHECK (planner_default_view IN ('week', 'month')),
    activity_notifications boolean NOT NULL DEFAULT true,
    analytics_opt_in boolean NOT NULL DEFAULT false,
    version integer NOT NULL DEFAULT 1
        CONSTRAINT user_settings_version_positive CHECK (version >= 1),
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE TRIGGER trg_user_settings_updated_at
BEFORE UPDATE ON public.user_settings
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 2. account_consents
CREATE TABLE IF NOT EXISTS public.account_consents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    kind text NOT NULL
        CONSTRAINT account_consents_kind_check CHECK (kind IN ('terms', 'privacy', 'ai', 'analytics')),
    policy_version text NOT NULL,
    action text NOT NULL,
    revision integer NOT NULL
        CONSTRAINT account_consents_revision_positive CHECK (revision >= 1),
    request_key text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (owner_id, kind, revision),
    UNIQUE (owner_id, request_key),
    CONSTRAINT account_consents_kind_action_check CHECK (
        (kind = 'terms' AND action IN ('accepted')) OR
        (kind = 'privacy' AND action IN ('acknowledged')) OR
        (kind = 'ai' AND action IN ('accepted', 'withdrawn')) OR
        (kind = 'analytics' AND action IN ('accepted', 'withdrawn'))
    )
);

CREATE INDEX IF NOT EXISTS idx_account_consents_owner_created ON public.account_consents(owner_id, created_at DESC, id DESC);

-- 3. data_export_requests
CREATE TABLE IF NOT EXISTS public.data_export_requests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    request_key text NOT NULL,
    status text NOT NULL DEFAULT 'queued'
        CONSTRAINT data_export_requests_status_check CHECK (
            status IN ('queued', 'running', 'ready', 'failed', 'expired', 'cancelled')
        ),
    snapshot_at timestamptz NULL,
    object_path text NULL,
    expires_at timestamptz NULL,
    error_code text NULL,
    attempts integer NOT NULL DEFAULT 0,
    available_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    lease_token uuid NULL,
    lease_until timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (owner_id, request_key)
);

-- Only one queued or running export request per owner at a time
CREATE UNIQUE INDEX IF NOT EXISTS idx_data_exports_one_active_per_owner
ON public.data_export_requests(owner_id)
WHERE status IN ('queued', 'running');

CREATE INDEX IF NOT EXISTS idx_data_exports_owner_created
ON public.data_export_requests(owner_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_data_exports_queue
ON public.data_export_requests(status, available_at)
WHERE status IN ('queued', 'running');

CREATE INDEX IF NOT EXISTS idx_data_exports_expires
ON public.data_export_requests(expires_at)
WHERE status = 'ready';

CREATE TRIGGER trg_data_export_requests_updated_at
BEFORE UPDATE ON public.data_export_requests
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 4. account_deletion_requests
CREATE TABLE IF NOT EXISTS public.account_deletion_requests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NULL,
    request_key text NOT NULL,
    reference_code text NOT NULL UNIQUE,
    status text NOT NULL DEFAULT 'requested'
        CONSTRAINT account_deletion_requests_status_check CHECK (
            status IN ('requested', 'running', 'failed', 'completed')
        ),
    cleanup_manifest jsonb NOT NULL DEFAULT '{}'::jsonb,
    attempts integer NOT NULL DEFAULT 0,
    available_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    lease_token uuid NULL,
    lease_until timestamptz NULL,
    error_code text NULL,
    requested_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    finished_at timestamptz NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_account_deletion_one_active_per_user
ON public.account_deletion_requests(user_id)
WHERE user_id IS NOT NULL AND status IN ('requested', 'running', 'failed');

CREATE INDEX IF NOT EXISTS idx_account_deletion_queue
ON public.account_deletion_requests(status, available_at)
WHERE status IN ('requested', 'running');

CREATE TRIGGER trg_account_deletion_requests_updated_at
BEFORE UPDATE ON public.account_deletion_requests
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

