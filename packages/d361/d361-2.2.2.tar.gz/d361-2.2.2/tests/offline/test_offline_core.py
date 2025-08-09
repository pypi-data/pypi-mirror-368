import pytest
from pathlib import Path
from d361.offline.config import Config
from d361.offline.d361_offline import D361Offline


# Fixtures for Config and D361Offline
@pytest.fixture
def default_config_dict() -> dict[str, str]:
    return {
        "map_url": "https://example.com/sitemap.xml",
        "output_dir": "test_output",
    }


from typing import Any
import pytest # Ensure pytest is imported if not already for type hints like MockerFixture

@pytest.fixture
def default_config(default_config_dict: dict[str, str], tmp_path: Path) -> Config:
    config_dict_any: dict[str, Any] = default_config_dict.copy() # Make type checker happy for Path assignment
    config_dict_any["output_dir"] = tmp_path / default_config_dict["output_dir"]
    return Config(**config_dict_any) # Corrected variable name


@pytest.fixture
def d361_offline_instance(default_config: Config) -> D361Offline:
    return D361Offline(config=default_config)


# Tests for Config
def test_config_creation(default_config_dict: dict[str, str], tmp_path: Path) -> None:
    """Test basic Config creation and default values."""
    output_path = tmp_path / default_config_dict["output_dir"]
    config = Config(map_url=default_config_dict["map_url"], output_dir=output_path)
    assert str(config.map_url) == default_config_dict["map_url"]  # Cast to string
    assert config.output_dir == output_path
    # Config class now creates directories in model_post_init.
    assert output_path.exists()
    assert config.html_dir.exists()  # Check computed field path
    assert config.md_dir.exists()  # Check computed field path
    assert (output_path / "html").exists()  # Also check concrete path
    assert (output_path / "md").exists()  # Also check concrete path

    assert config.nav_url is None
    assert config.css_file is None  # default_config_dict doesn't set it.
    assert config.effort is False  # Default is False
    assert config.max_concurrent == 5  # Default is 5
    assert config.retries == 3  # Default is 3
    assert config.timeout == 60
    assert not config.verbose
    assert not config.test
    assert config.pause == 0
    assert config.prep_filename == "prep.json"
    assert config.fetch_filename == "fetch.json"
    assert config.nav_json_filename == "nav.json"
    assert config.nav_html_filename == "nav.html"
    assert config.nav_md_filename == "nav.md"
    assert config.all_docs_html_filename == "all_docs.html"
    assert config.all_docs_md_filename == "all_docs.md"


# Tests for D361Offline
def test_d361_offline_initialization(d361_offline_instance: D361Offline, default_config: Config) -> None:
    """Test D361Offline initialization."""
    assert d361_offline_instance.config == default_config
    # sitemap_urls, nav_items, processed_content are populated by methods, not at init
    # For example, check for initial state of attributes that are set in __init__
    assert hasattr(d361_offline_instance, "state")
    assert d361_offline_instance.state == {}
    # Add more specific checks if D361Offline initializes other attributes


# More tests will be added here for prep, fetch, and build methods,
# using mocker for network calls and file system interactions.


def test_config_root_domain_extraction_and_paths(tmp_path: Path) -> None:  # Combined and renamed
    """Test root_domain extraction and related path properties in Config."""
    # Test with a specific output_dir
    output_dir = tmp_path / "specific_docs"
    config1 = Config(map_url="https://docs.example.com/path", output_dir=output_dir)
    assert config1.root_domain == "docs.example.com"
    assert config1.output_dir == output_dir
    assert output_dir.exists()  # model_post_init should create it
    assert config1.html_dir == output_dir / "html"
    assert config1.md_dir == output_dir / "md"
    assert config1.prep_file == output_dir / "prep.json"
    assert config1.html_dir.exists()
    assert config1.md_dir.exists()

    # Test with default output_dir (which becomes CWD / domain)
    runtime_cwd = Path.cwd()
    config2 = Config(map_url="http://another.example.org")
    expected_output_dir2 = runtime_cwd / "another.example.org"
    assert config2.root_domain == "another.example.org"
    assert config2.output_dir == expected_output_dir2
    assert expected_output_dir2.exists()
    assert config2.html_dir.exists()  # Check subdirs are created

    # Test with map_url that might make root_domain tricky (e.g. localhost)
    config3 = Config(
        map_url="http://localhost:8000/sitemap.xml",
        output_dir=tmp_path / "localhost_docs",
    )
    assert config3.root_domain == "localhost"
    assert (tmp_path / "localhost_docs").exists()

    # Test ValueError if map_url is None and root_domain is accessed
    config_no_map_url = Config(map_url=None)
    with pytest.raises(
        ValueError, match="map_url must be set to determine root_domain"
    ):
        _ = config_no_map_url.root_domain  # Access root_domain directly


