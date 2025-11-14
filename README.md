# Persona-Poker: A Multi Agent Framework for Personalized Texas Hold em Playing Styles

## Introduction
While extensive research on Texas Hold’em has focused on game-theoretic optimal (GTO) strategies and computational approaches to decision-making, this work shifts the focus from pure strategy optimization to the impact of personalized behavior on player performance. Personalization encompasses a wide range of human-like attributes, including playing style (e.g., tight-aggressive or loose-passive), betting patterns, timing behavior, and even non-verbal cues such as facial expressions and body language—elements that are critical in real-world poker but often overlooked in traditional AI models.

To this end, we propose a personalized multi-agent framework in which each agent is endowed with distinct behavioral profiles and strategic tendencies that reflect diverse human playing styles. We further enhance the agents with memory mechanisms and context-aware decision-making modules, enabling them to adapt their actions based on historical interactions, table dynamics, and opponent behaviors. By simulating realistic psychological and strategic dimensions, our approach not only improves the believability of agent behavior but also allows for in-depth analysis of how personalization influences bluffing effectiveness, exploitability, and long-term performance in multi-agent Texas Hold’em environments.

## Run

1. Build your own config under **configs/profiles.yaml**

2. Follow the demo in run.py to design serveral agents. Below is a demo agent.

```python
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
        ),...
]
```

3. Run the script.

```bash
python run.py
```
