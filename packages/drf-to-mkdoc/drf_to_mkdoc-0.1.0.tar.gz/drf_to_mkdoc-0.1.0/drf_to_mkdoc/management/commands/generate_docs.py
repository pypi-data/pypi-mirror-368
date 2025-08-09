#!/usr/bin/env python3

from pathlib import Path

from django.core.management.base import BaseCommand

from drf_to_mkdoc.utils.common import get_schema, load_model_json_data
from drf_to_mkdoc.utils.endpoint_generator import (
    create_endpoints_index,
    generate_endpoint_files,
    parse_endpoints_from_schema,
)
from drf_to_mkdoc.utils.model_generator import create_models_index, generate_model_docs
from drf_to_mkdoc.conf.settings import drf_to_mkdoc_settings



class Command(BaseCommand):
    help = "Generate complete API documentation (models + endpoints + navigation)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--endpoints-only",
            action="store_true",
            help="Generate only endpoint documentation",
        )
        parser.add_argument(
            "--models-only",
            action="store_true",
            help="Generate only model documentation",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Starting documentation generation..."))

        docs_dir = Path(drf_to_mkdoc_settings.DOCS_DIR)
        docs_dir.mkdir(parents=True, exist_ok=True)

        if options["models_only"]:
            self._generate_models_only()
        elif options["endpoints_only"]:
            self._generate_endpoints_only()
        else:
            self._generate_all()

        self.stdout.write(self.style.SUCCESS("✅ Documentation generation complete!"))

    def _generate_models_only(self):
        """Generate only model documentation"""
        self.stdout.write("📋 Generating model documentation...")

        # Load model data
        json_data = load_model_json_data()
        models_data = json_data.get("models", {}) if json_data else {}

        if not models_data:
            self.stdout.write(self.style.WARNING("⚠️  No model data found"))
            return

        docs_dir = Path(drf_to_mkdoc_settings.DOCS_DIR)

        # Generate model documentation
        generate_model_docs(models_data, docs_dir)
        create_models_index(models_data, docs_dir)

        self.stdout.write(self.style.SUCCESS("✅ Model documentation generated"))

    def _generate_endpoints_only(self):
        """Generate only endpoint documentation"""
        self.stdout.write("🔗 Generating endpoint documentation...")

        # Load schema
        schema = get_schema()
        if not schema:
            self.stdout.write(self.style.ERROR("❌ Failed to load OpenAPI schema"))
            return

        paths = schema.get("paths", {})
        components = schema.get("components", {})

        self.stdout.write(f"📊 Loaded {len(paths)} API paths")

        docs_dir = Path(drf_to_mkdoc_settings.DOCS_DIR)

        # Parse and generate endpoints
        endpoints_by_app = parse_endpoints_from_schema(paths)
        total_endpoints = generate_endpoint_files(endpoints_by_app, components)
        create_endpoints_index(endpoints_by_app, docs_dir)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Generated {total_endpoints} endpoint files with Django view introspection"
            )
        )

    def _generate_all(self):
        """Generate complete documentation"""
        self.stdout.write("📚 Generating complete documentation...")

        docs_dir = Path(drf_to_mkdoc_settings.DOCS_DIR)

        # Load data
        json_data = load_model_json_data()
        models_data = json_data.get("models", {}) if json_data else {}
        schema = get_schema()

        if not schema:
            self.stdout.write(self.style.ERROR("❌ Failed to load OpenAPI schema"))
            return

        paths = schema.get("paths", {})
        components = schema.get("components", {})

        self.stdout.write(f"📊 Loaded {len(paths)} API paths")

        # Generate model documentation
        if models_data:
            self.stdout.write("📋 Generating model documentation...")
            try:
                generate_model_docs(models_data)
                create_models_index(models_data, docs_dir)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Failed to generate model docs: {e}"))
                self.stdout.write(self.style.WARNING("Continuing with endpoint generation..."))
        else:
            self.stdout.write(self.style.WARNING("⚠️  No model data found"))

        # Generate endpoint documentation
        self.stdout.write("🔗 Generating endpoint documentation...")
        endpoints_by_app = parse_endpoints_from_schema(paths)
        total_endpoints = generate_endpoint_files(endpoints_by_app, components)
        create_endpoints_index(endpoints_by_app, docs_dir)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Generated {total_endpoints} endpoint files with Django view introspection"
            )
        )
