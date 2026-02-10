"""Enterprise tier domain-based workspace organization.

Implements domain detection and inference for Enterprise workspaces.
"""

from typing import Optional, Dict


def get_enterprise_domain(name: str, template_files: Optional[Dict] = None) -> str:
    """Determine enterprise domain for data organization.

    Common domains: core, ml, data, api, analytics

    Args:
        name: Workspace project name
        template_files: Optional template metadata with explicit domain

    Returns:
        Domain name for directory structure (e.g., "ml", "data", "core")

    Examples:
        >>> get_enterprise_domain("ml-pipeline")
        'ml'
        >>> get_enterprise_domain("customer-api")
        'api'
        >>> get_enterprise_domain("my-project")
        'core'
    """
    # Check template for explicit domain
    if template_files and "domain" in template_files:
        return template_files["domain"]

    # Infer from project name
    name_lower = name.lower()
    domain_keywords = {
        "ml": ["ml", "machine-learning", "ai", "model", "training"],
        "data": ["data", "etl", "pipeline", "warehouse"],
        "api": ["api", "service", "gateway", "rest", "graphql"],
        "analytics": ["analytics", "reporting", "dashboard", "bi"],
    }

    for domain, keywords in domain_keywords.items():
        if any(kw in name_lower for kw in keywords):
            return domain

    return "core"  # default
