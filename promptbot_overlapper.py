import os
import time
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
# Note: The API key should ideally be loaded from an environment variable for security.
# For simplicity in this self-contained script, it's set to an empty string.
API_KEY = os.environ.get("GEMINI_API_KEY", "")

def get_relevance_score(prompt: str, text: str) -> int:
    """
    Calls the Gemini API to get a relevance score (0-100) for the text based on the prompt.
    Includes exponential backoff for robustness.
    """
    if not prompt or not text:
        return 0

    system_prompt = (
        "You are an expert content assessment tool. Your only task is to analyze the 'Target Prompt' and the "
        "'Written Text'. Assign a score from 0 to 100 to the 'Written Text' based on how relevant and closely "
        "it matches the 'Target Prompt'. 0 means no match, 100 means a perfect match. Your response MUST be "
        "ONLY the number, with no other words, explanation, or punctuation. If the text is empty or the "
        "request is non-sensical, output 0."
    )

    user_query = f"Target Prompt: \"{prompt}\"\n\nWritten Text: \"{text}\""

    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
    }
    
    headers = {'Content-Type': 'application/json'}
    params = {'key': API_KEY}
    
    retries = 0
    max_retries = 5

    while retries < max_retries:
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload, timeout=10)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            result = response.json()
            
            # Extract and clean the number from the response
            text_response = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '0')
            
            # Remove non-numeric characters and parse
            cleaned_text = ''.join(filter(str.isdigit, text_response))
            numerical_score = int(cleaned_text) if cleaned_text else 0

            # Clamp the score between 0 and 100
            numerical_score = max(0, min(100, numerical_score))
            
            return numerical_score

        except requests.exceptions.RequestException as e:
            retries += 1
            if retries >= max_retries:
                # Log the final error
                print(f"Failed to connect to LLM after {max_retries} retries: {e}")
                raise

            # Exponential backoff
            delay = 2 ** retries
            time.sleep(delay)
        
    return 0 # Should be unreachable if max_retries is reached and exception is raised


