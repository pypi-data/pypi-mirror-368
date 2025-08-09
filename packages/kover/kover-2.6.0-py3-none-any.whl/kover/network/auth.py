from __future__ import annotations

import base64
import hashlib
from hmac import HMAC, compare_digest
import os
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from ..bson import Binary
from ..exceptions import CredentialsException

if TYPE_CHECKING:
    from ..client import MongoTransport
    from ..typings import xJsonT


class AuthCredentials(BaseModel):
    """Stores authentication credentials for MongoDB.

    Attributes:
        username : The username for authentication.
        password : The password for authentication.
        db_name : The database name to authenticate against
            (default is "admin").
    """

    username: str
    password: str = Field(repr=False)
    db_name: str = Field(default="admin")

    def md5_hash(self) -> bytes:
        """Returns md5 hashed string for MongoDB. Internal use."""
        hashed = hashlib.md5(f"{self.username}:mongo:{self.password}".encode())
        return hashed.hexdigest().encode("u8")

    def apply_to(self, document: xJsonT) -> None:
        """Internal use only. Applies auth credentials to hello payload."""
        document["saslSupportedMechs"] = f"{self.db_name}.{self.username}"

    @classmethod
    def from_environ(cls) -> AuthCredentials | None:
        """Create AuthCredentials from environment variables.

        Returns:
            AuthCredentials instance if both MONGO_USER and MONGO_PASSWORD
                are set in the environment, otherwise returns None.

        Raises:
            CredentialsException : If only one of MONGO_USER
                or MONGO_PASSWORD is set.
        """
        user, password = os.environ.get("MONGO_USER"), \
            os.environ.get("MONGO_PASSWORD")
        if user is not None and password is not None:
            return cls(username=user, password=password)
        if (user and not password) or (password and not user):
            raise CredentialsException
        return None  # ruff force


class Auth:
    """Handles authentication mechanisms for MongoDB connections.

    Attributes:
        transport : The transport used for communication
            with the MongoDB server.
    """

    def __init__(self, transport: MongoTransport) -> None:
        self.transport = transport

    @staticmethod
    def _parse_scram_response(payload: bytes) -> dict[str, bytes]:
        values = [
            item.split(b"=", 1)
            for item in payload.split(b",")
        ]
        return {
            k.decode(): v
            for k, v in values
        }

    @staticmethod
    def xor(fir: bytes, sec: bytes) -> bytes:
        """XOR two byte strings together."""
        return b"".join(
            [bytes([x ^ y]) for x, y in zip(fir, sec, strict=True)],
        )

    @staticmethod
    def _clear_username(username: bytes) -> bytes:
        for x, y in {b"=": b"=3D", b",": b"=2C"}.items():
            username = username.replace(x, y)
        return username

    async def _sasl_start(
        self,
        mechanism: str,
        username: str,
        db_name: str,
    ) -> tuple[bytes, bytes, bytes, int]:
        user = self._clear_username(username.encode("u8"))
        nonce = base64.b64encode(os.urandom(32))
        first_bare = b"n=" + user + b",r=" + nonce
        command: xJsonT = {
            "saslStart": 1.0,
            "mechanism": mechanism,
            "payload": Binary(b"n,," + first_bare),
            "autoAuthorize": 1,
            "options": {
                "skipEmptyExchange": True,
            },
        }
        request = await self.transport.request(command, db_name=db_name)
        return nonce, request["payload"], first_bare, request["conversationId"]

    async def create(  # noqa: PLR0914
        self,
        mechanism: str,
        credentials: AuthCredentials,
    ) -> bytes:
        """Perform SCRAM authentication with the MongoDB server.

        Parameters:
            mechanism : The authentication mechanism to use
                (e.g., "SCRAM-SHA-1", "SCRAM-SHA-256").
            credentials : The authentication credentials containing
                username, password, and database name.

        Returns:
            The server signature after successful authentication.

        Raises:
            AssertionError : If the server returns an invalid
                iteration count or nonce,
                or if the server signature does not match.
        """
        if mechanism == "SCRAM-SHA-1":
            digest = "sha1"
            digestmod = hashlib.sha1
            data = credentials.md5_hash()
        else:
            digest = "sha256"
            digestmod = hashlib.sha256
            data = credentials.password.encode()

        nonce, server_first, first_bare, cid = await self._sasl_start(
            mechanism,
            credentials.username,
            credentials.db_name,
        )

        parsed = self._parse_scram_response(server_first)
        iterations = int(parsed["i"])
        assert iterations > 4096, "Server returned an invalid iteration count."
        salt, rnonce = parsed["s"], parsed["r"]
        assert rnonce.startswith(nonce), "Server returned an invalid nonce."

        without_proof = b"c=biws,r=" + rnonce
        salted_pass = hashlib.pbkdf2_hmac(
            digest,
            data,
            base64.b64decode(salt),
            iterations,
        )
        client_key = HMAC(salted_pass, b"Client Key", digestmod).digest()
        server_key = HMAC(salted_pass, b"Server Key", digestmod).digest()

        stored_key = digestmod(client_key).digest()
        auth_msg = b",".join((first_bare, server_first, without_proof))
        client_sig = HMAC(stored_key, auth_msg, digestmod).digest()
        client_proof = b"p=" + base64.b64encode(
            self.xor(client_key, client_sig),
        )
        client_final = b",".join((without_proof, client_proof))
        server_sig = base64.b64encode(
            HMAC(server_key, auth_msg, digestmod).digest(),
        )
        cmd: xJsonT = {
            "saslContinue": 1.0,
            "conversationId": cid,
            "payload": Binary(client_final),
        }
        request = await self.transport.request(
            cmd,
            db_name=credentials.db_name,
        )
        parsed = self._parse_scram_response(request["payload"])

        assert request["done"]
        assert compare_digest(parsed["v"], server_sig)

        return parsed["v"]
