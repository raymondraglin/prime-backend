"""PRIME data spine - full 13-table architecture

Revision ID: 001_prime_data_spine
Revises: 
Create Date: 2026-02-26
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_prime_data_spine'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    # ─────────────────────────────────────────────
    # 1. TAXONOMY SPINE
    # ─────────────────────────────────────────────

    op.create_table('domains',
        sa.Column('id',          sa.Integer(),  primary_key=True),
        sa.Column('code',        sa.Text(),     nullable=False, unique=True),
        sa.Column('name',        sa.Text(),     nullable=False),
        sa.Column('description', sa.Text(),     nullable=True),
        sa.Column('sort_order',  sa.Integer(),  nullable=True),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )

    op.create_table('subjects',
        sa.Column('id',            sa.Integer(), primary_key=True),
        sa.Column('domain_id',     sa.Integer(),
                  sa.ForeignKey('domains.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code',          sa.Text(),    nullable=False),
        sa.Column('name',          sa.Text(),    nullable=False),
        sa.Column('level_tag',     sa.Text(),    nullable=False),
        # SCHOOL_BASIC | SCHOOL_SEC | UG_CORE | GRAD_CORE | PHD_CORE | INNOVATOR
        sa.Column('description',   sa.Text(),    nullable=True),
        sa.Column('language_code', sa.Text(),    nullable=True),
        # ISO 639 for natural langs; lang slug for prog langs
        sa.Column('sort_order',    sa.Integer(), nullable=True),
        sa.Column('created_at',    sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('domain_id', 'code', name='uq_subjects_domain_code'),
    )

    op.create_table('subfields',
        sa.Column('id',          sa.Integer(), primary_key=True),
        sa.Column('subject_id',  sa.Integer(),
                  sa.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code',        sa.Text(),    nullable=False),
        sa.Column('name',        sa.Text(),    nullable=False),
        sa.Column('description', sa.Text(),    nullable=True),
        sa.Column('sort_order',  sa.Integer(), nullable=True),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('subject_id', 'code', name='uq_subfields_subject_code'),
    )

    # ─────────────────────────────────────────────
    # 2. FOUNDATIONS (cliff notes — fastest layer)
    # ─────────────────────────────────────────────

    op.create_table('foundations',
        sa.Column('id',             sa.Integer(), primary_key=True),
        sa.Column('domain_id',      sa.Integer(),
                  sa.ForeignKey('domains.id',   ondelete='CASCADE'), nullable=False),
        sa.Column('subject_id',     sa.Integer(),
                  sa.ForeignKey('subjects.id',  ondelete='CASCADE'), nullable=False),
        sa.Column('subfield_id',    sa.Integer(),
                  sa.ForeignKey('subfields.id', ondelete='SET NULL'), nullable=True),
        sa.Column('level_tag',      sa.Text(),    nullable=False),
        sa.Column('summary',        sa.Text(),    nullable=False),
        # 2-5 paragraphs: what this subfield IS
        sa.Column('key_concepts',   postgresql.JSONB(), server_default='[]', nullable=False),
        # ["σ-algebra","measure","outer measure",...]
        sa.Column('synonyms',       postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('common_notation',postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('examples',       postgresql.JSONB(), server_default='[]', nullable=False),
        # 5-7 canonical examples
        sa.Column('counterexamples',postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('historical_notes',sa.Text(),   nullable=True),
        sa.Column('canonical_refs', postgresql.JSONB(), server_default='[]', nullable=False),
        # [corpus_document_id, ...]
        sa.Column('related_concept_ids', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('innovator_gaps', sa.Text(),    nullable=True),
        # what is STILL unsolved / contested in this subfield
        sa.Column('notes',          sa.Text(),    nullable=True),
        sa.Column('last_updated_at',sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint(
            'domain_id','subject_id','subfield_id','level_tag',
            name='uq_foundations_slot'
        ),
    )

    # ─────────────────────────────────────────────
    # 3. CATHEDRAL LIBRARY
    # ─────────────────────────────────────────────

    op.create_table('corpus_documents',
        sa.Column('id',              sa.Integer(), primary_key=True),
        sa.Column('domain_id',       sa.Integer(),
                  sa.ForeignKey('domains.id',   ondelete='CASCADE'), nullable=False),
        sa.Column('subject_id',      sa.Integer(),
                  sa.ForeignKey('subjects.id',  ondelete='SET NULL'), nullable=True),
        sa.Column('subfield_id',     sa.Integer(),
                  sa.ForeignKey('subfields.id', ondelete='SET NULL'), nullable=True),
        sa.Column('level_tag',       sa.Text(),    nullable=True),
        sa.Column('kind',            sa.Text(),    nullable=False),
        # textbook | paper | guideline | failure_case_source |
        # report | prime_book | prime_article | prime_guide |
        # prime_case_study | prime_innovation | language_reference
        sa.Column('title',           sa.Text(),    nullable=False),
        sa.Column('source',          sa.Text(),    nullable=True),
        sa.Column('author',          sa.Text(),    nullable=True),
        sa.Column('year',            sa.Integer(), nullable=True),
        sa.Column('source_language', sa.Text(),    nullable=True),
        # ISO 639 code — 'la','he','arc','grc','en', etc.
        sa.Column('path',            sa.Text(),    nullable=False),
        sa.Column('content_hash',    sa.Text(),    nullable=True),
        # sha256 of file — detect changes
        sa.Column('extra_metadata',  postgresql.JSONB(), server_default='{}', nullable=False),
        sa.Column('ingested_at',     sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active',       sa.Boolean(), server_default='true', nullable=False),
    )

    op.create_table('corpus_chunks',
        sa.Column('id',           sa.Integer(), primary_key=True),
        sa.Column('document_id',  sa.Integer(),
                  sa.ForeignKey('corpus_documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_index',  sa.Integer(), nullable=False),
        sa.Column('text',         sa.Text(),    nullable=False),
        sa.Column('token_count',  sa.Integer(), nullable=True),
        sa.Column('embedding',    sa.LargeBinary(), nullable=True),
        # swap to VECTOR(1536) when pgvector is enabled
        sa.Column('chunk_metadata', postgresql.JSONB(), server_default='{}', nullable=False),
        sa.UniqueConstraint('document_id','chunk_index', name='uq_chunks_doc_idx'),
    )

    # ─────────────────────────────────────────────
    # 4. PRIME NOTEBOOK (medium layer)
    # ─────────────────────────────────────────────

    op.create_table('prime_notebook_entries',
        sa.Column('id',                  sa.Integer(), primary_key=True),
        sa.Column('prime_id',            sa.Integer(), nullable=False, server_default='1'),
        sa.Column('domain_id',           sa.Integer(),
                  sa.ForeignKey('domains.id',   ondelete='SET NULL'), nullable=True),
        sa.Column('subject_id',          sa.Integer(),
                  sa.ForeignKey('subjects.id',  ondelete='SET NULL'), nullable=True),
        sa.Column('subfield_id',         sa.Integer(),
                  sa.ForeignKey('subfields.id', ondelete='SET NULL'), nullable=True),
        sa.Column('kind',                sa.Text(),    nullable=False),
        # domain_overview | book_notes | concept_map |
        # failure_pattern | reflection | language_notes | innovation_seed
        sa.Column('title',               sa.Text(),    nullable=False),
        sa.Column('body',                sa.Text(),    nullable=False),
        sa.Column('source_document_ids', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('created_at',          sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at',          sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('version',             sa.Integer(), server_default='1', nullable=False),
    )

    # ─────────────────────────────────────────────
    # 5. STUDY JOBS (PRIME reads the library)
    # ─────────────────────────────────────────────

    op.create_table('study_jobs',
        sa.Column('id',          sa.Integer(), primary_key=True),
        sa.Column('document_id', sa.Integer(),
                  sa.ForeignKey('corpus_documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status',      sa.Text(),    nullable=False, server_default='pending'),
        # pending | running | done | error
        sa.Column('priority',    sa.Integer(), server_default='5', nullable=False),
        # 1 (highest) – 10 (lowest)
        sa.Column('last_error',  sa.Text(),    nullable=True),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at',  sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )

    # ─────────────────────────────────────────────
    # 6. FAILURE CASES (innovator fuel)
    # ─────────────────────────────────────────────

    op.create_table('failure_cases',
        sa.Column('id',              sa.Integer(), primary_key=True),
        sa.Column('domain_id',       sa.Integer(),
                  sa.ForeignKey('domains.id', ondelete='SET NULL'), nullable=True),
        sa.Column('subject_id',      sa.Integer(),
                  sa.ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title',           sa.Text(),    nullable=False),
        sa.Column('summary',         sa.Text(),    nullable=False),
        sa.Column('what_failed',     sa.Text(),    nullable=False),
        sa.Column('root_causes',     postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('failed_controls', postgresql.JSONB(), server_default='[]', nullable=False),
        # governance, engineering, social, financial controls that broke
        sa.Column('lessons',         postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('what_should_exist', sa.Text(),  nullable=True),
        # PRIME's innovator take: what the world needs because of this failure
        sa.Column('source_document_ids', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('year',            sa.Integer(), nullable=True),
        sa.Column('location',        sa.Text(),    nullable=True),
        sa.Column('created_at',      sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )

    # ─────────────────────────────────────────────
    # 7. PRIME ARTIFACTS (what PRIME produces)
    # ─────────────────────────────────────────────

    op.create_table('prime_artifacts',
        sa.Column('id',           sa.Integer(), primary_key=True),
        sa.Column('prime_id',     sa.Integer(), nullable=False, server_default='1'),
        sa.Column('domain_id',    sa.Integer(),
                  sa.ForeignKey('domains.id', ondelete='SET NULL'), nullable=True),
        sa.Column('subject_id',   sa.Integer(),
                  sa.ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('kind',         sa.Text(),    nullable=False),
        # book | article | case_study | guide | innovation_proposal
        sa.Column('title',        sa.Text(),    nullable=False),
        sa.Column('abstract',     sa.Text(),    nullable=True),
        sa.Column('body',         sa.Text(),    nullable=False),
        # full text of the artifact
        sa.Column('outline',      postgresql.JSONB(), server_default='[]', nullable=False),
        # chapter/section structure
        sa.Column('source_document_ids', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('failure_case_ids',    postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('status',       sa.Text(),    server_default='draft', nullable=False),
        # draft | in_progress | complete | published_to_corpus
        sa.Column('version',      sa.Integer(), server_default='1',  nullable=False),
        sa.Column('created_at',   sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at',   sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )

    # ─────────────────────────────────────────────
    # 8. PRIME MEMORIES (episodic + procedural)
    # ─────────────────────────────────────────────

    op.create_table('prime_memories',
        sa.Column('id',          sa.Integer(), primary_key=True),
        sa.Column('kind',        sa.Text(),    nullable=False),
        # raymond_preference | decision | open_question | project_update
        # prime_learned | raymond_said | procedural | relationship_note
        sa.Column('subject',     sa.Text(),    nullable=False),
        sa.Column('body',        sa.Text(),    nullable=False),
        sa.Column('importance',  sa.Integer(), server_default='5', nullable=False),
        # 1-10, PRIME scores this himself. 10 = never forget
        sa.Column('domain_id',   sa.Integer(),
                  sa.ForeignKey('domains.id', ondelete='SET NULL'), nullable=True),
        sa.Column('source_conversation_ids', postgresql.JSONB(),
                  server_default='[]', nullable=False),
        sa.Column('tags',        postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('last_recalled', sa.TIMESTAMP(timezone=True), nullable=True),
    )

    # ─────────────────────────────────────────────
    # 9. PRIME CONVERSATIONS (the permanent log)
    # ─────────────────────────────────────────────

    op.create_table('prime_conversations',
        sa.Column('id',         sa.Integer(),  primary_key=True),
        sa.Column('session_id', sa.Text(),     nullable=True),
        # optional soft grouping — never resets the thread
        sa.Column('speaker',    sa.Text(),     nullable=False),
        # 'raymond' | 'prime'
        sa.Column('message',    sa.Text(),     nullable=False),
        sa.Column('conv_metadata', postgresql.JSONB(), server_default='{}', nullable=False),
        # topic_tags, domain_ids, project_refs, memory_ids extracted
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )

    # ─────────────────────────────────────────────
    # 10. PRIME PROJECTS (active builds)
    # ─────────────────────────────────────────────

    op.create_table('prime_projects',
        sa.Column('id',          sa.Integer(), primary_key=True),
        sa.Column('name',        sa.Text(),    nullable=False),
        sa.Column('description', sa.Text(),    nullable=True),
        sa.Column('status',      sa.Text(),    server_default='active', nullable=False),
        # active | paused | complete | archived
        sa.Column('domain_ids',  postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('goals',       postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('decisions',   postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('open_questions', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('artifact_ids',   postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('notes',       sa.Text(),    nullable=True),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at',  sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )

    # ─────────────────────────────────────────────
    # INDEXES — performance at scale
    # ─────────────────────────────────────────────

    # Taxonomy lookups
    op.create_index('ix_subjects_domain_id',   'subjects',  ['domain_id'])
    op.create_index('ix_subfields_subject_id', 'subfields', ['subject_id'])

    # Foundations retrieval
    op.create_index('ix_foundations_domain_subject',
                    'foundations', ['domain_id', 'subject_id'])
    op.create_index('ix_foundations_level_tag',
                    'foundations', ['level_tag'])

    # Corpus retrieval
    op.create_index('ix_corpus_docs_domain_subject',
                    'corpus_documents', ['domain_id', 'subject_id'])
    op.create_index('ix_corpus_docs_kind',
                    'corpus_documents', ['kind'])
    op.create_index('ix_corpus_docs_hash',
                    'corpus_documents', ['content_hash'])
    op.create_index('ix_corpus_chunks_doc_id',
                    'corpus_chunks', ['document_id'])

    # Notebook retrieval
    op.create_index('ix_notebook_domain_subject',
                    'prime_notebook_entries', ['domain_id', 'subject_id'])
    op.create_index('ix_notebook_kind',
                    'prime_notebook_entries', ['kind'])

    # Study jobs queue
    op.create_index('ix_study_jobs_status_priority',
                    'study_jobs', ['status', 'priority'])

    # Failure cases
    op.create_index('ix_failure_cases_domain',
                    'failure_cases', ['domain_id'])

    # Artifacts
    op.create_index('ix_prime_artifacts_kind_status',
                    'prime_artifacts', ['kind', 'status'])

    # Memory recall
    op.create_index('ix_prime_memories_kind',
                    'prime_memories', ['kind'])
    op.create_index('ix_prime_memories_importance',
                    'prime_memories', ['importance'])

    # Conversation log — time-ordered lookup
    op.create_index('ix_prime_conversations_created_at',
                    'prime_conversations', ['created_at'])
    op.create_index('ix_prime_conversations_session',
                    'prime_conversations', ['session_id'])

    # Projects
    op.create_index('ix_prime_projects_status',
                    'prime_projects', ['status'])


def downgrade():
    # Drop indexes first
    indexes = [
        ('ix_prime_projects_status',           'prime_projects'),
        ('ix_prime_conversations_session',      'prime_conversations'),
        ('ix_prime_conversations_created_at',   'prime_conversations'),
        ('ix_prime_memories_importance',        'prime_memories'),
        ('ix_prime_memories_kind',              'prime_memories'),
        ('ix_prime_artifacts_kind_status',      'prime_artifacts'),
        ('ix_failure_cases_domain',             'failure_cases'),
        ('ix_study_jobs_status_priority',       'study_jobs'),
        ('ix_notebook_kind',                    'prime_notebook_entries'),
        ('ix_notebook_domain_subject',          'prime_notebook_entries'),
        ('ix_corpus_chunks_doc_id',             'corpus_chunks'),
        ('ix_corpus_docs_hash',                 'corpus_documents'),
        ('ix_corpus_docs_kind',                 'corpus_documents'),
        ('ix_corpus_docs_domain_subject',       'corpus_documents'),
        ('ix_foundations_level_tag',            'foundations'),
        ('ix_foundations_domain_subject',       'foundations'),
        ('ix_subfields_subject_id',             'subfields'),
        ('ix_subjects_domain_id',               'subjects'),
    ]
    for idx_name, table_name in indexes:
        op.drop_index(idx_name, table_name=table_name)

    # Drop tables in reverse FK order
    tables = [
        'prime_projects',
        'prime_conversations',
        'prime_memories',
        'prime_artifacts',
        'failure_cases',
        'study_jobs',
        'prime_notebook_entries',
        'corpus_chunks',
        'corpus_documents',
        'foundations',
        'subfields',
        'subjects',
        'domains',
    ]
    for t in tables:
        op.drop_table(t)
