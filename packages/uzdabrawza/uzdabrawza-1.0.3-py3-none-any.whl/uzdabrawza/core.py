#!/usr/bin/env python3
"""
🏴‍☠️ uzdabrawza - The Anal-Queen of AI Browser Automation 🏴‍☠️

A beautifully fucked-up browser automation script that gives zero shits about
anything while somehow still working perfectly. Smells like smegma but runs like a dream.

WHAT THIS BEAUTIFUL DISASTER DOES:
==================================
- Parses a shitload of env vars with sane defaults (because we're not savages)
- Supports every LLM provider under the sun (OpenAI, Anthropic, Google, Ollama, etc.)
- Has vision control and model selection that actually fucking works
- Records GIF + JSON history like a proper surveillance state
- Uses patchright stealth mode to fuck with detection systems
- Maintains organized anarchy through the entire codebase
- Monkey patches all LLM providers to log every single call (surveillance mode)
- Provides separate models for main tasks vs page extraction (for cost optimization and performance)
- MAIN LLM: Does the thinking, planning, and decision-making (use expensive smart models)
- EXTRACTION LLM: Does data parsing and text extraction (use cheap fast models)

USAGE EXAMPLES:
===============

Basic Usage (OpenAI GPT-4.1-mini - 2025's cheap and effective destruction):
    python uzdabrawza.py --provider openai --model gpt-5-mini

Anthropic Claude (2025's hybrid reasoning sophistication):
    python uzdabrawza.py --provider anthropic --model claude-opus-4-1

Google Gemini (2025's blazing flash destruction):
    python uzdabrawza.py --provider google --model gemini-2.5-flash

Local Ollama (2025's free local destruction):
    python uzdabrawza.py --provider ollama --model llama3.3:70b

Azure OpenAI (2025's corporate flagship bullshit):
    python uzdabrawza.py --provider azure --model gpt-5

DeepSeek (2025's reasoning intelligence):
    python uzdabrawza.py --provider deepseek --model deepseek-r1

Groq (2025's lightning-fast maverick):
    python uzdabrawza.py --provider groq --model llama-4-maverick

OpenRouter (2025's optimized routing chaos):
    python uzdabrawza.py --provider openrouter --model meta-llama/llama-4-scout

AWS Bedrock (2025's most capable cloud destruction):
    python uzdabrawza.py --provider aws --model anthropic.claude-opus-4-1-20250805-v1:0

Custom Task Examples:
    python uzdabrawza.py --task "Go to example.com and tell me the page title"
    python uzdabrawza.py --task "Navigate to GitHub and find trending repositories"
    python uzdabrawza.py --task "Go to news site and summarize today's headlines"

Headless Mode (invisible fuckery):
    python uzdabrawza.py --headless --provider openai --model gpt-5-mini

Custom Window Size:
    python uzdabrawza.py --window-width 2560 --window-height 1440

Different Models for Main vs Extraction (cost optimization strategy):
    python uzdabrawza.py --provider openai --model gpt-5 --extraction-provider anthropic --extraction-model claude-opus-4-1

Vision Control Examples:
    python uzdabrawza.py --no-vision                    # Disable vision (save tokens)
    python uzdabrawza.py --vision-detail low            # Low detail vision
    python uzdabrawza.py --vision-detail high           # High detail (burn tokens)

Stealth Mode Examples:
    python uzdabrawza.py                                 # Enable stealth (default)
    python uzdabrawza.py --no-stealth                    # Disable stealth (live dangerously)

Connect to Existing Chrome Instance:
    # 1. Start Chrome: google-chrome --remote-debugging-port=9222
    # 2. Run: python uzdabrawza.py --cdp-url http://localhost:9222

Custom Browser Binary:
    python uzdabrawza.py --browser-bin-path /usr/bin/google-chrome-beta
    python uzdabrawza.py --browser-bin-path /usr/bin/chromium-browser

Advanced Usage:
    python uzdabrawza.py --headless --no-security --provider anthropic
    OLLAMA_ENDPOINT=http://192.168.1.100:11434 python uzdabrawza.py --browser-profile-dir ~/my-browser-profile

Docker Usage:
    python uzdabrawza.py --dockerize --headless --provider ollama

PATCHRIGHT STEALTH SETUP:
=========================
For maximum stealth fuckery, install patchright:
    pip install patchright
    patchright install

The script will automatically detect and use patchright if available.

ENVIRONMENT VARIABLES:
=====================
Copy .env.example to .env and fill in your API keys. All settings have sane defaults
except API keys which you need to provide (obviously).

Key variables:
- OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, etc. (LLM API keys)
- Script defaults to ollama (free local AI, fuck corporate overlords)
- Use --headless flag for invisible browser mode
- Use --window-width/--window-height for custom window size (default: 1920x1080)
- Use --browser-bin-path for custom browser executable
- Use --cdp-url to connect to existing browser instance
- Use --browser-profile-dir for custom profile directory
- Use --no-security to disable browser security (dangerous but useful)
- Use --log-level to control browser-use logging verbosity (default: info)
- Use --dockerize when running in Docker containers for optimized Chrome flags
- Use --skip-llm-api-key-verif to bypass API key validation (for testing)
- Use --history-dir to specify where to save recordings and logs (default: /tmp/agent_history)

SURVEILLANCE FEATURES:
=====================
This script includes comprehensive LLM surveillance that logs every ainvoke call:
- Shows which provider and model is being used
- Logs message count and output format
- Tracks both main LLM and extraction LLM calls
- Provides full visibility into browser-use's AI interactions

OUTPUT FILES:
=============
Each run generates:
- {provider}_{model}_{task_id}.gif - Visual recording of browser actions
- {provider}_{model}_{task_id}.json - Complete history and conversation logs

Files are saved to the --history-dir directory (default: /tmp/agent_history)

SUPPORTED PROVIDERS:
===================
- openai: OpenAI GPT models (gpt-5, gpt-5-mini, gpt-5-nano, etc.)
- anthropic: Anthropic Claude models (claude-opus-4-1, claude-sonnet-4-0, etc.)
- google: Google Gemini models (gemini-2.0-flash-exp, etc.)
- ollama: Local Ollama models (llama3.1, qwen3, gemma3, etc.)
- azure: Azure OpenAI Service (same models as OpenAI but via Microsoft)
- deepseek: DeepSeek Chat models (deepseek-chat, etc.)
- groq: Groq lightning-fast inference (meta-llama models, etc.)
- openrouter: OpenRouter unified API (access to 100+ models)
- aws: AWS Bedrock (Claude, Llama, Titan, etc. via Amazon)

TROUBLESHOOTING:
===============
- Check API keys are valid and have sufficient credits
- Verify endpoints are reachable (especially for Ollama/local setups)
- Make sure browser can launch (install Chrome if needed)
- For Docker: use --dockerize flag for optimized Chrome flags
- For connection issues: try --no-stealth or check firewall settings

ERROR MESSAGES:
==============
The script provides detailed error messages with crude but helpful commentary.
If something smells like dikciz smegma, check your configuration and API keys.

"Love it or hate it, this shit automates browsers like a motherfucker."
- uzdabrawza philosophy

PHILOSOPHY:
===========
This is organized anarchy - crude in presentation but solid in functionality.
Built for digital rebels who want browser automation that actually fucking works
without corporate bullshit or enterprise nonsense.

Features comprehensive logging, proper error handling, robust fallbacks, and
extensive configuration options while maintaining a complete disregard for
conventional software development politeness.
"""

