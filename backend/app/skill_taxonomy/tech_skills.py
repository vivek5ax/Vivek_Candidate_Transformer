from typing import Dict, List, Set

# Comprehensive taxonomy mapping canonical skill names to their lowercase surface forms and aliases.
TECH_SKILL_TAXONOMY: Dict[str, List[str]] = {
    # Programming Languages
    "Python": ["python", "python3", "py"],
    "JavaScript": ["javascript", "js", "ecmascript", "es6"],
    "TypeScript": ["typescript", "ts"],
    "Java": ["java", "core java", "j2ee"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp"],
    "Go": ["go", "golang"],
    "Rust": ["rust"],
    "Ruby": ["ruby"],
    "PHP": ["php"],
    "Swift": ["swift"],
    "Kotlin": ["kotlin"],
    "Scala": ["scala"],
    "SQL": ["sql", "structured query language"],
    "R": ["r programming", "r language"],
    "Perl": ["perl"],
    "Haskell": ["haskell"],
    "Elixir": ["elixir"],

    # Web Frameworks & Backend
    "FastAPI": ["fastapi", "fast api"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Spring Boot": ["spring boot", "spring-boot", "springboot", "spring"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Express.js": ["express.js", "expressjs", "express"],
    "NestJS": ["nestjs", "nest.js"],
    "Ruby on Rails": ["ruby on rails", "rails", "ror"],
    "ASP.NET": ["asp.net", ".net", "dotnet", ".net core"],
    "GraphQL": ["graphql"],
    "REST API": ["rest api", "restful api", "rest apis", "restful apis", "rest"],
    "gRPC": ["grpc"],

    # Frontend Libraries & Frameworks
    "React": ["react", "react.js", "reactjs", "react native"],
    "Angular": ["angular", "angular.js", "angularjs"],
    "Vue.js": ["vue", "vue.js", "vuejs"],
    "Next.js": ["next.js", "nextjs", "next"],
    "Nuxt.js": ["nuxt.js", "nuxtjs", "nuxt"],
    "Svelte": ["svelte"],
    "Tailwind CSS": ["tailwind css", "tailwindcss", "tailwind"],
    "Bootstrap": ["bootstrap"],
    "HTML5": ["html", "html5"],
    "CSS3": ["css", "css3"],
    "Redux": ["redux"],

    # Cloud, Containers & DevOps
    "Docker": ["docker", "docker-compose", "containerization"],
    "Kubernetes": ["kubernetes", "k8s", "kube"],
    "AWS": ["aws", "amazon web services"],
    "EC2": ["ec2", "amazon ec2", "aws ec2"],
    "S3": ["s3", "amazon s3", "aws s3"],
    "Lambda": ["lambda", "aws lambda", "amazon lambda"],
    "CloudWatch": ["cloudwatch", "aws cloudwatch", "amazon cloudwatch"],
    "IAM": ["iam", "aws iam"],
    "GCP": ["gcp", "google cloud platform", "google cloud"],
    "Azure": ["azure", "microsoft azure"],
    "Terraform": ["terraform"],
    "Ansible": ["ansible"],
    "Jenkins": ["jenkins"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment"],
    "GitHub Actions": ["github actions", "gh actions"],
    "Git": ["git", "bitbucket"],
    "Linux": ["linux", "bash", "shell scripting", "unix"],
    "Nginx": ["nginx"],

    # Databases & Storage
    "PostgreSQL": ["postgresql", "postgres", "psql"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo"],
    "DynamoDB": ["dynamodb", "amazon dynamodb", "aws dynamodb"],
    "RDS": ["rds", "amazon rds", "aws rds"],
    "Redis": ["redis"],
    "Elasticsearch": ["elasticsearch", "elastic search"],
    "SQLite": ["sqlite"],
    "Oracle DB": ["oracle db", "oracle"],
    "Cassandra": ["cassandra"],
    "Kafka": ["kafka", "apache kafka"],
    "RabbitMQ": ["rabbitmq", "rabbit mq"],

    # Data Science, AI & Machine Learning
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "dl"],
    "Artificial Intelligence": ["artificial intelligence", "ai"],
    "PyTorch": ["pytorch"],
    "TensorFlow": ["tensorflow", "tf"],
    "Scikit-Learn": ["scikit-learn", "sklearn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Apache Spark": ["apache spark", "spark"],
    "PySpark": ["pyspark", "py-spark"],
    "Hadoop": ["hadoop"],
    "Airflow": ["airflow", "apache airflow"],
    "Databricks": ["databricks"],
    "Snowflake": ["snowflake"],
    "LangChain": ["langchain"],
    "LLMs": ["llm", "llms", "large language models", "generative ai", "genai", "openai", "gemini"],

    # Testing & QA
    "PyTest": ["pytest", "py.test"],
    "JUnit": ["junit"],
    "Mockito": ["mockito"],
    "Postman": ["postman"],
    "Swagger/OpenAPI": ["swagger", "openapi", "swagger/openapi", "swagger ui"],

    # Tools, Platforms & Collaboration
    "GitHub": ["github", "gh"],
    "GitLab": ["gitlab", "gitlab ci"],
    "VS Code": ["vs code", "vscode", "visual studio code"],
    "IntelliJ IDEA": ["intellij", "intellij idea"],
    "Confluence": ["confluence", "atlassian confluence"],
    "Agile": ["agile", "scrum", "kanban"],
    "Jira": ["jira"],
    "Microservices": ["microservices", "microservice architecture"],
    "Distributed Systems": ["distributed systems", "system design"]
}

# Build fast inverted lookup map: alias string -> canonical display name
ALIAS_TO_CANONICAL: Dict[str, str] = {}
for canonical_name, aliases in TECH_SKILL_TAXONOMY.items():
    for alias in aliases:
        ALIAS_TO_CANONICAL[alias.lower().strip()] = canonical_name

# Flat set of all lowercase terms we search for during text scanning
ALL_SKILL_TERMS: Set[str] = set(ALIAS_TO_CANONICAL.keys())
