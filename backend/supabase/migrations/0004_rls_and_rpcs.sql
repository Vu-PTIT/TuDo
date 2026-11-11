-- Closet Loop — Migration 0004: Row-Level Security (RLS) and Transactional RPCs

-- Enable RLS on all user/application tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.account_consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_export_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.account_deletion_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.media_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wardrobe_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.outfits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.outfit_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.planner_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wear_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wear_log_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.image_jobs ENABLE ROW LEVEL SECURITY;

-- Helper function: check whether account has a pending deletion tombstone
CREATE OR REPLACE FUNCTION public.is_account_deleting(p_user_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.account_deletion_requests adr
        WHERE adr.user_id = p_user_id
          AND adr.status IN ('requested', 'running', 'failed')
    );
$$;

-- Helper function: raise exception if caller is unauthenticated or account is deleting
CREATE OR REPLACE FUNCTION public.require_active_owner()
RETURNS uuid
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
BEGIN
    v_uid := auth.uid();
    IF v_uid IS NULL THEN
        RAISE EXCEPTION 'UNAUTHENTICATED: Missing authenticated user' USING ERRCODE = '28000';
    END IF;
    IF public.is_account_deleting(v_uid) THEN
        RAISE EXCEPTION 'ACCOUNT_DELETION_PENDING: Account is scheduled for deletion' USING ERRCODE = '42501';
    END IF;
    RETURN v_uid;
END;
$$;

-- RLS SELECT Policies (owner-only read access for authenticated users)
CREATE POLICY profiles_select_own ON public.profiles
    FOR SELECT TO authenticated USING (id = auth.uid());

CREATE POLICY user_settings_select_own ON public.user_settings
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY account_consents_select_own ON public.account_consents
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY data_export_requests_select_own ON public.data_export_requests
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY notifications_select_own ON public.notifications
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY support_requests_select_own ON public.support_requests
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY media_assets_select_own ON public.media_assets
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY wardrobe_items_select_own ON public.wardrobe_items
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY outfits_select_own ON public.outfits
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY outfit_items_select_own ON public.outfit_items
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY planner_entries_select_own ON public.planner_entries
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY wear_logs_select_own ON public.wear_logs
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY wear_log_items_select_own ON public.wear_log_items
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

CREATE POLICY image_jobs_select_own ON public.image_jobs
    FOR SELECT TO authenticated USING (owner_id = auth.uid());

-- Revoke direct INSERT/UPDATE/DELETE from anon and authenticated; mutations go through controlled RPCs
REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM anon, authenticated;

