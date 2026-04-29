# Diagramme d'Architecture - Livrable Final

Ce document présente l'architecture finale déployée pour la MarketPlace Locale Intelligente, livrable obligatoire pour la soutenance. Il modélise les interactions entre les différents services (Backend, Frontend, Base de données), l'infrastructure SRE/Monitoring, et le pipeline Data.

## 1. Diagramme d'Architecture Global

```mermaid
flowchart TD
    %% Définition des utilisateurs
    Client([Client / Acheteur])
    Producteur([Producteur Local])
    EquipeData([Equipe Data / Power BI])
    EquipeSRE([Equipe SRE / DevOps])

    %% Zone Cloud / Déploiement
    subgraph Infrastructure Cloud [Infastructure Cloud AWS / EKS]
        direction TB

        %% Frontend
        subgraph FrontTier [Frontend Tier]
            Nginx[Nginx Web Server\n(Port 80/3000)]
            ReactApp[Application React.js\nVite + TailwindCSS]
            Nginx --- ReactApp
        end

        %% Backend
        subgraph BackTier [Backend Tier]
            FastAPI[FastAPI Server\nPython/Uvicorn (Port 8000)]
        end

        %% Base de données
        subgraph DataTier [Database Tier]
            DB_Master[(PostgreSQL Master\nmarketplace_db)]
            DB_Replica[(PostgreSQL Read-Replica)]
            DB_Master -. Replication .-> DB_Replica
        end

        %% Monitoring SRE
        subgraph MonitorTier [Monitoring & Observabilité]
            Prometheus[Prometheus\n(Scraping Metrics)]
            Grafana[Grafana Dashboards\n(SLO, Error Budget)]
            Prometheus --> Grafana
        end

        %% Interaction services internes
        ReactApp -- Requêtes REST / JSON --> FastAPI
        FastAPI -- Read / Write --> DB_Master
        Prometheus -- Métriques système --> Nginx
        Prometheus -- Exposition /metrics --> FastAPI
        Prometheus -- Exporter --> DB_Master
    end

    %% Zone Data Pipeline
    subgraph DataPipeline [Pipeline Analytique / ML]
        PythonETL[Scripts ETL\nClustering & Anomalies]
        PythonETL -- Extraction requêtes lourdes --> DB_Replica
        PythonETL -- Réinjection KPIs --> DB_Master
    end

    %% Liens externes
    Client -- HTTP/HTTPS --> Nginx
    Producteur -- HTTP/HTTPS --> Nginx
    EquipeData -- Requêtes DirectQuery --> DB_Replica
    EquipeData -- Exploitation --> PythonETL
    EquipeSRE -- Supervision --> Grafana

    %% Styles
    classDef client fill:#f9f,stroke:#333,stroke-width:2px;
    classDef frontend fill:#bbf,stroke:#333,stroke-width:2px;
    classDef backend fill:#bfb,stroke:#333,stroke-width:2px;
    classDef database fill:#fcf,stroke:#333,stroke-width:2px;
    classDef monitoring fill:#ffb,stroke:#333,stroke-width:2px;
    classDef data fill:#eee,stroke:#333,stroke-width:2px;

    class Client,Producteur,EquipeData,EquipeSRE client;
    class ReactApp,Nginx frontend;
    class FastAPI backend;
    class DB_Master,DB_Replica database;
    class Prometheus,Grafana monitoring;
    class PythonETL,DataPipeline data;
```

## 2. Description des Composants de l'Architecture

Conformément à nos objectifs de Sprint 4 et de fiabilisation :

1. **Frontend (React.js + Nginx) :** L'application utilisateur est buildée à l'aide de Vite. L'artefact statique est servi par un conteneur Nginx léger et performant, qui expose l'interface sur le port 3000 (en dev) ou 80/443 (en production).
2. **Backend (FastAPI) :** Le service Backend gère la logique métier (gestion des catalogues, validation de commandes, simulation de paiement). FastAPI garantit de solides performances asynchrones tout en générant nativement l'OpenAPI nécessaire au front.
3. **Database (PostgreSQL) :** 
   - L'instance primaire (Master) gère toutes les opérations transactionnelles pour éviter l'incohérence des stocks et des commandes. 
   - Un système de *Read-Replica* est provisionné dans le flux logique de production pour décharger la base principale des requêtes analytiques massives, sécurisant ainsi l'Error Budget SRE de l'application métier.
4. **Pipeline Data & ML :** Les scripts (ETL et Clustering) extraient les données brutes via le Replica, calculent la segmentation clients/producteurs et réinjectent éventuellement des données de catégorisation. Les outils BI (PowerBI) consomment le domaine de données en mode Read-Only.
5. **Monitoring (Prometheus & Grafana) :** Ils assurent l'observabilité. Prometheus récupère (scrap) les métriques du cluster pour alimenter les dashboards Grafana sur lesquels s'appuie le rôle DevOps/SRE pour surveiller le SLA et l'Error Budget.

Cette stack respecte rigoureusement les contraintes du sujet pour le livrable final : **Architecture logicielle distribuée (Front/Back), conteneurisation Docker, SRE et flux opérationnel de données.**