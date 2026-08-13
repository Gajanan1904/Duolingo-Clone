# Duolingo Clone — Frontend API Contract

## Status

**FINAL — Chat 4 REST API + Contract Verification**

This document is the frontend-facing API contract for the Duolingo Clone backend.

The frontend must use the endpoints and field names documented here.

The frontend must NOT invent:

- endpoint names
- request fields
- response fields
- XP values
- heart values
- progress values
- crown values
- streak values
- completion state
- skill unlocking state

Django remains authoritative for all learning and gamification state.

---

# 1. Base API

Base path:

```text
/api/
```

All API responses use JSON unless otherwise noted.

---

# 2. Authentication / Demo User

The current assignment uses Django's built-in User model and a simplified authenticated demo-user flow.

The seeded demo learner is:

```text
username: demo_user
```

The API endpoints require an authenticated user.

For the current demo/development environment, authentication is established through Django session authentication.

Unauthenticated requests return:

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication is required."
  }
}
```

HTTP status:

```text
401 Unauthorized
```

There is no frontend authentication endpoint included in the current Chat 4 API scope.

---

# 3. Common Error Contract

All API errors use:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

Possible domain/API error codes include:

```text
INVALID_REQUEST
UNAUTHORIZED
NOT_FOUND
LESSON_NOT_FOUND
EXERCISE_NOT_FOUND
INVALID_EXERCISE
INVALID_ANSWER
OUT_OF_HEARTS
LESSON_ALREADY_COMPLETED
LESSON_NOT_COMPLETED
SKILL_LOCKED
INVALID_ATTEMPT
```

Important:

The existing Chat 3 domain behavior returns:

```text
INVALID_ATTEMPT
```

when a lesson attempt fails because hearts are exhausted.

Example:

```json
{
  "error": {
    "code": "INVALID_ATTEMPT",
    "message": "Lesson attempt has failed because hearts are exhausted."
  }
}
```

The frontend must handle the actual returned error code rather than assuming every heart-related failure is `OUT_OF_HEARTS`.

---

# 4. GET /api/path/

## Purpose

Returns the authenticated learner's complete learning path.

The response contains:

- course
- units
- skills
- skill status
- progress
- crowns
- lesson counts

## Request

```http
GET /api/path/
```

Request body:

```text
None
```

## Success

HTTP:

```text
200 OK
```

Example:

```json
{
  "course": {
    "id": 1,
    "name": "Spanish",
    "source_language": "English",
    "target_language": "Spanish"
  },
  "units": [
    {
      "id": 1,
      "title": "Basics",
      "description": "Learn basic Spanish",
      "order": 1,
      "skills": [
        {
          "id": 1,
          "title": "Greetings",
          "description": "Basic greetings",
          "order": 1,
          "status": "completed",
          "progress": 100,
          "crowns": 3,
          "total_lessons": 1,
          "completed_lessons": 1
        },
        {
          "id": 2,
          "title": "Introductions",
          "description": "Introduce yourself in Spanish",
          "order": 2,
          "status": "in_progress",
          "progress": 40,
          "crowns": 2,
          "total_lessons": 1,
          "completed_lessons": 0
        }
      ]
    },
    {
      "id": 2,
      "title": "Food",
      "description": "Learn Spanish words for food and drinks",
      "order": 2,
      "skills": [
        {
          "id": 3,
          "title": "Common Foods",
          "description": "Common food vocabulary",
          "order": 1,
          "status": "locked",
          "progress": 0,
          "crowns": 0,
          "total_lessons": 1,
          "completed_lessons": 0
        },
        {
          "id": 4,
          "title": "Drinks",
          "description": "Common drink vocabulary",
          "order": 2,
          "status": "locked",
          "progress": 0,
          "crowns": 0,
          "total_lessons": 1,
          "completed_lessons": 0
        }
      ]
    }
  ]
}
```

## Field types

### Course

| Field | Type |
|---|---|
| id | integer |
| name | string |
| source_language | string |
| target_language | string |

### Unit

| Field | Type |
|---|---|
| id | integer |
| title | string |
| description | string |
| order | integer |
| skills | array |

### Skill

| Field | Type |
|---|---|
| id | integer |
| title | string |
| description | string |
| order | integer |
| status | string enum |
| progress | integer |
| crowns | integer |
| total_lessons | integer |
| completed_lessons | integer |

### Skill status enum

```text
locked
in_progress
completed
```

Progress range:

```text
0–100
```

Crowns:

```text
0 or greater
```

## Errors

### Unauthorized

HTTP:

```text
401
```

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication is required."
  }
}
```

