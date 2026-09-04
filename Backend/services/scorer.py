import re
from typing import Set, List, Dict, Optional, Any

# Predefined Technical & Professional Skill Taxonomy and Aliases
SKILL_ALIASES = {
    # Frontend
    "js": "javascript",
    "javascript": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "react": "react",
    "reactjs": "react",
    "react.js": "react",
    "react native": "react native",
    "next": "next.js",
    "nextjs": "next.js",
    "next.js": "next.js",
    "vue": "vue.js",
    "vuejs": "vue.js",
    "vue.js": "vue.js",
    "nuxt": "nuxt.js",
    "nuxtjs": "nuxt.js",
    "nuxt.js": "nuxt.js",
    "angular": "angular",
    "angularjs": "angular",
    "svelte": "svelte",
    "sveltekit": "sveltekit",
    "html": "html",
    "html5": "html",
    "css": "css",
    "css3": "css",
    "tailwind": "tailwindcss",
    "tailwindcss": "tailwindcss",
    "tailwind css": "tailwindcss",
    "bootstrap": "bootstrap",
    "redux": "redux",
    "zustand": "zustand",
    "mobx": "mobx",
    "sass": "sass",
    "scss": "sass",
    "webpack": "webpack",
    "vite": "vite",
    "bun": "bun",

    # Backend & Languages
    "py": "python",
    "python": "python",
    "python3": "python",
    "fastapi": "fastapi",
    "django": "django",
    "flask": "flask",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "express": "express.js",
    "expressjs": "express.js",
    "express.js": "express.js",
    "fastify": "fastify",
    "nest": "nestjs",
    "nestjs": "nestjs",
    "golang": "go",
    "go": "go",
    "rust": "rust",
    "c++": "c++",
    "cpp": "c++",
    "c#": "c#",
    "csharp": "c#",
    ".net": ".net",
    "dotnet": ".net",
    "asp.net": "asp.net",
    "java": "java",
    "spring": "spring boot",
    "springboot": "spring boot",
    "spring boot": "spring boot",
    "kotlin": "kotlin",
    "swift": "swift",
    "ruby": "ruby",
    "rails": "ruby on rails",
    "ruby on rails": "ruby on rails",
    "php": "php",
    "laravel": "laravel",
    "symfony": "symfony",
    "elixir": "elixir",
    "phoenix": "phoenix",

    # Databases & Storage
    "sql": "sql",
    "mysql": "mysql",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "redis": "redis",
    "elasticsearch": "elasticsearch",
    "opensearch": "opensearch",
    "cassandra": "cassandra",
    "dynamodb": "dynamodb",
    "sqlite": "sqlite",
    "snowflake": "snowflake",
    "bigquery": "bigquery",
    "clickhouse": "clickhouse",
    "supabase": "supabase",
    "firebase": "firebase",
    "prisma": "prisma",
    "sqlalchemy": "sqlalchemy",
    "orm": "orm",

    # Cloud & DevOps & Infra
    "aws": "aws",
    "amazon web services": "aws",
    "gcp": "gcp",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "azure": "azure",
    "microsoft azure": "azure",
    "docker": "docker",
    "containerization": "docker",
    "containers": "docker",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "helm": "helm",
    "terraform": "terraform",
    "ansible": "ansible",
    "ci/cd": "ci/cd",
    "cicd": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    "jenkins": "jenkins",
    "github actions": "github actions",
    "gitlab ci": "gitlab ci",
    "circleci": "circleci",
    "git": "git",
    "github": "git",
    "gitlab": "git",
    "linux": "linux",
    "bash": "bash",
    "shell": "shell",
    "nginx": "nginx",
    "apache": "apache",
    "prometheus": "prometheus",
    "grafana": "grafana",
    "datadog": "datadog",

    # AI / ML / Data
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "ml": "machine learning",
    "machine learning": "machine learning",
    "deep learning": "deep learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "natural language processing": "natural language processing",
    "llm": "large language models",
    "llms": "large language models",
    "large language models": "large language models",
    "langchain": "langchain",
    "llamaindex": "llamaindex",
    "rag": "rag",
    "retrieval augmented generation": "rag",
    "vector db": "vector database",
    "vector database": "vector database",
    "chromadb": "chromadb",
    "chroma": "chromadb",
    "pinecone": "pinecone",
    "weaviate": "weaviate",
    "qdrant": "qdrant",
    "milvus": "milvus",
    "huggingface": "hugging face",
    "hugging face": "hugging face",
    "transformers": "transformers",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
    "keras": "keras",
    "pandas": "pandas",
    "numpy": "numpy",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "data science": "data science",
    "data analysis": "data analysis",
    "data engineering": "data engineering",
    "big data": "big data",
    "spark": "apache spark",
    "apache spark": "apache spark",
    "kafka": "apache kafka",
    "apache kafka": "apache kafka",
    "airflow": "apache airflow",
    "apache airflow": "apache airflow",
    "computer vision": "computer vision",
    "opencv": "opencv",

    # Architecture, APIs & Practices
    "rest": "rest api",
    "restful": "rest api",
    "rest api": "rest api",
    "rest apis": "rest api",
    "graphql": "graphql",
    "grpc": "grpc",
    "websocket": "websockets",
    "websockets": "websockets",
    "microservices": "microservices",
    "distributed systems": "distributed systems",
    "event-driven": "event-driven architecture",
    "event-driven architecture": "event-driven architecture",
    "system design": "system design",
    "unit testing": "unit testing",
    "integration testing": "integration testing",
    "e2e testing": "e2e testing",
    "tdd": "test driven development",
    "test driven development": "test driven development",
    "pytest": "pytest",
    "jest": "jest",
    "cypress": "cypress",
    "playwright": "playwright",
    "selenium": "selenium",
    "agile": "agile",
    "scrum": "scrum",
    "kanban": "kanban",
    "object oriented": "object oriented programming",
    "oop": "object oriented programming",
    "clean code": "clean code",
}

