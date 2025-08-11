"""
Auto-generated __init__.py for schema types.
"""

from typing import Any, Type

from .bot_death_event import BotDeathEvent
from .game_setup import GameSetup
from .bullet_fired_event import BulletFiredEvent
from .game_resumed_event_for_observer import GameResumedEventForObserver
from .event import Event
from .tick_event_for_observer import TickEventForObserver
from .results_for_bot import ResultsForBot
from .bot_list_update import BotListUpdate
from .stop_game import StopGame
from .bot_policy_update import BotPolicyUpdate
from .color import Color
from .scanned_bot_event import ScannedBotEvent
from .pause_game import PauseGame
from .game_started_event_for_observer import GameStartedEventForObserver
from .bot_intent import BotIntent
from .message import Message
from .bot_hit_bot_event import BotHitBotEvent
from .won_round_event import WonRoundEvent
from .bullet_hit_bot_event import BulletHitBotEvent
from .bullet_hit_bullet_event import BulletHitBulletEvent
from .bot_info import BotInfo
from .bot_ready import BotReady
from .skipped_turn_event import SkippedTurnEvent
from .results_for_observer import ResultsForObserver
from .change_tps import ChangeTps
from .server_handshake import ServerHandshake
from .team_message_event import TeamMessageEvent
from .observer_handshake import ObserverHandshake
from .bot_address import BotAddress
from .hit_by_bullet_event import HitByBulletEvent
from .game_aborted_event import GameAbortedEvent
from .participant import Participant
from .team_message import TeamMessage
from .game_started_event_for_bot import GameStartedEventForBot
from .game_paused_event_for_observer import GamePausedEventForObserver
from .round_started_event import RoundStartedEvent
from .bullet_state import BulletState
from .next_turn import NextTurn
from .resume_game import ResumeGame
from .initial_position import InitialPosition
from .round_ended_event_for_observer import RoundEndedEventForObserver
from .bot_state import BotState
from .game_ended_event_for_bot import GameEndedEventForBot
from .bot_handshake import BotHandshake
from .tick_event_for_bot import TickEventForBot
from .bullet_hit_wall_event import BulletHitWallEvent
from .controller_handshake import ControllerHandshake
from .round_ended_event_for_bot import RoundEndedEventForBot
from .start_game import StartGame
from .game_ended_event_for_observer import GameEndedEventForObserver
from .tps_changed_event import TpsChangedEvent
from .bot_state_with_id import BotStateWithId
from .bot_hit_wall_event import BotHitWallEvent

__all__ = [
    "BotDeathEvent",
    "GameSetup",
    "BulletFiredEvent",
    "GameResumedEventForObserver",
    "Event",
    "TickEventForObserver",
    "ResultsForBot",
    "BotListUpdate",
    "StopGame",
    "BotPolicyUpdate",
    "Color",
    "ScannedBotEvent",
    "PauseGame",
    "GameStartedEventForObserver",
    "BotIntent",
    "Message",
    "BotHitBotEvent",
    "WonRoundEvent",
    "BulletHitBotEvent",
    "BulletHitBulletEvent",
    "BotInfo",
    "BotReady",
    "SkippedTurnEvent",
    "ResultsForObserver",
    "ChangeTps",
    "ServerHandshake",
    "TeamMessageEvent",
    "ObserverHandshake",
    "BotAddress",
    "HitByBulletEvent",
    "GameAbortedEvent",
    "Participant",
    "TeamMessage",
    "GameStartedEventForBot",
    "GamePausedEventForObserver",
    "RoundStartedEvent",
    "BulletState",
    "NextTurn",
    "ResumeGame",
    "InitialPosition",
    "RoundEndedEventForObserver",
    "BotState",
    "GameEndedEventForBot",
    "BotHandshake",
    "TickEventForBot",
    "BulletHitWallEvent",
    "ControllerHandshake",
    "RoundEndedEventForBot",
    "StartGame",
    "GameEndedEventForObserver",
    "TpsChangedEvent",
    "BotStateWithId",
    "BotHitWallEvent"
]

CLASS_MAP: dict[str, Type[Any]] = {
    "BotDeathEvent": BotDeathEvent,
    "GameSetup": GameSetup,
    "BulletFiredEvent": BulletFiredEvent,
    "GameResumedEventForObserver": GameResumedEventForObserver,
    "Event": Event,
    "TickEventForObserver": TickEventForObserver,
    "ResultsForBot": ResultsForBot,
    "BotListUpdate": BotListUpdate,
    "StopGame": StopGame,
    "BotPolicyUpdate": BotPolicyUpdate,
    "Color": Color,
    "ScannedBotEvent": ScannedBotEvent,
    "PauseGame": PauseGame,
    "GameStartedEventForObserver": GameStartedEventForObserver,
    "BotIntent": BotIntent,
    "Message": Message,
    "BotHitBotEvent": BotHitBotEvent,
    "WonRoundEvent": WonRoundEvent,
    "BulletHitBotEvent": BulletHitBotEvent,
    "BulletHitBulletEvent": BulletHitBulletEvent,
    "BotInfo": BotInfo,
    "BotReady": BotReady,
    "SkippedTurnEvent": SkippedTurnEvent,
    "ResultsForObserver": ResultsForObserver,
    "ChangeTps": ChangeTps,
    "ServerHandshake": ServerHandshake,
    "TeamMessageEvent": TeamMessageEvent,
    "ObserverHandshake": ObserverHandshake,
    "BotAddress": BotAddress,
    "HitByBulletEvent": HitByBulletEvent,
    "GameAbortedEvent": GameAbortedEvent,
    "Participant": Participant,
    "TeamMessage": TeamMessage,
    "GameStartedEventForBot": GameStartedEventForBot,
    "GamePausedEventForObserver": GamePausedEventForObserver,
    "RoundStartedEvent": RoundStartedEvent,
    "BulletState": BulletState,
    "NextTurn": NextTurn,
    "ResumeGame": ResumeGame,
    "InitialPosition": InitialPosition,
    "RoundEndedEventForObserver": RoundEndedEventForObserver,
    "BotState": BotState,
    "GameEndedEventForBot": GameEndedEventForBot,
    "BotHandshake": BotHandshake,
    "TickEventForBot": TickEventForBot,
    "BulletHitWallEvent": BulletHitWallEvent,
    "ControllerHandshake": ControllerHandshake,
    "RoundEndedEventForBot": RoundEndedEventForBot,
    "StartGame": StartGame,
    "GameEndedEventForObserver": GameEndedEventForObserver,
    "TpsChangedEvent": TpsChangedEvent,
    "BotStateWithId": BotStateWithId,
    "BotHitWallEvent": BotHitWallEvent,
}
