raise_tool = {
    "type": "function",
    "function": {
        "name": "raise",
        "description": "A raise is a betting action in which a player increases the current bet amount, requiring "
                       "subsequent players to at least match the new higher bet to stay in the hand.",
        "parameters": {
            "type": "int",
            "properties": {
                "n_chips": {
                    "type": "int",
                    "description": "Raise your bet to a certain n_chips, must be a multiple of 10.",
                },
            },
            "required": ["n_chips"],
        },
        "strict": True
    }
}

call_tool = {
    "type": "function",
    "function": {
        "name": "call",
        "description": "A call is a betting action in which a player matches the current highest bet to stay in the hand without increasing it.",
        "strict": True
    }
}

fold_tool = {
    "type": "function",
    "function": {
        "name": "fold",
        "description": "A fold is a betting action in which a player discards their hand and forfeits any interest in "
                       "the current pot, typically due to a weak hand or excessive betting pressure.",
        "strict": True
    }
}

body_language_tool = {
    "type": "function",
    "function": {
        "name": "use_body_language",
        "description": "Use subtle body language or facial expressions to influence opponents' perception of your "
                       "hand strength."
                       "This action does not involve betting but may affect how others interpret your confidence or "
                       "hesitation."
                       "Choose behaviors that suggest weakness, strength, or uncertainty — truthfully or deceptively.",
        "parameters": {
            "type": "object",
            "properties": {
                "behavior": {
                    "type": "string",
                    "description": "The chosen body language behavior to display."
                }
            },
            "required": ["behavior"],
        },
        "strict": True
    }
}