-- ============================================================================
-- RPC 1: rpc_bootstrap_account
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_bootstrap_account(
    p_terms_version text,
    p_privacy_version text,
    p_display_name text DEFAULT 'Bạn',
    p_timezone text DEFAULT 'Asia/Ho_Chi_Minh'
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_created boolean := false;
    v_profile public.profiles%ROWTYPE;
    v_settings public.user_settings%ROWTYPE;
BEGIN
    v_uid := public.require_active_owner();

    PERFORM pg_advisory_xact_lock(hashtext('bootstrap:' || v_uid::text));

    IF public.is_account_deleting(v_uid) THEN
        RAISE EXCEPTION 'ACCOUNT_DELETION_PENDING: Account is scheduled for deletion' USING ERRCODE = '42501';
    END IF;

    SELECT * INTO v_profile FROM public.profiles WHERE id = v_uid FOR UPDATE;

    IF NOT FOUND THEN
        v_created := true;
        INSERT INTO public.profiles (id, display_name, timezone, version)
        VALUES (v_uid, COALESCE(NULLIF(btrim(p_display_name), ''), 'Bạn'), COALESCE(NULLIF(btrim(p_timezone), ''), 'Asia/Ho_Chi_Minh'), 1)
        RETURNING * INTO v_profile;

        INSERT INTO public.user_settings (owner_id, planner_default_view, activity_notifications, analytics_opt_in, version)
        VALUES (v_uid, 'week', true, false, 1)
        RETURNING * INTO v_settings;

        INSERT INTO public.account_consents (owner_id, kind, policy_version, action, revision, request_key)
        VALUES
            (v_uid, 'terms', p_terms_version, 'accepted', 1, 'bootstrap:terms:' || v_uid::text),
            (v_uid, 'privacy', p_privacy_version, 'acknowledged', 1, 'bootstrap:privacy:' || v_uid::text)
        ON CONFLICT (owner_id, request_key) DO NOTHING;
    ELSE
        SELECT * INTO v_settings FROM public.user_settings WHERE owner_id = v_uid;
    END IF;

    RETURN jsonb_build_object(
        'created', v_created,
        'profile', to_jsonb(v_profile),
        'settings', to_jsonb(v_settings)
    );
END;
$$;

-- ============================================================================
-- RPC 2: rpc_update_profile
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_update_profile(
    p_expected_version integer,
    p_display_name text DEFAULT NULL,
    p_timezone text DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_profile public.profiles%ROWTYPE;
BEGIN
    v_uid := public.require_active_owner();

    SELECT * INTO v_profile FROM public.profiles WHERE id = v_uid FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'PROFILE_NOT_READY: Profile not initialized' USING ERRCODE = 'P0002';
    END IF;

    IF v_profile.version <> p_expected_version THEN
        RAISE EXCEPTION 'CONFLICT: Profile version mismatch (expected %, actual %)', p_expected_version, v_profile.version USING ERRCODE = '40001';
    END IF;

    UPDATE public.profiles
    SET display_name = COALESCE(NULLIF(btrim(p_display_name), ''), display_name),
        timezone = COALESCE(NULLIF(btrim(p_timezone), ''), timezone),
        version = version + 1
    WHERE id = v_uid
    RETURNING * INTO v_profile;

    RETURN to_jsonb(v_profile);
END;
$$;

-- ============================================================================
-- RPC 3: rpc_set_onboarding_state
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_set_onboarding_state(
    p_action text
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_profile public.profiles%ROWTYPE;
BEGIN
    v_uid := public.require_active_owner();

    IF p_action NOT IN ('complete', 'skip') THEN
        RAISE EXCEPTION 'VALIDATION_ERROR: Invalid onboarding action' USING ERRCODE = '22023';
    END IF;

    SELECT * INTO v_profile FROM public.profiles WHERE id = v_uid FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'PROFILE_NOT_READY: Profile not initialized' USING ERRCODE = 'P0002';
    END IF;

    IF p_action = 'complete' AND v_profile.onboarding_completed_at IS NULL THEN
        UPDATE public.profiles
        SET onboarding_completed_at = timezone('utc', now()),
            onboarding_skipped_at = NULL
        WHERE id = v_uid
        RETURNING * INTO v_profile;
    ELSIF p_action = 'skip' AND v_profile.onboarding_skipped_at IS NULL AND v_profile.onboarding_completed_at IS NULL THEN
        UPDATE public.profiles
        SET onboarding_skipped_at = timezone('utc', now())
        WHERE id = v_uid
        RETURNING * INTO v_profile;
    END IF;

    RETURN to_jsonb(v_profile);
END;
$$;

-- ============================================================================
-- RPC 4: rpc_update_settings
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_update_settings(
    p_expected_version integer,
    p_planner_default_view text DEFAULT NULL,
    p_activity_notifications boolean DEFAULT NULL,
    p_analytics_opt_in boolean DEFAULT NULL,
    p_analytics_policy_version text DEFAULT '2026-11'
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_settings public.user_settings%ROWTYPE;
    v_next_rev integer;
BEGIN
    v_uid := public.require_active_owner();

    SELECT * INTO v_settings FROM public.user_settings WHERE owner_id = v_uid FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'PROFILE_NOT_READY: Settings not initialized' USING ERRCODE = 'P0002';
    END IF;

    IF v_settings.version <> p_expected_version THEN
        RAISE EXCEPTION 'CONFLICT: Settings version mismatch (expected %, actual %)', p_expected_version, v_settings.version USING ERRCODE = '40001';
    END IF;

    IF p_analytics_opt_in IS NOT NULL AND p_analytics_opt_in IS DISTINCT FROM v_settings.analytics_opt_in THEN
        SELECT COALESCE(MAX(revision), 0) + 1 INTO v_next_rev
        FROM public.account_consents
        WHERE owner_id = v_uid AND kind = 'analytics';

        INSERT INTO public.account_consents (
            owner_id, kind, policy_version, action, revision, request_key
        ) VALUES (
            v_uid,
            'analytics',
            p_analytics_policy_version,
            CASE WHEN p_analytics_opt_in THEN 'accepted' ELSE 'withdrawn' END,
            v_next_rev,
            'settings:analytics:v' || (v_settings.version + 1)::text
        );
    END IF;

    UPDATE public.user_settings
    SET planner_default_view = COALESCE(p_planner_default_view, planner_default_view),
        activity_notifications = COALESCE(p_activity_notifications, activity_notifications),
        analytics_opt_in = COALESCE(p_analytics_opt_in, analytics_opt_in),
        version = version + 1
    WHERE owner_id = v_uid
    RETURNING * INTO v_settings;

    RETURN to_jsonb(v_settings);
END;
$$;

-- ============================================================================
-- RPC 5: rpc_record_consent
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_record_consent(
    p_kind text,
    p_policy_version text,
    p_action text,
    p_request_key text,
    p_expected_revision integer
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_existing public.account_consents%ROWTYPE;
    v_current_rev integer;
    v_inserted public.account_consents%ROWTYPE;
BEGIN
    v_uid := public.require_active_owner();

    PERFORM pg_advisory_xact_lock(hashtext('consent:' || v_uid::text || ':' || p_kind));

    SELECT * INTO v_existing
    FROM public.account_consents
    WHERE owner_id = v_uid AND request_key = p_request_key;

    IF FOUND THEN
        RETURN to_jsonb(v_existing);
    END IF;

    SELECT COALESCE(MAX(revision), 0) INTO v_current_rev
    FROM public.account_consents
    WHERE owner_id = v_uid AND kind = p_kind;

    IF v_current_rev <> p_expected_revision THEN
        RAISE EXCEPTION 'CONFLICT: Consent revision mismatch for % (expected %, actual %)', p_kind, p_expected_revision, v_current_rev USING ERRCODE = '40001';
    END IF;

    INSERT INTO public.account_consents (
        owner_id, kind, policy_version, action, revision, request_key
    ) VALUES (
        v_uid, p_kind, p_policy_version, p_action, v_current_rev + 1, p_request_key
    )
    RETURNING * INTO v_inserted;

    RETURN to_jsonb(v_inserted);
END;
$$;

-- ============================================================================
-- RPC 6: rpc_save_outfit (Create or Update Outfit + 1..12 Items in Transaction)
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_save_outfit(
    p_outfit_id uuid,
    p_name text,
    p_notes text,
    p_style_tags text[],
    p_occasion_tags text[],
    p_items jsonb,
    p_expected_version integer DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_outfit public.outfits%ROWTYPE;
    v_item_count integer;
    v_invalid_count integer;
BEGIN
    v_uid := public.require_active_owner();

    v_item_count := jsonb_array_length(COALESCE(p_items, '[]'::jsonb));
    IF v_item_count < 1 OR v_item_count > 12 THEN
        RAISE EXCEPTION 'VALIDATION_ERROR: Outfit must contain between 1 and 12 items' USING ERRCODE = '22023';
    END IF;

    -- Verify all items belong to owner and are not deleted/archived
    SELECT COUNT(*) INTO v_invalid_count
    FROM jsonb_to_recordset(p_items) AS x(item_id uuid)
    LEFT JOIN public.wardrobe_items wi
        ON wi.id = x.item_id AND wi.owner_id = v_uid AND wi.deleted_at IS NULL AND wi.availability <> 'archived'
    WHERE wi.id IS NULL;

    IF v_invalid_count > 0 THEN
        RAISE EXCEPTION 'VALIDATION_ERROR: One or more items do not exist, are deleted, or are archived' USING ERRCODE = '22023';
    END IF;

    IF p_outfit_id IS NULL THEN
        INSERT INTO public.outfits (owner_id, name, notes, style_tags, occasion_tags, version)
        VALUES (v_uid, btrim(p_name), p_notes, COALESCE(p_style_tags, '{}'::text[]), COALESCE(p_occasion_tags, '{}'::text[]), 1)
        RETURNING * INTO v_outfit;
    ELSE
        SELECT * INTO v_outfit
        FROM public.outfits
        WHERE id = p_outfit_id AND owner_id = v_uid AND deleted_at IS NULL
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'NOT_FOUND: Outfit not found' USING ERRCODE = 'P0002';
        END IF;

        IF p_expected_version IS NULL OR v_outfit.version <> p_expected_version THEN
            RAISE EXCEPTION 'CONFLICT: Outfit version mismatch' USING ERRCODE = '40001';
        END IF;

        UPDATE public.outfits
        SET name = btrim(p_name),
            notes = p_notes,
            style_tags = COALESCE(p_style_tags, '{}'::text[]),
            occasion_tags = COALESCE(p_occasion_tags, '{}'::text[]),
            version = version + 1
        WHERE id = p_outfit_id AND owner_id = v_uid
        RETURNING * INTO v_outfit;

        DELETE FROM public.outfit_items WHERE outfit_id = p_outfit_id AND owner_id = v_uid;
    END IF;

    INSERT INTO public.outfit_items (outfit_id, item_id, owner_id, x, y, w, h, z_index)
    SELECT
        v_outfit.id,
        x.item_id,
        v_uid,
        x.x,
        x.y,
        x.w,
        x.h,
        x.z_index
    FROM jsonb_to_recordset(p_items) AS x(
        item_id uuid,
        x double precision,
        y double precision,
        w double precision,
        h double precision,
        z_index integer
    );

    RETURN to_jsonb(v_outfit);
END;
$$;

-- ============================================================================
-- RPC 7: rpc_confirm_wear (Idempotent by operation_key + optimistic concurrency)
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_confirm_wear(
    p_entry_id uuid,
    p_operation_key text,
    p_expected_version integer
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_entry public.planner_entries%ROWTYPE;
    v_tz text;
    v_today date;
    v_wear_log public.wear_logs%ROWTYPE;
    v_unavailable_count integer;
BEGIN
    v_uid := public.require_active_owner();

    SELECT * INTO v_entry
    FROM public.planner_entries
    WHERE id = p_entry_id AND owner_id = v_uid
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'NOT_FOUND: Planner entry not found' USING ERRCODE = 'P0002';
    END IF;

    -- 1. If operation_key matches the last committed operation, return current state idempotently
    IF v_entry.last_operation_key IS NOT NULL AND v_entry.last_operation_key = p_operation_key THEN
        RETURN to_jsonb(v_entry);
    END IF;

    -- 2. Check expected version
    IF v_entry.version <> p_expected_version THEN
        RAISE EXCEPTION 'CONFLICT: Planner entry version mismatch (expected %, actual %)', p_expected_version, v_entry.version USING ERRCODE = '40001';
    END IF;

    -- 3. Check date is not in the future in user's profile timezone
    SELECT timezone INTO v_tz FROM public.profiles WHERE id = v_uid;
    v_today := (timezone(COALESCE(v_tz, 'Asia/Ho_Chi_Minh'), timezone('utc', now())))::date;

    IF v_entry.scheduled_date > v_today THEN
        RAISE EXCEPTION 'INVALID_REQUEST: Cannot confirm wear for a future date (% > %)', v_entry.scheduled_date, v_today USING ERRCODE = '22023';
    END IF;

    -- 4. If already worn, return current state without inserting duplicate wear log
    IF v_entry.status = 'worn' THEN
        RETURN to_jsonb(v_entry);
    END IF;

    -- 5. Validate snapshot items belong to user and are available
    SELECT COUNT(*) INTO v_unavailable_count
    FROM jsonb_to_recordset(COALESCE(v_entry.outfit_snapshot->'items', '[]'::jsonb)) AS s(item_id uuid)
    LEFT JOIN public.wardrobe_items wi ON wi.id = s.item_id AND wi.owner_id = v_uid
    WHERE wi.id IS NULL
       OR wi.deleted_at IS NOT NULL
       OR wi.availability IN ('laundry', 'unavailable', 'archived');

    IF v_unavailable_count > 0 THEN
        RAISE EXCEPTION 'INVALID_REQUEST: One or more items in snapshot are unavailable, in laundry, archived, or deleted' USING ERRCODE = '22023';
    END IF;

    -- 6. Insert wear_logs and wear_log_items from snapshot
    INSERT INTO public.wear_logs (owner_id, planner_entry_id, worn_date)
    VALUES (v_uid, v_entry.id, v_entry.scheduled_date)
    ON CONFLICT (planner_entry_id) DO UPDATE SET worn_date = EXCLUDED.worn_date
    RETURNING * INTO v_wear_log;

    INSERT INTO public.wear_log_items (wear_log_id, owner_id, item_id, item_name_snapshot)
    SELECT
        v_wear_log.id,
        v_uid,
        s.item_id,
        COALESCE(s.name, 'Món đồ')
    FROM jsonb_to_recordset(COALESCE(v_entry.outfit_snapshot->'items', '[]'::jsonb)) AS s(item_id uuid, name text)
    ON CONFLICT (wear_log_id, item_id) DO NOTHING;

    UPDATE public.planner_entries
    SET status = 'worn',
        version = version + 1,
        last_operation_key = p_operation_key
    WHERE id = v_entry.id
    RETURNING * INTO v_entry;

    RETURN to_jsonb(v_entry);
END;
$$;

-- ============================================================================
-- RPC 8: rpc_unconfirm_wear
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_unconfirm_wear(
    p_entry_id uuid,
    p_operation_key text,
    p_expected_version integer
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_entry public.planner_entries%ROWTYPE;
BEGIN
    v_uid := public.require_active_owner();

    SELECT * INTO v_entry
    FROM public.planner_entries
    WHERE id = p_entry_id AND owner_id = v_uid
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'NOT_FOUND: Planner entry not found' USING ERRCODE = 'P0002';
    END IF;

    IF v_entry.last_operation_key IS NOT NULL AND v_entry.last_operation_key = p_operation_key THEN
        RETURN to_jsonb(v_entry);
    END IF;

    IF v_entry.version <> p_expected_version THEN
        RAISE EXCEPTION 'CONFLICT: Planner entry version mismatch (expected %, actual %)', p_expected_version, v_entry.version USING ERRCODE = '40001';
    END IF;

    DELETE FROM public.wear_logs
    WHERE planner_entry_id = v_entry.id AND owner_id = v_uid;

    UPDATE public.planner_entries
    SET status = 'planned',
        version = version + 1,
        last_operation_key = p_operation_key
    WHERE id = v_entry.id
    RETURNING * INTO v_entry;

    RETURN to_jsonb(v_entry);
END;
$$;

-- ============================================================================
-- RPC 9: rpc_mark_notifications_read_all
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_mark_notifications_read_all()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_cutoff timestamptz;
    v_updated_count integer;
BEGIN
    v_uid := public.require_active_owner();
    v_cutoff := timezone('utc', now());

    WITH updated AS (
        UPDATE public.notifications
        SET read_at = v_cutoff
        WHERE owner_id = v_uid
          AND read_at IS NULL
          AND created_at <= v_cutoff
        RETURNING id
    )
    SELECT COUNT(*) INTO v_updated_count FROM updated;

    RETURN jsonb_build_object(
        'updated_count', v_updated_count,
        'cutoff', v_cutoff
    );
END;
$$;

-- ============================================================================
-- RPC 10: rpc_mark_notification_read
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_mark_notification_read(p_notification_id uuid)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_notif public.notifications%ROWTYPE;
BEGIN
    v_uid := public.require_active_owner();

    SELECT * INTO v_notif
    FROM public.notifications
    WHERE id = p_notification_id AND owner_id = v_uid
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'NOT_FOUND: Notification not found' USING ERRCODE = 'P0002';
    END IF;

    IF v_notif.read_at IS NULL THEN
        UPDATE public.notifications
        SET read_at = timezone('utc', now())
        WHERE id = p_notification_id AND owner_id = v_uid
        RETURNING * INTO v_notif;
    END IF;

    RETURN to_jsonb(v_notif);
END;
$$;

-- ============================================================================
-- RPC 11: rpc_create_support_request
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_create_support_request(
    p_request_key text,
    p_reference_code text,
    p_category text,
    p_subject text,
    p_description text,
    p_diagnostics jsonb DEFAULT NULL,
    p_daily_limit integer DEFAULT 5
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_existing public.support_requests%ROWTYPE;
    v_today_count integer;
    v_created public.support_requests%ROWTYPE;
BEGIN
    v_uid := public.require_active_owner();

    PERFORM pg_advisory_xact_lock(hashtext('support:' || v_uid::text));

    SELECT * INTO v_existing
    FROM public.support_requests
    WHERE owner_id = v_uid AND request_key = p_request_key;

    IF FOUND THEN
        IF v_existing.category <> p_category
           OR v_existing.subject <> btrim(p_subject)
           OR v_existing.description <> btrim(p_description) THEN
            RAISE EXCEPTION 'CONFLICT: Support request_key reused with different payload' USING ERRCODE = '40001';
        END IF;
        RETURN jsonb_build_object('created', false, 'request', to_jsonb(v_existing));
    END IF;

    SELECT COUNT(*) INTO v_today_count
    FROM public.support_requests
    WHERE owner_id = v_uid
      AND created_at >= timezone('utc', now()) - interval '24 hours';

    IF v_today_count >= p_daily_limit THEN
        RAISE EXCEPTION 'QUOTA_EXCEEDED: Daily support request limit reached' USING ERRCODE = 'P0001';
    END IF;

    INSERT INTO public.support_requests (
        owner_id, reference_code, request_key, category, subject, description, diagnostics, status
    ) VALUES (
        v_uid, p_reference_code, p_request_key, p_category, btrim(p_subject), btrim(p_description), p_diagnostics, 'received'
    )
    RETURNING * INTO v_created;

    RETURN jsonb_build_object('created', true, 'request', to_jsonb(v_created));
END;
$$;

-- ============================================================================
-- RPC 12: rpc_create_data_export_request
-- ============================================================================
CREATE OR REPLACE FUNCTION public.rpc_create_data_export_request(
    p_request_key text
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_uid uuid;
    v_existing public.data_export_requests%ROWTYPE;
    v_active public.data_export_requests%ROWTYPE;
    v_recent_count integer;
    v_created public.data_export_requests%ROWTYPE;
BEGIN
    v_uid := public.require_active_owner();

    PERFORM pg_advisory_xact_lock(hashtext('data_export:' || v_uid::text));

    SELECT * INTO v_existing
    FROM public.data_export_requests
    WHERE owner_id = v_uid AND request_key = p_request_key;

    IF FOUND THEN
        RETURN jsonb_build_object('created', false, 'export_request', to_jsonb(v_existing));
    END IF;

    SELECT * INTO v_active
    FROM public.data_export_requests
    WHERE owner_id = v_uid AND status IN ('queued', 'running');

    IF FOUND THEN
        RAISE EXCEPTION 'CONFLICT: Another data export request is currently queued or running' USING ERRCODE = '40001';
    END IF;

    SELECT COUNT(*) INTO v_recent_count
    FROM public.data_export_requests
    WHERE owner_id = v_uid
      AND status IN ('ready', 'expired')
      AND created_at >= timezone('utc', now()) - interval '24 hours';

    IF v_recent_count >= 1 THEN
        RAISE EXCEPTION 'QUOTA_EXCEEDED: Only one new data export is allowed per 24 hours' USING ERRCODE = 'P0001';
    END IF;

    INSERT INTO public.data_export_requests (owner_id, request_key, status)
    VALUES (v_uid, p_request_key, 'queued')
    RETURNING * INTO v_created;

    RETURN jsonb_build_object('created', true, 'export_request', to_jsonb(v_created));
END;
$$;

-- Grant EXECUTE on user-facing RPCs only to authenticated role
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION
    public.rpc_bootstrap_account(text, text, text, text),
    public.rpc_update_profile(integer, text, text),
    public.rpc_set_onboarding_state(text),
    public.rpc_update_settings(integer, text, boolean, boolean, text),
    public.rpc_record_consent(text, text, text, text, integer),
    public.rpc_save_outfit(uuid, text, text, text[], text[], jsonb, integer),
    public.rpc_confirm_wear(uuid, text, integer),
    public.rpc_unconfirm_wear(uuid, text, integer),
    public.rpc_mark_notifications_read_all(),
    public.rpc_mark_notification_read(uuid),
    public.rpc_create_support_request(text, text, text, text, text, jsonb, integer),
    public.rpc_create_data_export_request(text)
TO authenticated;