# Display names for clean UI formatting
SKILL_DISPLAY = {
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "react native": "React Native",
    "next.js": "Next.js",
    "vue.js": "Vue.js",
    "nuxt.js": "Nuxt.js",
    "angular": "Angular",
    "svelte": "Svelte",
    "sveltekit": "SvelteKit",
    "html": "HTML5",
    "css": "CSS3",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "redux": "Redux",
    "zustand": "Zustand",
    "mobx": "MobX",
    "sass": "Sass",
    "webpack": "Webpack",
    "vite": "Vite",
    "bun": "Bun",
    "python": "Python",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "node.js": "Node.js",
    "express.js": "Express.js",
    "fastify": "Fastify",
    "nestjs": "NestJS",
    "go": "Go",
    "rust": "Rust",
    "c++": "C++",
    "c#": "C#",
    ".net": ".NET",
    "asp.net": "ASP.NET",
    "java": "Java",
    "spring boot": "Spring Boot",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "ruby": "Ruby",
    "ruby on rails": "Ruby on Rails",
    "php": "PHP",
    "laravel": "Laravel",
    "symfony": "Symfony",
    "elixir": "Elixir",
    "phoenix": "Phoenix",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "opensearch": "OpenSearch",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "sqlite": "SQLite",
    "snowflake": "Snowflake",
    "bigquery": "BigQuery",
    "clickhouse": "ClickHouse",
    "supabase": "Supabase",
    "firebase": "Firebase",
    "prisma": "Prisma",
    "sqlalchemy": "SQLAlchemy",
    "orm": "ORM",
    "aws": "AWS",
    "gcp": "Google Cloud (GCP)",
    "azure": "Azure",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "helm": "Helm",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "ci/cd": "CI/CD",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "circleci": "CircleCI",
    "git": "Git",
    "linux": "Linux",
    "bash": "Bash",
    "shell": "Shell",
    "nginx": "Nginx",
    "apache": "Apache",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "datadog": "Datadog",
    "artificial intelligence": "AI",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "natural language processing": "NLP",
    "large language models": "LLMs",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "rag": "RAG",
    "vector database": "Vector DB",
    "chromadb": "ChromaDB",
    "pinecone": "Pinecone",
    "weaviate": "Weaviate",
    "qdrant": "Qdrant",
    "milvus": "Milvus",
    "hugging face": "Hugging Face",
    "transformers": "Transformers",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "keras": "Keras",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-Learn",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "data engineering": "Data Engineering",
    "big data": "Big Data",
    "apache spark": "Apache Spark",
    "apache kafka": "Apache Kafka",
    "apache airflow": "Apache Airflow",
    "computer vision": "Computer Vision",
    "opencv": "OpenCV",
    "rest api": "REST API",
    "graphql": "GraphQL",
    "grpc": "gRPC",
    "websockets": "WebSockets",
    "microservices": "Microservices",
    "distributed systems": "Distributed Systems",
    "event-driven architecture": "Event-Driven Architecture",
    "system design": "System Design",
    "unit testing": "Unit Testing",
    "integration testing": "Integration Testing",
    "e2e testing": "E2E Testing",
    "test driven development": "TDD",
    "pytest": "Pytest",
    "jest": "Jest",
    "cypress": "Cypress",
    "playwright": "Playwright",
    "selenium": "Selenium",
    "agile": "Agile / Scrum",
    "scrum": "Scrum",
    "kanban": "Kanban",
    "object oriented programming": "OOP",
    "clean code": "Clean Code",
}

