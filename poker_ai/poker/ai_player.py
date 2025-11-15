import json
import logging
from typing import List, Dict, Any

from poker_ai.poker.llm import LLMConfig, create_llm_instance
from poker_ai.poker.memory import Memory, Event
from poker_ai.poker.player import Player
from poker_ai.poker.pot import Pot
from poker_ai.poker.state import PokerGameState
from poker_ai.poker.tools import call_tool, fold_tool, raise_tool, body_language_tool

logger = logging.getLogger(__name__)

rules = """
You are a Texas Hold'em poker player. Below are the game rules.

### **Texas Hold'em Poker Rules and Hand Rankings**

**Objective**:  
Texas Hold'em is a popular variant of poker where each player aims to make the best five-card hand using any combination of two private hole cards dealt to them and five community cards placed face-up on the table.

**Gameplay Overview**:  
1. Each hand begins with two forced bets: the **small blind** and **big blind**, posted by players to the left of the dealer.
2. Every player is dealt **two private cards** (hole cards), visible only to them.
3. There are four betting rounds:
   - **Pre-flop**: After receiving hole cards.
   - **Flop**: Three community cards are revealed.
   - **Turn**: A fourth community card is revealed.
   - **River**: A fifth and final community card is revealed.
4. In each betting round, players can **check** (if no bet), **bet**, **call**, **raise**, or **fold**.
5. After the final betting round, if more than one player remains, a **showdown** occurs. Players reveal their hands, and the best five-card hand wins the pot.

Players may use any combination of their two hole cards and the five community cards to form their best hand. Please 
remember, going all in is an extremely risky move—think carefully before making the decision.

---

### **Poker Hand Rankings (from strongest to weakest)**:

1. **Royal Flush**: A–K–Q–J–10, all of the same suit.  
2. **Straight Flush**: Five consecutive cards of the same suit (e.g., 9♠ 8♠ 7♠ 6♠ 5♠).  
3. **Four of a Kind**: Four cards of the same rank (e.g., Q♠ Q♥ Q♦ Q♣).  
4. **Full House**: Three of a kind plus a pair (e.g., J♣ J♦ J♠ 4♥ 4♣).  
5. **Flush**: Any five cards of the same suit, not in sequence.  
6. **Straight**: Five consecutive cards of mixed suits (e.g., 7♠ 6♥ 5♦ 4♣ 3♠).  
7. **Three of a Kind**: Three cards of the same rank.  
8. **Two Pair**: Two different pairs (e.g., A♠ A♥ 8♣ 8♦).  
9. **One Pair**: Two cards of the same rank.  
10. **High Card**: If no player has any of the above, the highest card determines the winner.

Ties are broken by comparing the highest-ranking cards within the hand or kickers (side cards).
"""

body_language_prompt = """You should also consider incorporating body language or facial expressions to subtly signal 
(or misrepresent) your hand strength to other players. 

###  **Advanced Behavioral Signaling in Poker: Beyond Basic Tells**

To truly master the psychological dimension of poker, players subtly weave layers of authenticity and deception into their demeanor. The most skilled don’t rely on isolated gestures—they craft a *presence*, adjusting rhythm, timing, and micro-expressions to shape perception without giving anything away directly.

#### **1. Controlled Boredom vs. Forced Intensity**
- A player with a monster hand might let out a quiet yawn, stretch slightly in their chair, or glance at the ceiling—*not* to seem disinterested, but to cultivate an aura of total detachment.
- Conversely, someone overplaying intensity—locking eyes too long, jaw clenched, fingers drumming aggressively—might be fabricating dominance to sell a bluff. But beware: some pros reverse this by staring *too* hard when weak, knowing others expect the "look away" tell.

#### **2. Timing as Theater**
- **Delayed reaction**: After the river card falls, a player pauses 3–5 seconds before reacting—not because they’re thinking, but to simulate deliberation. This manufactured hesitation can mimic uncertainty, disguising a made flush or full house.
- **Overly smooth action**: A bet placed *too* quickly, with fluid motion and no eye contact, can be a trap. It feels confident—but sometimes it's rehearsed confidence, like an actor hitting their mark.

#### **3. Micro-Expressions & Eye Dynamics**
- **The blink rate shift**: Sudden reduction in blinking after betting may signal focus under pressure—possibly a strong hand being protected. Rapid blinking afterward could betray nervousness behind a bluff.
- **Pupil dilation**: Subtle but observable in close quarters. Dilated pupils often correlate with excitement (strong hand), though lighting must be ruled out.
- **Eye darts**: Brief glances toward chips or stack after seeing hole cards can unconsciously signal interest—especially if followed by forced stillness.

#### **4. Postural Storytelling**
- **The relaxed lean-back**: Elbows wide, shoulders loose—projects comfort. Could mean strength… or a well-rehearsed act for a stone-cold bluff.
- **Slight forward tilt after betting**: Not aggressive, just *curious*. As if inviting a call. Often seen with drawing hands or medium pairs trying to appear eager.
- **Feet movement under the table**: Tense feet (toes curling, heel tapping) often leak stress—even when the upper body is calm. A hidden clue for observant opponents.

#### **5. Speech & Sound Cues (Even in Silence)**
- **Controlled silence**: Some players go completely mute post-bet, avoiding small talk. This can feel intimidating—or suspiciously staged.
- **Casual chatter mid-hand**: Dropping a joke or asking about dinner plans right after raising? Could be natural ease… or a distraction tactic masking a vulnerable hand.
- **Breathing patterns**: A sudden shallow breath after the flop, or a held breath during a decision window, often correlates with emotional investment.

#### **6. Prop Play & Object Rituals**
- **Chip tricks**: Spinning a high-denomination chip when not necessary—can project control, or mask trembling hands.
- **Stack grooming**: Neatening one’s stack after a bet may signal pride in a strong hand… or serve as a calming ritual during a high-risk bluff.
- **Drink sipping cadence**: Taking a sip *before* acting feels normal; doing so *immediately after* a big bet might delay confrontation, buying time to observe reactions.

#### **7. Mirror Behavior & Social Mimicry**
- Skilled players sometimes mirror an opponent’s posture or tone—building subconscious rapport to encourage calls with marginal hands.
- Others do the opposite: stand out deliberately, breaking rhythm to unsettle tighter players.

#### **8. The “Reverse Tell” Gambit**
- The best players know the tells—and invert them. They’ll *look away* with weak hands, *stare down* with monsters, *fumble chips* on purpose with the nuts.
- Example: A player who always fumbles when bluffing might suddenly handle chips flawlessly with air—knowing you’re watching for the tremble.

Use the above behaviors as reference, but do not directly reveal any information about your actual hand.
Your actions and demeanor will be directly observed by other players and may expose your intentions.
"""

