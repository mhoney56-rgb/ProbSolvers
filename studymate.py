import os
import gradio as gr
import google.generativeai as genai
from typing import List, Tuple
import json
import time

class StudyMate:
    def __init__(self):
        # Initialize the Gemini API
        self.api_key = None
        self.model = None
        
        # Language mappings
        self.languages = {
            "English": "en",
            "Hindi": "hi", 
            "Tamil": "ta",
            "Spanish": "es",
            "Japanese": "ja"
        }
        
        # Subject categories for better responses
        self.subjects = [
            "Mathematics", "Physics", "Chemistry", "Biology", 
            "Computer Science", "History", "Geography", "Literature",
            "Economics", "Psychology", "Philosophy", "General"
        ]
        
    def setup_gemini(self, api_key: str):
        """Setup Gemini API with the provided key"""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.api_key = api_key
            return True, "✅ Gemini API configured successfully!"
        except Exception as e:
            return False, f"❌ Error configuring Gemini API: {str(e)}"
    
    def create_study_prompt(self, question: str, subject: str, language: str, difficulty: str) -> str:
        """Create a detailed prompt for the study companion"""
        
        language_instructions = {
            "English": "Respond in clear, simple English.",
            "Hindi": "हिंदी में उत्तर दें। सरल और स्पष्ट भाषा का उपयोग करें।",
            "Tamil": "தமிழில் பதிலளிக்கவும். எளிய மற்றும் தெளிவான மொழியைப் பயன்படுத்துங்கள்.",
            "Spanish": "Responde en español claro y sencillo.",
            "Japanese": "日本語で答えてください。分かりやすく簡潔な言葉を使ってください。"
        }
        
        prompt = f"""
You are StudyMate, a friendly and knowledgeable AI tutor. A student has asked you a question about {subject}.

QUESTION: {question}

INSTRUCTIONS:
- {language_instructions.get(language, "Respond in English.")}
- Act like a patient, encouraging tutor who wants to help the student truly understand
- Provide a detailed, step-by-step explanation
- Use real-life examples and analogies when possible
- Break down complex concepts into simple parts
- Adjust your explanation for {difficulty} level
- Be conversational and encouraging
- If it's a problem-solving question, show the complete solution process
- If it's a conceptual question, explain the 'why' behind the concept
- End with a summary or key takeaway
- Ask if the student needs clarification on any part

RESPONSE FORMAT:
1. Start with a friendly acknowledgment of their question
2. Provide the main explanation with examples
3. Give step-by-step breakdown if applicable
4. Include real-world applications or examples
5. Summarize key points
6. Encourage further questions

Remember: You're not just giving answers, you're helping students learn and understand!
"""
        return prompt
    
    def get_study_response(self, question: str, subject: str, language: str, difficulty: str) -> str:
        """Get response from Gemini API"""
        if not self.model:
            return "❌ Please configure your Gemini API key first!"
        
        if not question.strip():
            return "Please ask me a study question! I'm here to help you learn. 📚"
        
        try:
            prompt = self.create_study_prompt(question, subject, language, difficulty)
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text
            else:
                return "I couldn't generate a response. Please try rephrasing your question."
                
        except Exception as e:
            return f"❌ Error getting response: {str(e)}\n\nPlease check your API key and internet connection."
    
    def get_study_tips(self, subject: str, language: str) -> str:
        """Generate study tips for a specific subject"""
        if not self.model:
            return "❌ Please configure your Gemini API key first!"
        
        language_instructions = {
            "English": "Respond in clear, simple English.",
            "Hindi": "हिंदी में उत्तर दें।",
            "Tamil": "தமிழில் பதிலளிக்கவும்।", 
            "Spanish": "Responde en español.",
            "Japanese": "日本語で答えてください。"
        }
        
        prompt = f"""
You are StudyMate, a helpful AI tutor. Provide 5-7 practical study tips specifically for {subject}.

INSTRUCTIONS:
- {language_instructions.get(language, "Respond in English.")}
- Make tips actionable and specific to {subject}
- Include both study techniques and practical advice
- Be encouraging and motivational
- Format as numbered list for easy reading
- Include time management tips if relevant

Make it friendly and encouraging!
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else "Couldn't generate study tips right now."
        except Exception as e:
            return f"Error generating study tips: {str(e)}"

# Initialize StudyMate
study_mate = StudyMate()

# Gradio Interface Functions
def setup_api_key(api_key):
    """Setup the API key"""
    if not api_key.strip():
        return False, "❌ Please enter your Gemini API key", ""
    
    success, message = study_mate.setup_gemini(api_key.strip())
    
    if success:
        return True, message, "🎓 StudyMate is ready! Ask me any study question."
    else:
        return False, message, ""

def ask_question(question, subject, language, difficulty, history):
    """Process student question and return response"""
    if not study_mate.model:
        return history, "❌ Please configure your Gemini API key first!"
    
    # Get response from StudyMate
    response = study_mate.get_study_response(question, subject, language, difficulty)
    
    # Update chat history
    history.append([question, response])
    
    return history, ""

def get_study_tips(subject, language, history):
    """Get study tips for selected subject"""
    tips = study_mate.get_study_tips(subject, language)
    
    # Format as a question-answer pair for chat history
    question = f"Can you give me study tips for {subject}?"
    history.append([question, tips])
    
    return history

def clear_chat():
    """Clear chat history"""
    return []

# Custom CSS for better styling
css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.chat-message {
    padding: 10px;
    margin: 5px 0;
    border-radius: 10px;
}

.user-message {
    background-color: #e3f2fd;
    margin-left: 20px;
}

.bot-message {
    background-color: #f5f5f5;
    margin-right: 20px;
}

#title {
    text-align: center;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.subject-selector, .language-selector {
    margin: 10px 0;
}
"""

