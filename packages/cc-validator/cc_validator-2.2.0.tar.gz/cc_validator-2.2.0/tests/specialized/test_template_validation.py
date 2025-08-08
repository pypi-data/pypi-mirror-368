#!/usr/bin/env python3

import asyncio
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cc_validator.security_validator import SecurityValidator
from cc_validator.file_categorization import FileContextAnalyzer


def test_template_file_detection() -> None:
    """Test that various template files are correctly identified"""
    template_files = [
        "templates/base.html",
        "views/index.htm",
        "layouts/main.jinja2",
        "partials/header.hbs",
        "components/nav.ejs",
        "app.vue",
        "Button.svelte",
        "email.twig",
        "page.liquid",
        "view.erb",
        "template.mustache",
    ]

    for file_path in template_files:
        assert FileContextAnalyzer.is_template_file(
            file_path
        ), f"{file_path} should be detected as template"

        context = FileContextAnalyzer.categorize_file(file_path)
        assert (
            context["category"] == "template"
        ), f"{file_path} should be categorized as template"
        assert not context["requires_strict_security"]
        print(f"✓ {file_path} correctly identified as template")


def test_non_template_files() -> None:
    """Test that non-template files are not misidentified"""
    non_template_files = [
        "main.py",
        "app.js",
        "config.json",
        "README.md",
        "data.sql",
    ]

    for file_path in non_template_files:
        assert not FileContextAnalyzer.is_template_file(
            file_path
        ), f"{file_path} should NOT be a template"

        context = FileContextAnalyzer.categorize_file(file_path)
        assert (
            context["category"] != "template"
        ), f"{file_path} should NOT be categorized as template"
        print(f"✓ {file_path} correctly NOT identified as template")


def test_template_validation_with_strict_disabled() -> None:
    """Test that templates are allowed when STRICT_TEMPLATE_VALIDATION is False"""
    validator = SecurityValidator()

    # HTML template with external resources (should be allowed)
    html_content = """<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto">
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
    <style>
        body { font-family: 'Roboto', sans-serif; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <div>{{ content }}</div>
</body>
</html>"""

    tool_input = {"file_path": "templates/base.html", "content": html_content}

    # With STRICT_TEMPLATE_VALIDATION = False (default), this should be approved
    result = asyncio.run(validator.validate("Write", tool_input, ""))

    assert result[
        "approved"
    ], f"Template should be approved but got: {result.get('reason')}"
    print("✓ HTML template with external resources correctly approved")


def test_template_validation_blocks_critical_secrets() -> None:
    """Test that templates with real secrets are still blocked"""
    validator = SecurityValidator()

    # Template with real AWS key
    template_with_secret = """<html>
<body>
    <script>
        const AWS_KEY = 'AKIAIOSFODNN7EXAMPLE';
        const STRIPE_KEY = 'sk_live_4eC39HqLyjWDarjtT1zdp7dc';
    </script>
</body>
</html>"""

    tool_input = {"file_path": "templates/config.html", "content": template_with_secret}

    result = asyncio.run(validator.validate("Write", tool_input, ""))

    assert not result["approved"], "Template with real secrets should be blocked"
    assert (
        "AWS access key" in result["reason"] or "Stripe live secret" in result["reason"]
    )
    print("✓ Template with real secrets correctly blocked")


def test_template_xss_detection_with_strict_enabled() -> None:
    """Test XSS detection in templates when strict validation is enabled"""
    # Mock the config to enable strict validation
    with patch("cc_validator.security_validator.STRICT_TEMPLATE_VALIDATION", True):
        validator = SecurityValidator()

        # Template with |safe filter (XSS risk)
        unsafe_template = """<html>
<body>
    <h1>{{ user_input | safe }}</h1>
    <div>{{ content }}</div>
</body>
</html>"""

        tool_input = {"file_path": "templates/unsafe.html", "content": unsafe_template}

        result = asyncio.run(validator.validate("Write", tool_input, ""))

        assert not result[
            "approved"
        ], "Template with |safe filter should be blocked in strict mode"
        assert "Unescaped output" in result["reason"]
        print("✓ Template with |safe filter correctly blocked in strict mode")


def test_template_allows_safe_patterns() -> None:
    """Test that safe template patterns are allowed"""
    validator = SecurityValidator()

    # Safe template with proper escaping
    safe_template = """<!DOCTYPE html>
<html>
<head>
    <title>{{ page_title }}</title>
</head>
<body>
    <h1>{{ heading }}</h1>
    <div class="content">
        {% for item in items %}
            <p>{{ item.name }}</p>
            <span>{{ item.description }}</span>
        {% endfor %}
    </div>
    <footer>
        Copyright {{ current_year }}
    </footer>
</body>
</html>"""

    tool_input = {"file_path": "templates/safe.html", "content": safe_template}

    result = asyncio.run(validator.validate("Write", tool_input, ""))

    assert result[
        "approved"
    ], f"Safe template should be approved but got: {result.get('reason')}"
    print("✓ Safe template with proper escaping correctly approved")


def test_template_file_categorization() -> None:
    """Test that template files are correctly categorized for analysis"""
    # Test that template files get the right category
    template_paths = ["templates/large.html", "views/form.ejs", "layouts/main.hbs"]

    for path in template_paths:
        context = FileContextAnalyzer.categorize_file(path)
        assert (
            context["category"] == "template"
        ), f"{path} should be categorized as template"
        assert not context[
            "requires_strict_security"
        ], f"{path} should not require strict security"

    print("✓ Template files correctly categorized for appropriate analysis")


if __name__ == "__main__":
    print("Testing template validation scenarios...\n")

    test_template_file_detection()
    print()

    test_non_template_files()
    print()

    test_template_validation_with_strict_disabled()
    print()

    test_template_validation_blocks_critical_secrets()
    print()

    test_template_xss_detection_with_strict_enabled()
    print()

    test_template_allows_safe_patterns()
    print()

    test_template_file_categorization()
    print()

    print("\n✅ All template validation tests passed!")
