deploy : https://speckit-plus-hackathon-5m97lel5z-huzaifa206s-projects.vercel.app/

# 🤖 Physical AI & Humanoid Robotics: The Agentic Textbook

> **Bridging the gap between the digital brain and the physical body.**

> *A Spec-Driven Development (SDD) Project.*

[![Deployment Status](https://img.shields.io/badge/Deployed%20on-Vercel-000000?style=for-the-badge&logo=vercel)](https://vercel.com/)
[![Built With](https://img.shields.io/badge/Framework-Docusaurus-success?style=for-the-badge&logo=docusaurus)](https://docusaurus.io/)
[![Methodology](https://img.shields.io/badge/Methodology-Spec--Kit%20Plus-blueviolet?style=for-the-badge)](https://github.com/panaversity/spec-kit-plus)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-Claude%20Code%20%2B%20Qwen-FF6B00?style=for-the-badge)](https://claude.ai)

---

## 💡 Project Overview

**Zero Manual Code. Pure Intent.**

This project is a submission for the **Spec-Kit Plus Hackathon**. It serves as a proof-of-concept for the future of software engineering: **Spec-Driven Development (SDD)**.

Instead of writing code manually, I acted as the **Systems Architect**, defining natural language specifications (`sp.constitution`, `sp.specify`). The **Claude Code Agent (powered by the Qwen Model)** acted as the developer, interpreting these specs to architect, write, debug, and deploy this entire Docusaurus application.

The result is a fully functional, interactive textbook on **Physical AI and Humanoid Robotics**, deployed live on Vercel.

## 🌟 Key Features

The agent successfully implemented the following hackathon requirements:

### 1. 📚 The Interactive Book

A comprehensive syllabus generated from scratch, covering:
* **Module 1:** The Robotic Nervous System (ROS 2)
* **Module 2:** The Digital Twin (Gazebo & Unity)
* **Module 3:** The AI-Robot Brain (NVIDIA Isaac Sim)
* **Module 4:** Vision-Language-Action (VLA)

### 2. 🧠 Integrated RAG Chatbot

An embedded AI teaching assistant (powered by Qwen/Gemini) that answers student questions based strictly on the book's content.

### 3. 🇵🇰 Localization & Accessibility

* **One-Click Urdu Translation:** An AI-powered toggle that translates technical robotics concepts into Urdu for broader accessibility.

### 4. 🎨 Smart Personalization

* **Hardware-Aware Content:** The book detects user hardware (e.g., "RTX 4090" vs. "MacBook Air") and dynamically adjusts lab instructions (Sim-to-Real vs. Cloud Labs).
* **Authentication:** Secure Signup/Signin flows via **Better-Auth**.

---

## 🛠️ The "Zero-Code" Tech Stack

| Component | Technology Used | Role |
| :--- | :--- | :--- |
| **Orchestration** | **Spec-Kit Plus** | The managerial framework for SDD. |
| **AI Developer** | **Claude Code + Qwen** | The intelligence that wrote the code. |
| **Frontend** | **Docusaurus (React)** | The static site generator for the book. |
| **Backend** | **FastAPI + Qdrant** | Powering the RAG Chatbot. |
| **Deployment** | **Vercel** | CI/CD and Global Hosting. |

---

## 🤖 The Spec-Driven Workflow

This project followed a strict **Constitution → Specification → Execution** pipeline:

1.  **`sp.constitution`**: Defined the project's "Soul" (Mission: Teach Physical AI, Style: Sim-to-Real).
2.  **`sp.specify`**: The Source of Truth. Detailed the syllabus, hardware requirements, and feature list.
3.  **`sp.plan`**: The Strategic Roadmap. Broken down into phases (Skeleton -> RAG -> UI).
4.  **`sp.task`**: Atomic instructions fed to Claude Code/Qwen to execute the build.
5.  **`sp.implement`**: The trigger for the agent to write the actual Docusaurus components.

---

## 🚀 Running Locally

If you want to inspect the AI-generated code:

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/your-username/physical-ai-book.git](https://github.com/your-username/physical-ai-book.git)
    cd physical-ai-book
    ```

2.  **Install Dependencies**
    ```bash
    npm install
    ```

3.  **Start the Server**
    ```bash
    npm start
    ```
    The site will launch at `http://localhost:3000`.

---

## 🏆 Hackathon Context

* **Challenge:** Build a unified book project using Claude Code & Spec-Kit Plus.
* **Goal:** Demonstrate reusable intelligence and agentic workflows.
* **Result:** A fully deployed, personalized educational platform built in record time without manual coding.

---

*Generated with ❤️ by Human Intent + Machine Intelligence.*