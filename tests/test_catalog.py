import pytest

from ologos_aioc import EchoProvider, ModelCatalog


def test_register_and_get():
    catalog = ModelCatalog()
    provider = EchoProvider()
    catalog.register("fast-echo", provider, tags={"fast", "cheap"})

    entry = catalog.get("fast-echo")
    assert entry.name == "fast-echo"
    assert entry.provider is provider
    assert entry.tags == {"fast", "cheap"}
    assert "fast-echo" in catalog
    assert len(catalog) == 1


def test_get_unknown_raises():
    catalog = ModelCatalog()
    with pytest.raises(KeyError):
        catalog.get("nope")


def test_route_by_tag_first_match():
    catalog = ModelCatalog()
    slow = EchoProvider(canned_text="slow")
    fast = EchoProvider(canned_text="fast")
    catalog.register("slow-model", slow, tags={"reasoning"})
    catalog.register("fast-model", fast, tags={"fast"})

    entry = catalog.route("fast")
    assert entry.name == "fast-model"


def test_route_no_match_raises():
    catalog = ModelCatalog()
    catalog.register("m", EchoProvider(), tags={"a"})
    with pytest.raises(LookupError):
        catalog.route("z")
