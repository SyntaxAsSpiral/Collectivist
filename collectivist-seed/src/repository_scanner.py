#!/usr/bin/env python3
"""
Repository Scanner Plugin
Scans directory containing git repositories, extracts metadata + git status
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import sys
import os

from plugin_interface import CollectionScanner, CollectionItem, PluginRegistry


class RepositoryScanner(CollectionScanner):
    """Scanner for collections of git repositories"""

    def get_name(self) -> str:
        return "repositories"

    def get_supported_types(self) -> List[str]:
        return ["dir"]

    def get_categories(self) -> List[str]:
        return [
            'phext_hyperdimensional',
            'ai_llm_agents',
            'terminal_ui',
            'creative_aesthetic',
            'dev_tools',
            'esoteric_experimental',
            'system_infrastructure',
            'utilities_misc'
        ]

    def detect(self, path: Path) -> bool:
        """
        Detect if this path contains repositories.
        Heuristic: if >50% of subdirectories are git repos, it's a repository collection.
        """
        if not path.is_dir():
            return False

        subdirs = [d for d in path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        if len(subdirs) == 0:
            return False

        git_repos = sum(1 for d in subdirs if (d / '.git').exists())
        return git_repos / len(subdirs) >= 0.5

    def check_git_status(self, repo_path: Path) -> Dict[str, Any]:
        """
        Check git status for a repository.
        Returns dict with git_status and git_error fields.
        """
        git_dir = repo_path / '.git'

        # Not a git repo
        if not git_dir.exists():
            return {'git_status': 'not_a_repo', 'git_error': None}

        # Check for remote
        try:
            subprocess.run(
                ['git', '-C', str(repo_path), 'config', '--get', 'remote.origin.url'],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError:
            return {'git_status': 'no_remote', 'git_error': None}

        # Check upstream tracking
        try:
            subprocess.run(
                ['git', '-C', str(repo_path), 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError:
            return {'git_status': 'error', 'git_error': 'no upstream configured'}

        # Fetch latest remote state
        try:
            subprocess.run(
                ['git', '-C', str(repo_path), 'fetch', '--quiet'],
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            return {'git_status': 'error', 'git_error': 'fetch failed'}

        # Count commits behind
        try:
            result = subprocess.run(
                ['git', '-C', str(repo_path), 'rev-list', 'HEAD..@{u}', '--count'],
                check=True,
                capture_output=True,
                text=True
            )
            commits_behind = int(result.stdout.strip())

            if commits_behind > 0:
                return {'git_status': 'updates_available', 'git_error': None}
            else:
                return {'git_status': 'up_to_date', 'git_error': None}

        except (subprocess.CalledProcessError, ValueError) as e:
            return {'git_status': 'error', 'git_error': str(e)}

    def get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except (PermissionError, OSError):
            pass
        return total

    def scan(self, root_path: Path, config: Dict[str, Any]) -> List[CollectionItem]:
        """
        Scan repository collection.

        Config options:
        - exclude_hidden: bool (default True) - exclude directories starting with '.'
        - preserve_data: dict - existing descriptions/categories to preserve
        - always_pull: dict - repos to auto-pull when updates available
        """
        exclude_hidden = config.get('exclude_hidden', True)
        preserve_data = config.get('preserve_data', {})
        always_pull_repos = config.get('always_pull', {})

        items = []

        # Get all subdirectories
        subdirs = [d for d in root_path.iterdir() if d.is_dir()]

        # Filter hidden if configured
        if exclude_hidden:
            subdirs = [d for d in subdirs if not d.name.startswith('.')]

        for repo_dir in subdirs:
            # Get filesystem metadata
            stat = repo_dir.stat()

            # Check git status
            git_info = self.check_git_status(repo_dir)

            # Auto-pull if configured and updates available
            should_pull = always_pull_repos.get(repo_dir.name, False)
            if should_pull and git_info['git_status'] == 'updates_available':
                try:
                    subprocess.run(
                        ['git', '-C', str(repo_dir), 'pull', '--quiet'],
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    git_info = {'git_status': 'up_to_date', 'git_error': None}
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    git_info = {'git_status': 'error', 'git_error': 'pull failed'}

            # Get size (expensive operation, may want to cache)
            size = self.get_directory_size(repo_dir)

            # Preserve existing description/category if available
            existing = preserve_data.get(str(repo_dir), {})

            # Create item
            item = CollectionItem(
                short_name=repo_dir.name,
                type="dir",
                size=size,
                created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                accessed=datetime.fromtimestamp(stat.st_atime).isoformat(),
                path=str(repo_dir),
                description=existing.get('description'),
                category=existing.get('category'),
                metadata={
                    'git_status': git_info['git_status'],
                    'git_error': git_info['git_error'],
                    'always_pull': always_pull_repos.get(repo_dir.name, False),
                    'readonly': not os.access(repo_dir, os.W_OK)
                }
            )

            items.append(item)

        # Sort by size descending (matches original behavior)
        items.sort(key=lambda x: x.size, reverse=True)

        return items

    def get_description_prompt_template(self) -> str:
        return """You are a technical documentation assistant. Generate a one-sentence description and category for a software repository based on its README.

Available categories (choose ONE):
- phext_hyperdimensional: Phext, hyperdimensional text, multi-dimensional coordinate systems
- ai_llm_agents: AI agents, LLMs, machine learning infrastructure, agent frameworks
- terminal_ui: Terminal UI frameworks, TUI components, CLI styling libraries
- creative_aesthetic: Music, art, visualization, color schemes, aesthetic tools
- dev_tools: Development utilities, scaffolding, IDEs, build tools
- esoteric_experimental: Esoteric programming, experimental projects, occult/mystical systems
- system_infrastructure: System-level tools, SSH, networking, infrastructure
- utilities_misc: General utilities, miscellaneous tools

README content:
---
{content}
---

Generate a JSON response with:
1. "description": A single-sentence description (max 150 characters) that captures the repository's core purpose. Be concise and technical. Do not include 'This is' or 'A repository for'. Start directly with the purpose.
2. "category": ONE category from the list above that best matches this repository.

Example format:
{{"description": "Advanced task management system with Obsidian integration and MCP server", "category": "dev_tools"}}

JSON Response:"""

    def get_example_descriptions(self) -> List[str]:
        return [
            "Nushell-based SSH launcher with FZF selection and session management",
            "CLI tool for batch file operations with pattern matching and preview",
            "Terminal UI framework with component composition and reactive state",
            "AI agent system with multi-model orchestration and tool integration",
            "Hyperdimensional coordinate system for multi-dimensional text navigation"
        ]

    def get_content_for_description(self, item: CollectionItem) -> str:
        """
        Extract README content for LLM description generation.
        Returns first 3000 chars of README.
        """
        repo_path = Path(item.path)
        readme_patterns = ['README.md', 'readme.md', 'README', 'Readme.md']

        for pattern in readme_patterns:
            readme_path = repo_path / pattern
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()[:3000]
                except Exception:
                    continue

        return ""


# Register plugin on import
PluginRegistry.register(
    name="repositories",
    scanner_class=RepositoryScanner,
    version="1.0.0",
    description="Scanner for git repository collections"
)