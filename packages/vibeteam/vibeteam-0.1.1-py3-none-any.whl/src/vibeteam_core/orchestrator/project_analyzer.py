"""
Project analysis for understanding codebase structure and technologies.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class ProjectType(Enum):
    """Different types of software projects."""

    BACKEND = "backend"
    FRONTEND = "frontend"
    FULLSTACK = "fullstack"
    LIBRARY = "library"
    CLI_TOOL = "cli_tool"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    DEVOPS = "devops"
    UNKNOWN = "unknown"


class ProjectAnalyzer:
    """Analyzes project structure to understand technologies and patterns."""

    def __init__(self):
        self.project_indicators = {
            "backend": [
                "requirements.txt",
                "Pipfile",
                "go.mod",
                "pom.xml",
                "build.gradle",
                "Cargo.toml",
                "package.json",
                "api/",
                "server/",
                "backend/",
                "app.py",
                "main.py",
                "server.js",
                "index.js",
            ],
            "frontend": [
                "package.json",
                "index.html",
                "src/App.js",
                "src/App.tsx",
                "angular.json",
                "vue.config.js",
                "frontend/",
                "client/",
                "public/",
                "assets/",
                "styles/",
                "css/",
            ],
            "fullstack": [
                "docker-compose.yml",
                "Dockerfile",
                "kubernetes/",
                "frontend/",
                "backend/",
                "client/",
                "server/",
            ],
            "library": [
                "setup.py",
                "pyproject.toml",
                "lib/",
                "src/lib/",
                "dist/",
                "package.json",
                "Cargo.toml",
                "go.mod",
            ],
            "cli_tool": ["bin/", "cli.py", "main.py", "cmd/", "__main__.py"],
            "mobile": [
                "android/",
                "ios/",
                "mobile/",
                "App.tsx",
                "App.js",
                "pubspec.yaml",
                "flutter/",
                "react-native/",
            ],
            "desktop": [
                "electron/",
                "tauri/",
                "desktop/",
                "gui/",
                "qt/",
                "tkinter/",
                "kivy/",
                ".app/",
                ".exe",
            ],
            "data_science": [
                "notebooks/",
                "data/",
                "models/",
                "*.ipynb",
                "requirements.txt",
                "environment.yml",
                "analysis/",
            ],
            "machine_learning": [
                "models/",
                "training/",
                "inference/",
                "ml/",
                "ai/",
                "weights/",
                "checkpoints/",
                "datasets/",
            ],
            "devops": [
                ".github/",
                ".gitlab-ci.yml",
                "terraform/",
                "ansible/",
                "k8s/",
                "kubernetes/",
                "docker/",
                "scripts/",
            ],
        }

        self.tech_indicators = {
            "Python": ["*.py", "requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "JavaScript": ["*.js", "*.jsx", "package.json", "node_modules/"],
            "TypeScript": ["*.ts", "*.tsx", "tsconfig.json"],
            "Go": ["*.go", "go.mod", "go.sum"],
            "Rust": ["*.rs", "Cargo.toml", "Cargo.lock"],
            "Java": ["*.java", "pom.xml", "build.gradle", "*.jar"],
            "C++": ["*.cpp", "*.hpp", "*.cc", "Makefile", "CMakeLists.txt"],
            "C#": ["*.cs", "*.csproj", "*.sln"],
            "React": ["package.json", "src/App.js", "src/App.tsx", "public/index.html"],
            "Vue": ["vue.config.js", "*.vue", "package.json"],
            "Angular": ["angular.json", "*.component.ts"],
            "Django": ["manage.py", "settings.py", "models.py"],
            "Flask": ["app.py", "application.py", "flask/"],
            "FastAPI": ["main.py", "fastapi/", "uvicorn"],
            "Express": ["server.js", "app.js", "express"],
            "Next.js": ["next.config.js", "pages/", "app/"],
            "Docker": ["Dockerfile", "docker-compose.yml", ".dockerignore"],
            "Kubernetes": ["*.yaml", "k8s/", "kubernetes/"],
            "Terraform": ["*.tf", "terraform/"],
            "AWS": ["*.yaml", "cloudformation/", "cdk/"],
            "Jupyter": ["*.ipynb", "notebooks/"],
            "TensorFlow": ["*.h5", "saved_model/", "tensorflow"],
            "PyTorch": ["*.pth", "*.pt", "torch"],
        }

    def detect_project_type(self, cwd: Path) -> ProjectType:
        """Detect the primary project type based on file patterns."""
        if not cwd.exists():
            return ProjectType.UNKNOWN

        files = list(cwd.glob("*")) + list(cwd.glob("*/*"))
        file_paths = [str(f) for f in files]

        type_scores = {}

        for project_type, indicators in self.project_indicators.items():
            score = 0
            for indicator in indicators:
                if any(indicator in file_path for file_path in file_paths):
                    score += 1
            type_scores[project_type] = score

        # Special logic for determining project types
        backend_score = type_scores.get("backend", 0)
        frontend_score = type_scores.get("frontend", 0)
        fullstack_score = type_scores.get("fullstack", 0)

        if fullstack_score > 0 or (backend_score > 0 and frontend_score > 0):
            return ProjectType.FULLSTACK
        elif backend_score > frontend_score:
            return ProjectType.BACKEND
        elif frontend_score > backend_score:
            return ProjectType.FRONTEND
        elif type_scores.get("mobile", 0) > 0:
            return ProjectType.MOBILE
        elif type_scores.get("desktop", 0) > 0:
            return ProjectType.DESKTOP
        elif type_scores.get("data_science", 0) > 0:
            return ProjectType.DATA_SCIENCE
        elif type_scores.get("machine_learning", 0) > 0:
            return ProjectType.MACHINE_LEARNING
        elif type_scores.get("devops", 0) > 0:
            return ProjectType.DEVOPS
        elif type_scores.get("cli_tool", 0) > 0:
            return ProjectType.CLI_TOOL
        elif type_scores.get("library", 0) > 0:
            return ProjectType.LIBRARY
        elif any(f.suffix in [".py", ".js", ".ts", ".go", ".rs", ".java"] for f in files):
            return ProjectType.LIBRARY
        else:
            return ProjectType.UNKNOWN

    def get_project_context(self, cwd: Path) -> Dict[str, Any]:
        """Get comprehensive project context."""
        if not cwd.exists():
            return {
                "cwd": str(cwd),
                "type": ProjectType.UNKNOWN.value,
                "technologies": [],
                "files": [],
                "structure": {},
                "size": "unknown",
                "complexity": 1,
            }

        project_type = self.detect_project_type(cwd)
        technologies = self._detect_technologies(cwd)
        structure = self._analyze_structure(cwd)
        files = self._get_important_files(cwd)

        return {
            "cwd": str(cwd),
            "type": project_type.value,
            "technologies": technologies,
            "files": files,
            "structure": structure,
            "size": self._estimate_project_size(cwd),
            "complexity": self._estimate_complexity(cwd, technologies),
            "patterns": self._detect_patterns(cwd, technologies),
        }

    def _detect_technologies(self, cwd: Path) -> List[str]:
        """Detect technologies used in the project."""
        technologies = []

        for tech, patterns in self.tech_indicators.items():
            for pattern in patterns:
                # Handle glob patterns vs direct file checks
                if "*" in pattern:
                    if list(cwd.glob(pattern)) or list(cwd.rglob(pattern)):
                        technologies.append(tech)
                        break
                else:
                    # Check for directory or file existence
                    if (cwd / pattern).exists():
                        technologies.append(tech)
                        break
                    # Also check in subdirectories
                    if any(pattern in str(f) for f in cwd.rglob("*")):
                        technologies.append(tech)
                        break

        return technologies

    def _analyze_structure(self, cwd: Path) -> Dict[str, Any]:
        """Analyze project directory structure."""
        structure = {}

        try:
            for item in cwd.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    file_count = len(list(item.glob("*")))
                    structure[item.name] = {
                        "type": "directory",
                        "files": file_count,
                        "size": sum(f.stat().st_size for f in item.rglob("*") if f.is_file()),
                    }
                elif item.is_file():
                    structure[item.name] = {"type": "file", "size": item.stat().st_size}
        except PermissionError:
            pass  # Skip directories we can't read

        return structure

    def _get_important_files(self, cwd: Path) -> List[str]:
        """Get list of important files in the project."""
        important_patterns = [
            "README*",
            "package.json",
            "requirements.txt",
            "Dockerfile",
            "docker-compose.yml",
            "Makefile",
            "*.toml",
            "*.yaml",
            "*.yml",
            "go.mod",
            "Cargo.toml",
            "pom.xml",
            "build.gradle",
        ]

        important_files = []
        for pattern in important_patterns:
            important_files.extend([f.name for f in cwd.glob(pattern)])

        return important_files[:20]  # Limit to first 20

    def _estimate_project_size(self, cwd: Path) -> str:
        """Estimate project size category."""
        try:
            file_count = len(list(cwd.rglob("*")))

            if file_count < 50:
                return "small"
            elif file_count < 200:
                return "medium"
            elif file_count < 1000:
                return "large"
            else:
                return "very_large"
        except Exception:
            return "unknown"

    def _estimate_complexity(self, cwd: Path, technologies: List[str]) -> int:
        """Estimate project complexity (1-5)."""
        complexity = 1

        # Add complexity for multiple technologies
        if len(technologies) > 5:
            complexity += 2
        elif len(technologies) > 2:
            complexity += 1

        # Add complexity for specific technology combinations
        if "Docker" in technologies:
            complexity += 1
        if "Kubernetes" in technologies:
            complexity += 2
        if any(tech in technologies for tech in ["TensorFlow", "PyTorch"]):
            complexity += 2
        if "React" in technologies and "Node.js" in technologies:
            complexity += 1

        return min(complexity, 5)

    def _detect_patterns(self, cwd: Path, technologies: List[str]) -> List[str]:
        """Detect common architectural patterns."""
        patterns = []

        structure_dirs = [f.name for f in cwd.iterdir() if f.is_dir()]

        # Common patterns
        if "models" in structure_dirs and "views" in structure_dirs:
            patterns.append("mvc")
        if "components" in structure_dirs:
            patterns.append("component_based")
        if "api" in structure_dirs and "frontend" in structure_dirs:
            patterns.append("api_frontend_separation")
        if "tests" in structure_dirs or "test" in structure_dirs:
            patterns.append("test_driven")
        if "docker-compose.yml" in [f.name for f in cwd.glob("*")]:
            patterns.append("containerized")
        if any("microservice" in d for d in structure_dirs):
            patterns.append("microservices")

        return patterns
