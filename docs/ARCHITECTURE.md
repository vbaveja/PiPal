# PiPal Architecture

## High-Level Design

PiPal is organized around:

User
→ Projects
→ Memory
→ Hardware
→ AI Guidance

---

# Frontend

frontend/

Responsibilities:
- Login
- Student workspace
- Admin workspace
- Project selection
- Project creation
- User interaction

---

# Backend

backend/

## user_manager.py

Manages:
- Users
- Roles
- Authentication

## project_manager.py

Manages:
- Projects
- Project creation
- Project loading

## memory_manager.py

Manages:
- Project memory
- Conversation history
- Learning progress

## curriculum_manager.py

Manages:
- Devices by level
- Learning prompts
- Learning paths

## context_loader.py

Loads:
- Project context
- Hardware context
- Curriculum context

## prompt_builder.py

Constructs AI prompts.

---

# Hardware Layer

hardware/

Contains:
- components.json
- wiring_rules.json
- pin_reference.json

Purpose:
Provide structured hardware knowledge.

---

# Curriculum Layer

curriculum/

Levels:
- Beginner
- Intermediate
- Advanced

Each level contains:
- devices.json
- prompts.json
- learning_path.json

---

# User Layer

users/

Each user contains:

projects/
    memory.json
    code.py
    wiring.json

Purpose:
Persistent student workspaces.

---

# Core Principle

The project is the central object.

Everything revolves around:

Student
→ Project
→ Memory
→ Hardware
→ Learning