import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

class GitHubProfileBot:
    """
    GitHubProfileBot: An AI assistant for GitHub portfolio inquiries.
    Answers questions about developer skills, projects, and experience.
    """
    
    def __init__(self, portfolio_data_path: str = "portfolio_data.json"):
        """Initialize the bot with portfolio data."""
        self.portfolio_data = self._load_portfolio_data(portfolio_data_path)
        self.developer = self.portfolio_data.get("developer", {})
        self.skills = self.portfolio_data.get("skills", {})
        self.projects = {p["id"]: p for p in self.portfolio_data.get("projects", [])}
        self.experience = self.portfolio_data.get("experience", {})
    
    def _load_portfolio_data(self, path: str) -> Dict:
        """Load portfolio data from JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {path} not found. Please ensure portfolio_data.json exists.")
            return {}
    
    # ============ Developer & Overview Questions ============
    
    def about_developer(self) -> str:
        """Provide overview of the developer."""
        dev = self.developer
        return (
            f"Hi! I'm **{dev.get('name', 'Unknown')}** (also known as **{dev.get('alias', 'N/A')}**). \n\n"
            f"**Role:** {dev.get('role', 'N/A')}\n\n"
            f"**About:** {dev.get('summary', 'N/A')}\n\n"
            f"**GitHub:** {dev.get('github', 'N/A')}"
        )
    
    def get_skills_summary(self) -> str:
        """Provide a comprehensive skills overview."""
        if not self.skills:
            return "I don't have skills information available."
        
        summary = "**Technical Skills:**\n\n"
        for category, tech_list in self.skills.items():
            if isinstance(tech_list, list) and tech_list:
                formatted_category = category.replace('_', ' ').title()
                summary += f"**{formatted_category}:** {', '.join(tech_list)}\n"
        
        return summary
    
    def get_expertise_areas(self) -> str:
        """List areas of expertise."""
        areas = self.skills.get("expertise_areas", [])
        if not areas:
            return "I don't have expertise area information."
        
        return "**Areas of Expertise:**\n\n" + "\n".join(f"• {area}" for area in areas)
    
    # ============ Project Questions ============
    
    def list_all_projects(self) -> str:
        """List all projects with brief descriptions."""
        if not self.projects:
            return "No projects found."
        
        projects_list = "**Portfolio Projects:**\n\n"
        for project_id in sorted(self.projects.keys()):
            p = self.projects[project_id]
            projects_list += f"{project_id}. **{p.get('name', 'Unknown')}** – {p.get('subtitle', '')}\n"
        
        return projects_list
    
    def get_project_details(self, project_name: str) -> str:
        """Get detailed information about a specific project."""
        project = self._find_project(project_name)
        if not project:
            return f"I don't have information about a project called '{project_name}'."
        
        details = (
            f"**{project.get('name', 'Unknown')}**\n\n"
            f"*{project.get('subtitle', '')}*\n\n"
            f"**Type:** {project.get('type', 'N/A')}\n\n"
            f"**Description:** {project.get('description', 'N/A')}\n\n"
        )
        
        # Tech Stack
        tech = project.get("tech_stack", [])
        if tech:
            details += f"**Tech Stack:** {', '.join(tech)}\n\n"
        
        # Features
        features = project.get("features", [])
        if features:
            details += "**Key Features:**\n"
            for feature in features:
                details += f"• {feature}\n"
            details += "\n"
        
        # Impact & Learning
        details += f"**Impact:** {project.get('impact', 'N/A')}\n\n"
        details += f"**Key Learning:** {project.get('key_learning', 'N/A')}\n\n"
        details += f"**Status:** {project.get('status', 'N/A')}"
        
        return details
    
    def _find_project(self, name: str) -> Optional[Dict]:
        """Find a project by name (case-insensitive)."""
        name_lower = name.lower()
        for project in self.projects.values():
            if name_lower in project.get("name", "").lower():
                return project
        return None
    
    def get_project_tech_stack(self, project_name: str) -> str:
        """Get the tech stack for a specific project."""
        project = self._find_project(project_name)
        if not project:
            return f"I don't have information about '{project_name}'."
        
        tech = project.get("tech_stack", [])
        if not tech:
            return f"Tech stack information not available for {project.get('name', 'this project')}."
        
        return f"**{project.get('name', 'Project')} Tech Stack:**\n\n{', '.join(tech)}"
    
    def get_projects_by_tech(self, technology: str) -> str:
        """Find all projects that use a specific technology."""
        tech_lower = technology.lower()
        matching_projects = []
        
        for project in self.projects.values():
            tech_stack = [t.lower() for t in project.get("tech_stack", [])]
            if any(tech_lower in t for t in tech_stack):
                matching_projects.append(project.get("name", "Unknown"))
        
        if not matching_projects:
            return f"I don't have projects using {technology}."
        
        return f"**Projects using {technology}:**\n\n" + "\n".join(f"• {p}" for p in matching_projects)
    
    # ============ Recommendations & Suggestions ============
    
    def suggest_project_improvement(self, project_name: str) -> str:
        """Suggest improvements for a project."""
        project = self._find_project(project_name)
        if not project:
            return f"I don't have information about '{project_name}'."
        
        suggestions = f"**Improvement Suggestions for {project.get('name', 'this project')}:**\n\n"
        
        improvements = {
            "SmartLeaf": [
                "Add model explainability using SHAP or LIME",
                "Implement mobile app for easier access",
                "Create API for integration with agriculture platforms",
                "Add multi-language support for global farmers"
            ],
            "BreatheEasy": [
                "Implement real-time notifications for pollution spikes",
                "Add historical data visualization and trend analysis",
                "Integrate with wearable devices for health metrics",
                "Create a mobile app for on-the-go monitoring"
            ],
            "Student Management System": [
                "Add automated email notifications for alerts",
                "Implement parent portal for progress tracking",
                "Create export functionality (PDF reports)",
                "Add advanced analytics and predictive insights"
            ],
            "Movie Recommendation System": [
                "Integrate with real streaming APIs (TMDB, IMDb)",
                "Add social features (friend recommendations, ratings)",
                "Implement A/B testing for algorithm optimization",
                "Create visualization of recommendation reasoning"
            ],
            "Smart Grocery AI": [
                "Add price comparison across multiple stores",
                "Implement barcode scanning for quick shopping",
                "Create loyalty program integration",
                "Add nutritional analysis and dietary preferences"
            ]
        }
        
        project_key = project.get("name")
        default_improvements = [
            "Write comprehensive documentation",
            "Add automated testing",
            "Deploy to cloud platform",
            "Create CI/CD pipeline"
        ]
        
        items = improvements.get(project_key, default_improvements)
        for i, suggestion in enumerate(items, 1):
            suggestions += f"{i}. {suggestion}\n"
        
        return suggestions
    
    def suggest_new_projects(self) -> str:
        """Suggest new project ideas based on existing skills."""
        suggestions = (
            "**Suggested Project Ideas:**\n\n"
            "1. **Healthcare Chatbot with ML** – Build an AI-powered chatbot using NLP and ML to provide health recommendations. Combine TensorFlow, Node.js, and MongoDB.\n\n"
            "2. **Stock Market Predictor** – Predict stock prices using LSTM neural networks and real-time data. Display predictions in a React dashboard.\n\n"
            "3. **Face Recognition Attendance System** – Use CNN for face detection and recognition. Integrate with the Student Management System for automated attendance.\n\n"
            "4. **E-commerce Recommendation Engine** – Build an advanced system combining content-based and collaborative filtering with personalization.\n\n"
            "5. **Weather Forecasting with ML** – Use historical weather data and deep learning to improve weather predictions.\n\n"
            "6. **Smart Crop Yield Predictor** – Combine SmartLeaf data with soil, weather, and other factors to predict crop yields.\n\n"
            "7. **Real-time Traffic Analyzer** – Analyze traffic patterns and suggest optimal routes using computer vision and ML."
        )
        return suggestions
    
    # ============ Learning & Career Path ============
    
    def learning_roadmap(self, focus: str = "general") -> str:
        """Provide a learning roadmap for skill development."""
        roadmaps = {
            "ml": (
                "**Machine Learning Roadmap:**\n\n"
                "1. **Foundation** – Linear Algebra, Calculus, Statistics\n"
                "2. **ML Basics** – Supervised/Unsupervised Learning, Regression, Classification\n"
                "3. **Advanced ML** – Ensemble Methods, Feature Engineering, Hyperparameter Tuning\n"
                "4. **Deep Learning** – Neural Networks, CNNs, RNNs, Transformers\n"
                "5. **Specializations** – NLP, Computer Vision, Reinforcement Learning\n"
                "6. **Production ML** – Model Deployment, MLOps, Monitoring\n"
                "7. **Advanced Topics** – Federated Learning, Transfer Learning, Meta-Learning"
            ),
            "nlp": (
                "**NLP Learning Roadmap:**\n\n"
                "1. **Basics** – Text preprocessing, Tokenization, Stemming, Lemmatization\n"
                "2. **Traditional NLP** – TF-IDF, Bag of Words, N-grams\n"
                "3. **Word Embeddings** – Word2Vec, GloVe, FastText\n"
                "4. **Deep Learning** – RNNs, LSTMs, GRUs\n"
                "5. **Transformers** – BERT, GPT, Attention Mechanisms\n"
                "6. **Advanced** – Fine-tuning, Transfer Learning, Few-shot Learning\n"
                "7. **Applications** – Chatbots, Machine Translation, Question Answering"
            ),
            "fullstack": (
                "**Full-Stack Development Roadmap:**\n\n"
                "1. **Frontend** – HTML/CSS, JavaScript, React Advanced Patterns\n"
                "2. **Backend** – Node.js, Express, REST APIs, Authentication\n"
                "3. **Databases** – MongoDB, PostgreSQL, Query Optimization\n"
                "4. **DevOps** – Docker, Kubernetes, CI/CD\n"
                "5. **Cloud** – AWS, GCP, or Azure Deployment\n"
                "6. **Testing** – Unit Testing, Integration Testing, E2E Testing\n"
                "7. **System Design** – Scalability, Caching, Microservices"
            ),
            "general": (
                "**Overall Development Roadmap:**\n\n"
                "**Current Strengths:**\n"
                "• ML/AI fundamentals and projects\n"
                "• Full-stack web development\n"
                "• Data analysis and preprocessing\n\n"
                "**Next Steps:**\n"
                "1. **Deepen ML Expertise** – Advanced algorithms, model deployment\n"
                "2. **NLP Specialization** – Transformers, pre-trained models\n"
                "3. **Cloud & DevOps** – Deploy models, CI/CD pipelines\n"
                "4. **System Design** – Build scalable systems\n"
                "5. **Contribute to Open Source** – Real-world impact\n"
                "6. **Technical Writing** – Share knowledge, build personal brand"
            )
        }
        
        return roadmaps.get(focus.lower(), roadmaps["general"])
    
    def career_interests(self) -> str:
        """Show career interests and paths."""
        interests = self.experience.get("career_interests", [])
        if not interests:
            return "I don't have career interest information."
        
        summary = "**Career Interests:**\n\n"
        for interest in interests:
            summary += f"• {interest}\n"
        
        summary += (
            "\n**Why these paths?**\n\n"
            "These roles combine your strengths in ML, data science, and full-stack development. "
            "You can specialize in any direction based on your interests and the projects demonstrate "
            "readiness for professional roles."
        )
        
        return summary
    
    # ============ Recruiter-Specific Questions ============
    
    def pitch_to_recruiter(self) -> str:
        """Generate a professional pitch for recruiters."""
        return (
            f"**Hi! I'm {self.developer.get('name', 'Nishan')}.**\n\n"
            "I'm an ML/AI student and full-stack developer passionate about building intelligent applications. "
            "I've completed 5 production-level projects spanning computer vision, recommendation systems, "
            "full-stack web development, and data science.\n\n"
            "**What I bring:**\n"
            "• Strong ML/AI foundation with TensorFlow, Keras, and scikit-learn\n"
            "• Full-stack development skills (React, Node.js, databases)\n"
            "• Experience with real-world problems (agriculture, health, e-commerce)\n"
            "• Clean code, version control, and collaborative development\n\n"
            "**Why I'm a great fit:**\n"
            "My projects show I can take complex problems and deliver working solutions. "
            "I'm eager to learn, adapt quickly, and contribute meaningfully to your team. "
            "Whether it's building ML pipelines, web apps, or data solutions, I'm ready to make an impact."
        )
    
    def ai_ml_specialist(self) -> str:
        """Highlight AI/ML expertise for technical roles."""
        return (
            "**AI/ML Specialist Profile:**\n\n"
            "**Deep Learning Projects:**\n"
            "• SmartLeaf (CNN-based plant disease detection)\n"
            "• Movie Recommendation System (Collaborative filtering + NLP)\n"
            "• Smart Grocery AI (Hybrid recommendation engine)\n\n"
            "**Technical Competencies:**\n"
            "• CNNs, RNNs, Neural Network Architecture\n"
            "• Recommendation Systems & Algorithms\n"
            "• NLP & Sentiment Analysis\n"
            "• Data Preprocessing & Feature Engineering\n"
            "• Model Evaluation & Optimization\n\n"
            "**Tools & Frameworks:**\n"
            "TensorFlow, Keras, Scikit-Learn, Pandas, Numpy\n\n"
            "**Ready For:**\n"
            "ML Engineer, Data Scientist, AI Research, Computer Vision roles"
        )
    
    def fullstack_developer_profile(self) -> str:
        """Highlight full-stack development expertise."""
        return (
            "**Full-Stack Developer Profile:**\n\n"
            "**Completed Projects:**\n"
            "• BreatheEasy (React + Node.js + MongoDB with real-time data)\n"
            "• Student Management System (CRUD operations, authentication, analytics)\n\n"
            "**Frontend Skills:**\n"
            "React, HTML5, CSS3, Tailwind CSS, Responsive Design\n\n"
            "**Backend Skills:**\n"
            "Node.js, Express, RESTful APIs, Authentication, Database Design\n\n"
            "**Database Expertise:**\n"
            "MongoDB (NoSQL), PostgreSQL (SQL), Data Modeling\n\n"
            "**Development Practices:**\n"
            "Git version control, clean code, component architecture, API design\n\n"
            "**Ready For:**\n"
            "Full-Stack Developer, Backend Engineer, Frontend Engineer, Web Developer roles"
        )
    
    # ============ Main Query Handler ============
    
    def answer_query(self, query: str) -> str:
        """Process user query and return appropriate answer."""
        query_lower = query.lower()
        
        # Intent detection
        if any(word in query_lower for word in ["about", "who are you", "tell me about yourself", "introduce"]):
            return self.about_developer()
        
        elif any(word in query_lower for word in ["skills", "technologies", "tech"]):
            return self.get_skills_summary()
        
        elif any(word in query_lower for word in ["expertise", "specialization", "strong at"]):
            return self.get_expertise_areas()
        
        elif any(word in query_lower for word in ["all projects", "portfolio", "what have you built"]):
            return self.list_all_projects()
        
        elif any(word in query_lower for word in ["smartleaf", "plant", "disease"]):
            return self.get_project_details("SmartLeaf")
        
        elif any(word in query_lower for word in ["breatheasy", "pollution", "air quality", "health"]):
            return self.get_project_details("BreatheEasy")
        
        elif any(word in query_lower for word in ["student", "management", "school"]):
            return self.get_project_details("Student Management System")
        
        elif any(word in query_lower for word in ["movie", "recommendation", "sentiment"]):
            return self.get_project_details("Movie Recommendation System")
        
        elif any(word in query_lower for word in ["grocery", "shopping", "smart"]):
            return self.get_project_details("Smart Grocery AI")
        
        elif any(word in query_lower for word in ["tech stack", "used in", "built with"]):
            # Try to extract project name
            projects_list = list(self.projects.values())
            for project in projects_list:
                if project.get("name").lower() in query_lower:
                    return self.get_project_tech_stack(project.get("name"))
            return "Please specify which project you'd like to know about."
        
        elif any(word in query_lower for word in ["improve", "improvement", "better", "enhance"]):
            # Extract project name
            projects_list = list(self.projects.values())
            for project in projects_list:
                if project.get("name").lower() in query_lower:
                    return self.suggest_project_improvement(project.get("name"))
            return "Please specify which project you'd like suggestions for."
        
        elif any(word in query_lower for word in ["new project", "project ideas", "what should i build"]):
            return self.suggest_new_projects()
        
        elif any(word in query_lower for word in ["learning", "roadmap", "improve skills"]):
            if any(word in query_lower for word in ["machine learning", "ml", "ai"]):
                return self.learning_roadmap("ml")
            elif any(word in query_lower for word in ["nlp", "language"]):
                return self.learning_roadmap("nlp")
            elif any(word in query_lower for word in ["fullstack", "full-stack", "web"]):
                return self.learning_roadmap("fullstack")
            else:
                return self.learning_roadmap()
        
        elif any(word in query_lower for word in ["career", "interests", "what roles"]):
            return self.career_interests()
        
        elif any(word in query_lower for word in ["recruiter", "hiring", "job", "interview", "pitch"]):
            return self.pitch_to_recruiter()
        
        elif any(word in query_lower for word in ["ai/ml", "ai specialist", "ml engineer"]):
            return self.ai_ml_specialist()
        
        elif any(word in query_lower for word in ["fullstack", "full-stack", "backend", "frontend"]):
            return self.fullstack_developer_profile()
        
        else:
            return (
                "I'm not sure how to answer that. Try asking me about:\n\n"
                "• My background and skills\n"
                "• My projects and tech stack\n"
                "• Project-specific improvements\n"
                "• Learning roadmaps\n"
                "• Career interests\n"
                "• AI/ML or Full-Stack expertise\n\n"
                "Feel free to rephrase your question!"
            )


def main():
    """Main interactive loop for the bot."""
    print("=" * 60)
    print("Welcome to GitHubProfileBot!")
    print("=" * 60)
    print("\nI'm an AI assistant for Nishan Bhurtel's GitHub portfolio.")
    print("Ask me about projects, skills, tech stack, career interests, and more!\n")
    print("Type 'exit' to quit.\n")
    
    bot = GitHubProfileBot()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nBot: Thanks for visiting! Check out my projects on GitHub. Goodbye! 👋")
            break
        
        if not user_input:
            continue
        
        response = bot.answer_query(user_input)
        print(f"\nBot: {response}\n")


if __name__ == "__main__":
    main()
