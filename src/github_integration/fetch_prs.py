"""
GitHub integration for fetching pull requests between Git references.
Supports GitHub.com, GitHub Enterprise, and various authentication methods.
Can use Git tags (v1.2.3) or commit SHAs (abc123f) as references.
"""

import re
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

import requests
from github import Github, GithubException
from github.PullRequest import PullRequest

from src.config.config import GitHubConfig
from src.utils.logging import get_logger, log_api_call, log_workflow_step


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
                login_or_token=config.token,
                base_url=config.api_url
            )
        else:
            # GitHub.com
            self.github = Github(login_or_token=config.token)
        
        self.repo = self.github.get_repo(config.repo)
        self.logger.info(f"Initialized GitHub client for {config.repo}")
    
    def fetch_prs_between_refs(self, old_ref: str, new_ref: str) -> List[PullRequest]:
        """
        Fetch pull requests between two Git references (tags or commit SHAs).
        
        Args:
            old_ref: Older Git reference (tag like v1.2.3 or commit SHA like abc123f)
            new_ref: Newer Git reference (tag like v1.3.0 or commit SHA like def456a)
            
        Returns:
            List of PullRequest objects
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Fetching PRs between {old_ref} and {new_ref}")
            
            # Get commit SHAs from references (tags or commit SHAs)
            old_commit = self._get_commit_sha(old_ref)
            new_commit = self._get_commit_sha(new_ref)
            
            if not old_commit or not new_commit:
                raise ValueError(f"Could not find commits for references {old_ref} or {new_ref}")
            
            # Get commits between references
            commits = self._get_commits_between(old_commit, new_commit)
            
            # Extract PR numbers from commit messages
            pr_numbers = self._extract_pr_numbers_from_commits(commits)
            
            # Fetch full PR objects
            prs = self._fetch_pr_objects(pr_numbers)
            
            duration_ms = (time.time() - start_time) * 1000
            log_workflow_step(
                self.logger,
                step="fetch_prs_between_refs",
                status="completed",
                duration_ms=duration_ms,
                old_ref=old_ref,
                new_ref=new_ref,
                pr_count=len(prs)
            )
            
            return prs
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_workflow_step(
                self.logger,
                step="fetch_prs_between_refs", 
                status="failed",
                duration_ms=duration_ms,
                error=str(e)
            )
            raise
    
    def _get_commit_sha(self, ref: str) -> Optional[str]:
        """
        Get the commit SHA for a given reference (tag or commit SHA).
        
        Args:
            ref: Git tag name or commit SHA (short or full)
            
        Returns:
            Full commit SHA or None if not found
        """
        try:
            # Check if it's already a commit SHA (7-40 characters, alphanumeric)
            if re.match(r'^[a-f0-9]{7,40}$', ref.lower()):
                try:
                    # Try to get the commit directly
                    commit = self.repo.get_commit(ref)
                    self.logger.info(f"Found commit SHA: {ref} -> {commit.sha}")
                    return commit.sha
                except GithubException as e:
                    self.logger.warning(f"Commit SHA {ref} not found: {e}")
                    return None
            
            # Otherwise, treat as a tag
            # Remove 'v' prefix if present for consistency
            tag_name = ref.lstrip('v')
            
            # Try to find tag with and without 'v' prefix
            possible_tags = [tag_name, f"v{tag_name}"]
            
            for possible_tag in possible_tags:
                try:
                    tag = self.repo.get_git_ref(f"tags/{possible_tag}")
                    
                    # Handle annotated vs lightweight tags
                    if tag.object.type == "tag":
                        # Annotated tag
                        tag_obj = self.repo.get_git_tag(tag.object.sha)
                        self.logger.info(f"Found annotated tag: {possible_tag} -> {tag_obj.object.sha}")
                        return tag_obj.object.sha
                    else:
                        # Lightweight tag
                        self.logger.info(f"Found lightweight tag: {possible_tag} -> {tag.object.sha}")
                        return tag.object.sha
                        
                except GithubException:
                    continue
            
            # If not found, try to search in all tags
            self.logger.warning(f"Tag {ref} not found, searching in all tags")
            tags = self.repo.get_tags()
            
            for tag in tags:
                if tag.name in possible_tags:
                    self.logger.info(f"Found tag in search: {tag.name} -> {tag.commit.sha}")
                    return tag.commit.sha
            
            self.logger.error(f"Could not find tag or commit: {ref}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting commit for reference {ref}: {e}")
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
                    # Enhance PR object with additional user info
                    self._enhance_pr_user_info(pr)
                    prs.append(pr)
                    self.logger.debug(f"Fetched PR #{pr_number}: {pr.title}")
                else:
                    self.logger.debug(f"Skipping unmerged PR #{pr_number}")
                    
            except GithubException as e:
                self.logger.warning(f"Could not fetch PR #{pr_number}: {e}")
                continue
        
        self.logger.info(f"Successfully fetched {len(prs)} merged PRs")
        return prs
    
    def _enhance_pr_user_info(self, pr: PullRequest):
        """
        Enhance PR object with additional user information including full name.
        
        Args:
            pr: PullRequest object to enhance
        """
        try:
            # Get full user details
            user = pr.user
            if user:
                # Try to get full name from user profile
                user_details = self.github.get_user(user.login)
                
                # Add enhanced user info to the PR object
                if not hasattr(pr.user, 'display_name'):
                    pr.user.display_name = self._format_user_display_name(user_details)
                if not hasattr(pr.user, 'full_name'):
                    pr.user.full_name = user_details.name or user.login
                    
                self.logger.debug(f"Enhanced user info for {user.login}: {pr.user.display_name}")
                
        except Exception as e:
            self.logger.debug(f"Could not enhance user info for PR #{pr.number}: {e}")
            # Set fallback values
            if not hasattr(pr.user, 'display_name'):
                pr.user.display_name = f"@{pr.user.login}"
            if not hasattr(pr.user, 'full_name'):
                pr.user.full_name = pr.user.login
    
    def _format_user_display_name(self, user) -> str:
        """
        Format user display name as "Full Name (@username)" or fallback to "@username".
        
        Args:
            user: GitHub User object
            
        Returns:
            Formatted display name
        """
        try:
            full_name = user.name
            username = user.login
            
            if full_name and full_name.strip():
                return f"{full_name} (@{username})"
            else:
                return f"@{username}"
        except Exception:
            return f"@{user.login}"
    
    def get_user_display_name(self, username: str) -> str:
        """
        Get enhanced display name for a GitHub user.
        
        Args:
            username: GitHub username
            
        Returns:
            Formatted display name "Full Name (@username)" or "@username"
        """
        try:
            user = self.github.get_user(username)
            return self._format_user_display_name(user)
        except Exception as e:
            self.logger.debug(f"Could not fetch user details for {username}: {e}")
            return f"@{username}"
    
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
    
    def validate_ref(self, ref: str) -> bool:
        """
        Validate if a reference (tag or commit SHA) exists in the repository.
        
        Args:
            ref: Git tag name or commit SHA to validate
            
        Returns:
            True if reference exists, False otherwise
        """
        commit = self._get_commit_sha(ref)
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


def fetch_prs(prod_ref: str, new_ref: str, config: GitHubConfig) -> List[PullRequest]:
    """
    Convenience function to fetch PRs between Git references (tags or commit SHAs).
    
    Args:
        prod_ref: Production reference (older tag or commit SHA)
        new_ref: New release reference (newer tag or commit SHA)
        config: GitHub configuration
        
    Returns:
        List of PullRequest objects
    """
    client = GitHubClient(config)
    return client.fetch_prs_between_refs(prod_ref, new_ref)


def validate_refs(prod_ref: str, new_ref: str, config: GitHubConfig) -> tuple[bool, Optional[str]]:
    """
    Validate that both references (tags or commit SHAs) exist and are accessible.
    
    Args:
        prod_ref: Production reference (tag or commit SHA)
        new_ref: New release reference (tag or commit SHA)
        config: GitHub configuration
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    client = GitHubClient(config)
    
    # Check if both references exist
    if not client.validate_ref(prod_ref):
        return False, f"Production reference '{prod_ref}' not found in repository"
    
    if not client.validate_ref(new_ref):
        return False, f"New reference '{new_ref}' not found in repository"
    
    # Additional validation could include:
    # - Semantic version comparison
    # - Chronological order check
    # - Branch validation
    
    return True, None 