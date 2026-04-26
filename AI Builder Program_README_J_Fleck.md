**Klaviyo AI Builder Residency Application** Review submission terms & complete all required sections (optional sections are noted). Your video and README will be evaluated using the rubric at the end of this document. 

**Video Walkthrough (Required, 5 min max)** 

*Record a Loom or equivalent walkthrough.* 

Your video should cover: 

• The problem you chose and why you picked it 

• A live demo of the working solution 

• A brief walkthrough of your architecture and key design decisions 

• What you would do differently or build next 

Paste your video link here: 

**Video URL:** [https://www.loom.com/share/10eb7e0cf8164bb98a155a47b7ef5772](https://www.loom.com/share/10eb7e0cf8164bb98a155a47b7ef5772)

**README Template** 

**Project Title** 

My Anchor — Daily Briefing 

**Problem Statement** 

I wanted to tackle the excess of newsletter repetition and full inbox that affects myself, my friends, and busy professionals managing valuable subscriptions. As the volume of written content scales due to AI, important insights can be lost in the shuffle. My Anchor’s success is the transformation of raw information into a streamlined, trustworthy feed that provides trusted intelligence.

**Solution Overview** 

My Anchor is a personalized AI-powered news aggregator that securely reads a user's Gmail for newsletter subscriptions and converts the content into a cohesive, podcast-style audio briefing. The application highlights top stories and provides a side-by-side comparison of differing source perspectives. AI is core to the solution, as it performs the heavy lifting of multi-source summarization and angle analysis that would be impossible for a manual aggregator to perform at scale.

**AI Integration** 

The application utilizes an AI pipeline to process and deliver news:

* **Models used**: **Google Gemini LLM** is used for content analysis and summarization, while **Google Cloud Text-to-Speech** (utilizing Journey and Neural2 voices) generates the audio content.  
* **Orchestration**: The system employs a "Model Council" pattern to analyze raw text from multiple newsletters. It groups related stories from different sources into single news events and identifies perspectives where sources disagree.  
* **Tradeoffs**: To manage latency during audio generation, the system chunks the script and synthesizes audio in parallel using a `ThreadPoolExecutor`.  
* **Optimization**: A custom `optimize_newsletter_for_llm` function uses regex to strip HTML and non-essential content, reducing token usage and improving processing speed.

**Architecture / Design Decisions** 

**Backend**: Built with **Flask/Python**, focusing on a trust-first design that emphasizes intelligence over noise.

**Parallel Processing**: The architecture uses background threads to fetch emails and generate audio chunks concurrently, significantly reducing the time to brief the user.

**Reliability & Security**:

* Implemented "Sentinel" guards, such as a 2MB request payload limit, to prevent resource exhaustion.  
* Uses **Sentry** for real-time error tracking and **PostHog** for product metrics.  
* Employs a module-level regex compilation strategy to improve performance in high-frequency string parsing tasks.

**UI/UX**: Features a perspective split accent in Amber to signal where news sources differ, avoiding generic color coding.

**What did AI help you do faster, and where did it get in your way?** 

I primarily used Cursor and Antigravity to compare the different coding harnesses. AI gave me the ability to code at a speed and skill I could not accomplish on my own in the time I worked on this project. I had mixed success asking coding questions of AI in chatbot form, as I believe it struggled to handle the context of the Github repo. Cursor was good at the beginning, because the planning feature helped me think through my ideas. Antigravity has been less helpful, because it is more likely to act when I want to plan, and plan when I want action, but it is stronger at multi coding agent work. Using AI in the CLI has been solid when using skills developed by others, but is a little less easy to control. The biggest issue is AI getting ahead of me when I try to work quickly, and developing bugs that I struggle to identify, even with AI, causing a broad rollback of my version.

**Getting Started / Setup Instructions** 

*Include clear steps for running your project locally.* 

| git clone https://github.com/jfleck25/my-anchor-news.git  cd my-anchor-news  pip install \-r requirements.txt  \# Set up environment variables  cp .env.example .env  \# Edit .env with your keys \# Configure your `GOOGLE_API_KEY`, `FLASK_SECRET_KEY`, and Google OAuth client secrets. \# Demo mode exists without calling AI or real emails python main.py |
| :---- |

**Demo** 

1. Login with Gmail or select “Demo Mode”  
2. Sync Newsletters \~20s  
3. Wait for audio briefing to load \~30s  
4. Play Audio

**Testing / Error Handling (Recommended)** 

The project includes a robust testing and error management framework:

* **Automated Testing**: Uses `pytest` for unit testing across the backend and frontend components.  
* **Fail-Safe Mechanisms**: Implements global error handlers to ensure raw upstream API errors (from Google or Gemini) are not exposed to the client, providing safe, user-friendly messages instead.  
* **Rate Limiting**: Integrated `Flask-Limiter` to protect API endpoints from abuse and manage quota usage for LLM and TTS services.  
* **Validation**: Strict type validation and "Sentinel" keys are used in settings updates to prevent mass assignment vulnerabilities.

**Future Improvements / Stretch Goals (Optional)** 

**What to do differently:** \* **Vector Database (RAG):** Instead of processing only the latest newsletters, implement a vector store to allow users to ask follow-up questions about news from earlier in the week.

* **Webhooks over Polling:** Move from manual Gmail syncing to a webhook-based architecture so the briefing is ready the moment the user wakes up, without them having to trigger a fetch.

**What to build next:**

* **Interactivity:** Implement agentic tools where a user can say "tell me more about that story" and have the AI immediately pull more context from the source newsletters to expand the briefing on the fly.  
* **Mobile Push Integration:** Moving beyond a web app to a native mobile experience with lock-screen audio controls for commuters.

**Link to website URL or application (Optional)** 

[https://my-anchor-app.onrender.com/](https://my-anchor-app.onrender.com/)

**Evaluation Rubric** 

Projects are scored out of 100 points across four categories. 

| Category  | Score  | What Evaluators Look For |
| :---- | ----- | ----- |
| Problem Framing & Real-World Impact | 0-25  | **Good:** Interesting problem or use case with a defined audience. Candidate explains the pain point and why they chose to build it.  **Great:** Specific, well-scoped problem tied to a meaningful workflow. Candidate shows product thinking: who is affected, what success looks like, and why AI was the right tool. Understands how to quantity its impact on the intended audience. |
| Technical Execution  | 0-35  | **Good:** Functional solution with readable code. README covers setup. Shows end-to-end build capability.  **Great:** Clean, well-structured code with clear architecture decisions. Solution is reproducible. Demonstrates thoughtful design: modularity, error handling, sensible tradeoffs. Setup instructions work out of the box. |
| AI Fluency: Building with AI and using AI | 0-25  | **Good:** LLM/AI tools are central to the solution. Candidate describes how coding tools accelerated development with some reflection.  **Great:** Agentic patterns, RAG, tool use, or non-trivial orchestration. Candidate clearly articulates how AI coding tools changed their process, where they hit limits, and how they adapted. Shows AI as a force multiplier at both the product and dev levels. |
| Communication &  Documentation | 0-15  | **Good:** Video walkthrough is clear and covers core functionality. README explains solution, architecture, and setup.  **Great:** Video explains not just 'what' but 'why.' README includes architecture decisions, tradeoffs, and future improvements. Candidate can speak to technical decisions for a non-technical audience. |
| Tie Breaker: Builder Mindset | N/A  | Did the candidate go beyond the prompt? Is there evidence of curiosity and iteration, honest reflection on what didn't work, or creative problem framing? Does the candidate seem like someone who would take initiative from day one? |

**Submission Terms** 

*By submitting this README and accompanying video, you acknowledge and agree to the following terms.* 

• **Ownership & Originality.** The project described in this submission is your own original work. You have all necessary rights to share the materials included (code, video, documentation, and any third-party libraries or assets used), and no part of this submission infringes on the intellectual property rights of any third party or violates any confidentiality obligation you owe to a current or former employer or other party. 

• **No Transfer of Rights.** Klaviyo, Inc. (“Klaviyo”) does not claim any ownership interest in, or license to, the project, code, or materials you submit. Your submission is provided solely for the purpose of evaluating your candidacy for the AI Builder Resident Program. Klaviyo will not use, reproduce, distribute, or create derivative works from your submission for any purpose other than evaluating your application. 

• **Confidentiality of Submissions.** Klaviyo will treat your submission as confidential and will limit access to members of the hiring and evaluation committee. Your submission will not be shared externally. Klaviyo  
will retain your submission materials in accordance with its data retention policies applicable to job applications. 

• **Third-Party Content & Obligations.** If your project incorporates open-source libraries, third-party APIs, or other materials you did not create, you must identify them in your README (e.g., in the Architecture / Design Decisions section or a separate “Acknowledgments” section). Do not include any proprietary code, trade secrets, or confidential information belonging to a current or former employer or any other third party. 

• **Privacy.** Your personal information included in your submission materials (including your image in the video submission) will be processed in accordance with Klaviyo’s Job Applicant Privacy Notice. By submitting your application, you acknowledge that you have reviewed and understood this notice. 

• **Credentials & Sensitive Data.** Do not include live API keys, passwords, or other credentials in your submission. Use placeholder values in any .env.example or configuration files. 

• **Content.** The submission does not contain any material that is unlawful, defamatory, obscene, 

threatening, harassing, or otherwise objectionable; does not contain any viruses, malware, or other harmful code; and complies with all applicable laws and regulations. 

*Any applicant whose submission does not comply with these terms will **not** be eligible to participate in the AI Builder Resident Program. Non-compliance discovered after acceptance will result in immediate removal from the Program.*