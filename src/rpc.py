import time
import asyncio
import threading
import atexit
from typing import Any, Dict, Optional

from pypresence import AioPresence
from pypresence.exceptions import DiscordNotFound, InvalidID, PipeClosed


class Rpc:
    def __init__(self, map_dict, gamemodes, colors, log):
        self.log = log
        self.map_dict = map_dict
        self.gamemodes = gamemodes
        self.colors = colors

        # Config
        self.client_id = "1012402211134910546"

        self.discord_running: bool = False
        self.last_presence_data: Dict[str, Any] = {}

        self._rpc: Optional[AioPresence] = None
        self._connected: bool = False

        self._data: Dict[str, Any] = {"agent": None, "rank": None, "rank_name": None}
        self._desired_presence: Dict[str, Any] = {}

        # Shadows (before the loop)
        self._shadow_data = dict(self._data)
        self._shadow_presence = dict(self._desired_presence)

        # Update/reconnect controls
        self._update_event: Optional[asyncio.Event] = None
        self._min_interval: float = 1.0
        self._last_sent_ts: float = 0.0
        self._backoff: float = 1.0  # 1, 2, 4, ... até 30
        self._last_loop_state: Optional[str] = None
        self.start_time: float = time.time()
        self._max_backoff_notice: bool = False

        # Base payload
        self._base_payload: Dict[str, Any] = {
            "buttons": [
                {"label": "What's this? 👀", "url": "https://zaykenyon.github.io/VALORANT-rank-yoinker/"}
            ]
        }
        # Cache last payload (for dedupe)
        self._last_sent_payload: Optional[Dict[str, Any]] = None

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._runner_task: Optional[asyncio.Task] = None
        self._thread: Optional[threading.Thread] = None

        self._start_thread()
        atexit.register(self.shutdown)

    def set_data(self, data: Dict[str, Any]):
        if not isinstance(data, dict):
            return

        # Update shadow
        self._shadow_data = {**self._shadow_data, **data}

        if self._loop and self._loop.is_running():
            def _apply():
                self._data = {**self._data, **data}
                self.log("RPC: New data set")
                if self._update_event:
                    self._update_event.set()
            self._loop.call_soon_threadsafe(_apply)
        else:
            self.log("RPC: New data set (queued)")
            self.set_rpc(self.last_presence_data)

    def set_rpc(self, presence: Dict[str, Any]):
        presence = presence or {}
        self.last_presence_data = presence
        self._shadow_presence = presence

        if self._loop and self._loop.is_running():
            def _apply():
                self._desired_presence = presence
                if self._update_event:
                    self._update_event.set()
            self._loop.call_soon_threadsafe(_apply)

    def shutdown(self):
        if not self._thread or not self._thread.is_alive():
            return

        def _cancel_runner():
            if self._runner_task and not self._runner_task.done():
                self._runner_task.cancel()

        try:
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(_cancel_runner)
                self._thread.join(timeout=3.0)
        except Exception:
            pass

    def _start_thread(self):
        if self._thread and self._thread.is_alive():
            return

        def _thread_target():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._update_event = asyncio.Event()

            # Initializes internal state from the shadows
            self._data = dict(self._shadow_data)
            self._desired_presence = dict(self._shadow_presence)

            self._runner_task = self._loop.create_task(self._run())

            try:
                self._loop.run_until_complete(self._runner_task)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                try:
                    self.log(f"RPC: Loop crashed: {e}")
                except Exception:
                    pass
            finally:
                try:
                    self._loop.run_until_complete(self._safe_close())
                except Exception:
                    pass
                try:
                    self._loop.run_until_complete(self._loop.shutdown_asyncgens())
                except Exception:
                    pass
                try:
                    self._loop.close()
                except Exception:
                    pass

        self._thread = threading.Thread(target=_thread_target, name="RpcAioPresenceLoop", daemon=True)
        self._thread.start()

    async def _run(self):
        await self._connect()

        while True:
            try:
                # Waits update signal or sends a keep-alive
                try:
                    await asyncio.wait_for(self._update_event.wait(), timeout=30.0)
                except asyncio.TimeoutError:
                    pass

                self._update_event.clear()

                if not self._connected:
                    await self._connect()

                # Rate-limit
                now = time.monotonic()
                if now - self._last_sent_ts < self._min_interval:
                    await asyncio.sleep(self._min_interval - (now - self._last_sent_ts))

                dynamic = self._build_payload(self._desired_presence, self._data)
                if dynamic is None:
                    continue

                payload = self._finalize_payload(dynamic)

                # Dedupe: only sends if changed
                if payload == self._last_sent_payload:
                    continue

                await self._rpc.update(**payload)
                self._last_sent_ts = time.monotonic()
                self._last_sent_payload = payload

                # Logs
                state = (self._desired_presence.get("matchPresenceData") or {}).get("sessionLoopState")
                if state == "INGAME":
                    self.log("RPC: in-game data update")
                elif state == "MENUS":
                    self.log("RPC: menu data updated")
                elif state == "PREGAME":
                    self.log("RPC: agent-select data update")

            except asyncio.CancelledError:
                break

            except (PipeClosed, ConnectionError, OSError, InvalidID) as e:
                self.log(f"RPC: Transport lost: {e}")
                await self._safe_close()
                await asyncio.sleep(self._backoff)
                self._backoff = min(self._backoff * 2, 30.0)

            except Exception as e:
                self.log(f"RPC: Unexpected error in main loop: {e}")
                await self._safe_close()
                await asyncio.sleep(self._backoff)
                self._backoff = min(self._backoff * 2, 30.0)

    async def _connect(self):
        while True:
            try:
                if self._rpc is None:
                    self._rpc = AioPresence(self.client_id)

                await self._rpc.connect()
                self._connected = True
                self.discord_running = True
                self._backoff = 1.0
                self._max_backoff_notice = False
                self.log("RPC: Connected to discord")
                return
            except asyncio.CancelledError:
                raise
            except DiscordNotFound:
                self._connected = False
                self.discord_running = False
                if self._backoff < 30.0:
                    self.log(f"RPC: Discord not found, retrying in {self._backoff:.1f}s...")
                    self._max_backoff_notice = False
                else:
                    if not self._max_backoff_notice:
                        self.log("RPC: Waiting for Discord client, Retry loop initiated (30s).")
                        self._max_backoff_notice = True
            except Exception as e:
                self._connected = False
                self.discord_running = False
                self.log(f"RPC: Failed to connect: {e}")

            await asyncio.sleep(self._backoff)
            self._backoff = min(self._backoff * 2, 30.0)

    async def _safe_close(self):
        if self._rpc and self._connected:
            try:
                await self._rpc.close()
                self.log("RPC: Connection closed gracefully.")
            except Exception as e:
                self.log(f"RPC: close() reported: {e}")

        self._connected = False
        self.discord_running = False
        self._rpc = None
        self._last_sent_payload = None  # Forces a full resend on reconnect

    def _finalize_payload(self, dynamic: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**self._base_payload, **dynamic}
        return {k: v for k, v in merged.items() if v is not None}

    def _build_payload(self, presence: Dict[str, Any], data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not presence or not presence.get("isValid"):
            return None

        match_data = presence.get("matchPresenceData", {}) or {}
        party_data = presence.get("partyPresenceData", {}) or {}

        session_state = match_data.get("sessionLoopState")
        if not session_state:
            return None

        if session_state != self._last_loop_state:
            self.start_time = time.time()
            self._last_loop_state = session_state

        if session_state == "INGAME":
            if data.get("agent") in (None, ""):
                agent_img = None
                agent = None
            else:
                agent_name = (self.colors.agent_dict.get(data.get("agent", "").lower())
                              if getattr(self.colors, "agent_dict", None) else None)
                agent = agent_name
                agent_img = agent_name.lower().replace("/", "") if agent_name else None

            gamemode = "Custom Game" if presence.get("provisioningFlow") == "CustomGame" else self.gamemodes.get(presence.get("queueId"))

            ally = presence.get("partyOwnerMatchScoreAllyTeam")
            enemy = presence.get("partyOwnerMatchScoreEnemyTeam")
            details = f"{gamemode} // {ally} - {enemy}"

            match_map = (match_data.get("matchMap") or "").lower()
            mapText = self.map_dict.get(match_map)
            if mapText == "The Range":
                mapImage = "splash_range_square"
                details = "in Range"
                agent_img = str(data.get("rank"))
                agent = data.get("rank_name")
            else:
                mi = self.map_dict.get(match_map)
                mapImage = f"splash_{mi}_square".lower() if mi else None

            if not mapText:
                mapText = None
                mapImage = None

            party_size = party_data.get("partySize")
            max_party = party_data.get("maxPartySize")

            return dict(
                state=f"In a Party ({party_size} of {max_party})",
                details=details,
                large_image=mapImage,
                large_text=mapText,
                small_image=agent_img,
                small_text=agent,
                start=int(self.start_time),
            )

        if session_state == "MENUS":
            is_idle = presence.get("isIdle")
            image = "game_icon_yellow" if is_idle else "game_icon"
            image_text = "VALORANT - Idle" if is_idle else "VALORANT - Online"

            party_access = party_data.get("partyAccessibility")
            party_string = "Open Party" if party_access == "OPEN" else "Closed Party"

            gamemode = "Custom Game" if party_data.get("partyState") == "CUSTOM_GAME_SETUP" else self.gamemodes.get(presence.get("queueId"))

            party_size = party_data.get("partySize")
            max_party = party_data.get("maxPartySize")

            return dict(
                state=f"{party_string} ({party_size} of {max_party})",
                details=f" Lobby - {gamemode}",
                large_image=image,
                large_text=image_text,
                small_image=str(data.get("rank")),
                small_text=data.get("rank_name"),
            )

        if session_state == "PREGAME":
            is_custom = presence.get("provisioningFlow") == "CustomGame" or party_data.get("partyState") == "CUSTOM_GAME_SETUP"
            gamemode = "Custom Game" if is_custom else self.gamemodes.get(presence.get("queueId"))

            match_map = (match_data.get("matchMap") or "").lower()
            mapText = self.map_dict.get(match_map)
            mapImage = f"splash_{mapText}_square".lower() if mapText else None

            party_size = party_data.get("partySize")
            max_party = party_data.get("maxPartySize")

            return dict(
                state=f"In a Party ({party_size} of {max_party})",
                details=f"Agent Select - {gamemode}",
                large_image=mapImage,
                large_text=mapText if mapText else None,
                small_image=str(data.get("rank")),
                small_text=data.get("rank_name"),
            )

        return None
