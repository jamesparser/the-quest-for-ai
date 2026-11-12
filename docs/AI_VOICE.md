# The AI Helper's Voice

## What it does
After each choice, the game asks an AI to write 1 or 2 kind sentences in the helper's voice. The AI is **asi1-mini** on **ASI Cloud** (free, OpenAI-style API).

## How the key stays secret
- The key is **never** in the code, on GitHub, or in the web page.
- **Online:** the key is saved in the Vercel project settings as `TQFAI_LLM_API_KEY`. Only the server can read it.
- **Players cannot type to the AI.** The server writes every question to the AI from the story files, so nobody can use the key as a free chatbot.
- Every AI reply is checked. Too long, a link, a bad word, or a personal question means the reply is thrown away and a written line is used instead.

## Running it on your own computer
Without a key, the game works fine and uses the written lines. To hear the AI voice locally:

1. Get your own free key from ASI Cloud. Please don't ask for someone else's.
2. Make a file called `.env` in the main project folder (it is ignored by git) with:
   ```
   TQFAI_LLM_API_KEY=your-key-here
   ```
3. Run `python -m tqfai serve` and open http://127.0.0.1:8787

Optional settings: `TQFAI_LLM_BASE_URL` (default `https://inference.asicloud.cudos.org/v1`) and `TQFAI_LLM_MODEL` (default `asi1-mini`). Any OpenAI-style API works, for example M3.1 if you have your own key.

## Changing how the helper talks
Edit `SYSTEM_PROMPT` in `src/tqfai/reasoning/llm.py`. Then play a few games and read the replies.