---

# 5. GET /api/lessons/{lesson_id}/

## Purpose

Returns playable lesson data.

The response is intentionally safe for frontend consumption.

### SECURITY REQUIREMENT

`correct_answer` MUST NEVER appear in this response.

The frontend must determine what UI to render using:

- type
- question
- data
- order

The frontend must submit the user's answer to the answer endpoint.

## Request

```http
GET /api/lessons/{lesson_id}/
```

Request body:

```text
None
```

Example:

```text
GET /api/lessons/2/
```

## Success

HTTP:

```text
200 OK
```

Example:

```json
{
  "id": 2,
  "title": "Basic Introductions",
  "skill_id": 2,
  "xp_reward": 10,
  "total_exercises": 6,
  "exercises": [
    {
      "id": 7,
      "type": "multiple_choice",
      "question": "What does 'Hola' mean?",
      "data": {
        "options": [
          "Hello",
          "Goodbye",
          "Thanks",
          "Please"
        ]
      },
      "order": 1
    },
    {
      "id": 8,
      "type": "translate",
      "question": "Translate: Hello",
      "data": {
        "source_text": "Hello"
      },
      "order": 2
    },
    {
      "id": 9,
      "type": "word_bank",
      "question": "Build the Spanish sentence",
      "data": {
        "words": [
          "Yo",
          "como",
          "una",
          "manzana"
        ]
      },
      "order": 3
    },
    {
      "id": 10,
      "type": "match_pairs",
      "question": "Match the words",
      "data": {
        "pairs": [
          {
            "id": "1",
            "left": "Hello",
            "right": "Hola"
          },
          {
            "id": "2",
            "left": "Goodbye",
            "right": "Adiós"
          }
        ]
      },
      "order": 4
    },
    {
      "id": 11,
      "type": "fill_blank",
      "question": "Yo ___ una manzana.",
      "data": {},
      "order": 5
    },
    {
      "id": 12,
      "type": "type_answer",
      "question": "Translate: Thank you",
      "data": {
        "source_text": "Thank you"
      },
      "order": 6
    }
  ]
}
```

## Lesson fields

| Field | Type |
|---|---|
| id | integer |
| title | string |
| skill_id | integer |
| xp_reward | integer |
| total_exercises | integer |
| exercises | array |

## Exercise fields

| Field | Type |
|---|---|
| id | integer |
| type | string enum |
| question | string |
| data | object |
| order | integer |

## Exercise type enum

```text
multiple_choice
translate
word_bank
match_pairs
fill_blank
type_answer
```

`data` is an object whose contents depend on the exercise type.

The frontend should use the exercise `type` to determine the appropriate UI.

## Forbidden field

The following field MUST NOT be present:

```text
correct_answer
```

## Lesson not found

HTTP:

```text
404
```

```json
{
  "error": {
    "code": "LESSON_NOT_FOUND",
    "message": "Lesson does not exist."
  }
}
```

---

# 6. POST /api/lessons/{lesson_id}/answer/

## Purpose

Submits one exercise answer.

The backend evaluates the answer using the existing LessonService.

The client must NOT submit authoritative:

- XP
- hearts
- progress
- crowns
- streak
- completion state

## Request

```http
POST /api/lessons/{lesson_id}/answer/
```

Example:

```text
POST /api/lessons/2/answer/
```

Content-Type:

```text
application/json
```

## Request JSON

The verified API request shape is:

