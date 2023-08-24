# RemindMe! ChatBot
This project focuses on the development of a Reminder Chatbot with the aim of providing users with a convenient solution to set reminders, manage events, and receive timely notifications. The chatbot is designed to be user-friendly, easily accessible, and scalable to accommodate a growing user base. Key functionalities include the ability to set and delete reminders and events, as well as listing all active reminders and events for each user. The development plan encompasses various stages, including defining the purpose and scope of the project, designing data structures, preprocessing and tokenizing text input, creating a simple Natural Language Processing (NLP) model, defining intents and entities, implementing intent recognition and entity extraction, and developing the conversation flow. For data training, a Feed Forward Neural Network with the Adam optimizer and Cross-Entropy Loss function is utilized. Preprocessing techniques such as data cleaning, tokenization, and bag of words methods are employed. The project uses a JSON file containing a list of dictionaries as the dataset to create a responsive and context-aware chatbot.

In the evaluation of the chatbot, two distinct datasets were utilized to assess its performance in terms of accuracy and loss. The NER training, which focused on Named Entity Recognition, achieved an overall accuracy of 88% with a loss of 0.41. On the other hand, the intent training, which aimed at intent recognition, achieved an accuracy of 91% with a loss of 0.35. These results demonstrate improvements in accuracy and reductions in loss, indicating the chatbot's ability to learn and adapt to the provided training data.

However, it is worth noting that the chatbot faced challenges in accurately extracting entities and correctly incorporating them into the generated responses
