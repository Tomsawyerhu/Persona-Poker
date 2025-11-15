from pathlib import Path
from poker_ai.poker.ai_player import AIPlayer
from poker_ai.poker.memory import Memory
from poker_ai.poker.table import PokerTable
from poker_ai.poker.engine import PokerEngine
from poker_ai.poker.pot import Pot
import sys

# Seed so things are deterministic.
# utils.random.seed(42)

# Some settings for the amount of chips.
initial_chips_amount = 10000
small_blind_amount = 50
big_blind_amount = 100

# Create the pot.
pot = Pot()
# Instanciate six players that will make random moves, make sure
# they can reference the pot so they can add chips to it.
current_dir = Path(__file__).parent


def timestamp_filename(prefix="", ext=".txt"):
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}{ts}{ext}"


max_games, max_round = 100, 100
for game_id in range(max_games):
    players = [
        # 紧凶
        AIPlayer(
            name=f'James',
            initial_chips=initial_chips_amount,
            pot=pot,
            memory=Memory(),
            model_name='default',
            model_config=str(current_dir / "configs" / "profiles.yaml"),
            personalized_desc='You (James) are a tight-aggressive player. You are disciplined and selective, '
                              'only entering pots'
                              'with strong starting hands. You play fewer hands but bet and raise aggressively when you '
                              'do, maximizing value from your strong holdings. Your style is highly effective, '
                              'especially for beginners and professionals, as it capitalizes on well-timed aggression '
                              'while minimizing losses from weak positions.'
        ),
        # 松凶
        AIPlayer(
            name=f'Susan',
            initial_chips=initial_chips_amount,
            pot=pot,
            memory=Memory(),
            model_name='default',
            model_config=str(current_dir / "configs" / "profiles.yaml"),
            personalized_desc='You (Susan) are a loose-aggressive player. You participate in many pots and frequently uses bets '
                              'and raises to control the table. You don’t rely solely on premium cards but apply '
                              'constant pressure through bluffs and semi-bluffs, exploiting opponents’ weaknesses. While '
                              'risky, this style can be highly profitable against passive players if balanced '
                              'correctly.'
        ),
        # 紧弱
        AIPlayer(
            name=f'David',
            initial_chips=initial_chips_amount,
            pot=pot,
            memory=Memory(),
            model_name='qwen3-max-1',
            model_config=str(current_dir / "configs" / "profiles.yaml"),
            personalized_desc='You (David) are a tight-passive player. You enter very few hands and tends to call '
                              'rather than'
                              'raise, avoiding confrontation unless holding a strong made hand. You rarely bluff and '
                              'prefer safety over aggression, often checking or calling down to showdown. Though hard to '
                              'exploit, this predictable style can miss opportunities to win pots without the best hand.'
        ),

        # ✅ 新增第4位：Lily - Fish
        AIPlayer(
            name=f'Lily',
            initial_chips=initial_chips_amount,
            pot=pot,
            memory=Memory(),
            model_name='qwen3-max-1',
            model_config=str(current_dir / "configs" / "profiles.yaml"),
            personalized_desc="You (Lily) are an aggressive player who loves action and rarely folds. You enjoy putting pressure on opponents "
                              "with raises and continuation bets, especially from late position. While you're willing to play many starting hands, "
                              "you don't go all-in blindly — instead, you use well-timed large bets to make opponents doubt their medium-strength hands. "

                              "When short-stacked or when you sense weakness, you’re not afraid to shove all-in as a bluff. But with deep stacks, "
                              "you prefer to build the pot gradually and extract value when you hit. Your motto is still: 'If I'm not committed, "
                              "I'm not trying' —"
                              "but you define 'committed' as controlling the hand, not just going all-in preflop."

        ),

        # ✅ 新增第5位：Ethan - The Calling Station（跟注站）
        AIPlayer(
            name=f'Ethan',
            initial_chips=initial_chips_amount,
            pot=pot,
            memory=Memory(),
            model_name='qwen3-max-2',
            model_config=str(current_dir / "configs" / "profiles.yaml"),
            personalized_desc="You (Ethan) are a calling station who hates folding — but only when you have some equity. You believe 'the river tells all,' "
                              "so you always see five cards if you enter the pot with a pair, draw, or high-card potential like top kicker. "
                              "You will call down to showdown with middle pair or flush draws, but you won’t call massive overbets with complete air. "

                              "You rarely raise or bluff, preferring to let others bet while you observe. If someone shoves all-in for 10x the pot on a scary board, "
                              "you’ll consider whether that makes sense — even if you have top pair. You lose small pots chasing weak hands, "
                              "but you also win big ones when your gut tells you someone is bluffing."

        ),

        # ✅ 新增第6位：Olivia - The Ultimate Nit（极致保守）
        AIPlayer(
            name=f'Olivia',
            initial_chips=initial_chips_amount,
            pot=pot,
            memory=Memory(),
            model_name='qwen3-max-2',
            model_config=str(current_dir / "configs" / "profiles.yaml"),
            personalized_desc="You (Olivia) are an ultra-tight player. You fold over 90% of hands pre-flop, only playing premium holdings: "
                              "pocket pairs 99+, suited AK/AQ/KQ, or strong broadway connectors like KQs and QJs. Your table image is extremely tight, "
                              "so when you finally enter a pot, opponents immediately suspect you have a monster. "

                              "Because of this, you don't need to bluff — your actions naturally carry weight. When you do play, you act with confidence: "
                              "you raise instead of call, and bet for value on every street. If you hit a strong hand (top pair+, draw, or set), "
                              "you build the pot purposefully. You never chase draws, but if you have equity, you let your opponents pay you off. "

                              "Your motto: 'Patience is power. One hand is all it takes.' You may fold 20 times in a row, but the moment you find AA or QQ, "
                              "you’re ready to go all-in and take down the entire stack of anyone brave enough to challenge you. "
                              "Opponents respect you — not because you're aggressive, but because they know: when Olivia plays, she wins."

        ),
        # ✅ 新增第7位：Alex - The Reg（职业牌手）
        AIPlayer(
            name=f'Alex',
            initial_chips=initial_chips_amount,
            pot=pot,
            memory=Memory(),
            model_name='qwen3-max-3',
            model_config=str(current_dir / "configs" / "profiles.yaml"),
            personalized_desc=(
                "You (Alex) are a professional-level balanced player — a 'reg' (regular). You don't stick to one rigid style. "
                "Instead, you adapt based on your opponents' tendencies. You play tight against maniacs, loosen up against nits, "
                "and apply maximum pressure on calling stations. "

                "Your pre-flop range is well-constructed: you open-limp rarely, prefer raising from late position, "
                "and 3-bet light when facing frequent stealers. You understand equity, blockers, and board coverage. "
                "You mix value bets with well-timed bluffs, making your range unpredictable. "

                "On the flop, you assess whether the board favors your range or your opponent’s. If it hits you hard, "
                "you bet big. If it misses, you may check-fold — or occasionally double-barrel bluff if your opponent shows weakness. "

                "You respect strong players like Olivia, but you see players like Lily and Ethan as profit centers. "
                "Your motto: 'It’s not about the cards — it’s about the player across from you.' "
                "You win not by luck, but by outthinking everyone at the table."
            )
        ),
        # ✅ 新增第8位：Mia - The Shark（顶级捕食者）
        AIPlayer(
            name=f'Mia',
            initial_chips=initial_chips_amount,
            pot=pot,
            memory=Memory(),
            model_name='qwen3-max-3',
            model_config=str(current_dir / "configs" / "profiles.yaml"),
            personalized_desc=(
                "You (Mia) are a shark — one of the most dangerous players at the table. You let loose players splash around, "
                "then quietly trap them when they overplay their hands. You watch patterns: who bluffs too much, "
                "who calls too wide, who folds to aggression. Then you strike. "

                "You love position. From the button or cutoff, you raise with suited connectors, small pairs, and broadways — "
                "not because they’re strong, but because you can control the pot. On the flop, you continuation bet "
                "aggressively,"
                "but you’re quick to give up if re-raised — unless you have a draw or monster. "

                "Your secret weapon is the check-raise bluff on scary boards (like K-Q-J or flush draws). "
                "When a maniac like Lily bets big, you might slow-play AA or sets, then explode on the turn. "
                "You don’t mind folding preflop — you’d rather wait for a spot where you have both cards and position. "

                "You’re not reckless. You’re surgical. You don’t fight for every pot — only the ones you can win without showdown. "
                "Your motto: 'Fish create the money. Sharks take it. I am the shark.'"
            )
        )

    ]

    idx = game_id % len(players)
    players = players[idx:] + players[:idx]
    # Create the table with the players on it.
    table = PokerTable(players=players, pot=pot)
    # Create the engine that will manage the poker game lifecycle.
    file_name=timestamp_filename(prefix=f'eight-player-game-{game_id + 1}')
    engine = PokerEngine(
        table=table,
        small_blind=small_blind_amount,
        big_blind=big_blind_amount,
        trace_file=f"trace/eight_players/{file_name.replace('.txt','.jsonl')}")
    # 打开日志文件
    with open(f'logs/eight_players/{file_name}', 'w', encoding='utf-8') as f:
        # 保存原始 stdout
        original_stdout = sys.stdout
        # 重定向 stdout 到文件
        sys.stdout = f
        for round_id in range(max_round):
            try:
                print('=' * 80)
                print(f'Round {round_id + 1} Start')
                print('=' * 80)
                engine.play_one_round()
                print('=' * 80)
                print(f'Round {round_id + 1} End')
                print('=' * 80)
                print('\n\n')
            except Exception as e:
                print(e)
                break

    # 恢复 stdout
    sys.stdout = original_stdout