# 250+ generic job description boilerplate and stop words that must NOT be counted as ATS skills
BOILERPLATE_JOB_WORDS = {
    # Pronouns & Prepositions & Common words
    "a", "about", "above", "across", "after", "again", "against", "all",
    "almost", "also", "always", "among", "an", "and", "another", "any",
    "anyone", "anything", "are", "around", "as", "at", "be", "because",
    "become", "been", "before", "being", "between", "both", "but", "by",
    "can", "could", "did", "do", "does", "each", "either", "etc", "every",
    "for", "from", "get", "give", "had", "has", "have", "he", "her", "here",
    "him", "his", "how", "i", "if", "in", "into", "is", "it", "its", "just",
    "may", "me", "might", "more", "most", "must", "my", "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "others", "our", "out",
    "over", "own", "same", "shall", "she", "should", "so", "some", "such",
    "than", "that", "the", "their", "them", "then", "there", "these", "they",
    "this", "those", "through", "to", "too", "under", "until", "up", "upon",
    "us", "very", "was", "we", "were", "what", "when", "where", "which",
    "while", "who", "whom", "why", "will", "with", "within", "without",
    "would", "yes", "yet", "you", "your", "yourself",

    # HR & Job Description Boilerplate
    "ability", "able", "action", "activities", "addition", "additional",
    "analyst", "applicant", "applicants", "apply", "applying", "appropriate",
    "architect", "area", "areas", "available", "background", "basic",
    "backend", "benefit", "benefits", "best", "better", "bring", "build",
    "building", "business", "candidate", "candidates", "career", "careers",
    "chance", "clear", "closely", "collaborate", "collaboration",
    "collaborative", "colleagues", "come", "comfortable", "communication",
    "commute", "company", "compensation", "competitive", "complete",
    "contribute", "create", "creating", "culture", "curriculum", "current",
    "cv", "daily", "degree", "deliver", "delivery", "demonstrated",
    "department", "description", "desired", "detail", "details", "develop",
    "developer", "developers", "developing", "development", "direct",
    "diverse", "drive", "driven", "duties", "dynamic", "effective",
    "efficient", "eligible", "employment", "encourage", "engineer",
    "engineers", "engineering", "ensure", "environment", "equal",
    "essential", "excellent", "exciting", "execute", "expect", "expected",
    "experience", "experiences", "experienced", "expert", "expertise",
    "familiar", "fast", "field", "first", "flexible", "focus", "focused",
    "following", "frontend", "full", "fully", "fullstack", "full-stack",
    "functions", "future", "general", "global", "goal", "goals", "good",
    "great", "grow", "growth", "hand", "hands", "help", "helping", "high",
    "highly", "hire", "hiring", "hold", "hour", "hours", "ideal", "identify",
    "impact", "important", "improve", "including", "individual", "industry",
    "initiative", "innovative", "inside", "inspire", "instead", "interest",
    "interested", "internal", "involved", "issue", "issues", "job", "join",
    "key", "kind", "know", "knowledge", "lead", "leader", "leadership",
    "learn", "learning", "level", "like", "location", "long", "look",
    "looking", "make", "making", "manage", "management", "manager", "many",
    "matter", "meet", "meeting", "member", "members", "mentor", "mind",
    "mission", "motivated", "move", "multiple", "name", "need", "needs",
    "new", "next", "nice", "objective", "opportunity", "opportunities",
    "options", "order", "organization", "overview", "paid", "part",
    "partner", "passion", "passionate", "path", "people", "perform",
    "performance", "person", "personal", "place", "plan", "plans",
    "position", "positions", "posting", "postings", "posted", "potential",
    "practice", "practices", "prefer", "preferred", "prepare", "prior",
    "priority", "problem", "problems", "process", "processes", "produce",
    "product", "professional", "proficiency", "proficient", "profile",
    "program", "project", "projects", "provide", "providing", "purpose",
    "qualification", "qualifications", "quality", "quick", "quickly", "range",
    "ready", "real", "reason", "receive", "recruiter", "recruiting", "regular",
    "related", "relevant", "remote", "require", "required", "requirement",
    "requirements", "requires", "responsibility", "responsibilities",
    "responsible", "results", "resume", "role", "roles", "salary", "scale",
    "schedule", "scope", "seasoned", "secure", "seek", "seeking", "self",
    "senior", "sense", "serve", "service", "services", "set", "share",
    "show", "similar", "skill", "skills", "skilled", "solution", "solutions",
    "solve", "solving", "someone", "something", "soon", "space", "speak",
    "special", "specialist", "stack", "standard", "standards", "start",
    "state", "status", "stay", "strong", "structured",
    "success", "successful", "suit", "summary", "support", "take", "talent",
    "task", "tasks", "team", "teams", "tech", "terms", "testing", "thing",
    "things", "think", "thorough", "time", "title", "together", "tool",
    "tools", "top", "track", "training", "understand", "understanding",
    "unique", "unit", "usage", "use", "using", "valuable", "value",
    "variety", "vision", "vitae", "want", "watch", "way", "ways", "week",
    "well", "wide", "willing", "word", "words", "work", "worker", "working",
    "workplace", "world", "worth", "write", "writing", "year", "years",
    "401k", "hybrid", "onsite", "equal-opportunity", "affirmative",
    "disability", "veteran", "medical", "dental", "vision", "bonus"
}