# Create Gradio Interface
with gr.Blocks(css=css, title="StudyMate - AI Study Companion") as app:
    gr.HTML("""
    <div id="title">
        <h1>🎓 StudyMate</h1>
        <p>Your AI-Powered Study Companion</p>
        <p>Get detailed explanations, step-by-step solutions, and personalized study help!</p>
    </div>
    """)
    
    # API Key Setup Section
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🔑 Setup Your Gemini API Key")
            gr.Markdown("Get your free API key from: [Google AI Studio](https://aistudio.google.com/app/apikey)")
            
            api_key_input = gr.Textbox(
                label="Gemini API Key", 
                placeholder="Enter your Gemini API key here...",
                type="password"
            )
            setup_btn = gr.Button("🚀 Setup StudyMate", variant="primary")
            setup_status = gr.Textbox(label="Status", interactive=False)
    
    # Main Chat Interface
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="💬 Chat with StudyMate",
                height=400,
                placeholder="Ask me any study question! I'm here to help you learn and understand concepts better. 📚"
            )
            
            with gr.Row():
                question_input = gr.Textbox(
                    label="Ask your question",
                    placeholder="e.g., Explain photosynthesis, Solve this math problem, What is machine learning?",
                    scale=4
                )
                ask_btn = gr.Button("📤 Ask", variant="primary", scale=1)
        
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Study Settings")
            
            subject_select = gr.Dropdown(
                choices=study_mate.subjects,
                value="General",
                label="📚 Subject",
                info="Select your subject area"
            )
            
            language_select = gr.Dropdown(
                choices=list(study_mate.languages.keys()),
                value="English", 
                label="🌍 Language",
                info="Choose your preferred language"
            )
            
            difficulty_select = gr.Dropdown(
                choices=["Beginner", "Intermediate", "Advanced"],
                value="Intermediate",
                label="📊 Difficulty Level",
                info="Set explanation complexity"
            )
            
            gr.Markdown("### 🎯 Quick Actions")
            tips_btn = gr.Button("💡 Get Study Tips", variant="secondary")
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
    
    # Instructions Section
    with gr.Row():
        gr.Markdown("""
        ### 📋 How to Use StudyMate:
        1. **Setup**: Enter your Gemini API key and click "Setup StudyMate"
        2. **Configure**: Select your subject, language, and difficulty level
        3. **Ask**: Type your study question and click "Ask" 
        4. **Learn**: Get detailed explanations with examples and step-by-step solutions
        5. **Explore**: Use "Get Study Tips" for subject-specific study strategies
        
        ### 💡 Example Questions:
        - *"Explain the water cycle with real-world examples"*
        - *"How do I solve quadratic equations step by step?"*
        - *"What is the difference between mitosis and meiosis?"*
        - *"Explain machine learning in simple terms"*
        """)
    
    # Event Handlers
    setup_btn.click(
        fn=setup_api_key,
        inputs=[api_key_input],
        outputs=[gr.State(), setup_status, question_input]
    )
    
    ask_btn.click(
        fn=ask_question,
        inputs=[question_input, subject_select, language_select, difficulty_select, chatbot],
        outputs=[chatbot, question_input]
    )
    
    question_input.submit(
        fn=ask_question,
        inputs=[question_input, subject_select, language_select, difficulty_select, chatbot],
        outputs=[chatbot, question_input]
    )
    
    tips_btn.click(
        fn=get_study_tips,
        inputs=[subject_select, language_select, chatbot],
        outputs=[chatbot]
    )
    
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot]
    )

# Launch the application
if __name__ == "__main__":
    print("🎓 Starting StudyMate - AI Study Companion...")
    print("📝 Make sure you have your Gemini API key ready!")
    print("🌐 The app will open in your browser automatically.")
    
    app.launch(
        share=False,          # Set to True if you want to share publicly
        server_name="127.0.0.1",  # Only accessible locally for security
        server_port=7860,     # You can change this port if needed
        show_error=True       # Show detailed error messages
    )