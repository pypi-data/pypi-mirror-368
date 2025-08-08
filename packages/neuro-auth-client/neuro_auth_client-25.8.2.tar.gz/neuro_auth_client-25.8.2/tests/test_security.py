from unittest.mock import Mock

import pytest
from aiohttp import BasicAuth
from aiohttp.test_utils import make_mocked_request
from jose import jwt

from neuro_auth_client.security import (
    JWT_CLUSTER_CLAIM,
    JWT_IDENTITY_CLAIM,
    JWT_KIND_CLAIM,
    AuthPolicy,
    AuthScheme,
    IdentityError,
    IdentityPolicy,
    Kind,
)


async def test_identity_bearer() -> None:
    req = make_mocked_request("GET", "/path", {"Authorization": "Bearer token1"})
    ip = IdentityPolicy()
    assert await ip.identify(req) == "token1"


async def test_identity_query() -> None:
    req = make_mocked_request("GET", "/path?neuro-auth-token=token2")
    ip = IdentityPolicy()
    assert await ip.identify(req) == "token2"


async def test_identity_default() -> None:
    req = make_mocked_request("GET", "/path")
    ip = IdentityPolicy(default_identity="default")
    assert await ip.identify(req) == "default"


async def test_identity_basic() -> None:
    auth = BasicAuth("user", "passwd")
    req = make_mocked_request("GET", "/path", {"Authorization": auth.encode()})
    ip = IdentityPolicy(AuthScheme.BASIC)
    assert await ip.identify(req) == "passwd"


async def test_identity_ws() -> None:
    req = make_mocked_request(
        "GET", "/path", {"Sec-WebSocket-Protocol": "bearer.apolo.us-token4"}
    )
    ip = IdentityPolicy()
    assert await ip.identify(req) == "token4"


async def test_identity_ws_multiple_subprotocols() -> None:
    req = make_mocked_request(
        "GET", "/path", {"Sec-WebSocket-Protocol": "chat bearer.apolo.us-token4 other"}
    )
    ip = IdentityPolicy()
    assert await ip.identify(req) == "token4"


@pytest.mark.parametrize(
    "path,headers,token",
    [
        (  # all
            "/path?neuro-auth-token=token1",
            {
                "Authorization": "Bearer token2",
                "Sec-WebSocket-Protocol": "bearer.apolo.us-token3",
            },
            "token2",
        ),
        (  # header + query
            "/path?neuro-auth-token=token1",
            {
                "Authorization": "Bearer token2",
            },
            "token2",
        ),
        (  # header + ws
            "/path",
            {
                "Authorization": "Bearer token2",
                "Sec-WebSocket-Protocol": "bearer.apolo.us-token3",
            },
            "token2",
        ),
        (  # query + ws
            "/path?neuro-auth-token=token1",
            {
                "Sec-WebSocket-Protocol": "bearer.apolo.us-token3",
            },
            "token3",
        ),
        (  # default
            "/path",
            {},
            "default",
        ),
    ],
)
async def test_identity_precedence(
    path: str, headers: dict[str, str], token: str
) -> None:
    req = make_mocked_request("GET", path, headers)
    ip = IdentityPolicy(default_identity="default")
    assert await ip.identify(req) == token


def test_get_kind() -> None:
    identity = jwt.encode(
        {JWT_IDENTITY_CLAIM: "test", JWT_KIND_CLAIM: Kind.CLUSTER}, "secret"
    )
    auth_policy = AuthPolicy(Mock())
    assert auth_policy.get_kind(identity) == Kind.CLUSTER


def test_get_kind_default() -> None:
    identity = jwt.encode({JWT_IDENTITY_CLAIM: "test"}, "secret")
    auth_policy = AuthPolicy(Mock())
    assert auth_policy.get_kind(identity) == Kind.USER


def test_get_cluster() -> None:
    identity = jwt.encode(
        {
            JWT_IDENTITY_CLAIM: "test",
            JWT_KIND_CLAIM: "cluster",
            JWT_CLUSTER_CLAIM: "cl1",
        },
        "secret",
    )
    auth_policy = AuthPolicy(Mock())
    assert auth_policy.get_cluster(identity) == "cl1"


def test_get_cluster_invalid_kind() -> None:
    identity = jwt.encode(
        {JWT_IDENTITY_CLAIM: "test", JWT_KIND_CLAIM: "user", JWT_CLUSTER_CLAIM: "cl1"},
        "secret",
    )
    auth_policy = AuthPolicy(Mock())
    with pytest.raises(IdentityError, match="^identity has unexpected kind"):
        auth_policy.get_cluster(identity)


def test_get_cluster_invalid_claim() -> None:
    identity = jwt.encode(
        {JWT_IDENTITY_CLAIM: "test", JWT_KIND_CLAIM: "cluster", JWT_CLUSTER_CLAIM: ""},
        "secret",
    )
    auth_policy = AuthPolicy(Mock())
    with pytest.raises(IdentityError, match="^identity has kind 'cluster', but"):
        auth_policy.get_cluster(identity)