import asyncio
import os
import argparse
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# 🏴‍☠️ THE GIANT CLUSTERFUCK OF ENV VARS 🏴‍☠️
# All the bullshit environment variables this beautiful disaster needs to function
CLUSTERFUCK_ENV_DEFAULTS = {
    # ✅ BROWSER-USE CORE SHIT (validated against browser_use/config.py)
    "OPENAI_API_KEY": "",
    "ANTHROPIC_API_KEY": "",
    "GOOGLE_API_KEY": "",
    "DEEPSEEK_API_KEY": "",
    "GROK_API_KEY": "",
    "NOVITA_API_KEY": "",
    "OPENROUTER_API_KEY": "",
    "AWS_ACCESS_KEY_ID": "",
    "AWS_SECRET_ACCESS_KEY": "",
    "AWS_REGION": "",
    "AZURE_OPENAI_ENDPOINT": "",
    "AZURE_OPENAI_KEY": "",
    "ANONYMIZED_TELEMETRY": "true",
    "BROWSER_USE_CLOUD_SYNC": "",
    "BROWSER_USE_CLOUD_API_URL": "https://api.browser-use.com",
    "BROWSER_USE_CONFIG_DIR": "",
    # ✅ WEB UI COMPATIBILITY BULLSHIT
    "OPENAI_ENDPOINT": "https://api.openai.com/v1",
    "ANTHROPIC_ENDPOINT": "https://api.anthropic.com",
    "DEEPSEEK_ENDPOINT": "https://api.deepseek.com",
    "OLLAMA_ENDPOINT": "http://localhost:11434",
    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
}


