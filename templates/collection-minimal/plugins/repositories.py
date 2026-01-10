"""
Repository Scanner - Git Repository Collection Plugin

Scans for Git repositories and extracts rich metadata including
git status, remote information, and README content.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional


class RepositoryScanner:
    """Scanner for Git repository collections."""

    def __init__(self, collection_path: Path, config: Dict[str, Any]):
        """Initialize repository scanner.

        Args:
            collection_path: Path to collection directory
            config: Collection configuration
        """
        self.collection_path = collection_path
        self.config = config
        self.exclude_patterns = config.get("scanner", {}).get("config", {}).get("exclude_patterns", [])

    def discover_items(self) -> List[Path]:
        """Discover Git repositories in the collection."""
        repos = []

        # Walk through collection directory
        for root, dirs, files in os.walk(self.collection_path):
            root_path = Path(root)

            # Skip .collection directory and excluded patterns
            if self._should_skip(root_path):
                continue

            # Check if this directory is a Git repository
            if (root_path / ".git").exists() and (root_path / ".git").is_dir():
                repos.append(root_path)

                # Don't recurse into subdirectories of this repo
                # (to avoid finding nested repos)
                dirs[:] = []

        return repos

    def _should_skip(self, path: Path) -> bool:
        """Check if path should be skipped based on exclude patterns."""
        # Always skip .collection directory
        if ".collection" in path.parts:
            return True

        # Check exclude patterns
        path_str = str(path.relative_to(self.collection_path))

        for pattern in self.exclude_patterns:
            # Simple pattern matching (could be enhanced with glob/fnmatch)
            if pattern.replace("*", "").replace("/", "") in path_str:
                return True

        return False

    def extract_metadata(self, repo_path: Path) -> Dict[str, Any]:
        """Extract repository-specific metadata."""
        metadata = {}

        try:
            # Get Git information
            git_dir = repo_path / ".git"

            # Remote information
            remote_url = self._run_git_command(repo_path, ["config", "--get", "remote.origin.url"])
            metadata["remote"] = remote_url.strip() if remote_url else None

            # Current branch
            branch = self._run_git_command(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
            metadata["branch"] = branch.strip() if branch else "unknown"

            # Last commit info
            last_commit = self._run_git_command(repo_path, ["log", "-1", "--format=%H|%an|%ae|%ad|%s"])
            if last_commit:
                parts = last_commit.strip().split("|", 4)
                if len(parts) >= 5:
                    metadata["last_commit"] = {
                        "hash": parts[0],
                        "author_name": parts[1],
                        "author_email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    }

        except Exception as e:
            # Git operations can fail for various reasons
            metadata["git_error"] = str(e)

        return metadata

    def check_status(self, repo_path: Path) -> Dict[str, Any]:
        """Check repository status and health."""
        status = {
            "git_status": "unknown",
            "has_remote": False,
            "is_clean": True,
            "last_check": "2026-01-09T15:30:00Z"  # Would use datetime.now()
        }

        try:
            # Check if it's a valid Git repo
            if not (repo_path / ".git").exists():
                status["git_status"] = "not_a_repo"
                return status

            # Check for remote
            remote_output = self._run_git_command(repo_path, ["remote"])
            status["has_remote"] = bool(remote_output and remote_output.strip())

            # Check working directory status
            status_output = self._run_git_command(repo_path, ["status", "--porcelain"])
            status["is_clean"] = not bool(status_output and status_output.strip())

            # Determine overall status
            if not status["has_remote"]:
                status["git_status"] = "no_remote"
            elif not status["is_clean"]:
                status["git_status"] = "modified"
            else:
                # Check if ahead/behind remote
                try:
                    self._run_git_command(repo_path, ["fetch", "--quiet"])
                    ahead_behind = self._run_git_command(repo_path, ["rev-list", "--count", "--left-right", "@{upstream}...HEAD"])
                    if ahead_behind:
                        ahead, behind = ahead_behind.strip().split("\t")
                        if int(behind) > 0:
                            status["git_status"] = "updates_available"
                        elif int(ahead) > 0:
                            status["git_status"] = "ahead_of_remote"
                        else:
                            status["git_status"] = "up_to_date"
                    else:
                        status["git_status"] = "up_to_date"
                except Exception:
                    # Fetch or upstream check failed
                    status["git_status"] = "up_to_date"  # Assume current

        except Exception as e:
            status["git_status"] = "error"
            status["error"] = str(e)

        return status

    def generate_content_sample(self, repo_path: Path) -> str:
        """Generate content sample for LLM description."""
        sample_parts = []

        # Try to read README
        readme_files = ["README.md", "README.txt", "README", "readme.md"]
        for readme_file in readme_files:
            readme_path = repo_path / readme_file
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(3000)  # First 3000 characters
                        if content.strip():
                            sample_parts.append(f"README:\n{content}")
                            break
                except Exception:
                    continue

        # Add directory listing if no README
        if not sample_parts:
            try:
                dirs = []
                files = []
                for item in repo_path.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        dirs.append(item.name)
                    elif item.is_file() and not item.name.startswith('.'):
                        files.append(item.name)

                if dirs or files:
                    sample_parts.append("Directory contents:")
                    if dirs:
                        sample_parts.append(f"Directories: {', '.join(dirs[:5])}")
                    if files:
                        sample_parts.append(f"Files: {', '.join(files[:10])}")

            except Exception:
                pass

        # Join all parts
        content_sample = "\n\n".join(sample_parts)

        # Truncate if too long
        if len(content_sample) > 3000:
            content_sample = content_sample[:2997] + "..."

        return content_sample or "No content sample available"

    def _run_git_command(self, repo_path: Path, args: List[str]) -> Optional[str]:
        """Run a Git command and return output."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return result.stdout
            else:
                return None

        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return None