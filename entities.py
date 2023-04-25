dataset = [
    
    
    
    
    ("Set a reminder to buy groceries on March 24th at 2pm", {"entities": [(20, 33, "reminder_text"), (37, 46, "date"), (50, 54, "time")]}),
    ("Cancel the March 24th reminder about meeting John", {"entities": [(12, 21, "date"), (32, 45, "reminder_text")]}),
    
    
    
    
    
    
    {
        "text": "Set a reminder for today at 5 pm",
        "annotations": [
            {"start": 20, "end": 25, "label": "date"},
            {"start": 29, "end": 33, "label": "time"},
        ],
    },
    {
        "text": "Remind me to buy milk tomorrow morning",
        "annotations": [
            {"start": 22, "end": 29, "label": "date"},
            {"start": 30, "end": 36, "label": "time"},
        ],
    },
    {
        "text": "What were my reminders for yesterday?",
        "annotations": [
            {"start": 27, "end": 36, "label": "date"},
        ],
    },
]
