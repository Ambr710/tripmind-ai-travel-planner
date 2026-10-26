"""
app.py - runs the Travel Assistant as a website on http://localhost:5000
Put this file in the same folder as main.py, agents.py, rag_engine.py, tools.py
Run:  python app.py
"""
import os
from flask import Flask, request, jsonify, render_template_string

from rag_engine import VectorStore
from agents import RouterAgent

PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pdfs")

app = Flask(__name__)
store = VectorStore().load_pdfs(PDF_DIR)   # built once when the server starts
router = RouterAgent(store)

PAGE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Smart Travel Planning Assistant</title>
<style>
  body { font-family: Arial, sans-serif; background:#f1f5f9; margin:0; }
  .wrap { max-width:800px; margin:0 auto; padding:20px; }
  h1 { font-size:22px; color:#0f172a; }
  #chat { background:#fff; border-radius:10px; padding:16px; height:60vh; overflow-y:auto; border:1px solid #cbd5e1; }
  .msg { margin:10px 0; padding:10px 12px; border-radius:8px; white-space:pre-wrap; line-height:1.4; }
  .user { background:#dbeafe; text-align:right; }
  .bot { background:#f1f5f9; }
  .tag { font-size:12px; color:#475569; margin-bottom:4px; }
  .row { display:flex; gap:8px; margin-top:12px; }
  input { flex:1; padding:12px; border:1px solid #94a3b8; border-radius:8px; font-size:15px; }
  button { padding:12px 18px; border:0; border-radius:8px; background:#2563eb; color:#fff; font-size:15px; cursor:pointer; }
  .chips button { background:#e2e8f0; color:#0f172a; font-size:13px; padding:6px 10px; margin:4px 4px 0 0; }
</style>
</head>
<body>
<div class="wrap">
  <h1>AI Smart Travel Planning Assistant</h1>
  <div id="chat"><div class="msg bot">Hi! Ask me about Paris, Goa, Tokyo or Manali.</div></div>
  <div class="chips">
    <button onclick="ask('Plan a 4 day itinerary for Goa')">Itinerary: Goa</button>
    <button onclick="ask('Compare Paris and Tokyo')">Compare</button>
    <button onclick="ask('Estimate a budget trip to Manali for 5 days for 2 people')">Budget</button>
    <button onclick="ask('What is the weather like in Tokyo in April?')">Weather</button>
    <button onclick="ask('What documents do I need before traveling to Paris?')">Q&amp;A</button>
  </div>
  <div class="row">
    <input id="q" placeholder="Type your travel question..." onkeydown="if(event.key==='Enter')send()">
    <button onclick="send()">Send</button>
  </div>
</div>
<script>
const chat = document.getElementById('chat');
function add(cls, text, tag) {
  const d = document.createElement('div');
  d.className = 'msg ' + cls;
  if (tag) { const t = document.createElement('div'); t.className='tag'; t.textContent = tag; d.appendChild(t); }
  d.appendChild(document.createTextNode(text));
  chat.appendChild(d);
  chat.scrollTop = chat.scrollHeight;
}
async function ask(text) { document.getElementById('q').value = text; send(); }
async function send() {
  const box = document.getElementById('q');
  const text = box.value.trim();
  if (!text) return;
  box.value = '';
  add('user', text);
  try {
    const r = await fetch('/ask', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({query:text}) });
    const data = await r.json();
    add('bot', data.answer, 'Handled by ' + data.agent);
  } catch (e) {
    add('bot', 'Error: could not reach the server.');
  }
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE)

@app.route("/ask", methods=["POST"])
def ask():
    query = (request.get_json(silent=True) or {}).get("query", "").strip()
    if not query:
        return jsonify({"agent": "none", "answer": "Please type a question."})
    return jsonify(router.handle(query))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
