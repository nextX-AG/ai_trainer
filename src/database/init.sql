-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Projects Tabelle (existiert bereits)
create table if not exists projects (
    id uuid default uuid_generate_v4() primary key,
    name text not null,
    description text,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    updated_at timestamp with time zone default timezone('utc'::text, now()),
    owner text not null,
    status text default 'active'
);

-- Scenes Tabelle
create table if not exists scenes (
    id uuid default uuid_generate_v4() primary key,
    project_id uuid references projects(id) on delete cascade,
    name text not null,
    description text,
    keywords jsonb default '[]'::jsonb,
    target_attributes jsonb default '{}'::jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Downloads Tabelle
create table if not exists downloads (
    id uuid default uuid_generate_v4() primary key,
    project_id uuid references projects(id) on delete cascade,
    url text not null,
    status text default 'pending',
    progress float default 0.0,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    metadata jsonb default '{}'::jsonb
);

-- Indices für bessere Performance
create index if not exists scenes_project_id_idx on scenes(project_id);
create index if not exists downloads_project_id_idx on downloads(project_id);
create index if not exists projects_owner_idx on projects(owner); 