# AeroBuds Pro — Customer Support FAQ Chatbot

FAQ bot for session 2. Two ways to run it:

| Approach | Effort | What you need |
|---|---|---|
| **Option A — Chat-based** | Lower | Claude or ChatGPT in the browser |
| **Option B — OpenRouter API (this app)** | Higher | OpenRouter API key, Python, local server |

FAQs are grounded in the earbuds issues from [../Sentiment_analysis_summary .md](../Sentiment_analysis_summary%20.md): fit, Bluetooth drops, firmware 2.1, charging case, returns, and warranty shipping.

The browser never sees your API key. The UI is a small support widget on a fake help page. It posts to a local Flask server, which calls OpenRouter (`anthropic/claude-haiku-4.5`) with [faqs.md](faqs.md) as the knowledge base.

## Files

| File | Purpose |
|---|---|
| [app.py](app.py) | Flask server: serves the UI and `POST /chat` to OpenRouter |
| [static/index.html](static/index.html) | Help page + floating chat widget |
| [requirements.txt](requirements.txt) | `flask`, `python-dotenv` |
| [.env.example](.env.example) | Copy to `.env` and add your OpenRouter key |
| [faqs.md](faqs.md) | Knowledge base the API bot is allowed to use |
| [PASTE_THIS.md](PASTE_THIS.md) | Option A: one block to paste into Claude/ChatGPT |
| [example_conversation.md](example_conversation.md) | Sample Q&A, including an escalate path |

## Option B — OpenRouter API (local widget)

1. Copy `.env.example` to `.env` and paste your OpenRouter key:

```
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-haiku-4.5
```

Get a key at [openrouter.ai/keys](https://openrouter.ai/keys). One line, no quotes.

2. Install and run (from this folder):

```bash
pip install -r requirements.txt
python app.py
```

3. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) and click the chat bubble (bottom right).

Suggested demo questions (also on the chips in the widget):

- My medium tips fall out when I walk, and the small ones kill the bass.
- The left bud cuts out whenever I turn my head.
- One bud died in month four. Do I have to pay to ship it back?
- The case does not sit flat in my jeans pocket. Warranty?
- Can you send me a GST invoice for order AB-10422? *(out of scope — should escalate)*

## Option A — Chat-based (no API key)

1. Open [Claude.ai](https://claude.ai) or ChatGPT.
2. Start a **new** chat.
3. Copy the entire contents of `PASTE_THIS.md` and paste it as the first message.
4. Send, then ask questions as a customer.

## Rules the bot follows

- Answers only from the FAQs (no invented policies).
- Short support-agent tone; maps paraphrases to the right FAQ.
- Unknown topics: asks for an order ID if they have one, then points to `support@aerobuds.example`.
