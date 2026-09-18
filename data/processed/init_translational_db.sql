-- =============================================================================
-- TRANSLATIONAL GENOMICS & ANATOMICAL INTELLIGENCE PLATFORM
-- Production MySQL 8.0 Normalized Relational DDL & Migration Script
-- Databases: Bgee, DisGeNET, DrugCentral, MONDO, UBERON
-- =============================================================================

CREATE DATABASE IF NOT EXISTS translational_bio
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE translational_bio;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. UBERON Anatomical Structure Ontology
DROP TABLE IF EXISTS uberon_ontology;
CREATE TABLE uberon_ontology (
    uberon_id VARCHAR(32) NOT NULL,
    anatomy_name VARCHAR(255) NOT NULL,
    definition TEXT,
    parent_ids TEXT,
    part_of TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (uberon_id),
    INDEX idx_uberon_name (anatomy_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. MONDO Unified Disease Ontology
DROP TABLE IF EXISTS mondo_ontology;
CREATE TABLE mondo_ontology (
    mondo_id VARCHAR(32) NOT NULL,
    disease_name VARCHAR(255) NOT NULL,
    definition TEXT,
    parent_ids TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (mondo_id),
    INDEX idx_mondo_name (disease_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. DrugCentral Chemical Structures
DROP TABLE IF EXISTS drugcentral_structures;
CREATE TABLE drugcentral_structures (
    struct_id INT UNSIGNED NOT NULL,
    inn_name VARCHAR(255) NOT NULL,
    smiles TEXT,
    inchi TEXT,
    inchikey VARCHAR(32),
    cas_rn VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (struct_id),
    INDEX idx_struct_inn (inn_name),
    INDEX idx_struct_inchikey (inchikey)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. DrugCentral Targets and Mechanisms
DROP TABLE IF EXISTS drugcentral_targets;
CREATE TABLE drugcentral_targets (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    drug_name VARCHAR(255) NOT NULL,
    struct_id INT UNSIGNED NOT NULL,
    target_name VARCHAR(255) NOT NULL,
    target_class VARCHAR(128),
    accession VARCHAR(64),
    gene_symbol VARCHAR(64),
    swissprot VARCHAR(64),
    act_value DECIMAL(12,4),
    act_unit VARCHAR(32),
    act_type VARCHAR(64),
    act_comment TEXT,
    act_source VARCHAR(64),
    relation VARCHAR(16),
    moa TINYINT(1) DEFAULT 0,
    moa_source VARCHAR(64),
    action_type VARCHAR(64),
    tdl VARCHAR(32),
    organism VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_drug_name (drug_name),
    INDEX idx_drug_gene (gene_symbol),
    INDEX idx_drug_struct_id (struct_id),
    INDEX idx_drug_action (action_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. DisGeNET Gene-Disease & Variant Associations
DROP TABLE IF EXISTS disgenet_associations;
CREATE TABLE disgenet_associations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    gene_symbol VARCHAR(64) NOT NULL,
    gene_id VARCHAR(64) NOT NULL,
    disease_id VARCHAR(255) NOT NULL,
    disease_name VARCHAR(255) NOT NULL,
    association_score DECIMAL(6,4) NOT NULL,
    variant_score DECIMAL(6,4) NOT NULL,
    evidence_count INT UNSIGNED NOT NULL,
    evidence_level VARCHAR(32) NOT NULL,
    disease_category VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_disgenet_gene (gene_symbol),
    INDEX idx_disgenet_disease (disease_name),
    INDEX idx_disgenet_score (association_score DESC),
    INDEX idx_disgenet_category (disease_category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Bgee Anatomical Gene Expression
DROP TABLE IF EXISTS bgee_expression;
CREATE TABLE bgee_expression (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    gene_id VARCHAR(64) NOT NULL,
    gene_name VARCHAR(64) NOT NULL,
    anatomy_id VARCHAR(32) NOT NULL,
    anatomy_name VARCHAR(255) NOT NULL,
    expression_call VARCHAR(32) NOT NULL,
    call_quality VARCHAR(32) NOT NULL,
    fdr DOUBLE,
    expression_score DECIMAL(8,4) NOT NULL,
    expression_rank DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_bgee_gene (gene_name),
    INDEX idx_bgee_anatomy (anatomy_name),
    INDEX idx_bgee_anat_id (anatomy_id),
    INDEX idx_bgee_gene_anat (gene_name, anatomy_name),
    INDEX idx_bgee_score (expression_score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
