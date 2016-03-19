# Ideas

## Data Structures

### Question
- Attributes
  - Text: string
  - Choices: [string]
  - Correct choice: int
  - Time limit: int

### User
- Attributes
  - Name
  - Picture
  - Fbid
- Actions on app
  - Invite user to quiz
  - Answer question

### Quiz
- Attributes
  - Questions: [Question(9)]
  - Users: [User]
  - Winner: User


## Some notes on the server:

- Register the cellphones in GCM
- Send push notifications when receiving an answer
- Generate questions based on models provided by Aran and Roger
- Generate a leaderboard with your friends