```json
{
  "exercise_id": 7,
  "answer": {
    "value": "Hello"
  }
}
```

### Fields

| Field | Type | Required |
|---|---|---|
| exercise_id | integer | yes |
| answer | object | yes |
| answer.value | string | yes for the currently seeded answer flow |

The frontend must send only the answer data necessary to evaluate the exercise.

## Success

HTTP:

```text
200 OK
```

### Correct answer example

```json
{
  "correct": true,
  "exercise_id": 7,
  "feedback": {
    "message": "Correct!"
  },
  "hearts": {
    "current": 5,
    "max": 5
  },
  "lesson": {
    "status": "in_progress"
  }
}
```

### Wrong answer example

```json
{
  "correct": false,
  "exercise_id": 8,
  "feedback": {
    "message": "Not quite."
  },
  "hearts": {
    "current": 4,
    "max": 5
  },
  "lesson": {
    "status": "in_progress"
  }
}
```

## Response fields

| Field | Type |
|---|---|
| correct | boolean |
| exercise_id | integer |
| feedback | object |
| feedback.message | string |
| hearts | object |
| hearts.current | integer |
| hearts.max | integer |
| lesson | object |
| lesson.status | string |

Lesson status currently used by the API:

```text
in_progress
completed
```

## Important behavior

A wrong answer reduces hearts through Chat 3 business logic.

The frontend must NOT calculate or modify hearts itself.

The backend is authoritative.

## Invalid request

HTTP:

```text
400
```

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request payload."
  }
}
```

## Out of hearts / failed attempt

The existing domain behavior returns:

HTTP:

```text
400
```

```json
{
  "error": {
    "code": "INVALID_ATTEMPT",
    "message": "Lesson attempt has failed because hearts are exhausted."
  }
}
```

## Unauthorized

HTTP:

```text
401
```

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication is required."
  }
}
```

---

# 7. POST /api/lessons/{lesson_id}/complete/

## Purpose

Completes a lesson after all required exercises have been answered.

The backend performs:

- lesson completion
- XP reward
- skill progress
- crowns
- skill status
- streak/daily XP updates
- other authoritative state changes

The frontend must not calculate these values.

## Request

```http
POST /api/lessons/{lesson_id}/complete/
```

Content-Type:

```text
application/json
```

## Request JSON

```json
{
  "attempt_id": 4
}
```

| Field | Type | Required |
|---|---|---|
| attempt_id | integer | yes |

The `attempt_id` identifies the active lesson attempt.

## Successful response

HTTP:

```text
200 OK
```

Example:

```json
{
  "success": true,
  "lesson": {
    "id": 2,
    "status": "completed"
  },
  "rewards": {
    "xp_earned": 10
  },
  "skill": {
    "id": 2,
    "progress": 100,
    "crowns": 1,
    "status": "completed"
  },
  "stats": {
    "total_xp": 260,
    "daily_xp": 30,
    "daily_xp_goal": 20,
    "current_streak": 5,
    "hearts": 5
  }
}
```

## Response fields

| Field | Type |
|---|---|
| success | boolean |
| lesson | object |
| lesson.id | integer |
| lesson.status | string |
| rewards | object |
| rewards.xp_earned | integer |
| skill | object |
| skill.id | integer |
| skill.progress | integer |
| skill.crowns | integer |
| skill.status | string |
| stats | object |
| stats.total_xp | integer |
| stats.daily_xp | integer |
| stats.daily_xp_goal | integer |
| stats.current_streak | integer |
| stats.hearts | integer |

Skill status enum:

```text
locked
in_progress
completed
```

## Incomplete lesson

HTTP:

```text
400
```

```json
{
  "error": {
    "code": "LESSON_NOT_COMPLETED",
    "message": "Lesson completion requirements have not been met."
  }
}
```

## Already completed

HTTP:

```text
400
```

```json
{
  "error": {
    "code": "LESSON_ALREADY_COMPLETED",
    "message": "Lesson has already been completed."
  }
}
```

