-- Closet Loop — Migration 0001: Core Schema (Profiles, Media, Wardrobe, Outfits, Planner, Wear Logs, Image Jobs)

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Helper trigger function for updated_at
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = timezone('utc', now());
    RETURN NEW;
END;
$$;

-- 1. profiles
CREATE TABLE IF NOT EXISTS public.profiles (
    id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE RESTRICT,
    display_name text NOT NULL DEFAULT 'Bạn'
        CONSTRAINT profiles_display_name_len CHECK (char_length(btrim(display_name)) BETWEEN 1 AND 50),
    timezone text NOT NULL DEFAULT 'Asia/Ho_Chi_Minh'
        CONSTRAINT profiles_timezone_nonempty CHECK (char_length(btrim(timezone)) BETWEEN 1 AND 100),
    onboarding_completed_at timestamptz NULL,
    onboarding_skipped_at timestamptz NULL,
    version integer NOT NULL DEFAULT 1
        CONSTRAINT profiles_version_positive CHECK (version >= 1),
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT profiles_onboarding_mutually_exclusive CHECK (
        NOT (onboarding_completed_at IS NOT NULL AND onboarding_skipped_at IS NOT NULL)
    )
);

CREATE TRIGGER trg_profiles_updated_at
BEFORE UPDATE ON public.profiles
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 2. media_assets
CREATE TABLE IF NOT EXISTS public.media_assets (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    staging_path text NULL,
    upload_expires_at timestamptz NULL,
    original_path text NULL,
    cutout_path text NULL,
    variant_metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    status text NOT NULL DEFAULT 'upload_pending'
        CONSTRAINT media_assets_status_check CHECK (status IN ('upload_pending', 'ready', 'rejected')),
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (id, owner_id)
);

CREATE INDEX IF NOT EXISTS idx_media_assets_owner_status ON public.media_assets(owner_id, status);
CREATE INDEX IF NOT EXISTS idx_media_assets_upload_expires ON public.media_assets(upload_expires_at) WHERE status = 'upload_pending';

