import { ChangeDetectionStrategy, Component, computed, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';

// --- Firebase Imports (Standard Canvas Setup) ---
// Not directly used for this LLM-only task, but included for completeness.
// import { initializeApp } from 'firebase/app';
// import { getAuth, signInAnonymously, signInWithCustomToken } from 'firebase/auth';
// import { getFirestore } from 'firebase/firestore';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="p-4 sm:p-8 md:p-12 min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200">
      <h1 class="text-3xl sm:text-4xl font-extrabold text-center mb-6 text-indigo-600 dark:text-indigo-400">
        LLM Content Relevance Evaluator
      </h1>
      <p class="text-center mb-8 text-sm sm:text-base max-w-2xl mx-auto">
        Enter a **Prompt** (the goal) and the **Written Text** (the submission). Click "Evaluate" to get a relevance score (0-100) from the LLM.
      </p>

      <!-- Input Section -->
      <div class="max-w-4xl mx-auto space-y-6">
        <!-- Prompt Text Area -->
        <div>
          <label for="prompt" class="block text-lg font-medium mb-2">Target Prompt / Description</label>
          <textarea
            id="prompt"
            [ngModel]="prompt()"
            (ngModelChange)="prompt.set($event)"
            class="w-full h-32 p-3 border border-gray-300 dark:border-gray-700 rounded-lg shadow-inner bg-white dark:bg-gray-800 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
            placeholder="e.g., Write a 500-word essay on the impact of quantum computing on modern cryptography."
          ></textarea>
        </div>

        <!-- Written Text Area -->
        <div>
          <label for="writtenText" class="block text-lg font-medium mb-2">Written Text (For Evaluation)</label>
          <textarea
            id="writtenText"
            [ngModel]="writtenText()"
            (ngModelChange)="writtenText.set($event)"
            class="w-full h-48 p-3 border border-gray-300 dark:border-gray-700 rounded-lg shadow-inner bg-white dark:bg-gray-800 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
            placeholder="Type your content here..."
          ></textarea>
        </div>

        <!-- Submit Button -->
        <div class="flex justify-center">
          <button
            (click)="evaluateContent()"
            [disabled]="isLoading() || !prompt() || !writtenText()"
            class="px-8 py-3 text-lg font-semibold rounded-xl shadow-lg transition duration-200 focus:outline-none focus:ring-4 disabled:opacity-50 disabled:cursor-not-allowed"
            [ngClass]="{
              'bg-indigo-600 hover:bg-indigo-700 text-white focus:ring-indigo-500/50': !isLoading(),
              'bg-indigo-400 text-indigo-100': isLoading()
            }"
          >
            <span *ngIf="!isLoading()">Evaluate Content Score</span>
            <span *ngIf="isLoading()">Evaluating...</span>
          </button>
        </div>

        <!-- Error Message -->
        <div *ngIf="error()" class="mt-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 rounded-lg text-red-700 dark:text-red-300">
          <p class="font-medium">Evaluation Error:</p>
          <p class="text-sm">{{ error() }}</p>
        </div>

        <!-- Result Section -->
        <div class="pt-8 space-y-4">
          <h2 class="text-2xl font-bold text-center">Relevance Score: {{ score() }}%</h2>

          <!-- Evaluation Bar -->
          <div class="h-8 w-full bg-gray-300 dark:bg-gray-700 rounded-xl overflow-hidden shadow-xl">
            <div
              class="h-full transition-all duration-700 ease-out flex items-center justify-end px-3 font-bold text-white shadow-inner"
              [style.width]="score() + '%'"
              [ngStyle]="barStyles()"
            >
              <span *ngIf="score() > 10" class="text-sm">{{ score() }}%</span>
            </div>
          </div>

          <p class="text-center text-sm text-gray-500 dark:text-gray-400">
            A score of 100% indicates a perfect match between the written text and the prompt's requirements.
          </p>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      /* Include Tailwind for responsiveness and aesthetics */
      @tailwind base;
      @tailwind components;
      @tailwind utilities;

      /* Custom scrollbar for text areas */
      textarea::-webkit-scrollbar {
        width: 8px;
      }
      textarea::-webkit-scrollbar-thumb {
        background-color: #a0aec0;
        border-radius: 4px;
      }
      textarea::-webkit-scrollbar-track {
        background-color: #f7fafc;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  // Global variables provided by the Canvas environment
  private appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
  private firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : null;
  private initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : undefined;

  // Application State
  prompt = signal<string>('');
  writtenText = signal<string>('');
  score = signal<number>(0);
  isLoading = signal<boolean>(false);
  error = signal<string | null>(null);

  // Computed style for the evaluation bar (visual feedback)
  barStyles = computed(() => {
    const s = this.score();
    let color = '';
    // Gradient from Red (low) to Yellow (mid) to Green (high)
    if (s < 50) {
      // Red to Orange
      const intensity = (s / 50) * 100;
      color = `linear-gradient(90deg, #ef4444 0%, #f97316 ${intensity}%)`;
    } else {
      // Orange to Green
      const intensity = ((s - 50) / 50) * 100;
      color = `linear-gradient(90deg, #f97316 0%, #10b981 ${intensity}%)`;
    }

    return {
      'background': color,
      'min-width': '20px', // Ensure visibility even at low scores
    };
  });

  // Constructor is mainly for setup/auth if needed, but not strictly for this logic
  constructor() {
    // try {
    //   if (this.firebaseConfig) {
    //     const app = initializeApp(this.firebaseConfig);
    //     const auth = getAuth(app);
    //     const db = getFirestore(app);
    //     // Handle authentication logic here if persistence/multi-user was needed
    //     // if (this.initialAuthToken) { signInWithCustomToken(auth, this.initialAuthToken); } else { signInAnonymously(auth); }
    //   }
    // } catch (e) {
    //   console.error("Firebase initialization failed:", e);
    // }
  }


  /**
   * Calls the Gemini API to assess the relevance score.
   */
  async evaluateContent() {
    this.isLoading.set(true);
    this.error.set(null);
    this.score.set(0);

    const currentPrompt = this.prompt();
    const currentText = this.writtenText();

    // System instruction: Crucial for forcing a numerical output
    const systemPrompt = `You are an expert content assessment tool. Your only task is to analyze the 'Target Prompt' and the 'Written Text'. Assign a score from 0 to 100 to the 'Written Text' based on how relevant and closely it matches the 'Target Prompt'. 0 means no match, 100 means a perfect match. Your response MUST be ONLY the number, with no other words, explanation, or punctuation. If the text is empty or the request is non-sensical, output 0.`;

    // User query: Consolidates both inputs
    const userQuery = `Target Prompt: "${currentPrompt}"\n\nWritten Text: "${currentText}"`;

    const apiKey = "";
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`;

    const payload = {
        contents: [{ parts: [{ text: userQuery }] }],
        systemInstruction: { parts: [{ text: systemPrompt }] },
    };

    let result = null;
    let retries = 0;
    const maxRetries = 5;

    while (retries < maxRetries) {
      try {
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        result = await response.json();
        break; // Success, exit loop

      } catch (e) {
        retries++;
        if (retries >= maxRetries) {
          this.error.set('Failed to connect to the LLM after multiple retries.');
          this.isLoading.set(false);
          return;
        }
        // Exponential backoff
        const delay = Math.pow(2, retries) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    this.isLoading.set(false);

    if (result && result.candidates && result.candidates.length > 0) {
      try {
        // Extract and clean the number
        const textResponse = result.candidates[0].content.parts[0].text;
        const cleanedText = textResponse.replace(/[^0-9]/g, ''); // Remove non-numeric characters
        let numericalScore = parseInt(cleanedText, 10);

        // Clamp the score between 0 and 100
        if (isNaN(numericalScore)) {
            numericalScore = 0;
        } else if (numericalScore > 100) {
            numericalScore = 100;
        } else if (numericalScore < 0) {
            numericalScore = 0;
        }

        this.score.set(numericalScore);

      } catch (e) {
        this.error.set('LLM returned an unparseable response. Try modifying your prompt.');
      }
    } else {
      this.error.set('LLM response was empty or malformed.');
    }
  }
}
