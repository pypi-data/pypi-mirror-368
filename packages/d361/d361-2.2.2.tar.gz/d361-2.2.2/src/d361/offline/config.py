# this_file: src/d361/offline/config.py

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import AnyHttpUrl, BaseModel, Field, TypeAdapter, computed_field

# Constants
DEFAULT_TIMEOUT = 60  # seconds
DEFAULT_RETRIES = 3
DEFAULT_MAX_CONCURRENT = 5
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
DEFAULT_MAP_URL = TypeAdapter(AnyHttpUrl).validate_python(
    "https://docs.document360.com/sitemap-en.xml"
)


class Config(BaseModel):
    """Configuration model for d361_offline."""

    map_url: AnyHttpUrl | None = Field(
        default=None, description="URL of the sitemap that defines the scope"
    )
    nav_url: AnyHttpUrl | None = Field(
        default=None, description="URL of the page to gather navigation from"
    )
    output_dir: Path = Field(
        default_factory=Path.cwd, description="Output directory for downloaded content"
    )
    css_file: Path | None = Field(
        default=None, description="Path to CSS file for styling"
    )
    effort: bool = Field(
        default=False, description="Try harder to map all sitemap links in navigation"
    )
    max_concurrent: int = Field(
        default=DEFAULT_MAX_CONCURRENT,
        description="Maximum number of concurrent requests",
    )
    retries: int = Field(
        default=DEFAULT_RETRIES,
        description="Number of retry attempts for failed requests",
    )
    timeout: int = Field(
        default=DEFAULT_TIMEOUT, description="Request timeout in seconds"
    )
    verbose: bool = Field(default=False, description="Enable verbose logging")
    test: bool = Field(
        default=False, description="Test mode - only process first 5 items"
    )
    pause: bool = Field(
        default=False, description="Pause during navigation to allow user inspection"
    )

    # Computed field for root_domain
    @computed_field  # type: ignore[prop-decorator]
    @property
    def root_domain(self) -> str:
        """Extracts the root domain from the map_url."""
        if not self.map_url:
            # Or handle as a validation error, or return a default/empty string
            _message = "map_url must be set to determine root_domain"
            raise ValueError(_message)
        url_str = str(self.map_url)
        parsed_url = urlparse(url_str)
        domain = parsed_url.hostname
        if domain is None:
            msg = f"Could not parse domain from URL: {url_str}"
            raise ValueError(msg)
        return domain

    # Filename computed fields
    @computed_field  # type: ignore[prop-decorator]
    @property
    def prep_filename(self) -> str:
        return "prep.json"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def fetch_filename(self) -> str:
        return "fetch.json"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def nav_json_filename(self) -> str:
        return "nav.json"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def nav_html_filename(self) -> str:
        return "nav.html"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def nav_md_filename(self) -> str:
        return "nav.md"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_docs_html_filename(self) -> str:
        return "all_docs.html"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_docs_md_filename(self) -> str:
        return "all_docs.md"

    # Directory path computed fields
    @computed_field  # type: ignore[prop-decorator]
    @property
    def html_dir(self) -> Path:
        return self.output_dir / "html"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def md_dir(self) -> Path:
        return self.output_dir / "md"

    # File path computed fields based on output_dir
    @computed_field  # type: ignore[prop-decorator]
    @property
    def prep_file(self) -> Path:
        return self.output_dir / self.prep_filename

    @computed_field  # type: ignore[prop-decorator]
    @property
    def fetch_file(self) -> Path:
        return self.output_dir / self.fetch_filename

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization logic."""
        # Adjust output_dir to be a subdirectory of CWD if it's default or "."
        # This logic is moved from the custom __init__ to model_post_init.
        # It needs self.root_domain, so computed fields must be available.
        # Note: self.output_dir is already resolved by default_factory=Path.cwd

        # Check if output_dir is the same as the initial CWD (from default_factory)
        # or if it was explicitly set to "."
        # This condition is a bit tricky because default_factory sets it to Path.cwd() already.
        # We need a way to know if it was the *default* or explicitly set to CWD by the user.
        # For simplicity, if map_url is present, and output_dir is CWD, make it CWD/domain.
        # This assumes if user sets output_dir to CWD explicitly, they still want the domain subdir.

        # A field to track if output_dir was explicitly set by user would be more robust.
        # Lacking that, we check if map_url is set and output_dir is the current CWD.
        if self.map_url and self.output_dir == Path.cwd():
            self.output_dir = Path.cwd() / self.root_domain

        # Ensure output directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.html_dir.mkdir(parents=True, exist_ok=True)
        self.md_dir.mkdir(parents=True, exist_ok=True)

        # Make css_file path absolute if it's relative
        if self.css_file and not self.css_file.is_absolute():
            # Resolve relative to CWD, or could be relative to config file if loaded from one.
            # For now, assume CWD.
            self.css_file = Path.cwd() / self.css_file

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override model_dump to ensure all fields are JSON serializable.

        Args:
            **kwargs: Arguments passed to model_dump

        Returns:
            Dictionary representation of the model
        """
        data = super().model_dump(**kwargs)
        # Convert AnyHttpUrl to string
        if data.get("map_url"):
            data["map_url"] = str(data["map_url"])
        if data.get("nav_url"):
            data["nav_url"] = str(data["nav_url"])
        # Convert Path to string
        if data.get("output_dir"):
            data["output_dir"] = str(data["output_dir"])
        if data.get("css_file"):
            data["css_file"] = str(data["css_file"])
        return data
