from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import threading

StateID = str
EventID = str

@dataclass
class Event:
    id: EventID
    payload: Any = None


@dataclass
class SessionCtx:
    session_id: str


Guard = Callable[[SessionCtx, Event], bool]
Action = Callable[[SessionCtx, Event], None]
Handler = Callable[[SessionCtx, Event], None]
Middleware = Callable[[Handler], Handler]

@dataclass
class Transition:
    from_state: StateID
    to_state: StateID
    trigger_event: EventID
    do: Optional[Action] = None
    guard: Optional[Guard] = None
    name: str = "" # for debugging only

class _TimerWheel:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._timers: Dict[str, List[threading.Timer]] = {}

    def after(self, session_id: str, delay_in_sec: float, fn: Callable[[], None]) -> Callable[[], None]:
        t = threading.Timer(delay_in_sec, fn)
        with self._lock:
            self._timers.setdefault(session_id, []).append(t)
        t.start()
        def cancel() -> None:
            t.cancel()
        return cancel

class FSM:
    def __init__(self, initial: StateID):
        self._initial = initial

        # transition_index is map[state][possible_actions] -> transition_cacndidates
        self._transition_index: Dict[StateID, Dict[EventID, List[Transition]]] = {}
        # states is map[session_id] -> current_state
        self._cur_states: Dict[str, StateID] = {}

        self._lock = threading.RLock()
        self._timer = _TimerWheel()
        self._middlewares: List[Middleware] = []

        def register(self, *transitions: Transition) -> None:
            with self._lock:
                for t in transitions:
                    # set map[state][action] -> t
                    self._transition_index.setdefault(t.from_state, {}) \
                    .setdefault(t.trigger_event, []) \
                    .append(t)

        def current_state(self, ctx: SessionCtx) -> StateID:
            with self._lock:
                st = self.cur_states.get(ctx.session_id)
            if st:
                return st
            else:
                with self._lock:
                    self._cur_states[ctx.session_id] = self._initial
                return self._initial

        def after(self, s: SessionCtx, delay_seconds: float, evt: Event) -> Callable[[], None]:
            def fire():
                s2 = SessionCtx(session_id=s.session_id)
                try:
                    self.dispatch(s2, evt)
                except Exception:
                    pass
            return self._timer.after(s.session_id, delay_seconds, fire)

        def dispatch(self, ctx: SessionCtx, evt: Event) -> None:
            cur = self.current_state(ctx)
            transition_candidates = self._match(cur, evt.id)
            if not transition_candidates:
                raise RuntimeError("no transition matched")

            def core(cctx: SessionCtx, ev: Event):
                chosen: Optional[Transition] = None
                for t in transition_candidates:
                    # TODO: try to match first valid transition
                    if t.guard is None or t.guard(cctx, ev):
                        chosen = t
                        break
                if chosen is None:
                    raise RuntimeError("no transition passed guard")

                if chosen.do:
                    chosen.do(cctx, ev)

                with self._lock:
                    self._cur_states[cctx.session_id] =  chosen.to_state

            h = core
            for mw in reversed(self._middlewares):
                h = mw(h)
            h(ctx, evt)
