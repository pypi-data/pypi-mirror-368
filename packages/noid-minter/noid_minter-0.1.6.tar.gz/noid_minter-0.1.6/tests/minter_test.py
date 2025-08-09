import json
import re

import pytest

import noid_minter.minter as nm
from noid_minter.minter import Minter, MintOrder


def test_minimal_configuration():
    with pytest.raises(nm.MissingConfigurationException):
        minter = Minter()
    with pytest.raises(nm.MissingConfigurationException):
        minter = Minter({})
    try:
        minter = Minter({"template": ".sd"})
    except Exception as message:
        pytest.fail(f"Unexpected exception raised: {message}")


def test_naan():
    minter = Minter({"template": ".sd"})
    assert minter.naan is None
    minter = Minter({"template": ".sd", "naan": "16417"})
    assert minter.naan == "16417"


def test_naan_is_included_in_minted_identifiers():
    minter = Minter({"template": ".sd", "naan": "16417"})
    assert minter.mint().ark == "16417/0"


def test_template_specifies_mint_order():
    minter = Minter({"template": ".rd"})
    assert minter.order == MintOrder.RANDOM
    minter = Minter({"template": ".sd"})
    assert minter.order == MintOrder.SEQUENTIAL
    minter = Minter({"template": ".zd"})
    assert minter.order == MintOrder.GROWING


def test_first_sequential_identifier_is_zero():
    minter = Minter({"template": ".sdd"})
    assert minter.mint().ark == "00"


def test_sequential_minter_mints_sequentially():
    minter = Minter({"template": ".sd"})
    assert minter.mint().ark == "0"
    assert minter.mint().ark == "1"
    assert minter.mint().ark == "2"
    assert minter.mint().ark == "3"


def test_sequential_minter_mints_digit_strings_and_exhausts():
    minter = Minter({"template": ".sddd"})
    for _ in range(1000):
        assert re.match(r"^\d\d\d$", minter.mint().ark)
    assert minter.is_exhausted()


def test_growing_minter_extends_ark_length():
    minter = Minter({"template": ".zddd"})
    for _ in range(1000):
        assert re.match(r"^\d\d\d$", minter.mint().ark)
    assert not minter.is_exhausted()
    assert minter.mint().ark == "1000"


def test_minter_uses_betanumeric_if_provided_in_template():
    minter = Minter({"template": ".se"})
    arks = []
    for _ in range(29):
        arks.append(minter.mint().ark)
    assert "".join(arks) == "0123456789bcdfghjkmnpqrstvwxz"


def test_mints_a_few_random_3_digit_numbers():
    minter = Minter({"template": ".rddd"})
    assert re.match(r"\d\d\d", minter.mint().ark)


def test_mints_random_7_char_numbers_with_betanumerics_at_2_4_and_5():
    minter = Minter({"template": ".rdedeedd"})
    for _ in range(1000):
        assert re.match(r"^\d\w\d\w\w\d\d$", minter.mint().ark)


def test_multibase_representation_works():
    minter = Minter({"template": ".sede"})
    minter.counter = 5678
    assert minter.mint().ark == "n5s"


def test_random_minter_preserves_noid_mint_order():
    minter = Minter({"template": ".reeedeeed"})
    assert minter.mint().ark == "4xg9f4v1"
    assert minter.mint().ark == "15d8nck7"
    assert minter.mint().ark == "wdb7vn02"
    assert minter.mint().ark == "rn872vq8"
    assert minter.mint().ark == "mw6693g4"
    assert minter.mint().ark == "h445hb70"
    assert minter.mint().ark == "cc24qjz6"
    assert minter.mint().ark == "7pv6b2x5"
    assert minter.mint().ark == "3xs5j9p1"
    assert minter.mint().ark == "05q4rjd7"


def test_prefix():
    minter = Minter({"template": "bc.rdddd"})
    for _ in range(1000):
        assert re.match(r"^bc\d\d\d\d$", minter.mint().ark)


def test_check_digit():
    minter = Minter({"template": ".seeeddd"})
    minter.counter = 22677123
    assert not minter.requires_checkchar
    assert minter.mint().ark == "wxz123"
    minter = Minter({"template": ".seeedddk"})
    minter.counter = 22677123
    assert minter.requires_checkchar
    assert minter.mint().ark == "wxz123r"


def test_naan_prefix_and_check_digit_together():
    minter = Minter({"template": "xt7.reeedeeedk", "naan": "16417"})
    assert minter.mint().ark == "16417/xt74xg9f4v1p"


def test_sequential_serialization():
    minter = Minter({"template": "v.sd", "naan": "16417"})
    minter.mint()  # advance counter
    minter2 = Minter.load(minter.to_json())
    assert minter2.mint().ark == "16417/v1"


def test_random_serialization():
    first_mint_streak = 300
    second_mint_streak = 365

    minter = Minter({"template": "xt7.reeedeeedk", "naan": "16417"})
    for _ in range(first_mint_streak + second_mint_streak):
        minter.mint()
    continuous_minting_ark = minter.mint().ark

    minter2 = Minter({"template": "xt7.reeedeeedk", "naan": "16417"})
    for _ in range(first_mint_streak):
        minter2.mint()

    minter3 = Minter.load(minter2.to_json())
    for _ in range(second_mint_streak):
        minter3.mint()
    discontinuous_minting_ark = minter3.mint().ark

    assert continuous_minting_ark == discontinuous_minting_ark


def test_exporting_constants_that_might_not_be():
    minter = Minter({"template": "xt7.reeedeeedk", "naan": "16417"})
    dump = json.loads(minter.to_json())
    assert dump["prng_identifier"] == "rand48"
    assert dump["max_buckets_count"] == 293


def test_importing_constants_that_might_not_be():
    minter = Minter({"template": "xt7.reeedeeedk", "naan": "16417"})
    dump = json.loads(minter.to_json())
    dump["max_buckets_count"] = 15
    minter2 = Minter.load(json.dumps(dump))
    assert minter2.max_buckets_count == 15