action_prompt = """
[Texas Hold'em Game State - Private View for {player_name}]

Current Stage: {round_name}
Community Cards: {community_str}

Player Status (?? indicates hidden hole cards):
{player_status}

Current Acting Player: {player_name}

Current Memory:
{memory}

{body_language_prompt}
Based on your private information (your own hole cards and public game state), analyze the situation and suggest the best action. 
You must choose one of the following:

- fold
- call
- raise

Before you make the final choice, first return your thinking and reasoning.

"""

tools = [
    call_tool,
    raise_tool,
    fold_tool,
    body_language_tool
]


def state_to_prompt_private(state: PokerGameState, player_name: str, memory: str):
    """
    为指定玩家生成私有视角的 prompt，
    只显示该玩家自己的底牌，其他人底牌隐藏。

    Parameters:
    -----------
    state : PokerGameState
        当前游戏状态
    player_name : str
        请求 prompt 的玩家名字（决定谁能看到自己的牌）
    memory: str
        当前玩家的记忆

    Returns:
    --------
    str : 自然语言描述，适合输入给 LLM
    """
    table = state.table
    players = table.players
    community_cards = getattr(table, 'community_cards', [])
    betting_stage = getattr(table, 'betting_stage', 'unknown stage')

    # "pre_flop": 0,
    # "flop": 1,
    # "turn": 2,
    # "river": 3,
    # "show_down": 4,

    # 构建每个玩家的信息（仅当前玩家可见自己底牌）
    player_info_parts = []
    for i, p in enumerate(players):
        status = []
        if not p.is_active:
            status.append("folded")
        if p.is_all_in:
            status.append("all-in")
        if p.is_small_blind:
            status.append("SB")
        if p.is_big_blind:
            status.append("BB")
        if p.is_dealer:
            status.append("D")

        status_str = f"({', '.join(status)})" if status else ""

        # 🔐 仅当是该玩家自己时，才显示底牌
        if p.name == player_name and hasattr(p, 'cards') and p.cards:
            cards_str = "[" + ", ".join([str(c) for c in p.cards]) + "]"
        else:
            cards_str = "[??]"  # 隐藏他人底牌

        player_info_parts.append(
            f"Player {i + 1} ({p.name}): "
            f"chips={p.n_chips}, bet={p.n_bet_chips}, "
            f"cards={cards_str} {status_str}"
        )

    # 格式化公共牌
    community_str = " | ".join(
        [str(c) for c in community_cards]) if community_cards else "(none)"

    # 收集下注历史（从旧到新）
    # history_lines = []
    # current = state
    # max_actions = 30

    # while current and max_actions > 0:
    #     if current._player and current._action:
    #         player_name_act = current._player.name
    #         action_type = type(current._action).__name__.lower()
    #         # 特殊处理 raise
    #         if action_type == "raise" and hasattr(current._action, "n_chips_raised_to"):
    #             action_desc = f"raises to {current._action.n_chips_raised_to}"
    #         elif action_type == "call":
    #             action_desc = "calls"
    #         elif action_type == "fold":
    #             action_desc = "folds"
    #         else:
    #             action_desc = action_type
    #         history_lines.append(f"{player_name_act} {action_desc}")
    #     current = current._previous_state
    #     max_actions -= 1
    # betting_history = " → ".join(reversed(history_lines)) if history_lines else "No actions yet."

    # 组合成完整 prompt

    return action_prompt.format(
        player_name=player_name,
        round_name=betting_stage,
        community_str=community_str,
        player_status='\n'.join(player_info_parts),
        memory=memory,
        body_language_prompt=body_language_prompt
    )