Calling completion again must NOT award duplicate XP.

## Invalid attempt

HTTP:

```text
400
```

```json
{
  "error": {
    "code": "INVALID_ATTEMPT",
    "message": "Lesson attempt is invalid or unavailable."
  }
}
```

## Unauthorized

HTTP:

```text
401
```

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication is required."
  }
}
```

---

# 8. GET /api/profile/

## Purpose

Returns the authenticated learner's profile summary.

## Request

```http
GET /api/profile/
```

Request body:

```text
None
```

## Success

HTTP:

```text
200 OK
```

Example:

```json
{
  "user": {
    "id": 1,
    "username": "demo_user",
    "first_name": "Demo",
    "last_name": "Learner"
  },
  "stats": {
    "total_xp": 260,
    "current_streak": 1,
    "longest_streak": 5,
    "daily_xp": 30,
    "daily_xp_goal": 20,
    "hearts": 4,
    "max_hearts": 5
  },
  "progress": {
    "skills_completed": 1,
    "lessons_completed": 1
  }
}
```

## Fields

### User

| Field | Type |
|---|---|
| id | integer |
| username | string |
| first_name | string |
| last_name | string |

### Stats

| Field | Type |
|---|---|
| total_xp | integer |
| current_streak | integer |
| longest_streak | integer |
| daily_xp | integer |
| daily_xp_goal | integer |
| hearts | integer |
| max_hearts | integer |

### Progress

| Field | Type |
|---|---|
| skills_completed | integer |
| lessons_completed | integer |

No documented field in the profile response is nullable in the currently verified demo response.

## Unauthorized

HTTP:

```text
401
```

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication is required."
  }
}
```

---

# 9. GET /api/stats/

## Purpose

Returns the authenticated learner's gamification statistics.

## Request

```http
GET /api/stats/
```

Request body:

```text
None
```

## Success

HTTP:

```text
200 OK
```

Example:

```json
{
  "total_xp": 260,
  "current_streak": 1,
  "longest_streak": 5,
  "hearts": 4,
  "max_hearts": 5,
  "daily_xp": 30,
  "daily_xp_goal": 20
}
```

## Fields

| Field | Type |
|---|---|
| total_xp | integer |
| current_streak | integer |
| longest_streak | integer |
| hearts | integer |
| max_hearts | integer |
| daily_xp | integer |
| daily_xp_goal | integer |

## Unauthorized

HTTP:

```text
401
```

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication is required."
  }
}
```

---

# 10. GET /api/leaderboard/

## Purpose

Returns the XP leaderboard and current user's rank.

Leaderboard ordering is determined by the backend LeaderboardService.

## Request

```http
GET /api/leaderboard/
```

Request body:

```text
None
```

## Success

HTTP:

```text
200 OK
```

Example:

```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user": {
        "id": 1,
        "username": "demo_user"
      },
      "xp": 260
    }
  ],
  "current_user_rank": 1
}
```

## Fields

### Leaderboard response

| Field | Type |
|---|---|
| leaderboard | array |
| current_user_rank | integer |

### Leaderboard entry

| Field | Type |
|---|---|
| rank | integer |
| user | object |
| xp | integer |

### Leaderboard user

| Field | Type |
|---|---|
| id | integer |
| username | string |

Ranks start at:

```text
1
```

XP is a non-negative integer.

## Unauthorized

HTTP:

```text
401
```

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication is required."
  }
}
```

---

# 11. POST /api/practice/hearts/

## Purpose

Refills the authenticated learner's hearts up to `max_hearts`.

The backend remains authoritative.

The frontend must not set the heart count directly.

Repeated refill calls are safe.

Hearts must never exceed `max_hearts`.

## Request

```http
POST /api/practice/hearts/
```

Request body:

```json
{}
```

## Success

HTTP:

```text
200 OK
```

Example:

```json
{
  "success": true,
  "hearts": {
    "current": 5,
    "max": 5
  }
}
```

## Fields

