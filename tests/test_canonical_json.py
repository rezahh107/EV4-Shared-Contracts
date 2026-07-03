import math

import pytest

from ev4_transition.canonical_json import CanonicalJsonError, canonical_dumps, canonical_sha256


def test_canonical_key_ordering():
    assert canonical_dumps({"b": 2, "a": 1}) == '{"a":1,"b":2}'


def test_stable_sha256_independent_of_key_order():
    assert canonical_sha256({"b": 2, "a": 1}) == canonical_sha256({"a": 1, "b": 2})


def test_nan_rejected():
    with pytest.raises(CanonicalJsonError):
        canonical_dumps({"bad": float("nan")})


def test_positive_infinity_rejected():
    with pytest.raises(CanonicalJsonError):
        canonical_dumps({"bad": float("inf")})


def test_negative_infinity_rejected():
    with pytest.raises(CanonicalJsonError):
        canonical_dumps({"bad": -math.inf})
