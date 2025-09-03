from fasthtml.common import *
from fasthtml.svg import *
from fasthtml.components import Zero_md
import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError
from starlette.responses import StreamingResponse

load_dotenv()

# Initialize async OpenAI client
client = AsyncOpenAI()

# Custom CSS for scrollbar and Inter font
custom_css = Style("""
body { font-family: 'Inter', sans-serif; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #2d3748; }
::-webkit-scrollbar-thumb { background: #4a5568; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #718096; }
textarea { resize: none; }
.htmx-indicator { opacity: 0; transition: opacity 200ms ease-in; }
.htmx-request .htmx-indicator { opacity: 1; }
button:disabled { opacity: 0.5; cursor: not-allowed; }
button:disabled:hover { background-color: inherit !important; }
""")

hdrs = (
    Script(src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"),
    Script(type="module", src="https://cdn.jsdelivr.net/npm/zero-md@3?register"),
    HighlightJS(langs=['python', 'javascript', 'html', 'css', 'bash', 'json', 'yaml', 'markdown']),
    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.css"),
    Script(src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.js"),
    Script(src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/contrib/auto-render.min.js", onload="window.katexLoaded = true;"),
    custom_css,
)
app, rt = fast_app(hdrs=hdrs, pico=False)

# Configuration
MAX_MESSAGES = 50

messages = [
    {"sender": "ai", "message": "Hello! I'm here to assist with your business needs. How can I help you today?"}
]

def manage_conversation_memory():
    """Keep conversation within memory limits"""
    global messages
    if len(messages) > MAX_MESSAGES:
        # Keep the first message (greeting) and the most recent messages
        messages = [messages[0]] + messages[-(MAX_MESSAGES-1):]

def build_api_messages(user_message, conversation_history):
    """Helper function to build API messages array"""
    api_messages = []
    
    # Add system message for business assistant context
    api_messages.append({
        "role": "system",
        "content": "You are a helpful business assistant. Be professional, friendly, and concise in your responses."
    })
    
    # Add conversation history
    for msg in conversation_history:
        role = "assistant" if msg["sender"] == "ai" else "user"
        api_messages.append({
            "role": role,
            "content": msg["message"]
        })
    
    # Add current user message
    api_messages.append({
        "role": "user",
        "content": user_message
    })
    
    return api_messages

def render_md(md, css='', **kwargs):
    """Simple markdown renderer using zero-md"""
    if css:
        css_template = Template(Style(css), data_append=True)
        return Zero_md(css_template, Script(md, type="text/markdown"), **kwargs)
    else:
        return Zero_md(Script(md, type="text/markdown"), **kwargs)

# Dark theme CSS for zero-md with HighlightJS integration and KaTeX
dark_md_css = '''
.markdown-body {
    background-color: unset !important; 
    color: unset !important;
}
.markdown-body pre {
    background-color: #1f2937 !important;
    padding: 1em !important;
    border-radius: 6px !important;
    overflow-x: auto !important;
}
.markdown-body code {
    background-color: #374151 !important;
    color: #f3f4f6 !important;
    padding: 0.2em 0.4em !important;
    border-radius: 3px !important;
    font-family: 'Monaco', 'Consolas', 'Courier New', monospace !important;
}
.markdown-body pre code {
    background-color: transparent !important;
    padding: 0 !important;
}
/* KaTeX math styling for dark theme */
.markdown-body .katex {
    color: #f3f4f6 !important;
}
.markdown-body .katex-display {
    margin: 1em 0 !important;
}
.markdown-body .katex .base {
    color: #f3f4f6 !important;
}
'''

async def get_ai_response_streaming_async(user_message, conversation_history):
    """Async generator for OpenAI streaming"""
    try:
        # Use helper function to build API messages
        api_messages = build_api_messages(user_message, conversation_history)
        
        # Use async streaming response from OpenAI
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=api_messages,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                
    except OpenAIError as e:
        print(f"OpenAI API error: {e}")
        yield f"OpenAI service error: {str(e)}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        yield f"Unexpected error occurred: {str(e)}"


def send_icon():
    return Svg(
        xmlns="http://www.w3.org/2000/svg", width="24", height="24", viewBox="0 0 24 24", fill="none",
        stroke="currentColor", stroke_width="2", stroke_linecap="round", stroke_linejoin="round"
    )(
        Line(x1="22", y1="2", x2="11", y2="13", cls="stroke-current"),
        Polygon(points="22 2 15 22 11 13 2 9 22 2", cls="stroke-current")
    )

def user_message(message):
    return Div(cls="chat-message flex items-start gap-4 justify-end")(
        Div(cls="bg-blue-600 rounded-lg p-4 max-w-lg order-1")(
            P("You", cls="font-semibold text-white mb-1"),
            P(message)
        ),
        Div(cls="flex-shrink-0 order-2")(
            Img(cls="w-10 h-10 rounded-full", src="https://placehold.co/40x40/38BDF8/FFFFFF?text=U", alt="User Avatar")
        )
    )

def ai_message(message, message_id=None, use_markdown=True):
    if message_id is None:
        message_id = f"ai-message-{len(messages)}"
    
    return Div(cls="chat-message flex items-start gap-4")(
        Div(cls="flex-shrink-0")(
            Img(cls="w-10 h-10 rounded-full", src="https://placehold.co/40x40/7E57C2/FFFFFF?text=AI", alt="AI Avatar")
        ),
        Div(cls="bg-gray-800 rounded-lg p-4 max-w-lg")(
            P("AI Assistant", cls="font-semibold text-gray-300 mb-1"),
            Div(cls="text-gray-300")(
                render_md(message, dark_md_css, id=message_id) if use_markdown 
                else P(message, cls="text-gray-300")
            )
        )
    )

def chat_messages():
    return Main(id="chat-messages", cls="flex-1 p-4 md:p-6 space-y-6 overflow-y-auto")(
        *[ai_message(msg["message"], use_markdown=False) if msg["sender"] == "ai" and msg == messages[0] 
          else ai_message(msg["message"]) if msg["sender"] == "ai" 
          else user_message(msg["message"]) for msg in messages]
    )

def chat_input():
    return Footer(id="chat-input-container", cls="bg-gray-800/50 backdrop-blur-sm border-t border-gray-700 mt-6 p-4 sticky bottom-0")(
        Form(
            id="chat-form",
            hx_post="/send_message",
            hx_target="#chat-messages",
            hx_swap="beforeend scroll:bottom",
            hx_indicator="#chat-input-container .htmx-indicator",
            cls="flex items-center space-x-4"
        )(
            Textarea(
                id="message-input",
                name="message",
                rows="1",
                placeholder="Type your message...",
                cls="flex-1 bg-gray-700 text-gray-200 rounded-lg px-4 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200",
                required=True
            ),
            Button(
                send_icon(),
                id="submit-btn",
                type="submit",
                cls="bg-blue-600 text-white rounded-full p-3 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-blue-500 transition duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-blue-600 cursor-pointer"
            ),
            Div(cls="htmx-indicator")(
                Div(cls="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin")
            )
        )
    )

@rt('/')
def index():
    return Div(cls="bg-gray-900 text-white font-sans antialiased")(
            Div(id="chat-container", cls="flex flex-col h-screen max-w-4xl mx-auto py-6")(
                chat_messages(),
                chat_input()
            ),
            Script("""
                // Auto-scroll to bottom on page load
                window.onload = () => {
                    const chatMessages = document.getElementById('chat-messages');
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                    
                    // Initialize KaTeX for existing content
                    const existingZeroMd = document.querySelectorAll('zero-md');
                    existingZeroMd.forEach(element => {
                        setTimeout(() => renderKaTeX(element), 200);
                    });
                };
                
                // Function to highlight code blocks in zero-md content
                function highlightCodeBlocks(container) {
                    if (typeof hljs !== 'undefined') {
                        const codeBlocks = container.querySelectorAll('pre code');
                        codeBlocks.forEach(block => {
                            hljs.highlightElement(block);
                        });
                    }
                }
                
                // Function to render KaTeX math expressions in zero-md content
                function renderKaTeX(container) {
                    function doRender() {
                        if (typeof renderMathInElement !== 'undefined') {
                            const target = container.shadowRoot || container;
                            try {
                                renderMathInElement(target, {
                                    delimiters: [
                                        {left: '$$', right: '$$', display: true},
                                        {left: '$', right: '$', display: false},
                                        {left: '\\(', right: '\\)', display: false},
                                        {left: '\\[', right: '\\]', display: true}
                                    ],
                                    throwOnError: false
                                });
                            } catch (e) {
                                console.error('KaTeX rendering error:', e);
                            }
                        }
                    }
                    
                    // Use requestAnimationFrame for better timing
                    if (window.katexLoaded || typeof renderMathInElement !== 'undefined') {
                        requestAnimationFrame(() => {
                            requestAnimationFrame(doRender); // Double RAF for stability
                        });
                    } else {
                        // Fallback with timeout
                        setTimeout(() => renderKaTeX(container), 100);
                    }
                }
                
                // Observer to highlight code and render KaTeX when zero-md content loads
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        mutation.addedNodes.forEach((node) => {
                            if (node.nodeType === Node.ELEMENT_NODE) {
                                // Check if it's a zero-md element or contains one
                                const zeroMdElements = node.tagName === 'ZERO-MD' ? [node] : node.querySelectorAll ? node.querySelectorAll('zero-md') : [];
                                zeroMdElements.forEach((zeroMd) => {
                                    // Use requestAnimationFrame instead of setTimeout
                                    requestAnimationFrame(() => {
                                        highlightCodeBlocks(zeroMd);
                                        renderKaTeX(zeroMd);
                                    });
                                });
                            }
                        });
                    });
                });
                // Only observe the chat messages container instead of entire document
                const chatContainer = document.getElementById('chat-messages');
                if (chatContainer) {
                    observer.observe(chatContainer, { childList: true, subtree: true });
                }
                
                // Auto-resize textarea
                document.addEventListener('input', (e) => {
                    if (e.target.tagName === 'TEXTAREA') {
                        e.target.style.height = 'auto';
                        e.target.style.height = (e.target.scrollHeight) + 'px';
                    }
                });
                
                // Handle Enter key (submit) vs Shift+Enter (new line)
                document.addEventListener('keydown', (e) => {
                    if (e.target.tagName === 'TEXTAREA' && e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        const form = e.target.closest('form');
                        // Only submit if not processing
                        if (!form.getAttribute('data-processing')) {
                            form.requestSubmit();
                        }
                    }
                });
                
                // Handle form submission - disable button and set processing flag
                document.addEventListener('submit', (e) => {
                    if (e.target.id === 'chat-form') {
                        if (e.target.getAttribute('data-processing')) {
                            e.preventDefault();
                        } else {
                            // Disable button and set processing flag
                            const submitBtn = document.getElementById('submit-btn');
                            submitBtn.disabled = true;
                            e.target.setAttribute('data-processing', 'true');
                        }
                    }
                });
                
                // Clear textarea on successful form submit
                document.addEventListener('htmx:afterRequest', (e) => {
                    if (e.target.id === 'chat-form' && e.detail.successful) {
                        const textarea = e.target.querySelector('textarea');
                        textarea.value = '';
                        textarea.style.height = 'auto';
                    }
                });
            """)
        )

@rt('/send_message')
def post(message: str):
    # Add user message
    messages.append({"sender": "user", "message": message})
    manage_conversation_memory()
    message_id = f"ai-message-{len(messages)}"
    
    return (
        user_message(message),
        Div(cls="chat-message flex items-start gap-4", id=f"container-{message_id}")(
            Div(cls="flex-shrink-0")(
                Img(cls="w-10 h-10 rounded-full", src="https://placehold.co/40x40/7E57C2/FFFFFF?text=AI", alt="AI Avatar")
            ),
            Div(cls="bg-gray-800 rounded-lg p-4 max-w-lg")(
                P("AI Assistant", cls="font-semibold text-gray-300 mb-1"),
                Div(cls="flex items-center", id=f"typing-{message_id}")(
                    Span("AI is thinking", cls="font-semibold text-gray-300 mr-3"),
                    Div(cls="flex items-center space-x-1")(
                        Div(cls="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse"),
                        Div(cls="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse", style="animation-delay: 0.2s;"),
                        Div(cls="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse", style="animation-delay: 0.4s;")
                    )
                ),
                Div(cls="text-gray-300", style="display: none;", id=f"content-{message_id}")(
                    render_md("", dark_md_css, id=message_id)
                )
            )
        ),
        Script(f"""
            (function() {{
                const messageId = {json.dumps(message_id)};
                const userMessage = {json.dumps(message)};
                
                const eventSource = new EventSource('/stream-response?message_id=' + messageId + '&user_message=' + encodeURIComponent(userMessage));
                let fullContent = '';
                
                eventSource.onmessage = function(event) {{
                    if (event.data === '[DONE]') {{
                        eventSource.close();
                        // Re-enable form
                        const form = document.getElementById('chat-form');
                        const submitBtn = document.getElementById('submit-btn');
                        form.removeAttribute('data-processing');
                        submitBtn.disabled = false;
                        return;
                    }}
                    
                    try {{
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'start') {{
                            // Hide typing indicator and show content on start
                            const typingDiv = document.getElementById('typing-{message_id}');
                            const contentDiv = document.getElementById('content-{message_id}');
                            if (typingDiv) typingDiv.style.display = 'none';
                            if (contentDiv) contentDiv.style.display = 'block';
                        }} else if (data.type === 'chunk') {{
                            fullContent += data.content;
                            const zeroMdElement = document.getElementById(messageId);
                            if (zeroMdElement) {{
                                const scriptElement = zeroMdElement.querySelector('script[type="text/markdown"]');
                                if (scriptElement) {{
                                    scriptElement.textContent = fullContent;
                                }}
                                // Don't render KaTeX during streaming to avoid incomplete expressions
                            }}
                        }} else if (data.type === 'complete') {{
                            // Final update and trigger syntax highlighting
                            const zeroMdElement = document.getElementById(messageId);
                            if (zeroMdElement) {{
                                const scriptElement = zeroMdElement.querySelector('script[type="text/markdown"]');
                                if (scriptElement) {{
                                    scriptElement.textContent = data.content;
                                    // Use requestAnimationFrame for better timing
                                    requestAnimationFrame(() => {{
                                        if (typeof hljs !== 'undefined') {{
                                            const codeBlocks = zeroMdElement.querySelectorAll('pre code');
                                            codeBlocks.forEach(block => {{
                                                hljs.highlightElement(block);
                                            }});
                                        }}
                                        renderKaTeX(zeroMdElement);
                                    }});
                                }}
                            }}
                        }} else if (data.type === 'error') {{
                            console.error('Streaming error:', data.content);
                            const contentDiv = document.getElementById('content-{message_id}');
                            if (contentDiv) {{
                                contentDiv.innerHTML = '<div class="text-red-500 p-4 bg-red-50 rounded border-l-4 border-red-400">❌ ' + data.content + '</div>';
                            }}
                        }}
                    }} catch (e) {{
                        console.error('Error parsing SSE data:', e, event.data);
                    }}
                }};
                
                eventSource.onerror = function(error) {{
                    console.error('EventSource failed:', error);
                    eventSource.close();
                    // Re-enable form on error
                    const form = document.getElementById('chat-form');
                    const submitBtn = document.getElementById('submit-btn');
                    form.removeAttribute('data-processing');
                    submitBtn.disabled = false;
                }};
            }})();
        """)
    )

@rt('/stream-response')
async def stream_response(message_id: str, user_message: str):
    async def generate():
        try:
            yield "data: " + json.dumps({"type": "start", "content": ""}) + "\n\n"
            
            full_response = ""
            # Stream chunks as they arrive from OpenAI
            async for chunk in get_ai_response_streaming_async(user_message, messages):
                full_response += chunk
                yield "data: " + json.dumps({"type": "chunk", "content": chunk}) + "\n\n"
            
            # Add complete response to messages
            messages.append({"sender": "ai", "message": full_response})
            manage_conversation_memory()
            yield "data: " + json.dumps({"type": "complete", "content": full_response}) + "\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            messages.append({"sender": "ai", "message": error_msg})
            yield "data: " + json.dumps({"type": "error", "content": error_msg}) + "\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache", 
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream; charset=utf-8"
        }
    )

serve()