| Field | Type |
|---|---|
| success | boolean |
| hearts | object |
| hearts.current | integer |
| hearts.max | integer |

## Unauthorized

HTTP:

```text
401
```

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication is required."
  }
}
```

---

# 12. Nullable Fields

The currently verified API responses do not require nullable fields for the documented frontend models.

Frontend types should therefore use the documented concrete types unless the backend later changes the contract.

Do not invent nullable fields.

---

# 13. Frontend State Rules

The frontend may display backend state but must not become the source of truth for:

```text
XP
hearts
streak
daily XP
progress
crowns
lesson completion
skill status
skill unlocking
leaderboard rank
```

These values come from Django.

After submitting an answer, use the returned heart and lesson state.

After completing a lesson, use the returned:

```text
rewards
skill
stats
```

values.

After lesson completion, the frontend may refresh:

```text
GET /api/path/
GET /api/stats/
```

to obtain the latest global learner state.

---

# 14. Standard Frontend Lesson Flow

The intended frontend flow is:

```text
GET /api/path/
        |
        v
Select available skill
        |
        v
GET /api/lessons/{lesson_id}/
        |
        v
Render exercise using:
type + question + data + order
        |
        v
POST /api/lessons/{lesson_id}/answer/
        |
        +---- correct ----> continue
        |
        +---- wrong ------> display feedback
                             update hearts
        |
        v
Answer all exercises
        |
        v
POST /api/lessons/{lesson_id}/complete/
        |
        v
Update:
XP
skill progress
crowns
skill status
streak
daily XP
hearts
        |
        v
Refresh learning path if necessary
```

---

# 15. Security Rules

The frontend must never expect `correct_answer` from:

```text
GET /api/lessons/{lesson_id}/
```

The backend stores and evaluates the correct answer.

The frontend receives only playable exercise information.

The client must never submit authoritative values for:

```text
xp
hearts
progress
crowns
streak
completion state
skill status
```

---

# 16. Verified Exercise Types

The seeded backend contains exactly six exercise types:

```text
multiple_choice
translate
word_bank
match_pairs
fill_blank
type_answer
```

Each lesson contains one of each required type in the current seed data.

---

# 17. Verified Seeded Course

The current deterministic seed contains:

```text
Course: Spanish
Source language: English
Target language: Spanish

Units: 3
Skills: 6
Lessons: 6
Exercises: 36
```

Unit structure:

```text
Basics
  - Greetings
  - Introductions

Food
  - Common Foods
  - Drinks

Everyday Life
  - Family
  - Daily Activities
```

Each lesson contains six exercises.

---

# 18. Contract Verification Status

The backend contract has been verified through:

- Django system checks
- Existing Chat 3 regression tests
- REST API tests
- Authentication tests
- Lesson security tests
- All six exercise types
- Wrong-answer heart deduction
- Exhausted-heart handling
- Lesson completion
- XP reward
- Skill progress
- Crowns
- Skill status
- Streak/daily XP response
- Heart refill
- Leaderboard
- Profile
- Stats
- Completion idempotency
- Full HTTP lesson loop
- OpenAPI schema generation
- Swagger UI

The frontend should treat this document as the API contract and should not invent additional endpoints or fields.

---

# 19. API Endpoint Summary

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/path/` | Learning path |
| GET | `/api/lessons/{lesson_id}/` | Playable lesson |
| POST | `/api/lessons/{lesson_id}/answer/` | Submit exercise answer |
| POST | `/api/lessons/{lesson_id}/complete/` | Complete lesson |
| GET | `/api/profile/` | Learner profile |
| GET | `/api/stats/` | Gamification statistics |
| GET | `/api/leaderboard/` | XP leaderboard |
| POST | `/api/practice/hearts/` | Refill hearts |

---

# 20. Contract Freeze

This document represents the verified Chat 4 backend behavior.

Frontend implementation should follow this document exactly.

If a backend behavior differs from an earlier conceptual example, the verified HTTP behavior documented here takes precedence.

No frontend business logic should duplicate Django's authoritative lesson/gamification logic.