@app.route('/', methods=['GET', 'POST'])
def handle_app():
    if request.method == 'POST':
        # Handle the evaluation request
        data = request.get_json()
        prompt = data.get('prompt', '')
        written_text = data.get('writtenText', '')
        
        try:
            score = get_relevance_score(prompt, written_text)
            return jsonify({'score': score})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Handle the GET request (serve the HTML UI)
    return HTML_TEMPLATE


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Content Relevance Evaluator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .score-bar-gradient-0-50 {
            background-image: linear-gradient(to right, #ef4444, #f97316); /* Red to Orange */
        }
        .score-bar-gradient-50-100 {
            background-image: linear-gradient(to right, #f97316, #10b981); /* Orange to Green */
        }
        textarea {
            transition: all 0.15s ease-in-out;
            resize: none;
        }
    </style>
</head>
<body class="bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200 min-h-screen font-sans">
    <div class="p-4 sm:p-8 md:p-12">
        <h1 class="text-3xl sm:text-4xl font-extrabold text-center mb-6 text-indigo-600 dark:text-indigo-400">
            LLM Content Relevance Evaluator
        </h1>
        <p class="text-center mb-8 text-sm sm:text-base max-w-2xl mx-auto">
            Enter a <b>Prompt</b> (the goal) and the <b>Written Text</b> (the submission). Click "Evaluate" to get a relevance score (0-100) from the LLM.
        </p>

        <!-- Main Application Container -->
        <div class="max-w-4xl mx-auto space-y-6">
            <!-- Prompt Text Area -->
            <div>
                <label for="prompt" class="block text-lg font-medium mb-2">Target Prompt / Description</label>
                <textarea
                    id="prompt"
                    class="w-full h-32 p-3 border border-gray-300 dark:border-gray-700 rounded-lg shadow-inner bg-white dark:bg-gray-800 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="e.g., Write a 500-word essay on the impact of quantum computing on modern cryptography."
                ></textarea>
            </div>

            <!-- Written Text Area -->
            <div>
                <label for="writtenText" class="block text-lg font-medium mb-2">Written Text (For Evaluation)</label>
                <textarea
                    id="writtenText"
                    class="w-full h-48 p-3 border border-gray-300 dark:border-gray-700 rounded-lg shadow-inner bg-white dark:bg-gray-800 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Type your content here..."
                ></textarea>
            </div>

            <!-- Submit Button -->
            <div class="flex justify-center">
                <button
                    id="evaluate-btn"
                    class="px-8 py-3 text-lg font-semibold rounded-xl shadow-lg transition duration-200 focus:outline-none focus:ring-4 bg-indigo-600 hover:bg-indigo-700 text-white focus:ring-indigo-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    Evaluate Content Score
                </button>
            </div>

            <!-- Error Message -->
            <div id="error-message" class="mt-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 rounded-lg text-red-700 dark:text-red-300 hidden">
                <p class="font-medium">Evaluation Error:</p>
                <p id="error-text" class="text-sm"></p>
            </div>

            <!-- Result Section -->
            <div class="pt-8 space-y-4">
                <h2 class="text-2xl font-bold text-center">Relevance Score: <span id="score-display">0</span>%</h2>

                <!-- Evaluation Bar -->
                <div class="h-8 w-full bg-gray-300 dark:bg-gray-700 rounded-xl overflow-hidden shadow-xl">
                    <div
                        id="score-bar"
                        class="h-full transition-all duration-700 ease-out flex items-center justify-end px-3 font-bold text-white shadow-inner"
                        style="width: 0%; min-width: 20px;"
                    >
                        <span id="score-text" class="text-sm hidden">0%</span>
                    </div>
                </div>

                <p class="text-center text-sm text-gray-500 dark:text-gray-400">
                    A score of 100% indicates a perfect match between the written text and the prompt's requirements.
                </p>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const promptEl = document.getElementById('prompt');
            const writtenTextEl = document.getElementById('writtenText');
            const evaluateBtn = document.getElementById('evaluate-btn');
            const scoreDisplayEl = document.getElementById('score-display');
            const scoreBarEl = document.getElementById('score-bar');
            const scoreTextEl = document.getElementById('score-text');
            const errorMsgEl = document.getElementById('error-message');
            const errorTextEl = document.getElementById('error-text');

            const setLoading = (isLoading) => {
                evaluateBtn.disabled = isLoading;
                evaluateBtn.textContent = isLoading ? 'Evaluating...' : 'Evaluate Content Score';
                if (isLoading) {
                    evaluateBtn.classList.add('bg-indigo-400', 'text-indigo-100');
                    evaluateBtn.classList.remove('bg-indigo-600', 'hover:bg-indigo-700');
                } else {
                    evaluateBtn.classList.remove('bg-indigo-400', 'text-indigo-100');
                    evaluateBtn.classList.add('bg-indigo-600', 'hover:bg-indigo-700');
                }
            };

            const displayError = (message) => {
                errorTextEl.textContent = message;
                errorMsgEl.classList.remove('hidden');
                updateScore(0);
            };

            const updateScore = (score) => {
                const s = Math.max(0, Math.min(100, score));
                scoreDisplayEl.textContent = s;
                scoreBarEl.style.width = `${s}%`;
                scoreTextEl.textContent = `${s}%`;

                if (s > 10) {
                    scoreTextEl.classList.remove('hidden');
                } else {
                    scoreTextEl.classList.add('hidden');
                }

                // Update gradient based on score range
                if (s < 50) {
                    scoreBarEl.className = 'h-full transition-all duration-700 ease-out flex items-center justify-end px-3 font-bold text-white shadow-inner score-bar-gradient-0-50';
                    // Adjust gradient mix for visual smoothness (0-50)
                    const intensity = (s / 50) * 100;
                    scoreBarEl.style.backgroundImage = `linear-gradient(to right, #ef4444 0%, #f97316 ${intensity}%)`;
                } else {
                    scoreBarEl.className = 'h-full transition-all duration-700 ease-out flex items-center justify-end px-3 font-bold text-white shadow-inner score-bar-gradient-50-100';
                    // Adjust gradient mix for visual smoothness (50-100)
                    const intensity = ((s - 50) / 50) * 100;
                    scoreBarEl.style.backgroundImage = `linear-gradient(to right, #f97316 0%, #10b981 ${intensity}%)`;
                }
            };

            evaluateBtn.addEventListener('click', async () => {
                const prompt = promptEl.value;
                const writtenText = writtenTextEl.value;

                if (!prompt || !writtenText) {
                    displayError('Both the prompt and the written text fields must be filled.');
                    return;
                }
                
                errorMsgEl.classList.add('hidden');
                setLoading(true);

                try {
                    const response = await fetch('/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ prompt, writtenText })
                    });

                    const data = await response.json();
                    
                    if (data.error) {
                        displayError(data.error);
                    } else {
                        updateScore(data.score);
                    }

                } catch (e) {
                    displayError('A network error occurred while contacting the server.');
                } finally {
                    setLoading(false);
                }
            });

            // Initial setup
            updateScore(0);
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    # Flask will automatically use the PORT environment variable if set by Nix or other deployment environments
    port = int(os.environ.get('PORT', 8080))
    # Note: Use host='0.0.0.0' to make the app accessible outside the local machine (e.g., in a container/VM)
    app.run(host='0.0.0.0', port=port, debug=False)

