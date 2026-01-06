# Data Model: Physical AI & Humanoid Robotics Book

## Core Entities

### Lesson Module
- **Fields**:
  - id: string (unique identifier)
  - title: string (lesson title)
  - description: string (brief description)
  - content: string (MDX content)
  - prerequisites: array of strings (required knowledge)
  - objectives: array of strings (learning goals)
  - handsOnLab: object (lab instructions and requirements)
  - simulationResults: string (expected outcomes)
  - commonErrors: array of objects (error scenarios and solutions)
  - industryNotes: array of strings (real-world applications)
  - miniChallenge: object (challenge description and criteria)
  - summary: string (key takeaways)

- **Validation Rules**:
  - Title must be 3-100 characters
  - Content must include conceptual overview section
  - At least one hands-on lab requirement must be specified
  - Learning objectives must be measurable

- **State Transitions**:
  - draft → review → published

### Chapter
- **Fields**:
  - id: string (unique identifier)
  - title: string (chapter title)
  - description: string (chapter overview)
  - lessons: array of Lesson Module references
  - theme: string (e.g., "Physical AI", "ROS 2", "Digital Twins")
  - progressionLevel: number (1-5 scale of complexity)
  - estimatedTime: number (minutes to complete)

- **Validation Rules**:
  - Must contain 1-10 lessons
  - Progression level must increase gradually
  - Estimated time must be realistic based on content

### Learning Environment
- **Fields**:
  - id: string (unique identifier)
  - name: string (environment name)
  - type: string (e.g., "simulation", "code", "theory")
  - requirements: array of strings (system/hardware requirements)
  - setupInstructions: string (step-by-step setup guide)
  - tools: array of strings (required software/tools)

- **Validation Rules**:
  - Type must be one of predefined values
  - Setup instructions must include all required steps
  - Requirements must be verifiable

### Learner Profile
- **Fields**:
  - skillLevel: string (e.g., "beginner", "intermediate", "advanced")
  - background: string (e.g., "CS student", "AI developer", "robotics enthusiast")
  - prerequisites: array of strings (required knowledge areas)
  - learningGoals: array of strings (what they want to achieve)

- **Validation Rules**:
  - Skill level must be one of predefined values
  - Background must align with content requirements

## Relationships

- Chapter 1-to-many Lesson Module (a chapter contains multiple lessons)
- Lesson Module 1-to-many Learning Environment (a lesson may require multiple environments)
- Learner Profile 1-to-many Lesson Module (a learner can access multiple lessons)

## State Management

### Lesson Progress
- **Fields**:
  - learnerId: string
  - lessonId: string
  - status: string ("not-started", "in-progress", "completed")
  - completionDate: date (when completed)
  - assessmentScore: number (0-100 scale)

### Navigation State
- **Fields**:
  - currentLesson: string (lesson ID)
  - completedLessons: array of strings
  - recommendedNext: string (suggested lesson based on progression)

## Content Validation Rules

- All code examples must be syntax-highlighted
- Diagrams must be accompanied by alt text for accessibility
- All external links must be verified and up-to-date
- Hands-on labs must have clear prerequisites and expected outcomes
- Industry notes must be current and relevant to the technology stack