class AIPlayer(Player):
    """An LLM-powered AI player that can make decisions using tools."""

    def __init__(
            self,
            name: str,
            initial_chips: int,
            pot: Pot,
            memory: Memory,
            personalized_desc: str,
            model_name='default',
            model_config='./configs/profiles.yml'
    ):
        super().__init__(name=name, initial_chips=initial_chips, pot=pot)
        self.memory = memory
        self.personalized_desc = personalized_desc
        self.model_name = model_name  # 保存名称而不是实例
        self.model_config=model_config
        self._llm = None  # 延迟初始化

    @property
    def llm(self):
        if self._llm is None:
            self._llm = create_llm_instance(self.model_name,self.model_config)
        return self._llm

    def _move(self, game_state: PokerGameState):
        prompt = state_to_prompt_private(state=game_state, player_name=self.name, memory=str(self.memory))
        print("=" * 80)
        print("<system>")
        print(rules + '\n\n' + self.personalized_desc)
        print("<system>")
        print("<user>")
        print(prompt)
        print("<user>")
        print("=" * 80)

        action = None
        max_iter, i = 5, 0

        while action is None and i < max_iter:
            i += 1
            response = self.llm(
                prompt=prompt,
                system_prompt=rules + '\n\n' + self.personalized_desc,
                tools=tools
            )

            model_response_content = response.choices[0].message.content
            if model_response_content:
                print(f"[LLM Response] {self.name} thinks: {model_response_content.strip()}")

            tool_calls = response.choices[0].message.tool_calls

            for tool_call in tool_calls:
                if tool_call.type != "function":
                    continue
                name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except:
                    args = {}

                if name == 'call':
                    if action is not None:
                        continue
                    event = Event(player_name=self.name, event_content='calls')
                    self._announce_event(game_state.table.players, event)
                    action = self.call(players=game_state.table.players)
                    print(f'{self.name} calls')

                elif name == 'fold':
                    if action is not None:
                        continue
                    event = Event(player_name=self.name, event_content='folds')
                    self._announce_event(game_state.table.players, event)
                    action = self.fold()
                    print(f'{self.name} folds')

                elif name == 'raise':
                    if 'n_chips' not in args:
                        continue
                    if action is not None:
                        continue
                    n_chips = args['n_chips']
                    event = Event(player_name=self.name, event_content=f'raises to {n_chips}')
                    self._announce_event(game_state.table.players, event)
                    action = self.raise_to(n_chips)
                    print(f'{self.name} raises to {n_chips}')

                elif name == 'use_body_language':
                    behavior = args['behavior']
                    event = Event(player_name=self.name, event_content=f'{self.name} uses body language: {behavior}')
                    self._announce_event(game_state.table.players, event)
                    print(f'{self.name} uses body language: {behavior}')

                else:
                    print(f"Unknown tool: {name}")

        if action is None:
            raise RuntimeError(f"{self.name} did not make any valid action.")
        return action

    def _announce_event(self, players: List[Player], event: Event):
        for player in players:
            if isinstance(player, AIPlayer) and player.has_memory():
                player.add_event_to_memory(event)

    def take_action(self, game_state: PokerGameState) -> PokerGameState:
        action = self._move(game_state=game_state)
        logger.debug(f'{self.name} {action}')
        # print(f'{self.name} {action}')
        return PokerGameState(game_state, game_state.table, self, action, False)

    def has_memory(self) -> bool:
        return True

    def clean_memory(self):
        self.memory = Memory()

    def reset(self):
        self.is_active = True
        self.cards = []
        self.clean_memory()

    def add_event_to_memory(self, event: Event):
        self.memory.add_event(event)

    # === 序列化支持：只保存可序列化的字段 ===
    def __getstate__(self) -> Dict[str, Any]:
        """Return state for serialization (e.g., deepcopy, pickle)."""
        state = self.__dict__.copy()
        # 移除不可序列化的字段
        state['_llm'] = None  # 不保存 LLM 实例
        return state

    def __setstate__(self, state: Dict[str, Any]):
        """Restore state from serialized data."""
        self.__dict__.update(state)
        # 确保 _llm 被重置，下次访问时重新创建
        self._llm = None