CREATE TRIGGER trg_media_assets_updated_at
BEFORE UPDATE ON public.media_assets
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 3. wardrobe_items
CREATE TABLE IF NOT EXISTS public.wardrobe_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    name text NOT NULL
        CONSTRAINT wardrobe_items_name_len CHECK (char_length(btrim(name)) BETWEEN 1 AND 100),
    category text NOT NULL
        CONSTRAINT wardrobe_items_category_check CHECK (
            category IN ('top', 'bottom', 'dress', 'skirt', 'outerwear', 'shoes', 'bag', 'accessory', 'other')
        ),
    colors text[] NOT NULL DEFAULT '{}'::text[],
    size text NULL
        CONSTRAINT wardrobe_items_size_len CHECK (size IS NULL OR char_length(size) <= 50),
    brand text NULL
        CONSTRAINT wardrobe_items_brand_len CHECK (brand IS NULL OR char_length(brand) <= 100),
    purchase_price_vnd bigint NULL
        CONSTRAINT wardrobe_items_price_non_negative CHECK (purchase_price_vnd IS NULL OR purchase_price_vnd >= 0),
    purchase_date date NULL,
    notes text NULL
        CONSTRAINT wardrobe_items_notes_len CHECK (notes IS NULL OR char_length(notes) <= 1000),
    source text NOT NULL DEFAULT 'photo'
        CONSTRAINT wardrobe_items_source_check CHECK (source IN ('photo', 'placeholder')),
    asset_id uuid NULL,
    image_variant text NULL
        CONSTRAINT wardrobe_items_variant_check CHECK (image_variant IS NULL OR image_variant IN ('original', 'cutout')),
    availability text NOT NULL DEFAULT 'available'
        CONSTRAINT wardrobe_items_availability_check CHECK (
            availability IN ('available', 'laundry', 'unavailable', 'archived')
        ),
    deleted_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (id, owner_id),
    CONSTRAINT wardrobe_items_source_asset_check CHECK (
        (source = 'placeholder') OR (source = 'photo' AND asset_id IS NOT NULL AND image_variant IS NOT NULL)
    ),
    CONSTRAINT wardrobe_items_asset_owner_fk FOREIGN KEY (asset_id, owner_id)
        REFERENCES public.media_assets(id, owner_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_wardrobe_items_owner_category ON public.wardrobe_items(owner_id, category) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_wardrobe_items_owner_updated ON public.wardrobe_items(owner_id, updated_at DESC);

CREATE TRIGGER trg_wardrobe_items_updated_at
BEFORE UPDATE ON public.wardrobe_items
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 4. outfits
CREATE TABLE IF NOT EXISTS public.outfits (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    name text NOT NULL
        CONSTRAINT outfits_name_len CHECK (char_length(btrim(name)) BETWEEN 1 AND 100),
    notes text NULL
        CONSTRAINT outfits_notes_len CHECK (notes IS NULL OR char_length(notes) <= 1000),
    style_tags text[] NOT NULL DEFAULT '{}'::text[],
    occasion_tags text[] NOT NULL DEFAULT '{}'::text[],
    version integer NOT NULL DEFAULT 1
        CONSTRAINT outfits_version_positive CHECK (version >= 1),
    deleted_at timestamptz NULL,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (id, owner_id)
);

CREATE INDEX IF NOT EXISTS idx_outfits_owner_updated ON public.outfits(owner_id, updated_at DESC);

CREATE TRIGGER trg_outfits_updated_at
BEFORE UPDATE ON public.outfits
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 5. outfit_items
CREATE TABLE IF NOT EXISTS public.outfit_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    outfit_id uuid NOT NULL,
    item_id uuid NOT NULL,
    owner_id uuid NOT NULL,
    x double precision NOT NULL,
    y double precision NOT NULL,
    w double precision NOT NULL,
    h double precision NOT NULL,
    z_index integer NOT NULL DEFAULT 0,
    UNIQUE (outfit_id, item_id),
    CONSTRAINT outfit_items_geometry_check CHECK (
        w > 0 AND h > 0 AND x >= 0 AND y >= 0 AND (x + w) <= 1.000001 AND (y + h) <= 1.000001 AND z_index >= 0
    ),
    CONSTRAINT outfit_items_outfit_owner_fk FOREIGN KEY (outfit_id, owner_id)
        REFERENCES public.outfits(id, owner_id) ON DELETE CASCADE,
    CONSTRAINT outfit_items_item_owner_fk FOREIGN KEY (item_id, owner_id)
        REFERENCES public.wardrobe_items(id, owner_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_outfit_items_outfit ON public.outfit_items(outfit_id);
CREATE INDEX IF NOT EXISTS idx_outfit_items_item ON public.outfit_items(item_id);

-- 6. planner_entries
CREATE TABLE IF NOT EXISTS public.planner_entries (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    outfit_id uuid NULL,
    scheduled_date date NOT NULL,
    event_label text NULL
        CONSTRAINT planner_entries_event_label_len CHECK (event_label IS NULL OR char_length(btrim(event_label)) <= 100),
    status text NOT NULL DEFAULT 'planned'
        CONSTRAINT planner_entries_status_check CHECK (status IN ('planned', 'worn', 'skipped')),
    outfit_snapshot jsonb NOT NULL,
    version integer NOT NULL DEFAULT 1
        CONSTRAINT planner_entries_version_positive CHECK (version >= 1),
    last_operation_key text NULL,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (id, owner_id),
    CONSTRAINT planner_entries_outfit_owner_fk FOREIGN KEY (outfit_id, owner_id)
        REFERENCES public.outfits(id, owner_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_planner_entries_owner_date ON public.planner_entries(owner_id, scheduled_date);

CREATE TRIGGER trg_planner_entries_updated_at
BEFORE UPDATE ON public.planner_entries
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- 7. wear_logs
CREATE TABLE IF NOT EXISTS public.wear_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    planner_entry_id uuid NOT NULL UNIQUE,
    worn_date date NOT NULL,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (id, owner_id),
    CONSTRAINT wear_logs_entry_owner_fk FOREIGN KEY (planner_entry_id, owner_id)
        REFERENCES public.planner_entries(id, owner_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_wear_logs_owner_date ON public.wear_logs(owner_id, worn_date);

-- 8. wear_log_items
CREATE TABLE IF NOT EXISTS public.wear_log_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    wear_log_id uuid NOT NULL,
    owner_id uuid NOT NULL,
    item_id uuid NOT NULL,
    item_name_snapshot text NOT NULL,
    UNIQUE (wear_log_id, item_id),
    CONSTRAINT wear_log_items_log_owner_fk FOREIGN KEY (wear_log_id, owner_id)
        REFERENCES public.wear_logs(id, owner_id) ON DELETE CASCADE,
    CONSTRAINT wear_log_items_item_owner_fk FOREIGN KEY (item_id, owner_id)
        REFERENCES public.wardrobe_items(id, owner_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_wear_log_items_item_log ON public.wear_log_items(item_id, wear_log_id);
CREATE INDEX IF NOT EXISTS idx_wear_log_items_owner ON public.wear_log_items(owner_id);

-- 9. image_jobs
CREATE TABLE IF NOT EXISTS public.image_jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
    asset_id uuid NOT NULL,
    request_key text NOT NULL,
    status text NOT NULL DEFAULT 'processing'
        CONSTRAINT image_jobs_status_check CHECK (status IN ('processing', 'succeeded', 'failed')),
    error_code text NULL,
    started_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    finished_at timestamptz NULL,
    UNIQUE (owner_id, request_key),
    CONSTRAINT image_jobs_asset_owner_fk FOREIGN KEY (asset_id, owner_id)
        REFERENCES public.media_assets(id, owner_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_image_jobs_owner_started ON public.image_jobs(owner_id, started_at DESC);