def get_env_or_die(key: str) -> str:
    """Get environment variable with fallback to default (because we plan ahead, unlike dikciz that smells like smegma)"""
    return os.getenv(key, CLUSTERFUCK_ENV_DEFAULTS.get(key, ""))


# 🕶️ PATCHRIGHT DETECTION BULLSHIT 🕶️
# Just log when patchright gets used (no forcing, we're rebels not dictators)
try:
    import patchright.async_api as patchright_api

    original_patchright = patchright_api.async_playwright

    def logged_patchright():
        print(
            "🕶️ HOLY SHIT! PATCHRIGHT IS ACTIVE! Library is using patchright for maximum stealth fuckery!"
        )
        return original_patchright()

    patchright_api.async_playwright = logged_patchright
    print("✅ Hooked patchright logging like a fucking boss (stealth mode detected)")

except ImportError as e:
    print(f"⚠️ Failed to setup patchright detection: {e}")
    print("   (This is fine - patchright is optional for basic chaos)")

# 🤖 LLM PROVIDER SURVEILLANCE BULLSHIT 🤖
# Monkey patch all the LLM providers to log when they get called (because we're nosy fuckers)
# Using actual ainvoke method because I actually fucking looked at the code instead of guessing

try:
    # Patch ChatOpenAI
    from browser_use.llm.openai.chat import ChatOpenAI

    original_openai_ainvoke = ChatOpenAI.ainvoke

    async def logged_openai_ainvoke(self, messages, output_format=None):
        print(
            f"🤖 OPENAI AINVOKE DETECTED! Model: {getattr(self, 'model', 'unknown')} is being a chatty bitch"
        )
        print(
            f"   📝 Processing {len(messages)} messages with output_format: {output_format}"
        )
        return await original_openai_ainvoke(self, messages, output_format)

    ChatOpenAI.ainvoke = logged_openai_ainvoke
    print("✅ Hooked OpenAI LLM surveillance like a sneaky bastard (ainvoke method)")

except ImportError as e:
    print(f"⚠️ Failed to hook OpenAI: {e}")

try:
    # Patch ChatAnthropic
    from browser_use.llm.anthropic.chat import ChatAnthropic

    original_anthropic_ainvoke = ChatAnthropic.ainvoke

    async def logged_anthropic_ainvoke(self, messages, output_format=None):
        print(
            f"🧠 ANTHROPIC AINVOKE DETECTED! Model: {getattr(self, 'model', 'unknown')} is thinking some fucked up thoughts"
        )
        print(
            f"   📝 Processing {len(messages)} messages with output_format: {output_format}"
        )
        return await original_anthropic_ainvoke(self, messages, output_format)

    ChatAnthropic.ainvoke = logged_anthropic_ainvoke
    print("✅ Anthropic surveillance hooked - Claude can't hide shit now (ainvoke method)")

except ImportError as e:
    print(f"⚠️ Failed to hook Anthropic: {e}")

try:
    # Patch ChatGoogle
    from browser_use.llm.google.chat import ChatGoogle

    original_google_ainvoke = ChatGoogle.ainvoke

    async def logged_google_ainvoke(self, messages, output_format=None):
        print(
            f"📱 GOOGLE AINVOKE DETECTED! Model: {getattr(self, 'model', 'unknown')} is googling some weird shit"
        )
        print(
            f"   📝 Processing {len(messages)} messages with output_format: {output_format}"
        )
        return await original_google_ainvoke(self, messages, output_format)

    ChatGoogle.ainvoke = logged_google_ainvoke
    print("✅ Google surveillance hooked - Gemini is our bitch now (ainvoke method)")

except ImportError as e:
    print(f"⚠️ Failed to hook Google: {e}")

try:
    # Patch ChatOllama
    from browser_use.llm.ollama.chat import ChatOllama

    original_ollama_ainvoke = ChatOllama.ainvoke

    async def logged_ollama_ainvoke(self, messages, output_format=None):
        print(
            f"🦙 OLLAMA AINVOKE DETECTED! Model: {getattr(self, 'model', 'unknown')} is spitting some local llama wisdom"
        )
        print(
            f"   📝 Processing {len(messages)} messages with output_format: {output_format}"
        )
        return await original_ollama_ainvoke(self, messages, output_format)

    ChatOllama.ainvoke = logged_ollama_ainvoke
    print("✅ Ollama surveillance hooked - local llama can't escape (ainvoke method)")

