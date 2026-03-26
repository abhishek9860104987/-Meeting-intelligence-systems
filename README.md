# -Meeting-intelligence-systems
It is a system which can integrate  with  any meeting app and any jira like tool for automatic task assign and track
# 🧠 Meeting Intelligence System

An AI-powered system that transforms meeting transcripts into **structured tasks, ownership insights, risk detection, and business impact metrics** using advanced LLMs.

---

## 🚀 Overview

The **Meeting Intelligence System** automates post-meeting workflows by converting unstructured discussions into actionable intelligence.

It leverages the **Groq LLM (`llama-3.1-8b-instant`)** to:

* Extract tasks
* Assign owners
* Detect ambiguities
* Track stalled tasks
* Generate AI summaries
* Calculate business impact

---

## ✨ Key Features

### 🔍 Task Extraction

* Extracts tasks from transcripts
* Identifies owners using NLP
* Removes duplicates

---

### 🤖 Decision Engine

* Assigns:

  * Priority (High / Medium / Low)
  * Deadlines
  * Risk levels
* Determines status:

  * ✅ CONFIRMED
  * 🤖 AUTO_ASSIGNED
  * ❗ NEEDS_CLARIFICATION
  * ⚠ SUGGESTED

---

### ❗ Clarification System

* Detects vague tasks
* Shows reason for ambiguity
* Generates smart questions why clarification needed
* Allows **manual owner assignment**

---

### 🚨 Stall Detection

* Detects inactive tasks
* Displays:

  * Stalled tasks list
  * Trend graph
  * Notifications

---

### 📊 Business Impact Dashboard

* Calculates:

  * ⏱ Time Saved
  * 💰 Cost Saved
  * 📊 Automation %
* Based on:

  * **CONFIRMED + automated tasks only**

---

### 📄 AI Meeting Summary

Generated using **Groq LLM (`llama-3.1-8b-instant`)**:

* Overview
* Key tasks
* Risks
* Insights
* Business impact

---

### 📩 Notifications System

* Alerts for stalled tasks
* Escalation messages
* Real-time updates

---

## 🛠️ Tech Stack

| Layer           | Technology                  |
| --------------- | --------------------------- |
| Frontend        | Streamlit                   |
| Backend         | Python                      |
| Database        | SQLite                      |
| AI Model        | Groq (llama-3.1-8b-instant) |
| Data Processing | Pandas                      |
| Visualization   | Matplotlib                  |

---

## 📂 Project Structure

```bash
agent_ai1.1/
│
├── app.py                     # Main Streamlit app
├── database.py               # DB operations
├── config.py                 # Config settings
├── security_config.py        # Security configs
├── agent.db                  # SQLite DB
│
├── agents/
│   ├── extractor.py          # Task extraction
│   ├── decision.py           # Decision engine
│   ├── ambiguity.py          # Ambiguity detection
│   ├── clarifier.py          # Clarification questions
│   ├── tracker.py            # Time tracking
│   ├── stall_detector.py     # Stall detection
│   ├── notifier.py           # Notifications
│   ├── impact_tracker.py     # Business impact
│   ├── summary.py            # AI summary
│   ├── ownership.py          # Owner detection
│   ├── orchestrator.py       # Workflow orchestration
│   ├── knowledge_graph.py    # Knowledge relationships
│   ├── smart_router.py       # Routing logic
│   ├── escalation.py         # Escalation logic
│   ├── enterprise_logger.py  # Logging
│   ├── logger.py             # Logging utils
│   ├── self_healing.py       # Error recovery
│
├── utils/
│   └── groq_client.py        # Groq API (LLM)
│
├── .env.example              # Environment variables
├── requirements.txt          # Dependencies
├── ENHANCEMENT_SUMMARY.md    # Enhancements
└── .gitignore
```

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/meeting-intelligence-system.git
cd agent_ai1.1
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup Environment Variables

Create `.env` file:

```env
in config file enter you API of groq
GROQ_API_KEY=your_api_key_here
MODEL_NAME=llama-3.1-8b-instant
```

---

### 5️⃣ Run Application

```bash
streamlit run app.py
```

---

## 🧪 Sample Transcript

```text
Abhishek will develop authentication system
Rohit will design database schema
Sneha will fix payment integration bug
Aman will deploy backend service
Priya will test application
John should review everything before demo
Team needs to improve UI performance
```

---

## 🎯 How It Works

1. Paste transcript
2. Click **Run AI**
3. System performs:

   * Task extraction
   * Decision processing
   * Owner assignment
4. Displays:

   * Task dashboard
   * Clarification panel
   * Stalled tasks
   * Notifications
   * Business impact

---

## 📊 Business Impact Logic

* Based on **confirmed automated tasks**
* Time Saved = `tasks × 5 minutes`
* Cost Saved = `time × ₹0.5 per minute`

---

## 🔥 Demo Highlights

* Real-time task generation
* Manual clarification resolution
* Dynamic KPI dashboard
* Graph + notifications UI
* AI-generated summary

---

## 🚀 Future Improvements

* 📈 Interactive charts (Plotly)
* 👤 User productivity tracking
* 🔔 Slack / Email alerts
* ☁ Cloud deployment
* 🧠 Advanced NLP

---

## 🤝 Contributing

1. Fork repository
2. Create branch
3. Commit changes
4. Open Pull Request

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Abhishek Chavan**

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