def test_config_output_dir_explicit_settings(tmp_path: Path) -> None:
    """Test Config.output_dir behavior with explicit settings."""

    runtime_cwd = Path.cwd()

    # Case 1: output_dir not provided, map_url provided
    # Expects: output_dir = CWD / domain
    map_url1 = "https://case1.example.com/sitemap.xml"
    config1 = Config(map_url=map_url1)
    expected_dir1 = runtime_cwd / "case1.example.com"
    assert config1.output_dir == expected_dir1
    assert expected_dir1.exists()

    # Case 2: output_dir = ".", map_url provided
    # Expects: output_dir = Path(".") (relative to CWD for operations)
    # model_post_init condition `self.output_dir == Path.cwd()` is false if Path(".") is not Path.cwd()
    map_url2 = "https://case2.example.com/sitemap.xml"
    config2 = Config(map_url=map_url2, output_dir=".")
    expected_dir2 = Path(".")
    assert config2.output_dir == expected_dir2
    assert (runtime_cwd / expected_dir2).exists()  # Check actual created path
    assert (runtime_cwd / expected_dir2 / "html").exists()

    # Case 3: output_dir = "relative_str", map_url provided
    # Expects: output_dir = Path("relative_str")
    map_url3 = "https://case3.example.com/sitemap.xml"
    relative_path_str = "my_custom_output_explicit"  # Different name
    config3 = Config(map_url=map_url3, output_dir=relative_path_str)
    expected_dir3 = Path(relative_path_str)
    assert config3.output_dir == expected_dir3
    assert (runtime_cwd / expected_dir3).exists()
    assert (runtime_cwd / expected_dir3 / "html").exists()

    # Case 4: output_dir = absolute_path, map_url provided
    # Expects: output_dir = absolute_path
    map_url4 = "https://case4.example.com/sitemap.xml"
    absolute_path = tmp_path / "abs_output_dir_explicit"  # Different name
    config4 = Config(map_url=map_url4, output_dir=absolute_path)
    assert config4.output_dir == absolute_path
    assert absolute_path.exists()
    assert (absolute_path / "html").exists()

    # Case 5: output_dir not provided, map_url is None
    # Expects: output_dir = CWD (model_post_init condition `self.map_url and ...` is false)
    config5 = Config(map_url=None)
    assert config5.output_dir == runtime_cwd
    assert runtime_cwd.exists()  # CWD should exist
    # Check if subdirs are made in CWD (be careful if CWD is project root)
    # For a clean test, this might need a temporary CWD change or specific output_dir.
    # Let's assume for now CWD is testable or use a dedicated temp dir for this case.
    temp_output_for_case5 = tmp_path / "case5_no_map_url_default_output"
    config5_alt = Config(map_url=None, output_dir=temp_output_for_case5)
    assert config5_alt.output_dir == temp_output_for_case5
    assert temp_output_for_case5.exists()
    assert (temp_output_for_case5 / "html").exists()

    # Case 6: output_dir = ".", map_url is None
    # Expects: output_dir = Path(".")
    config6 = Config(map_url=None, output_dir=".")
    assert config6.output_dir == Path(".")
    assert (runtime_cwd / Path(".")).exists()  # CWD should exist
    assert (runtime_cwd / Path(".") / "html").exists()


from pydantic import BaseModel, AnyHttpUrl, computed_field # Moved to top

# Minimal test for Pydantic computed_field
def test_minimal_config_root_domain() -> None:
    class MinimalConfig(BaseModel): # pydantic types are now globally available
        url: AnyHttpUrl

        @computed_field  # type: ignore[prop-decorator]
        @property
        def domain(self) -> str:
            # Ensure host is not None before casting to str, or handle potential None
            if self.url.host is None:
                _message = "URL has no host"
                raise ValueError(_message)
            return str(self.url.host)

    cfg = MinimalConfig(url="http://example.com/foo")
    assert cfg.domain == "example.com"

    cfg_https = MinimalConfig(url="https://sub.example.co.uk/bar")
    assert cfg_https.domain == "sub.example.co.uk"
