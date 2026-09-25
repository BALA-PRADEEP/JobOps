SUPPORTED_DRY_RUN_ATS = frozenset({"greenhouse"})
RECOGNIZED_ATS = frozenset({"greenhouse", "lever", "ashby", "workday", "linkedin", "generic"})

TARGET_TITLES = (
    "product engineer",
    "full stack engineer",
    "full-stack engineer",
    "software engineer",
    "backend engineer",
    "integration engineer",
    "platform integrations",
    "applied ai",
    "ai application",
    "ai product",
    "ai engineer",
    "founding engineer",
    "data engineer",
)

SKILL_ALIASES = {
    "Python": ["python"],
    "FastAPI": ["fastapi"],
    "REST APIs": ["rest api", "restful", "api design"],
    "SQLAlchemy": ["sqlalchemy"],
    "React": ["react", "react.js", "reactjs"],
    "TypeScript": ["typescript"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MongoDB": ["mongodb", "mongo"],
    "OAuth 2.0": ["oauth", "oauth2", "oidc"],
    "webhooks": ["webhook"],
    "multi-tenant SaaS": ["multi-tenant", "multitenant", "multi tenant"],
    "reconciliation": ["reconciliation", "reconcile"],
    "RAG": ["rag", "retrieval-augmented", "retrieval augmented"],
    "embeddings": ["embedding"],
    "vector search": ["vector search", "vector database", "pgvector", "pinecone", "weaviate"],
    "Azure": ["azure"],
    "Playwright": ["playwright"],
}

GAP_KEYWORDS = {
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "GCP": ["gcp", "google cloud"],
    "Go": ["golang", " go "],
    "Java": ["java"],
    "LangGraph": ["langgraph"],
    "Kafka": ["kafka"],
    "Terraform": ["terraform"],
}

PROTECTED_FIELD_HINTS = {
    "salary": ["salary", "compensation", "ctc"],
    "notice_period": ["notice period", "available to start", "start date"],
    "sponsorship": ["sponsorship", "visa sponsorship", "require sponsorship"],
    "work_authorization": ["authorized to work", "work authorization"],
    "relocation": ["relocate", "relocation"],
    "demographic": ["gender", "race", "ethnicity", "veteran", "disability"],
    "background": ["criminal", "conviction", "background check"],
}