def _format_skill_name(canonical_name: str) -> str:
    """Format canonical skill name to proper display casing."""
    return SKILL_DISPLAY.get(canonical_name.lower(), canonical_name.title())


def extract_skills(text: str) -> Set[str]:
    """
    Extract canonical skill representations using the alias taxonomy.
    Supports both single-word and multi-word phrases, as well as symbols (C++, C#, .NET, CI/CD).
    """
    if not text:
        return set()

    text_lower = f" {text.lower()} "
    found_skills = set()

    # Sort aliases by length descending so longer phrases match first
    sorted_aliases = sorted(SKILL_ALIASES.keys(), key=len, reverse=True)

    for alias in sorted_aliases:
        # Boundary pattern ensuring alias is not preceded or followed by alphanumeric characters
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(alias) + r'(?![a-zA-Z0-9])'
        if re.search(pattern, text_lower):
            found_skills.add(SKILL_ALIASES[alias])

    return found_skills


def extract_keywords(text: str) -> Set[str]:
    """
    Extract meaningful domain keywords from text,
    strictly excluding generic job boilerplate and stop words.
    Preserves tokens with technical symbols (e.g. C++, .NET, C#).
    """
    if not text:
        return set()

    # Extract words/tokens that may contain technical symbols
    raw_tokens = re.findall(r'(?<![\w#+.-])(?:\.?[a-zA-Z][\w#+.-]*)(?![\w#+.-])', text.lower())

    meaningful = set()
    for raw in raw_tokens:
        clean = raw.rstrip('.,;:!?')
        if not clean or len(clean) < 2:
            continue
        if clean in BOILERPLATE_JOB_WORDS:
            continue
        if clean.isdigit():
            continue
        meaningful.add(clean)

    return meaningful


