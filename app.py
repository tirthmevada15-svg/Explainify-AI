from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ===== AI FUNCTION =====
def ask_ai(prompt):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    return response.json()["choices"][0]["message"]["content"]


# ===== ROUTES =====
@app.route("/")
def home():
    return render_template_string(HTML_PAGE)


@app.route("/explain", methods=["POST"])
def explain():
    data = request.json
    user_input = data.get("text")

    prompt = f"""
You are Explainify AI.

Explain in a viral, clean format:

- Start with a bold hook
- Then simple explanation
- Then bullet points
- Keep it short and shareable

Topic:
{user_input}
"""

    result = ask_ai(prompt)

    return jsonify({"result": result})


# ===== FRONTEND =====
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Explainify</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: radial-gradient(circle at top, #0f172a, #020617); }
        .fade-in { animation: fadeIn 0.5s ease; }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        .cursor::after {
            content: "|";
            animation: blink 1s infinite;
        }
        @keyframes blink { 50% {opacity: 0;} }
        .loader {
            border: 3px solid rgba(255,255,255,0.1);
            border-top: 3px solid #3b82f6;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {100% {transform: rotate(360deg);}}
    </style>
</head>

<body class="text-white">

<!-- LANDING -->
<div id="landing" class="h-screen flex flex-col items-center justify-center text-center px-6 fade-in">

    <h1 class="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
        Explainify
    </h1>

    <p class="mt-4 text-gray-400">Ask anything. Understand everything.</p>

    <!-- Example Prompts -->
    <div class="mt-8 flex flex-wrap justify-center gap-3 max-w-xl">
        <button onclick="usePrompt('Explain AI simply')" class="px-4 py-2 bg-white/5 border border-white/10 rounded-xl">Explain AI</button>
        <button onclick="usePrompt('What is blockchain?')" class="px-4 py-2 bg-white/5 border border-white/10 rounded-xl">Blockchain</button>
        <button onclick="usePrompt('How stock market works?')" class="px-4 py-2 bg-white/5 border border-white/10 rounded-xl">Stock Market</button>
    </div>

    <button onclick="startApp()" class="mt-8 px-6 py-3 bg-blue-600 rounded-xl">
        Start →
    </button>

    <p class="mt-6 text-xs text-gray-500">
        Note: This website answers may be slow. Please wait ⏳
    </p>

</div>

<!-- CHAT -->
<div id="app" class="hidden flex flex-col h-screen max-w-3xl mx-auto">

    <div class="p-4 border-b border-white/10 flex justify-between">
        <h1>Explainify</h1>
    </div>

    <div id="chat" class="flex-1 overflow-y-auto p-4 space-y-5"></div>

    <div class="p-4 border-t border-white/10">
        <div class="flex gap-2 bg-white/5 border border-white/10 rounded-xl px-3 py-2">
            <input id="input" class="flex-1 bg-transparent outline-none" placeholder="Ask anything..." />
            <button onclick="sendMessage()" class="bg-blue-600 px-4 rounded">Send</button>
        </div>
    </div>

</div>

<script>
const chat = document.getElementById("chat");

// Start
function startApp() {
    document.getElementById("landing").classList.add("hidden");
    document.getElementById("app").classList.remove("hidden");
}

// Prompt click
function usePrompt(text) {
    startApp();
    document.getElementById("input").value = text;
    sendMessage();
}

// Render
function render(text, type) {
    let div = document.createElement("div");
    div.className = type === "user" ? "text-right fade-in" : "text-left fade-in";

    let formatted = text
        .replace(/\\*\\*(.*?)\\*\\*/g, "<b>$1</b>")
        .replace(/\\n/g, "<br>");

    div.innerHTML = `
        <div class="inline-block px-4 py-3 rounded-xl max-w-[75%]
        ${type === "user" ? "bg-blue-600" : "bg-white/5 border border-white/10"}">
        ${formatted}
        </div>
    `;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;

    return div.firstChild;
}

// Typing
async function typeText(text, el) {
    el.innerHTML = "";
    el.classList.add("cursor");

    let words = text.split(" ");
    for (let w of words) {
        el.innerHTML += w + " ";
        await new Promise(r => setTimeout(r, 25));
    }

    el.classList.remove("cursor");
}

// Loader
function showLoader() {
    let div = document.createElement("div");
    div.className = "text-left fade-in";

    div.innerHTML = `
        <div class="flex items-center gap-2 bg-white/5 border border-white/10 px-4 py-2 rounded-xl">
            <div class="loader"></div>
            <span class="text-sm text-gray-400">Thinking... please wait ⏳</span>
        </div>
    `;
    chat.appendChild(div);
    return div;
}

// Send
async function sendMessage() {
    let input = document.getElementById("input");
    let text = input.value.trim();
    if (!text) return;

    render(text, "user");
    input.value = "";

    let loader = showLoader();

    let res = await fetch("/explain", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text})
    });

    let data = await res.json();

    loader.remove();

    let bot = render("", "bot");
    await typeText(data.result, bot);
}
</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)