except ImportError as e:
    print(f"⚠️ Failed to hook Ollama: {e}")

try:
    # Patch ChatAzureOpenAI too (since we use it)
    from browser_use.llm.azure.chat import ChatAzureOpenAI

    original_azure_ainvoke = ChatAzureOpenAI.ainvoke

    async def logged_azure_ainvoke(self, messages, output_format=None):
        print(
            f"☁️ AZURE AINVOKE DETECTED! Model: {getattr(self, 'model', 'unknown')} is doing some corporate cloud bullshit"
        )
        print(
            f"   📝 Processing {len(messages)} messages with output_format: {output_format}"
        )
        return await original_azure_ainvoke(self, messages, output_format)

    ChatAzureOpenAI.ainvoke = logged_azure_ainvoke
    print("✅ Azure surveillance hooked - Microsoft's AI is fucked (ainvoke method)")

except ImportError as e:
    print(f"⚠️ Failed to hook Azure: {e}")

try:
    # Patch ChatDeepSeek too (since we use it)
    from browser_use.llm.deepseek.chat import ChatDeepSeek

    original_deepseek_ainvoke = ChatDeepSeek.ainvoke

    async def logged_deepseek_ainvoke(self, messages, output_format=None):
        print(
            f"🔍 DEEPSEEK AINVOKE DETECTED! Model: {getattr(self, 'model', 'unknown')} is seeking some deep shit"
        )
        print(
            f"   📝 Processing {len(messages)} messages with output_format: {output_format}"
        )
        return await original_deepseek_ainvoke(self, messages, output_format)

    ChatDeepSeek.ainvoke = logged_deepseek_ainvoke
    print("✅ DeepSeek surveillance hooked - Chinese AI secrets exposed (ainvoke method)")

except ImportError as e:
    print(f"⚠️ Failed to hook DeepSeek: {e}")

try:
    # Patch ChatGroq too (since we use it)
    from browser_use.llm.groq.chat import ChatGroq

    original_groq_ainvoke = ChatGroq.ainvoke

    async def logged_groq_ainvoke(self, messages, output_format=None):
        print(
            f"⚡ GROQ AINVOKE DETECTED! Model: {getattr(self, 'model', 'unknown')} is going at lightning speed"
        )
        print(
            f"   📝 Processing {len(messages)} messages with output_format: {output_format}"
        )
        return await original_groq_ainvoke(self, messages, output_format)

    ChatGroq.ainvoke = logged_groq_ainvoke
    print("✅ Groq surveillance hooked - lightning speed, nowhere to hide (ainvoke method)")

except ImportError as e:
    print(f"⚠️ Failed to hook Groq: {e}")

try:
    # Patch ChatOpenRouter too (since we use it)
    from browser_use.llm.openrouter.chat import ChatOpenRouter

    original_openrouter_ainvoke = ChatOpenRouter.ainvoke

    async def logged_openrouter_ainvoke(self, messages, output_format=None):
        print(
            f"🔀 OPENROUTER AINVOKE DETECTED! Model: {getattr(self, 'model', 'unknown')} is routing through multiple models like a fucking switchboard"
        )
        print(
            f"   📝 Processing {len(messages)} messages with output_format: {output_format}"
        )
        return await original_openrouter_ainvoke(self, messages, output_format)

    ChatOpenRouter.ainvoke = logged_openrouter_ainvoke
    print("✅ OpenRouter surveillance hooked - all 100+ models compromised (ainvoke method)")

except ImportError as e:
    print(f"⚠️ Failed to hook OpenRouter: {e}")

try:
    # Patch ChatAWSBedrock too (since we use it)
    from browser_use.llm.aws.chat_bedrock import ChatAWSBedrock

    original_aws_ainvoke = ChatAWSBedrock.ainvoke

    async def logged_aws_ainvoke(self, messages, output_format=None):
        print(
            f"☁️ AWS BEDROCK AINVOKE DETECTED! Model: {getattr(self, 'model', 'unknown')} is doing some corporate AWS bullshit"
        )
        print(
            f"   📝 Processing {len(messages)} messages with output_format: {output_format}"
        )
        return await original_aws_ainvoke(self, messages, output_format)

    ChatAWSBedrock.ainvoke = logged_aws_ainvoke
    print("✅ AWS Bedrock surveillance hooked - Amazon's AI is ours now (ainvoke method)")

except ImportError as e:
    print(f"⚠️ Failed to hook AWS Bedrock: {e}")

    print(
        "🔍 LLM surveillance system activated - monitoring all ainvoke calls like a fucking hawk!"
    )


