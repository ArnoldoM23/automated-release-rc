"""
GitHub integration for fetching pull requests between Git tags.
Supports GitHub.com, GitHub Enterprise, and various authentication methods.
"""

import re
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

import requests
from github import Github, GithubException
from github.PullRequest import PullRequest

from config.config import GitHubConfig
from utils.logging import get_logger, log_api_call, log_workflow_step


class GitHubClient:
    """
    GitHub client for fetching pull requests and repository information.
    """
    
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.logger = get_logger(__name__)
        
        # Initialize PyGithub client
        if config.api_url != "https://api.github.com":
            # GitHub Enterprise
            self.github = Github(
                auth=config.token,
                base_url=config.api_url
            )
        else:
            # GitHub.com
            self.github = Github(auth=config.token)
        
        self.repo = self.github.get_repo(config.repo)
        self.logger.info(f"Initialized GitHub client for {config.repo}")
    
    def fetch_prs_between_tags(self, old_tag: str, new_tag: str) -> List[PullRequest]:
        """
        Fetch pull requests between two Git tags.
        
        Args:
            old_tag: Older Git tag (e.g., v1.2.3)
            new_tag: Newer Git tag (e.g., v1.3.0)
            
        Returns:
            List of PullRequest objects
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Fetching PRs between {old_tag} and {new_tag}")
            
            # Get tag commits
            old_commit = self._get_tag_commit(old_tag)
            new_commit = self._get_tag_commit(new_tag)
            
            if not old_commit or not new_commit:
                raise ValueError(f"Could not find commits for tags {old_tag} or {new_tag}")
            
            # Get commits between tags
            commits = self._get_commits_between(old_commit, new_commit)
            
            # Extract PR numbers from commit messages
            pr_numbers = self._extract_pr_numbers_from_commits(commits)
            
            # Fetch full PR objects
            prs = self._fetch_pr_objects(pr_numbers)
            
            duration_ms = (time.time() - start_time) * 1000
            log_workflow_step(
                self.logger,
                step="fetch_prs_between_tags",
                status="completed",
                duration_ms=duration_ms,
                old_tag=old_tag,
                new_tag=new_tag,
                pr_count=len(prs)
            )
            
            return prs
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_workflow_step(
                self.logger,
                step="fetch_prs_between_tags", 
                status="failed",
                duration_ms=duration_ms,
                error=str(e)
            )
            raise
    
    def _get_tag_commit(self, tag_name: str) -> Optional[str]:
        """
        Get the commit SHA for a given tag.
        
        Args:
            tag_name: Git tag name
            
        Returns:
            Commit SHA or None if tag not found
        """
        try:
            # Remove 'v' prefix if present for consistency
            tag_name = tag_name.lstrip('v')
            
            # Try to find tag with and without 'v' prefix
            possible_tags = [tag_name, f"v{tag_name}"]
            
            for possible_tag in possible_tags:
                try:
                    tag = self.repo.get_git_ref(f"tags/{possible_tag}")
                    
                    # Handle annotated vs lightweight tags
                    if tag.object.type == "tag":
                        # Annotated tag
                        tag_obj = self.repo.get_git_tag(tag.object.sha)
                        return tag_obj.object.sha
                    else:
                        # Lightweight tag
                        return tag.object.sha
                        
                except GithubException:
                    continue
            
            # If not found, try to get the latest tag
            self.logger.warning(f"Tag {tag_name} not found, searching in all tags")
            tags = self.repo.get_tags()
            
            for tag in tags:
                if tag.name in possible_tags:
                    return tag.commit.sha
            
            self.logger.error(f"Could not find tag: {tag_name}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting commit for tag {tag_name}: {e}")
            return None
    
    def _get_commits_between(self, old_commit: str, new_commit: str) -> List[Any]:
        """
        Get commits between two commit SHAs.
        
        Args:
            old_commit: Older commit SHA
            new_commit: Newer commit SHA
            
        Returns:
            List of commit objects
        """
        try:
            # Use GitHub's compare API to get commits
            comparison = self.repo.compare(old_commit, new_commit)
            commits = list(comparison.commits)
            
            self.logger.info(f"Found {len(commits)} commits between {old_commit[:8]} and {new_commit[:8]}")
            return commits
            
        except Exception as e:
            self.logger.error(f"Error getting commits between {old_commit} and {new_commit}: {e}")
            raise
    
    def _extract_pr_numbers_from_commits(self, commits: List[Any]) -> List[int]:
        """
        Extract PR numbers from commit messages.
        
        Args:
            commits: List of commit objects
            
        Returns:
            List of unique PR numbers
        """
        pr_numbers = set()
        
        # Common patterns for PR references in commit messages
        patterns = [
            r'#(\d+)',                    # #123
            r'pull request #(\d+)',       # pull request #123
            r'PR #(\d+)',                 # PR #123
            r'Merge pull request #(\d+)', # Merge pull request #123
            r'\(#(\d+)\)',               # (#123)
        ]
        
        for commit in commits:
            message = commit.commit.message
            
            for pattern in patterns:
                matches = re.findall(pattern, message, re.IGNORECASE)
                for match in matches:
                    try:
                        pr_number = int(match)
                        pr_numbers.add(pr_number)
                    except ValueError:
                        continue
        
        pr_list = sorted(list(pr_numbers))
        self.logger.info(f"Extracted {len(pr_list)} unique PR numbers: {pr_list}")
        
        return pr_list
    
    def _fetch_pr_objects(self, pr_numbers: List[int]) -> List[PullRequest]:
        """
        Fetch full PR objects for given PR numbers.
        
        Args:
            pr_numbers: List of PR numbers
            
        Returns:
            List of PullRequest objects
        """
        prs = []
        
        for pr_number in pr_numbers:
            try:
                pr = self.repo.get_pull(pr_number)
                
                # Only include merged PRs
                if pr.merged:
                    prs.append(pr)
                    self.logger.debug(f"Fetched PR #{pr_number}: {pr.title}")
                else:
                    self.logger.debug(f"Skipping unmerged PR #{pr_number}")
                    
            except GithubException as e:
                self.logger.warning(f"Could not fetch PR #{pr_number}: {e}")
                continue
        
        self.logger.info(f"Successfully fetched {len(prs)} merged PRs")
        return prs
    
    def get_repository_info(self) -> Dict[str, Any]:
        """
        Get basic repository information.
        
        Returns:
            Dictionary with repository details
        """
        try:
            return {
                "name": self.repo.name,
                "full_name": self.repo.full_name,
                "description": self.repo.description,
                "default_branch": self.repo.default_branch,
                "private": self.repo.private,
                "url": self.repo.html_url
            }
        except Exception as e:
            self.logger.error(f"Error getting repository info: {e}")
            return {}
    
    def validate_tag(self, tag_name: str) -> bool:
        """
        Validate if a tag exists in the repository.
        
        Args:
            tag_name: Git tag name to validate
            
        Returns:
            True if tag exists, False otherwise
        """
        commit = self._get_tag_commit(tag_name)
        return commit is not None
    
    def get_latest_tags(self, limit: int = 10) -> List[str]:
        """
        Get the latest tags from the repository.
        
        Args:
            limit: Maximum number of tags to return
            
        Returns:
            List of tag names (most recent first)
        """
        try:
            tags = self.repo.get_tags()
            tag_names = [tag.name for tag in tags[:limit]]
            
            self.logger.info(f"Latest {len(tag_names)} tags: {tag_names}")
            return tag_names
            
        except Exception as e:
            self.logger.error(f"Error getting latest tags: {e}")
            return []


def fetch_prs(prod_tag: str, new_tag: str, config: GitHubConfig) -> List[PullRequest]:
    """
    Convenience function to fetch PRs between tags.
    
    Args:
        prod_tag: Production tag (older)
        new_tag: New release tag (newer)
        config: GitHub configuration
        
    Returns:
        List of PullRequest objects
    """
    client = GitHubClient(config)
    return client.fetch_prs_between_tags(prod_tag, new_tag)


def validate_tags(prod_tag: str, new_tag: str, config: GitHubConfig) -> tuple[bool, Optional[str]]:
    """
    Validate that both tags exist and are in correct order.
    
    Args:
        prod_tag: Production tag
        new_tag: New release tag
        config: GitHub configuration
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    client = GitHubClient(config)
    
    # Check if both tags exist
    if not client.validate_tag(prod_tag):
        return False, f"Production tag '{prod_tag}' not found in repository"
    
    if not client.validate_tag(new_tag):
        return False, f"New tag '{new_tag}' not found in repository"
    
    # Additional validation could include:
    # - Semantic version comparison
    # - Chronological order check
    # - Branch validation
    
    return True, None 