"""
FREQ AI WebSocket Manager

Real-time communication layer for the FREQ AI Command Center.
Provides live updates for lattice status, missions, and audit events.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from weakref import WeakSet

from .schemas import WebSocketMessage, WebSocketMessageType

logger = logging.getLogger(__name__)


class SubscriptionChannel(Enum):
    """Available subscription channels."""
    LATTICE = "lattice"       # Lattice node status updates
    MISSIONS = "missions"     # Mission progress updates
    AUDIT = "audit"           # Audit trail entries
    COMPLIANCE = "compliance" # FREQ LAW compliance updates
    PROVIDERS = "providers"   # AI provider status updates
    ALL = "all"               # All channels


@dataclass
class WebSocketClient:
    """Represents a connected WebSocket client."""

    client_id: str
    connection: Any  # WebSocket connection object
    subscriptions: Set[SubscriptionChannel] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_subscribed(self, channel: SubscriptionChannel) -> bool:
        """Check if client is subscribed to a channel."""
        return (
            channel in self.subscriptions
            or SubscriptionChannel.ALL in self.subscriptions
        )


class WebSocketManager:
    """
    WebSocket Manager for Real-Time Updates

    Manages WebSocket connections and provides pub/sub functionality
    for the FREQ AI Command Center dashboard.

    Features:
    - Connection lifecycle management
    - Channel-based subscriptions
    - Broadcast and targeted messaging
    - Heartbeat/keepalive handling
    - Graceful disconnect handling
    """

    def __init__(
        self,
        heartbeat_interval: float = 30.0,
        client_timeout: float = 120.0,
    ):
        self.clients: Dict[str, WebSocketClient] = {}
        self.heartbeat_interval = heartbeat_interval
        self.client_timeout = client_timeout

        # Event handlers
        self._on_connect_handlers: List[Callable] = []
        self._on_disconnect_handlers: List[Callable] = []
        self._on_message_handlers: List[Callable] = []

        # Background tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start the WebSocket manager background tasks."""
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("WebSocket manager started")

    async def stop(self) -> None:
        """Stop the WebSocket manager and close all connections."""
        self._running = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

        # Close all client connections
        for client in list(self.clients.values()):
            await self.disconnect(client.client_id)

        logger.info("WebSocket manager stopped")

    async def connect(
        self,
        client_id: str,
        connection: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WebSocketClient:
        """
        Register a new WebSocket connection.

        Args:
            client_id: Unique identifier for the client
            connection: WebSocket connection object
            metadata: Optional client metadata

        Returns:
            WebSocketClient instance
        """
        client = WebSocketClient(
            client_id=client_id,
            connection=connection,
            metadata=metadata or {},
        )

        self.clients[client_id] = client
        logger.info(f"WebSocket client connected: {client_id}")

        # Notify handlers
        for handler in self._on_connect_handlers:
            try:
                await handler(client)
            except Exception as e:
                logger.error(f"Error in connect handler: {e}")

        return client

    async def disconnect(self, client_id: str) -> None:
        """
        Disconnect a WebSocket client.

        Args:
            client_id: Client identifier to disconnect
        """
        client = self.clients.pop(client_id, None)

        if client:
            logger.info(f"WebSocket client disconnected: {client_id}")

            # Notify handlers
            for handler in self._on_disconnect_handlers:
                try:
                    await handler(client)
                except Exception as e:
                    logger.error(f"Error in disconnect handler: {e}")

    def subscribe(
        self,
        client_id: str,
        channels: List[SubscriptionChannel],
    ) -> bool:
        """
        Subscribe a client to channels.

        Args:
            client_id: Client identifier
            channels: List of channels to subscribe to

        Returns:
            True if successful
        """
        client = self.clients.get(client_id)
        if not client:
            return False

        for channel in channels:
            client.subscriptions.add(channel)

        logger.debug(f"Client {client_id} subscribed to: {channels}")
        return True

    def unsubscribe(
        self,
        client_id: str,
        channels: List[SubscriptionChannel],
    ) -> bool:
        """
        Unsubscribe a client from channels.

        Args:
            client_id: Client identifier
            channels: List of channels to unsubscribe from

        Returns:
            True if successful
        """
        client = self.clients.get(client_id)
        if not client:
            return False

        for channel in channels:
            client.subscriptions.discard(channel)

        logger.debug(f"Client {client_id} unsubscribed from: {channels}")
        return True

    async def send_to_client(
        self,
        client_id: str,
        message: WebSocketMessage,
    ) -> bool:
        """
        Send a message to a specific client.

        Args:
            client_id: Target client identifier
            message: Message to send

        Returns:
            True if sent successfully
        """
        client = self.clients.get(client_id)
        if not client:
            return False

        try:
            await self._send(client.connection, message)
            client.last_activity = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Failed to send to client {client_id}: {e}")
            await self.disconnect(client_id)
            return False

    async def broadcast(
        self,
        message: WebSocketMessage,
        channel: Optional[SubscriptionChannel] = None,
    ) -> int:
        """
        Broadcast a message to all subscribed clients.

        Args:
            message: Message to broadcast
            channel: Optional channel filter

        Returns:
            Number of clients that received the message
        """
        sent_count = 0

        for client_id, client in list(self.clients.items()):
            # Check channel subscription if specified
            if channel and not client.is_subscribed(channel):
                continue

            try:
                await self._send(client.connection, message)
                client.last_activity = datetime.now()
                sent_count += 1
            except Exception as e:
                logger.error(f"Broadcast to {client_id} failed: {e}")
                await self.disconnect(client_id)

        return sent_count

    async def handle_message(
        self,
        client_id: str,
        raw_message: str,
    ) -> None:
        """
        Handle an incoming message from a client.

        Args:
            client_id: Source client identifier
            raw_message: Raw message string (JSON)
        """
        client = self.clients.get(client_id)
        if not client:
            return

        client.last_activity = datetime.now()

        try:
            data = json.loads(raw_message)
            message = WebSocketMessage.from_dict(data)

            # Handle built-in message types
            if message.type == WebSocketMessageType.PING:
                await self.send_to_client(
                    client_id,
                    WebSocketMessage(
                        type=WebSocketMessageType.PONG,
                        payload={},
                        correlation_id=message.correlation_id,
                    ),
                )

            elif message.type == WebSocketMessageType.SUBSCRIBE:
                channels = [
                    SubscriptionChannel(c)
                    for c in message.payload.get("channels", [])
                ]
                self.subscribe(client_id, channels)

            elif message.type == WebSocketMessageType.UNSUBSCRIBE:
                channels = [
                    SubscriptionChannel(c)
                    for c in message.payload.get("channels", [])
                ]
                self.unsubscribe(client_id, channels)

            # Notify handlers
            for handler in self._on_message_handlers:
                try:
                    await handler(client, message)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client_id}")
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")

    # =========================================================================
    # BROADCAST HELPERS
    # =========================================================================

    async def broadcast_lattice_update(self, lattice_data: Dict[str, Any]) -> int:
        """Broadcast lattice status update."""
        return await self.broadcast(
            WebSocketMessage(
                type=WebSocketMessageType.LATTICE_UPDATE,
                payload=lattice_data,
            ),
            channel=SubscriptionChannel.LATTICE,
        )

    async def broadcast_mission_update(self, mission_data: Dict[str, Any]) -> int:
        """Broadcast mission progress update."""
        return await self.broadcast(
            WebSocketMessage(
                type=WebSocketMessageType.MISSION_UPDATE,
                payload=mission_data,
            ),
            channel=SubscriptionChannel.MISSIONS,
        )

    async def broadcast_audit_entry(self, audit_data: Dict[str, Any]) -> int:
        """Broadcast new audit trail entry."""
        return await self.broadcast(
            WebSocketMessage(
                type=WebSocketMessageType.AUDIT_ENTRY,
                payload=audit_data,
            ),
            channel=SubscriptionChannel.AUDIT,
        )

    async def broadcast_compliance_update(self, compliance_data: Dict[str, Any]) -> int:
        """Broadcast compliance status update."""
        return await self.broadcast(
            WebSocketMessage(
                type=WebSocketMessageType.COMPLIANCE_UPDATE,
                payload=compliance_data,
            ),
            channel=SubscriptionChannel.COMPLIANCE,
        )

    async def broadcast_provider_update(self, provider_data: Dict[str, Any]) -> int:
        """Broadcast provider status update."""
        return await self.broadcast(
            WebSocketMessage(
                type=WebSocketMessageType.PROVIDER_UPDATE,
                payload=provider_data,
            ),
            channel=SubscriptionChannel.PROVIDERS,
        )

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def on_connect(self, handler: Callable) -> None:
        """Register a connection handler."""
        self._on_connect_handlers.append(handler)

    def on_disconnect(self, handler: Callable) -> None:
        """Register a disconnection handler."""
        self._on_disconnect_handlers.append(handler)

    def on_message(self, handler: Callable) -> None:
        """Register a message handler."""
        self._on_message_handlers.append(handler)

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    async def _send(self, connection: Any, message: WebSocketMessage) -> None:
        """Send a message over a WebSocket connection."""
        # This is a placeholder - actual implementation depends on
        # the WebSocket library being used (websockets, aiohttp, etc.)
        if hasattr(connection, "send"):
            await connection.send(json.dumps(message.to_dict()))
        elif hasattr(connection, "send_json"):
            await connection.send_json(message.to_dict())
        else:
            raise NotImplementedError("Unknown WebSocket connection type")

    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats to keep connections alive."""
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                for client_id in list(self.clients.keys()):
                    await self.send_to_client(
                        client_id,
                        WebSocketMessage(
                            type=WebSocketMessageType.PONG,
                            payload={"heartbeat": True},
                        ),
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")

    async def _cleanup_loop(self) -> None:
        """Clean up stale connections periodically."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute

                now = datetime.now()
                for client_id, client in list(self.clients.items()):
                    idle_time = (now - client.last_activity).total_seconds()
                    if idle_time > self.client_timeout:
                        logger.info(f"Cleaning up stale client: {client_id}")
                        await self.disconnect(client_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics."""
        return {
            "connectedClients": len(self.clients),
            "subscriptions": {
                channel.value: sum(
                    1 for c in self.clients.values()
                    if c.is_subscribed(channel)
                )
                for channel in SubscriptionChannel
            },
        }