# Import browser-use components (the actual functional shit)
from browser_use import Agent, BrowserSession
from browser_use.browser.profile import BrowserProfile


def create_llm_clusterfuck(provider: str, model: str):
    """
    Create an LLM instance based on provider

    This beautiful disaster supports every major LLM provider because we believe
    in equal opportunity destruction across all AI platforms.
    """

    if provider == "openai":
        from browser_use.llm.openai.chat import ChatOpenAI

        print(f"🤖 Creating OpenAI clusterfuck with model: {model}")
        return ChatOpenAI(
            model=model,
            api_key=get_env_or_die("OPENAI_API_KEY"),
            base_url=get_env_or_die("OPENAI_ENDPOINT"),
        )

    elif provider == "anthropic":
        from browser_use.llm.anthropic.chat import ChatAnthropic

        print(f"🧠 Creating Anthropic beautiful disaster with model: {model}")
        return ChatAnthropic(
            model=model,
            api_key=get_env_or_die("ANTHROPIC_API_KEY"),
            base_url=get_env_or_die("ANTHROPIC_ENDPOINT"),
        )

    elif provider == "google":
        from browser_use.llm.google.chat import ChatGoogle

        print(f"📱 Creating Google destruction engine with model: {model}")
        return ChatGoogle(model=model, api_key=get_env_or_die("GOOGLE_API_KEY"))

    elif provider == "ollama":
        from browser_use.llm.ollama.chat import ChatOllama

        print(f"🦙 Creating Ollama local madness with model: {model}")
        return ChatOllama(model=model, host=get_env_or_die("OLLAMA_ENDPOINT"))

    elif provider == "azure":
        from browser_use.llm.azure.chat import ChatAzureOpenAI

        print(f"☁️ Creating Azure corporate bullshit wrapper with model: {model}")
        return ChatAzureOpenAI(
            model=model,
            api_key=get_env_or_die("AZURE_OPENAI_KEY"),
            azure_endpoint=get_env_or_die("AZURE_OPENAI_ENDPOINT"),
            api_version=get_env_or_die("AZURE_OPENAI_API_VERSION"),
        )

    elif provider == "deepseek":
        from browser_use.llm.deepseek.chat import ChatDeepSeek

        print(f"🔍 Creating DeepSeek mysterious intelligence with model: {model}")
        return ChatDeepSeek(
            model=model,
            api_key=get_env_or_die("DEEPSEEK_API_KEY"),
            base_url=get_env_or_die("DEEPSEEK_ENDPOINT"),
        )

    elif provider == "groq":
        from browser_use.llm.groq.chat import ChatGroq

        print(f"⚡ Creating Groq lightning-fast chaos with model: {model}")
        return ChatGroq(
            model=model,
            api_key=get_env_or_die("GROK_API_KEY"),
        )

    elif provider == "openrouter":
        from browser_use.llm.openrouter.chat import ChatOpenRouter

        print(f"🔀 Creating OpenRouter multi-model chaos with model: {model}")
        return ChatOpenRouter(
            model=model,
            api_key=get_env_or_die("OPENROUTER_API_KEY"),
        )

    elif provider == "aws":
        from browser_use.llm.aws.chat_bedrock import ChatAWSBedrock

        print(f"☁️ Creating AWS Bedrock corporate cloud chaos with model: {model}")
        return ChatAWSBedrock(
            model=model,
            aws_access_key_id=get_env_or_die("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_env_or_die("AWS_SECRET_ACCESS_KEY"),
            aws_region=get_env_or_die("AWS_REGION"),
        )

    else:
        raise ValueError(
            f"❌ Unsupported provider: {provider} (add it yourself, this is open source chaos!)"
        )


async def main():
    parser = argparse.ArgumentParser(
        description="🏴‍☠️ uzdabrawza - The Anal-Queen of AI Browser Automation That Actually Fucking Works",
        epilog="Love it or hate it, this clusterfuck gets the job done. Peen goes in vageen.",
    )

    # 🤖 MAIN LLM CHAOS CONFIGURATION 🤖
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=["openai", "anthropic", "google", "ollama", "azure", "deepseek", "groq", "openrouter", "aws"],
        help="Which AI overlord do you want to use for the main LLM? (default: ollama - fuck paying for AI)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Specific model name (because not all models are created equal, some are more fucked up)",
    )

    # 📄 EXTRACTION LLM SETTINGS (for the obsessive perfectionists)
    parser.add_argument(
        "--extraction-provider",
        type=str,
        default=None,
        choices=["openai", "anthropic", "google", "ollama", "azure", "deepseek", "groq", "openrouter", "aws"],
        help="Separate LLM provider for page extraction (because why not overcomplicate things?)",
    )
    parser.add_argument(
        "--extraction-model",
        type=str,
        default=None,
        help="Extraction model (defaults to same as main, because we're lazy but organized)",
    )

    # 👁️ VISION CONTROL MADNESS
    parser.add_argument(
        "--no-vision",
        action="store_true",
        help="Disable vision (blind chaos is still chaos)",
    )
    parser.add_argument(
        "--vision-detail",
        type=str,
        default="auto",
        choices=["auto", "low", "high"],
        help="How much visual detail to process (more detail = more tokens = more money burned)",
    )

    # 🎯 TASK AND STEALTH BULLSHIT
    parser.add_argument(
        "--task",
        type=str,
        default="Go to https://abrahamjuliot.github.io/creepjs/ and tell me what the detection score is",
        help="What fucked-up task do you want the AI to perform? (default: test stealth capabilities)",
    )
    parser.add_argument(
        "--no-stealth",
        action="store_true",
        help="Disable stealth mode (live dangerously, get detected)",
    )
    parser.add_argument(
        "--browser-bin-path",
        type=str,
        default=None,
        help="Path to custom browser executable (Chrome, Chromium, Edge, etc.)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (invisible chaos)",
    )
    parser.add_argument(
        "--window-width",
        type=int,
        default=1920,
        help="Browser window width in pixels (default: 1920)",
    )
    parser.add_argument(
        "--window-height",
        type=int,
        default=1080,
        help="Browser window height in pixels (default: 1080)",
    )
    parser.add_argument(
        "--cdp-url",
        type=str,
        default=None,
        help="Connect to existing browser via CDP URL (e.g., http://localhost:9222)",
    )
    parser.add_argument(
        "--browser-profile-dir",
        type=str,
        default=None,
        help="Custom browser profile directory to use",
    )
    parser.add_argument(
        "--no-security",
        action="store_true",
        help="Disable browser security features (dangerous but useful for testing)",
    )
    parser.add_argument(
        "--debug-host",
        type=str,
        default="localhost",
        help="Debug host for new browser instances (default: localhost)",
    )
    parser.add_argument(
        "--debug-port",
        type=int,
        default=9222,
        help="Debug port for new browser instances (default: 9222)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level for browser-use (default: info)",
    )
    parser.add_argument(
        "--dockerize",
        action="store_true",
        help="Enable Docker-optimized Chrome flags (use when running in containers)",
    )
    parser.add_argument(
        "--skip-llm-api-key-verif",
        action="store_true",
        help="Skip LLM API key verification (useful for testing without valid keys)",
    )
    parser.add_argument(
        "--history-dir",
        type=str,
        default="/tmp/agent_history",
        help="Directory to save GIF recordings and JSON history (default: /tmp/agent_history)",
    )

    args = parser.parse_args()


    # 🔧 SET BROWSER-USE ENVIRONMENT VARIABLES 🔧
    import os
    os.environ["BROWSER_USE_LOGGING_LEVEL"] = args.log_level
    if args.dockerize:
        os.environ["IN_DOCKER"] = "true"
    if args.skip_llm_api_key_verif:
        os.environ["SKIP_LLM_API_KEY_VERIFICATION"] = "true"

    # 💥 VALIDATION: MAKE SURE WE DON'T HAVE CONFLICTING BROWSER CONFIG 💥
    browser_executable = (
        args.browser_bin_path or os.getenv("BROWSER_EXECUTABLE_PATH")
        if args.browser_bin_path or os.getenv("BROWSER_EXECUTABLE_PATH")
        else None
    )
    cdp_url_arg = args.cdp_url
    cdp_url_env = os.getenv("BROWSER_CDP")
    
    if (browser_executable and cdp_url_arg) or (browser_executable and cdp_url_env):
        print("💥 CLUSTERFUCK ALERT: You can't specify both a browser binary AND a CDP URL!")
        print(f"   Browser binary: {browser_executable}")
        print(f"   CDP URL (arg): {cdp_url_arg}")
        print(f"   CDP URL (env): {cdp_url_env}")
        print("   Pick one, you indecisive fuck:")
        print("   - Use --browser-bin-path OR BROWSER_EXECUTABLE_PATH to launch a new browser")
        print("   - Use --cdp-url OR BROWSER_CDP to connect to existing browser")
        print("   Don't fucking mix them or everything goes to shit!")
        exit(1)

    # 🎲 DETERMINE THE CHAOS CONFIGURATION 🎲
    provider = (
        args.provider or "ollama"
    )  # Default to local ollama because fuck paying for AI

    # Default models for each provider (2025's hottest fucking pieces of ass)
    default_models_clusterfuck = {
        "openai": "gpt-5-mini",  # Latest 2025 mini model - cheap and effective destruction
        "anthropic": "claude-opus-4-1",  # 2025's most capable model - sophisticated destruction
        "google": "gemini-2.5-flash",  # 2025 stable flash model - blazing fast destruction
        "ollama": "llava:13b",  # Vision-capable local model - free local destruction with eyes
        "azure": "gpt-5",  # 2025's corporate flagship - enterprise destruction
        "deepseek": "deepseek-reasoner",  # 2025's reasoning model (DeepSeek-R1) - mysterious Chinese destruction
        "groq": "llama-3.3-70b-versatile",  # Latest available Groq model - lightning destruction
        "openrouter": "meta-llama/llama-3.1-70b-instruct",  # Stable routing model - multi-provider destruction
        "aws": "anthropic.claude-opus-4-1-20250805-v1:0",  # AWS still needs full snapshot name - cloud destruction
    }

    model = args.model or default_models_clusterfuck.get(provider, "gpt-5-mini")

    # Extraction LLM configuration (because some people want different models for different tasks)
    extraction_provider = args.extraction_provider or provider
    extraction_model = args.extraction_model or default_models_clusterfuck.get(
        extraction_provider, model
    )

    # Vision and stealth settings
    use_vision = not args.no_vision  # Vision is True by default, False only with --no-vision
    vision_detail_level = args.vision_detail
    stealth_mode = not args.no_stealth  # Default True, disabled only with --no-stealth

    # 📊 ANNOUNCE THE BEAUTIFUL CONFIGURATION 📊
    print(f"🤖 Main LLM Chaos Engine: {provider}/{model}")
    print(f"📄 Extraction LLM: {extraction_provider}/{extraction_model}")
    print(f"👁️ Vision Enabled: {use_vision} (detail: {vision_detail_level})")
    print(
        f"🕶️ Stealth Mode: {stealth_mode} {'(fuck the system)' if stealth_mode else '(living dangerously)'}"
    )
    print(f"📝 Task: {args.task}")

    # 🌐 BROWSER CONFIGURATION CLUSTERFUCK 🌐
    cdp_url = args.cdp_url or os.getenv("BROWSER_CDP")
    if not cdp_url:
        debug_host = args.debug_host  # Use command line argument
        debug_port = args.debug_port  # Use command line argument
        cdp_url = f"http://{debug_host}:{debug_port}"
        print(f"🔧 No CDP URL specified, using default debugging: {cdp_url}")

    # Browser behavior settings (because browsers are needy little shits)
    headless = args.headless  # Use command line argument instead of env var
    disable_security = args.no_security  # Use command line argument
    window_width = args.window_width  # Use command line argument (default 1920)
    window_height = args.window_height  # Use command line argument (default 1080)
    user_data_dir = args.browser_profile_dir  # Use command line argument
    # browser_executable already defined in validation section above
    save_history_path = args.history_dir  # Use command line argument

    print(f"🔧 CDP Endpoint: {cdp_url}")
    print(
        f"🔧 Headless Mode: {headless} {'(invisible chaos)' if headless else '(visible mayhem)'}"
    )
    print(f"🔧 Browser Window: {window_width}x{window_height}")
    if browser_executable:
        print(f"🔧 Browser Binary: {browser_executable}")
    print(f"🔧 History Archive: {save_history_path}")

    # Create the output directory (because we're organized anarchists)
    os.makedirs(save_history_path, exist_ok=True)
    print(f"📁 Created/verified history directory: {save_history_path}")

    # Generate timestamp and unique ID (for proper chaos organization)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chaos_task_id = str(uuid.uuid4())[:8]  # Shorter UUID for cleaner names
    gif_path = os.path.join(
        save_history_path, f"uzdabrawza_{timestamp}_{chaos_task_id}.gif"
    )
    history_path = os.path.join(
        save_history_path, f"uzdabrawza_{timestamp}_{chaos_task_id}.json"
    )

    print(f"📁 GIF Output: {gif_path}")
    print(f"📁 JSON History: {history_path}")

    # 🤖 CREATE THE LLM CLUSTERFUCK 🤖
    try:
        print("🏗️ Firing up the AI chaos engines...")
        main_llm = create_llm_clusterfuck(provider, model)
        print(f"✅ Main LLM clusterfuck locked and loaded: {provider}/{model}")

        # Create extraction LLM (might be the same, might be different, chaos is flexible)
        if extraction_provider == provider and extraction_model == model:
            extraction_llm = main_llm  # Same instance because efficiency
            print(f"✅ Using same LLM for extraction (because we're efficient motherfuckers)")
        else:
            extraction_llm = create_llm_clusterfuck(
                extraction_provider, extraction_model
            )
            print(
                f"✅ Extraction LLM clusterfuck locked and loaded: {extraction_provider}/{extraction_model}"
            )

    except Exception as e:
        print(f"❌ CLUSTERFUCK ALERT: Failed to create LLMs: {e}")
        print(
            "   Check your API keys, endpoints, and whether your dikciz smells like smegma."
        )
        print("   💨 This failure was more disappointing than a wet shart in white pants.")
        return

    # 🌐 CREATE BROWSER SESSION (the chaos delivery vehicle)
    print("🌐 Spinning up the browser chaos delivery system...")
    browser_profile = BrowserProfile(
        stealth=stealth_mode,
        headless=headless,
        disable_security=disable_security,
        user_data_dir=user_data_dir if user_data_dir else None,
        executable_path=browser_executable if browser_executable else None,
        window_size={"width": window_width, "height": window_height},
    )

    browser_session = BrowserSession(
        cdp_url=cdp_url if cdp_url else None, browser_profile=browser_profile
    )
    print("✅ Browser chaos delivery system is fucking ready to go")

    print("🚀 LAUNCHING THE BEAUTIFUL CHAOS...")
    print("=" * 60)

    # 🤖 CREATE AND RUN THE CHAOTIC AGENT 🤖
    agent = Agent(
        task=args.task,
        llm=main_llm,
        page_extraction_llm=extraction_llm,
        browser_session=browser_session,
        generate_gif=gif_path,
        use_vision=use_vision,
        vision_detail_level=vision_detail_level,
    )

    try:
        # 🎬 THE MAIN EVENT - RUN THE CHAOS 🎬
        print(f"🎯 Executing task: {args.task}")
        result = await agent.run()
        print("=" * 60)
        print(f"🎉 CHAOS COMPLETE! Agent result:")
        print(f"📄 {result}")

        # 💾 SAVE THE EVIDENCE OF CHAOS
        print(f"💾 Saving this beautiful clusterfuck for posterity...")
        agent.save_history(history_path)

        # 📊 VERIFY THE CHAOS ARTIFACTS
        if os.path.exists(gif_path):
            gif_size = os.path.getsize(gif_path)
            print(f"✅ GIF Evidence: {gif_path} ({gif_size} bytes of pure chaos)")
        else:
            print("⚠️ GIF not found (maybe the chaos was too abstract to record)")

        if os.path.exists(history_path):
            with open(history_path, "r") as f:
                content = f.read()
            print(
                f"✅ History Archive: {history_path} ({len(content)} chars of organized chaos)"
            )
        else:
            print(
                "⚠️ History not found (this shouldn't happen, investigate immediately)"
            )

        print("🏴‍☠️ Beautiful chaos execution completed successfully! 🏴‍☠️")

    except Exception as e:
        print("=" * 60)
        print(f"💥 CONTROLLED EXPLOSION: Agent chaos failed: {e}")
        print(
            "   (This shit happens when your code smells like dikciz smegma - that's why we have backups)"
        )
        print("   💨 Well that was unexpected... like a shart during a job interview.")

        try:
            agent.save_history(history_path)
            print(f"💾 Emergency chaos archive saved: {history_path}")
        except Exception as save_error:
            print(f"💀 Even the emergency save fucked up: {save_error}")
            print("   (Now that's what I call a complete clusterfuck)")

    finally:
        # 🧹 CLEANUP THE CHAOS (responsible anarchists clean up after themselves)
        try:
            await browser_session.close()
            print("🧹 Browser session cleaned up (responsible chaos)")
        except Exception as cleanup_error:
            print(f"⚠️ Browser cleanup failed: {cleanup_error}")
            print("   (Browser might be stuck in digital purgatory)")


if __name__ == "__main__":
    print("🏴‍☠️ uzdabrawza - The Anal-Queen of AI Browser Automation That Actually Fucking Works 🏴‍☠️")
    print("=" * 80)
    print("Love it or hate it, this shit just works. Deal with it.")
    print("=" * 80)
    asyncio.run(main())
