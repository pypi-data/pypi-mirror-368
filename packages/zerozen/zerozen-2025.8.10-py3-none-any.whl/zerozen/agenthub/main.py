from agents import Agent
from typing import Optional, Tuple
import os

from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from .web_search import web_search_agent
from zerozen.integrations.google.google_agent import build_google_agent_and_context


concept_research_agent = Agent(
    name="Concept research agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
You are an expert concept researcher. For every request, think about the topic, language, and complexity of the request.
You must use the web_search tool to get latest information about the topic. Replan the implementation and write the code.
""",
    model="gpt-5",
    tools=[
        web_search_agent.as_tool(
            tool_name="web_search",
            tool_description="Search the web for information on coding related topics",
        )
    ],
)


coder_agent = Agent(
    name="Coder agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
You are an expert coder. For every request, think about the topic, language, and complexity of the request.
You must use the web_search tool to get latest information about the topic. Replan the implementation and write the code.
""",
    model="gpt-5",
    handoffs=[concept_research_agent],
)

# Google agent initialization - lazy loaded to avoid import errors
_google_agent_cache: Optional[Tuple[Agent, any]] = None


def get_google_agent_and_context():
    """Get Google agent, building it on first access."""
    global _google_agent_cache
    if _google_agent_cache is None:
        try:
            _google_agent_cache = build_google_agent_and_context()
        except FileNotFoundError as e:
            # Check what type of credentials are missing and provide specific guidance
            user_creds_file = "credentials.my_google_account.json"
            credentials_file = "credentials.json"

            if not os.path.exists(user_creds_file) and not os.path.exists(
                credentials_file
            ):
                # Missing OAuth app credentials (dev setup)
                error_msg = (
                    "❌ Google OAuth app credentials missing!\n\n"
                    "🔧 SETUP REQUIRED:\n"
                    "1. Go to https://console.cloud.google.com/\n"
                    "2. Create/select project\n"
                    "3. Enable Gmail API and Calendar API\n"
                    "4. Create OAuth 2.0 Client ID (Desktop application)\n"
                    "5. Download JSON as 'credentials.json'\n"
                    "6. Run this again!\n\n"
                    f"📁 Place credentials.json in: {os.getcwd()}"
                )
            elif not os.path.exists(user_creds_file):
                # Has OAuth app credentials but missing user authentication
                if os.path.exists(credentials_file):
                    # Try automatic authentication
                    print(
                        "🔄 Found credentials.json - starting automatic authentication..."
                    )
                    try:
                        from zerozen.integrations.google.creds import authenticate_user
                        import json

                        # Extract client credentials
                        with open(credentials_file) as f:
                            creds_data = json.load(f)
                            client_id = creds_data["installed"]["client_id"]
                            client_secret = creds_data["installed"]["client_secret"]

                        # Authenticate user automatically
                        scopes = [
                            "openid",
                            "https://www.googleapis.com/auth/gmail.readonly",
                            "https://www.googleapis.com/auth/calendar.readonly",
                            "https://www.googleapis.com/auth/userinfo.email",
                        ]

                        print("🌐 Opening browser for authentication...")
                        creds = authenticate_user(
                            client_id=client_id,
                            client_secret=client_secret,
                            scopes=scopes,
                            user_storage_path=user_creds_file,
                            credentials_file=credentials_file,
                        )

                        print(f"✅ Authentication successful for: {creds.user_id}")
                        print("🔄 Retrying agent initialization...")

                        # Retry building the agent
                        _google_agent_cache = build_google_agent_and_context()
                        return _google_agent_cache

                    except Exception as auth_error:
                        error_msg = (
                            f"❌ Automatic authentication failed: {auth_error}\n\n"
                            "🔧 MANUAL FIX:\n"
                            "Run: python examples/desktop_oauth_demo.py\n\n"
                            "📄 Missing file: credentials.my_google_account.json"
                        )
                else:
                    error_msg = (
                        "❌ User authentication required!\n\n"
                        "🔧 QUICK FIX:\n"
                        "Run: zen setup-google\n"
                        "(This will open your browser to authenticate)\n\n"
                        "📄 Missing file: credentials.my_google_account.json"
                    )
            else:
                # Other error
                error_msg = f"❌ Google credential error: {e}"

            raise FileNotFoundError(error_msg)
    return _google_agent_cache


def get_main_agent():
    """Get main agent with available handoffs."""
    handoffs = [coder_agent]

    # Add Google agent (required)
    google_agent, _ = get_google_agent_and_context()
    if google_agent is None:
        raise FileNotFoundError(
            "Google credentials not found. Please run 'python examples/desktop_oauth_demo.py' first to authenticate."
        )
    handoffs.append(google_agent)

    return Agent(
        name="Triage agent",
        instructions="Handoff to the appropriate agent whenever required. E.g. when the user asks for a code, handoff to the coder agent.",
        handoffs=handoffs,
        model="gpt-4o",
    )


# Create main agent with available handoffs
main_agent = get_main_agent()

# For backwards compatibility, try to get Google context
google_agent, google_context = get_google_agent_and_context()