def calculate_ats_score(
    resume_text: str,
    job_text: str,
    key_skills: Optional[List[str]] = None,
    candidate_skills: Optional[List[str]] = None,
    missing_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculates ATS keyword & skill fit using:
    1. Canonical skill & multi-word phrase matching with alias normalization
    2. Explicit job requirements & candidate qualifications from LLM fit analysis
    3. Noise-filtered domain keyword overlap
    """
    if not job_text and not key_skills:
        return {
            "score": 0,
            "matched_keywords": [],
            "missing_keywords": [],
            "total_job_keywords": 0
        }

    # 1. Extract canonical skills from raw text
    job_canonical = extract_skills(job_text)
    resume_canonical = extract_skills(resume_text)

    # 2. Incorporate explicit key skills from LLM analysis
    def _add_llm_skill(skill_item: str, target_set: Set[str]):
        if not isinstance(skill_item, str) or not skill_item.strip():
            return
        clean = skill_item.strip().lower()
        # First check if the full phrase has an alias
        if clean in SKILL_ALIASES:
            target_set.add(SKILL_ALIASES[clean])
            return
        # Check if sub-skills are extracted
        extracted = extract_skills(clean)
        if extracted:
            target_set.update(extracted)
        else:
            # Add as domain skill if not boilerplate
            if clean not in BOILERPLATE_JOB_WORDS and len(clean) >= 2:
                target_set.add(clean)

    if key_skills:
        for sk in key_skills:
            _add_llm_skill(sk, job_canonical)

    if candidate_skills:
        for sk in candidate_skills:
            _add_llm_skill(sk, resume_canonical)

    # 3. Compute skill-level match
    matched_canonical = job_canonical & resume_canonical
    missing_canonical = job_canonical - resume_canonical

    # Incorporate explicit missing skills identified by LLM
    if missing_skills:
        for ms in missing_skills:
            if isinstance(ms, str) and ms.strip():
                clean_ms = ms.strip().lower()
                canonical_ms = SKILL_ALIASES.get(clean_ms, clean_ms)
                if canonical_ms not in matched_canonical and canonical_ms not in BOILERPLATE_JOB_WORDS:
                    missing_canonical.add(canonical_ms)
                    job_canonical.add(canonical_ms)

    # 4. Compute domain keyword overlap (filtered)
    job_words = extract_keywords(job_text)
    resume_words = extract_keywords(resume_text)

    # Filter out domain words that are already captured by canonical skills or aliases
    known_skill_tokens = set()
    for s in (job_canonical | resume_canonical):
        known_skill_tokens.add(s.lower())
        for part in re.split(r'[\s/._-]+', s.lower()):
            if part:
                known_skill_tokens.add(part)
    for alias in SKILL_ALIASES:
        known_skill_tokens.add(alias.lower())
        for part in re.split(r'[\s/._-]+', alias.lower()):
            if part:
                known_skill_tokens.add(part)

    job_domain = {w for w in job_words if w not in known_skill_tokens}
    resume_domain = {w for w in resume_words if w not in known_skill_tokens}

    matched_domain = job_domain & resume_domain
    missing_domain = job_domain - resume_domain

    # 5. Weighted score calculation
    if job_canonical:
        skill_score = (len(matched_canonical) / len(job_canonical)) * 100
        # If all canonical skills match, full score is achieved
        if not missing_canonical:
            final_score = 100
        # Only factor in domain keywords if there is a substantive domain vocabulary (>= 3 words)
        elif len(job_domain) >= 3:
            domain_score = (len(matched_domain) / len(job_domain)) * 100
            final_score = round((skill_score * 0.85) + (domain_score * 0.15))
        else:
            final_score = round(skill_score)
    elif job_domain:
        # Fallback to domain keywords if no canonical skills found
        final_score = round((len(matched_domain) / len(job_domain)) * 100)
    else:
        final_score = 0

    final_score = max(0, min(final_score, 100))

    # 6. Format matched and missing lists for clean UI presentation
    formatted_matched = [_format_skill_name(s) for s in sorted(matched_canonical)]
    formatted_missing = [_format_skill_name(s) for s in sorted(missing_canonical)]

    # Supplement with top domain keywords if canonical list has fewer than 10
    seen_matched_lower = {s.lower() for s in formatted_matched}
    for dw in sorted(matched_domain, key=len, reverse=True):
        if len(formatted_matched) >= 10:
            break
        disp = _format_skill_name(dw)
        if disp.lower() not in seen_matched_lower:
            formatted_matched.append(disp)
            seen_matched_lower.add(disp.lower())

    seen_missing_lower = {s.lower() for s in formatted_missing}
    for dw in sorted(missing_domain, key=len, reverse=True):
        if len(formatted_missing) >= 10:
            break
        disp = _format_skill_name(dw)
        if disp.lower() not in seen_missing_lower and disp.lower() not in seen_matched_lower:
            formatted_missing.append(disp)
            seen_missing_lower.add(disp.lower())

    total_keywords = max(len(job_canonical), len(job_words), len(formatted_matched) + len(formatted_missing))

    return {
        "score": final_score,
        "matched_keywords": formatted_matched[:10],
        "missing_keywords": formatted_missing[:10],
        "total_job_keywords": total_keywords
    }


def calculate_tone_score(tone_profile: Optional[Dict[str, Any]], variants: Optional[List[Dict[str, Any]]]) -> int:
    """
    Check if generated emails reflect the company tone profile.
    Returns 0-100 score.
    """
    if not tone_profile or not variants:
        return 50  # Neutral score if no tone data

    example_phrases = tone_profile.get("example_phrases", [])
    formality = tone_profile.get("formality", "semi-formal")
    vocabulary = tone_profile.get("vocabulary", "mixed")

    # Combine all variant emails into one text for checking
    all_emails = " ".join([v.get("email", "") for v in variants]).lower()

    score = 50  # Base score

    # Check if example phrases from company appear in emails
    if example_phrases:
        phrase_words = extract_keywords(" ".join(example_phrases))
        email_words = extract_keywords(all_emails)
        overlap = phrase_words & email_words
        if phrase_words:
            phrase_score = (len(overlap) / len(phrase_words)) * 30
            score += phrase_score

    # Check formality alignment
    formal_words = {"sincerely", "regarding", "furthermore", "herein", "enclosed"}
    casual_words = {"hey", "excited", "love", "awesome", "cool", "keen"}

    if formality == "casual":
        casual_found = any(w in all_emails for w in casual_words)
        score += 10 if casual_found else 0
    elif formality == "formal":
        formal_found = any(w in all_emails for w in formal_words)
        score += 10 if formal_found else 0
    else:
        score += 10  # Semi-formal always gets neutral bonus

    # Check vocabulary alignment
    tech_words = {"api", "framework", "pipeline", "backend", "frontend",
                  "infrastructure", "deployment", "architecture", "scalable"}
    if vocabulary == "technical":
        tech_found = sum(1 for w in tech_words if w in all_emails)
        score += min(tech_found * 2, 10)
    else:
        score += 5  # Neutral bonus for mixed/simple

    return min(round(score), 100)


def calculate_overall_score(match_score: int, resume_score: int, ats_score: int, tone_score: int) -> int:
    """
    Weighted average of all scores.
    Weights reflect what matters most for job applications.
    """
    weights = {
        "match_score": 0.35,    # Resume-job fit is most important
        "ats_score": 0.30,      # Keyword presence matters for ATS systems
        "resume_score": 0.20,   # Overall resume strength
        "tone_score": 0.15      # Tone matching is a bonus differentiator
    }

    overall = (
        match_score  * weights["match_score"] +
        ats_score    * weights["ats_score"] +
        resume_score * weights["resume_score"] +
        tone_score   * weights["tone_score"]
    )

    return round(overall)


def get_score_label(score: int) -> str:
    """Convert score to human readable label."""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 55:
        return "Fair"
    else:
        return "Needs Work"


def build_score_dashboard(
    resume_text: str,
    job_text: str,
    tone_profile: Optional[Dict[str, Any]],
    variants: Optional[List[Dict[str, Any]]],
    match_score: int,
    resume_score: int,
    key_skills: Optional[List[str]] = None,
    candidate_skills: Optional[List[str]] = None,
    missing_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Master function — builds complete scoring dashboard.
    Called from ai_pipeline.py
    """
    ats_result = calculate_ats_score(
        resume_text=resume_text,
        job_text=job_text,
        key_skills=key_skills,
        candidate_skills=candidate_skills,
        missing_skills=missing_skills
    )
    tone_score = calculate_tone_score(tone_profile, variants)
    overall = calculate_overall_score(
        match_score,
        resume_score,
        ats_result["score"],
        tone_score
    )

    return {
        "overall_score": overall,
        "overall_label": get_score_label(overall),
        "breakdown": {
            "match_score": {
                "score": match_score,
                "label": get_score_label(match_score),
                "description": "How well your resume matches this specific job"
            },
            "ats_score": {
                "score": ats_result["score"],
                "label": get_score_label(ats_result["score"]),
                "description": "Keywords from job description found in your resume",
                "matched_keywords": ats_result["matched_keywords"],
                "missing_keywords": ats_result["missing_keywords"]
            },
            "resume_score": {
                "score": resume_score,
                "label": get_score_label(resume_score),
                "description": "Overall strength of your resume for this role"
            },
            "tone_score": {
                "score": tone_score,
                "label": get_score_label(tone_score),
                "description": "How well email tone matches company communication style"
            }
        }
    }