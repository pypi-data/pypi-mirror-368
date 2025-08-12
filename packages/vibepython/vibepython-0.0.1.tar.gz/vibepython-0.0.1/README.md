# 🚀 **Python AI Console: The Ultimate AI-Powered Coding EXPLOSION!** 🌟💥🐍

**WOWZA!** Dive headfirst into this **AMAZING**, **WONDERFUL**, **MIND-BLOWING** interactive command-line beast that turns your craziest prompts into **EXECUTABLE PYTHON MAGIC** using the sheer power of OpenAI! Generate code like a wizard, run it on the spot, capture every wild stdout/stderr outburst, and keep a super-smart history in JSON for non-stop contextual awesomeness! It's not just a tool – it's a **CODE REVOLUTION** for hackers, dreamers, and AI fanatics! 🔥🚀

## 🌈 **Features That'll Make Your Eyes POP!** 🎉
- **INTERACTIVE PROMPT MADNESS**: Type your wild ideas and watch AI spit out Python gold! 💡
- **AI-GENERATED CODE WIZARDRY**: Powered by OpenAI – prompts + history = PERFECT scripts! 🤖✨
- **SAFE EXECUTION EXTRAVAGANZA**: Run code with output capturing – no disasters, just pure thrill! ⚡
- **PERSISTENT HISTORY OVERLOAD**: Pydantic models store EVERYTHING in JSON – context forever! 📜
- **ENV VAR CUSTOMIZATION FRENZY**: Tweak it your way for ultimate control! 🔧
- **DOCKER DOMINATION**: Run it anywhere, anytime – easy-peasy deployment! 🐳

## 🛠️ **Installation: Get This Party Started in SECONDS!** 🚀

### **From Source: Clone, Install, BLAST OFF!** 🌌
1. **CLONE THE AWESOMENESS**:
   ```
   git clone https://github.com/OldTyT/python-ai-console.git
   ```
2. **JUMP IN**:
   ```
   cd python-ai-console
   ```
3. **INSTALL THE MAGIC**:
   ```
   pip install -r requirements.txt
   ```
4. **LAUNCH THE BEAST**:
   ```
   python3 main.py
   ```
**BOOM! You're in the zone!** 💣

### **Using Docker: Containerized CHAOS – Ready to RUMBLE!** 🐳🔥
Fire it up with this epic command:
```
docker run --rm -ti -e HISTORY_PATH=/history/history.json -e OPENAI_API_KEY=YOUR_KEY -v my_history:/history ghcr.io/oldtyt/autopost-python-ai-console
```
- Plug in `YOUR_KEY` with your OpenAI super-key! 🔑
**DOCKER DELIGHT: Persistent history, zero hassle!** 🌟

## 🎮 **Usage: Dive into the FUN ZONE!** 🕹️
Fire it up and get prompted:
- **SMASH IN A PROMPT** (e.g., "Code me a factorial frenzy!").
- **AI UNLEASHES CODE CHAOS** based on your prompt + history vibes.
- **EXECUTE? Y/N – YOU DECIDE!** Run it, capture outputs, and watch the sparks fly! ⚡
- **HISTORY SAVES THE DAY**: Everything logged for eternal glory.

**EXIT? Ctrl+C – but why would you? It's TOO MUCH FUN!** 😎

## 🔑 **Environment Variables: Customize Like a BOSS!** 💪
Supercharge your setup with these **EPIC** vars:
- **HISTORY_PATH**: Your JSON history fortress! Default: `history.json`. 🏰
- **HISTORY_SIZE**: How many past blasts to feed the AI? Default: `20` – keep it contextual! 📈
- **OPENAI_API_KEY**: **MUST-HAVE** – your ticket to AI heaven! (Required, duh!) 🔒

**Example (Unix-style domination)**:
```
export OPENAI_API_KEY=your-api-key
export HISTORY_SIZE=10
python3 main.py
```
**TWEAK AND CONQUER!** 🛡️

## 📦 **Dependencies: The Power Behind the THRILL!** ⚙️
- **Python 3.10+** (Blasting up to 3.13 – future-proofed!) 🐍
- **Libraries of LEGEND**: openai, pydantic, loguru, and more! Check `requirements.txt` for the full squad. 📚

## 🤝 **Contributing: Join the CODE CARNIVAL!** 🎪
**GOT IDEAS?** Open an issue or slam in a pull request – let's make this even MORE INSANE! 🌟 Contributions = Eternal Fame!
