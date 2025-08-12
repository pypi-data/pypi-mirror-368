# Copyright 2023-2025 Praetorian Security, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Glato - GitLab Attack Toolkit

A library for GitLab enumeration and security testing.
"""

__version__ = "1.0.0b3"

# Core imports for library usage
from .enumerate import Enumerator
from .attack import Attacker
from .gitlab.api import Api
from .models.user import User
from .models.project import Project, ProjectAccess, BranchProtection
from .models.group import Group, GroupAccess
from .models.variable import CICDVariable
from .models.secure_file import SecureFile
from .models.runner import Runner

# Convenience functions for common operations
def create_enumerator(token=None, cookies=None, gitlab_url='https://gitlab.com', 
                     proxy=None, verify_ssl=True, throttle=None):
    """
    Create an Enumerator instance for GitLab enumeration.
    
    Args:
        token: GitLab Personal Access Token
        cookies: Dictionary of cookies for authentication
        gitlab_url: GitLab instance URL (default: https://gitlab.com)
        proxy: HTTP proxy URL
        verify_ssl: Whether to verify SSL certificates
        throttle: Seconds to wait between API requests
        
    Returns:
        Enumerator instance
    """
    return Enumerator(
        token=token,
        cookies=cookies,
        gitlab_url=gitlab_url,
        proxy=proxy,
        verify_ssl=verify_ssl,
        throttle=throttle
    )


def enumerate_token(token=None, cookies=None, gitlab_url='https://gitlab.com'):
    """
    Quick function to enumerate token/cookie permissions and user info.
    
    Args:
        token: GitLab Personal Access Token
        cookies: Dictionary of cookies for authentication
        gitlab_url: GitLab instance URL
        
    Returns:
        Tuple of (user_info: User, scopes: list[str])
    """
    enumerator = create_enumerator(token=token, cookies=cookies, gitlab_url=gitlab_url)
    if enumerator.enumerate_token():
        return enumerator._user_info, enumerator.scopes
    return None, []


def enumerate_all_projects(token=None, cookies=None, gitlab_url='https://gitlab.com',
                          include_secrets=False, include_runners=False,
                          include_archived=False):
    """
    Enumerate all accessible projects.
    
    Args:
        token: GitLab Personal Access Token
        cookies: Dictionary of cookies for authentication  
        gitlab_url: GitLab instance URL
        include_secrets: Whether to enumerate project secrets
        include_runners: Whether to enumerate runners
        include_archived: Whether to include archived projects
        
    Yields:
        Project objects with enumerated data
    """
    enumerator = create_enumerator(token=token, cookies=cookies, gitlab_url=gitlab_url)
    
    # Setup user info first
    if not enumerator.enumerate_token():
        raise RuntimeError("Failed to authenticate with GitLab")
    
    # Enumerate projects
    for project in enumerator.enumerate_projects_v2(
            secrets_enum=include_secrets,
            runners_enum=include_runners,
            include_archived=include_archived):
        yield project


def enumerate_all_groups(token=None, cookies=None, gitlab_url='https://gitlab.com',
                        include_secrets=False):
    """
    Enumerate all accessible groups.
    
    Args:
        token: GitLab Personal Access Token
        cookies: Dictionary of cookies for authentication
        gitlab_url: GitLab instance URL
        include_secrets: Whether to enumerate group secrets
        
    Yields:
        Group objects with enumerated data
    """
    enumerator = create_enumerator(token=token, cookies=cookies, gitlab_url=gitlab_url)
    
    # Setup user info first
    if not enumerator.enumerate_token():
        raise RuntimeError("Failed to authenticate with GitLab")
        
    # Enumerate groups
    for group in enumerator.enumerate_groups(secrets_enum=include_secrets):
        yield group


def get_project_secrets(project_id, token=None, cookies=None, gitlab_url='https://gitlab.com'):
    """
    Get secrets for a specific project.
    
    Args:
        project_id: GitLab project ID
        token: GitLab Personal Access Token
        cookies: Dictionary of cookies for authentication
        gitlab_url: GitLab instance URL
        
    Returns:
        Dict containing variables and secure_files
    """
    from .gitlab.secrets import Secrets
    
    api = Api(pat=token, cookies=cookies, gitlab_url=gitlab_url)
    
    return {
        'variables': Secrets.list_secrets_for_project(project_id, api),
        'secure_files': Secrets.list_secure_files_for_project(project_id, api)
    }


# Export main classes and functions
__all__ = [
    # Core classes
    'Enumerator',
    'Attacker', 
    'Api',
    
    # Model classes
    'User',
    'Project',
    'ProjectAccess',
    'BranchProtection',
    'Group',
    'GroupAccess',
    'CICDVariable',
    'SecureFile',
    'Runner',
    
    # Convenience functions
    'create_enumerator',
    'enumerate_token',
    'enumerate_all_projects',
    'enumerate_all_groups',
    'get_project_secrets',
]
