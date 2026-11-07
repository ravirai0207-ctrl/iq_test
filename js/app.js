/**
 * Luminary NeuroIQ Client Controller v3.0 (GitHub Pages & Cloud Ready)
 * 100% Client-Side + Server Hybrid Engine:
 * - Direct registration (NO OTP)
 * - Questions sourced live from Global Question Servers (Open Trivia Database)
 * - Autonomous client-side scoring for GitHub Pages static hosting
 * - Dynamic 3D Three.js light background
 */

(function () {
  'use strict';

  const state = {
    user: {
      name: '',
      age: 24,
      email: '',
      sessionToken: null
    },
    questions: [],
    currentIndex: 0,
    answers: {},
    flagged: new Set(),
    timerSeconds: 900,
    elapsedSeconds: 0,
    timerInterval: null,
    scene: null
  };

  const views = {
    register: document.getElementById('view-register'),
    instructions: document.getElementById('view-instructions'),
    test: document.getElementById('view-test'),
    calculating: document.getElementById('view-calculating'),
    results: document.getElementById('view-results')
  };

  window.addEventListener('DOMContentLoaded', () => {
    init3DScene();
    setupNavigation();
    setupDirectRegistration();
    setupTestControls();
    setupKeyboardShortcuts();
    setupModals();
    setupResultActions();
  });

  function init3DScene() {
    if (window.Cognitive3DScene) {
      state.scene = new window.Cognitive3DScene('canvas-container');
    }
  }

  function switchView(viewName) {
    Object.keys(views).forEach(key => {
      if (views[key]) {
        views[key].classList.toggle('active', key === viewName);
      }
    });

    if (state.scene) {
      if (viewName === 'register') state.scene.setCategory('pattern');
      else if (viewName === 'instructions') state.scene.setCategory('spatial');
      else if (viewName === 'calculating') state.scene.setCategory('logic');
      else if (viewName === 'results') state.scene.celebrate();
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // --------------------------------------------------------------------------
  // Navigation & Audio
  // --------------------------------------------------------------------------
  function setupNavigation() {
    const brandBtn = document.getElementById('brand-home-btn');
    if (brandBtn) {
      brandBtn.addEventListener('click', () => {
        if (confirm('Return to home screen? Active test progress will be reset.')) {
          clearInterval(state.timerInterval);
          switchView('register');
        }
      });
    }

    const soundBtn = document.getElementById('sound-toggle-btn');
    if (soundBtn) {
      soundBtn.addEventListener('click', () => {
        const isMuted = window.soundEngine.toggleMute();
        soundBtn.textContent = isMuted ? '🔇' : '🔊';
        soundBtn.title = isMuted ? 'Sound Effects Muted' : 'Sound Effects Active';
      });
    }

    const ageInput = document.getElementById('reg-age');
    const ageBadge = document.getElementById('age-calibration-badge');
    if (ageInput && ageBadge) {
      ageInput.addEventListener('input', () => {
        const val = parseInt(ageInput.value, 10);
        if (!val) ageBadge.textContent = 'Norm Baseline';
        else if (val < 16) ageBadge.textContent = 'Youth Baseline (+3.5)';
        else if (val <= 21) ageBadge.textContent = 'Young Adult Norms';
        else if (val <= 35) ageBadge.textContent = 'Fluid Peak Norms';
        else if (val <= 50) ageBadge.textContent = 'Mature Adult Norms';
        else ageBadge.textContent = 'Senior Baseline (+4.0)';
      });
    }
  }

  // --------------------------------------------------------------------------
  // Online Question Server Sourcing (Open Trivia DB & The Trivia API)
  // --------------------------------------------------------------------------
  async function fetchAllQuestionsFromServer(count = 12) {
    let serverQuestions = [];

    // Primary: Open Trivia Database API
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 4500);

      const res = await fetch(`https://opentdb.com/api.php?amount=${count}&type=multiple`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        const data = await res.json();
        if (data.results && data.results.length >= 5) {
          serverQuestions = data.results.map((item, idx) => formatServerQuestion(item, idx + 1));
          console.log(`[Question Server] Loaded ${serverQuestions.length} items from OpenTDB.`);
          return serverQuestions;
        }
      }
    } catch (e) {
      console.warn('[Question Server] OpenTDB unavailable, querying secondary server...', e);
    }

    // Secondary: The Trivia API
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 4500);

      const res = await fetch(`https://the-trivia-api.com/v2/questions?limit=${count}`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        const list = await res.json();
        if (Array.isArray(list) && list.length >= 5) {
          serverQuestions = list.map((item, idx) => {
            const prompt = item.question ? item.question.text : String(item);
            const correct = item.correctAnswer;
            const wrongs = item.incorrectAnswers || [];
            return formatQuestionDirect(prompt, correct, wrongs, item.category || 'General Science & Logic', idx + 1, item.difficulty || 'medium');
          });
          console.log(`[Question Server] Loaded ${serverQuestions.length} items from The Trivia API.`);
          return serverQuestions;
        }
      }
    } catch (e) {
      console.warn('[Question Server] Secondary server unavailable:', e);
    }

    return null;
  }

  function formatServerQuestion(item, id) {
    const prompt = decodeHtml(item.question);
    const correct = decodeHtml(item.correct_answer);
    const wrongs = item.incorrect_answers.map(decodeHtml);
    return formatQuestionDirect(prompt, correct, wrongs, item.category, id, item.difficulty);
  }

  function formatQuestionDirect(prompt, correct, wrongs, categoryRaw, id, difficulty = 'medium') {
    const rawCategory = decodeHtml(categoryRaw || 'General Knowledge');
    let catKey = 'logic';
    let catIcon = '🌐';
    const lowerCat = rawCategory.toLowerCase();

    if (lowerCat.includes('computer') || lowerCat.includes('tech') || lowerCat.includes('gadget')) {
      catKey = 'speed';
      catIcon = '💻';
    } else if (lowerCat.includes('math') || lowerCat.includes('number') || lowerCat.includes('count')) {
      catKey = 'numerical';
      catIcon = '📐';
    } else if (lowerCat.includes('science') || lowerCat.includes('nature') || lowerCat.includes('physics')) {
      catKey = 'spatial';
      catIcon = '🧬';
    } else if (lowerCat.includes('history') || lowerCat.includes('geo') || lowerCat.includes('myth')) {
      catKey = 'pattern';
      catIcon = '🏛️';
    } else {
      catKey = 'logic';
      catIcon = '⚖️';
    }

    const allOptions = [correct, ...wrongs].sort(() => Math.random() - 0.5);
    const correctIdx = allOptions.indexOf(correct);

    const diffLabel = (difficulty || 'standard').toUpperCase();
    const cleanCat = escapeSvg(rawCategory.slice(0, 18));

    const svg = `
      <svg width="100%" height="150" viewBox="0 0 420 130" preserveAspectRatio="xMidYMid meet" class="q-svg">
        <rect x="15" y="15" width="390" height="100" rx="14" fill="#f8fafc" stroke="#6366f1" stroke-width="1.8"/>
        
        <rect x="32" y="28" width="145" height="26" rx="13" fill="#e0e7ff"/>
        <text x="45" y="46" font-size="13">${catIcon}</text>
        <text x="65" y="45" font-size="11" font-weight="bold" fill="#4338ca">${cleanCat}</text>

        <rect x="245" y="28" width="145" height="26" rx="13" fill="#dcfce7"/>
        <text x="256" y="45" font-size="10.5" font-weight="bold" fill="#15803d">🌐 Live Server Question</text>

        <path d="M 35 88 Q 75 68, 115 88 T 195 88 T 275 88 T 385 88" fill="none" stroke="#6366f1" stroke-width="1.5" stroke-dasharray="3"/>
        <circle cx="35" cy="88" r="3.5" fill="#4f46e5"/>
        <circle cx="195" cy="88" r="3.5" fill="#06b6d4"/>
        <circle cx="385" cy="88" r="3.5" fill="#10b981"/>
        <text x="210" y="104" font-size="10" fill="#64748b" text-anchor="middle">Difficulty: ${diffLabel} • Question Server Feed</text>
      </svg>
    `;

    return {
      id: id,
      category: rawCategory,
      category_key: catKey,
      title: `${rawCategory} Question #${id}`,
      prompt: prompt,
      visual_type: 'svg_matrix',
      visual_data: svg,
      options: allOptions,
      correct_index: correctIdx
    };
  }

  function decodeHtml(html) {
    if (!html) return '';
    const txt = document.createElement('textarea');
    txt.innerHTML = html;
    return txt.value;
  }

  function escapeSvg(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, s => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[s]));
  }

  // Fallback questions for offline environment
  function getStaticFallbackQuestions(count = 12) {
    const bank = [
      formatQuestionDirect("Which number logically continues the series: 3, 7, 15, 31, 63, ?", "127", ["120", "125", "131"], "Numerical Logic", 1),
      formatQuestionDirect("In binary computing, how many distinct values can be represented by 8 bits (1 byte)?", "256", ["128", "512", "1024"], "Computational Logic", 2),
      formatQuestionDirect("If all Bloops are Razzies and all Razzies are Lizzies, are all Bloops definitely Lizzies?", "Yes, absolutely", ["No, never", "Only sometimes", "Cannot be determined"], "Deductive Reasoning", 3),
      formatQuestionDirect("What is the next prime number following 29?", "31", ["33", "37", "39"], "Mathematical Logic", 4),
      formatQuestionDirect("Which fundamental particle has a positive elementary charge?", "Proton", ["Neutron", "Electron", "Neutrino"], "Physics & Nature", 5),
      formatQuestionDirect("In 3D Euclidean geometry, how many faces does a regular icosahedron have?", "20 faces", ["12 faces", "8 faces", "24 faces"], "Spatial Mechanics", 6),
      formatQuestionDirect("Which algorithm paradigm does Dijkstra's shortest path algorithm utilize?", "Greedy algorithm", ["Divide and conquer", "Backtracking", "Linear search"], "Computational Logic", 7),
      formatQuestionDirect("If a clock shows 3:15, what is the acute angle between the hour and minute hands?", "7.5 degrees", ["0 degrees", "15 degrees", "5 degrees"], "Spatial Mechanics", 8),
      formatQuestionDirect("Which element has the chemical atomic symbol 'Fe'?", "Iron", ["Fluorine", "Francium", "Fermium"], "Science & Chemistry", 9),
      formatQuestionDirect("Which sequence rule applies to: 2, 3, 5, 8, 13, 21, ?", "34 (Fibonacci series)", ["32", "29", "35"], "Numerical Logic", 10),
      formatQuestionDirect("What is the decimal equivalent of the binary number 1011?", "11", ["9", "13", "15"], "Computational Logic", 11),
      formatQuestionDirect("Which logical gate yields TRUE if and only if both inputs are distinct (exclusive)?", "XOR gate", ["AND gate", "NOR gate", "XNOR gate"], "Computational Logic", 12)
    ];
    return bank.slice(0, count);
  }

  // --------------------------------------------------------------------------
  // Direct Registration (NO OTP!) — Hybrid Online/Offline
  // --------------------------------------------------------------------------
  function setupDirectRegistration() {
    const form = document.getElementById('form-register');
    const startBtn = document.getElementById('btn-start-session');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      window.soundEngine.playClick();

      const name = document.getElementById('reg-name').value.trim();
      const age = parseInt(document.getElementById('reg-age').value, 10);
      let email = document.getElementById('reg-email').value.trim().toLowerCase();

      if (!name || isNaN(age)) {
        alert('Please enter your Name and Age.');
        return;
      }
      if (!email) {
        email = `${name.toLowerCase().replace(/[^a-z0-9]/g, '')}@cognitivelabs.ai`;
      }

      state.user.name = name;
      state.user.age = age;
      state.user.email = email;

      startBtn.disabled = true;
      startBtn.innerHTML = '<span>Querying Question Server...</span><span>🌐</span>';

      try {
        const onlineQuestions = await fetchAllQuestionsFromServer(12);
        const questionsToUse = (onlineQuestions && onlineQuestions.length >= 5) ? onlineQuestions : getStaticFallbackQuestions(12);

        startBtn.innerHTML = '<span>Initializing 3D Session...</span><span>⏳</span>';

        // Try registering with backend if available
        try {
          const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, age, email, server_questions: questionsToUse })
          });
          if (res.ok) {
            const data = await res.json();
            if (data.success) {
              state.user.sessionToken = data.session_token;
              state.questions = questionsToUse || data.questions || [];
            }
          }
        } catch (apiErr) {
          // GitHub Pages static mode
        }

        // Standalone fallback session for GitHub Pages
        if (!state.user.sessionToken) {
          state.user.sessionToken = 'gh_sess_' + Math.random().toString(36).substring(2);
          state.questions = questionsToUse;
        }

        document.getElementById('candidate-welcome-name').textContent = name;
        document.getElementById('brief-user-age').textContent = age;

        window.soundEngine.playSuccess();
        if (state.scene) state.scene.pulse();

        switchView('instructions');
      } catch (err) {
        alert('Session setup error: ' + err.message);
      } finally {
        startBtn.disabled = false;
        startBtn.innerHTML = '<span>Initialize 3D Assessment</span><span>→</span>';
      }
    });

    const launchTestBtn = document.getElementById('btn-launch-test');
    if (launchTestBtn) {
      launchTestBtn.addEventListener('click', () => {
        window.soundEngine.playPulse();
        startTest();
      });
    }
  }

  // --------------------------------------------------------------------------
  // Keyboard Shortcuts (1-4, A-D, Arrows, Enter)
  // --------------------------------------------------------------------------
  function setupKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
      if (!views.test.classList.contains('active')) return;

      const key = e.key.toLowerCase();
      const q = state.questions[state.currentIndex];
      if (!q) return;

      if (key === '1' || key === 'a') selectOption(0);
      else if (key === '2' || key === 'b') selectOption(1);
      else if (key === '3' || key === 'c') selectOption(2);
      else if (key === '4' || key === 'd') selectOption(3);
      else if (key === 'arrowright' || key === 'enter') {
        if (state.currentIndex < state.questions.length - 1) {
          state.currentIndex++;
          renderCurrentQuestion();
          window.soundEngine.playClick();
        } else {
          confirmAndSubmitTest();
        }
      } else if (key === 'arrowleft') {
        if (state.currentIndex > 0) {
          state.currentIndex--;
          renderCurrentQuestion();
          window.soundEngine.playClick();
        }
      }
    });
  }

  // --------------------------------------------------------------------------
  // Active Test Controls & Execution
  // --------------------------------------------------------------------------
  function setupTestControls() {
    const prevBtn = document.getElementById('btn-prev-question');
    const nextBtn = document.getElementById('btn-next-question');
    const flagBtn = document.getElementById('btn-flag-question');

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (state.currentIndex > 0) {
          state.currentIndex--;
          renderCurrentQuestion();
          window.soundEngine.playClick();
        }
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        window.soundEngine.playClick();
        if (state.currentIndex < state.questions.length - 1) {
          state.currentIndex++;
          renderCurrentQuestion();
        } else {
          confirmAndSubmitTest();
        }
      });
    }

    if (flagBtn) {
      flagBtn.addEventListener('click', () => {
        const q = state.questions[state.currentIndex];
        if (!q) return;
        if (state.flagged.has(q.id)) {
          state.flagged.delete(q.id);
          flagBtn.classList.remove('active');
        } else {
          state.flagged.add(q.id);
          flagBtn.classList.add('active');
        }
        updateQuestionsNav();
        window.soundEngine.playSelect();
      });
    }
  }

  function startTest() {
    state.currentIndex = 0;
    state.answers = {};
    state.flagged.clear();
    state.timerSeconds = 900;
    state.elapsedSeconds = 0;

    startTimer();
    renderQuestionsNav();
    renderCurrentQuestion();
    switchView('test');
  }

  function startTimer() {
    clearInterval(state.timerInterval);
    const clockEl = document.getElementById('test-timer-clock');

    state.timerInterval = setInterval(() => {
      state.timerSeconds--;
      state.elapsedSeconds++;

      const mins = Math.floor(state.timerSeconds / 60);
      const secs = state.timerSeconds % 60;
      if (clockEl) {
        clockEl.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
      }

      if (state.timerSeconds <= 0) {
        clearInterval(state.timerInterval);
        alert('Test duration reached! Finalizing cognitive evaluation.');
        submitTest();
      }
    }, 1000);
  }

  function renderCurrentQuestion() {
    const q = state.questions[state.currentIndex];
    if (!q) return;

    const total = state.questions.length;
    document.getElementById('test-q-index').textContent = `Question ${state.currentIndex + 1} of ${total}`;

    const catEl = document.getElementById('test-q-category');
    catEl.textContent = q.category;

    if (state.scene) {
      state.scene.setCategory(q.category_key);
    }

    const pct = ((state.currentIndex + 1) / total) * 100;
    document.getElementById('test-progress-fill').style.width = `${pct}%`;

    document.getElementById('test-q-title').textContent = q.title;
    document.getElementById('test-q-prompt').textContent = q.prompt;

    const visualContainer = document.getElementById('test-visual-container');
    visualContainer.innerHTML = '';
    if (q.visual_data && q.visual_data.trim()) {
      visualContainer.style.display = 'flex';
      visualContainer.innerHTML = q.visual_data;
    } else {
      visualContainer.style.display = 'none';
    }

    const optionsGrid = document.getElementById('test-options-grid');
    optionsGrid.innerHTML = '';
    const keys = ['1', '2', '3', '4'];
    const userSelected = state.answers[q.id];

    q.options.forEach((optText, idx) => {
      const tile = document.createElement('div');
      tile.className = 'option-tile' + (userSelected === idx ? ' selected' : '');
      tile.innerHTML = `
        <div class="option-key-badge">${keys[idx]}</div>
        <div class="option-content-text">${optText}</div>
      `;

      tile.addEventListener('click', () => {
        selectOption(idx);
      });

      optionsGrid.appendChild(tile);
    });

    const prevBtn = document.getElementById('btn-prev-question');
    const nextBtn = document.getElementById('btn-next-question');
    const flagBtn = document.getElementById('btn-flag-question');

    prevBtn.disabled = (state.currentIndex === 0);
    if (state.currentIndex === total - 1) {
      nextBtn.innerHTML = '<span>Finalize Assessment</span><span>✨</span>';
    } else {
      nextBtn.innerHTML = '<span>Next Question</span><span>→</span>';
    }

    flagBtn.classList.toggle('active', state.flagged.has(q.id));
    updateQuestionsNav();
  }

  function selectOption(idx) {
    const q = state.questions[state.currentIndex];
    if (!q || idx < 0 || idx >= q.options.length) return;

    state.answers[q.id] = idx;
    window.soundEngine.playSelect();
    if (state.scene) state.scene.pulse();

    const tiles = document.querySelectorAll('.option-tile');
    tiles.forEach((t, i) => {
      t.classList.toggle('selected', i === idx);
    });

    updateQuestionsNav();
  }

  function renderQuestionsNav() {
    const strip = document.getElementById('questions-nav-strip');
    if (!strip) return;
    strip.innerHTML = '';

    state.questions.forEach((q, idx) => {
      const pill = document.createElement('div');
      pill.className = 'nav-dot-pill';
      pill.textContent = idx + 1;
      pill.title = `Jump to Q${idx + 1}: ${q.title}`;

      pill.addEventListener('click', () => {
        state.currentIndex = idx;
        renderCurrentQuestion();
        window.soundEngine.playClick();
      });

      strip.appendChild(pill);
    });
  }

  function updateQuestionsNav() {
    const pills = document.querySelectorAll('.nav-dot-pill');
    pills.forEach((pill, idx) => {
      const q = state.questions[idx];
      pill.classList.toggle('active', idx === state.currentIndex);
      pill.classList.toggle('answered', q && state.answers[q.id] !== undefined);
      pill.classList.toggle('flagged', q && state.flagged.has(q.id));
    });
  }

  // --------------------------------------------------------------------------
  // Submitting Test & Hybrid Evaluation Engine
  // --------------------------------------------------------------------------
  function confirmAndSubmitTest() {
    const answeredCount = Object.keys(state.answers).length;
    const total = state.questions.length;

    if (answeredCount < total) {
      const unanswered = total - answeredCount;
      if (!confirm(`You have ${unanswered} unanswered item(s). Submit test now?`)) {
        return;
      }
    }
    submitTest();
  }

  async function submitTest() {
    clearInterval(state.timerInterval);
    window.soundEngine.playPulse();

    switchView('calculating');

    const statusEl = document.getElementById('calc-status-text');
    const steps = [
      'Normalizing age-calibrated Gaussian vectors...',
      'Quantifying response accuracy and velocity...',
      'Synthesizing standardized psychometric profile...',
      'Generating verifiable credential signature...'
    ];

    let stepIdx = 0;
    const stepInterval = setInterval(() => {
      if (statusEl && steps[stepIdx]) {
        statusEl.textContent = steps[stepIdx];
        stepIdx++;
      }
    }, 550);

    const payload = {
      session_token: state.user.sessionToken,
      name: state.user.name,
      age: state.user.age,
      answers: state.answers,
      time_taken_seconds: state.elapsedSeconds,
      questions: state.questions
    };

    let result = null;

    // 1. Try server evaluation
    try {
      const res = await fetch('/api/submit-test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${state.user.sessionToken}`
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.result) {
          result = data.result;
        }
      }
    } catch (e) {
      console.log('[App] Static evaluation mode active');
    }

    // 2. Client-side evaluation fallback (for GitHub Pages static hosting)
    if (!result) {
      result = evaluateClientSideIQ(state.user.age, state.questions, state.answers, state.elapsedSeconds);
    }

    clearInterval(stepInterval);

    setTimeout(() => {
      renderResults(result);
      switchView('results');
      if (state.scene) state.scene.celebrate();
      window.soundEngine.playSuccess();
    }, 1100);
  }

  // Client-Side Psychometric Scoring Engine (Exact replica of backend for GitHub Pages)
  function evaluateClientSideIQ(userAge, questions, answers, timeTaken) {
    const total = questions.length;
    let correct = 0;
    const catTotals = {};
    const catCorrect = {};

    questions.forEach(q => {
      const qid = String(q.id);
      const cat = q.category_key || 'logic';
      catTotals[cat] = (catTotals[cat] || 0) + 1;

      const userChoice = answers[qid];
      const isCorrect = (userChoice !== undefined && parseInt(userChoice) === q.correct_index);
      if (isCorrect) {
        correct++;
        catCorrect[cat] = (catCorrect[cat] || 0) + 1;
      }
    });

    let ageBonus = 0;
    if (userAge < 16) ageBonus = 3.5;
    else if (userAge <= 21) ageBonus = 1.0;
    else if (userAge <= 35) ageBonus = 0.0;
    else if (userAge <= 50) ageBonus = 2.0;
    else ageBonus = 4.0;

    let speedBonus = 0;
    if (correct / total >= 0.5) {
      if (timeTaken < 350) speedBonus = 3.0;
      else if (timeTaken < 550) speedBonus = 1.5;
    }

    const baselineMid = total * 0.5;
    const spread = Math.max(1.5, total * 0.18);
    const zScore = (correct - baselineMid) / spread;
    const rawIQ = 100 + (zScore * 15) + ageBonus + speedBonus;
    const iqScore = Math.round(Math.max(68, Math.min(160, rawIQ)));

    // Error function approximation for Gaussian percentile
    const z = (iqScore - 100) / 15;
    const t = 1.0 / (1.0 + 0.5 * Math.abs(z / Math.SQRT2));
    const tau = t * Math.exp(-Math.pow(z / Math.SQRT2, 2) - 1.26551223 + 1.00002368*t + 0.37409196*t*t + 0.09678418*Math.pow(t, 3) - 0.18628806*Math.pow(t, 4) + 0.27886807*Math.pow(t, 5) - 1.13520398*Math.pow(t, 6) + 1.48851587*Math.pow(t, 7) - 0.82215223*Math.pow(t, 8) + 0.17087277*Math.pow(t, 9));
    const erf = (z >= 0) ? (1 - tau) : (tau - 1);
    const percentile = Math.round(Math.max(0.1, Math.min(99.9, 0.5 * (1 + erf) * 100)) * 10) / 10;

    let classification = "Average Intelligence";
    let badge = "Tier 5: Normal Distribution";
    let desc = "Solid standard cognitive ability aligning with standard global benchmarks.";

    if (iqScore >= 145) {
      classification = "Genius / Highly Gifted";
      badge = "Tier 1: Exceptional";
      desc = "In the top 0.1% globally. Demonstrates elite abstract reasoning, fluid speed, and synthesis.";
    } else if (iqScore >= 130) {
      classification = "Very Superior Intelligence";
      badge = "Tier 2: Very Superior";
      desc = "Mensa-level cognitive aptitude. Exceptional multi-dimensional pattern logic and deductive agility.";
    } else if (iqScore >= 120) {
      classification = "Superior Intelligence";
      badge = "Tier 3: Superior";
      desc = "Substantially above standard population average across all evaluated dimensions.";
    } else if (iqScore >= 110) {
      classification = "High Average";
      badge = "Tier 4: High Average";
      desc = "Above average fluid reasoning and sequence extrapolation competence.";
    }

    const catScores = {};
    Object.keys(catTotals).forEach(cat => {
      const c = catCorrect[cat] || 0;
      const tot = catTotals[cat];
      catScores[cat] = {
        correct: c,
        total: tot,
        percentage: Math.round((c / tot) * 100)
      };
    });

    const certId = "CERT-IQ-" + Math.random().toString(36).substring(2, 6).toUpperCase() + "-" + Math.random().toString(36).substring(2, 6).toUpperCase();

    const resObj = {
      iq_score: iqScore,
      percentile: percentile,
      classification: classification,
      badge: badge,
      description: desc,
      correct_answers: correct,
      total_questions: total,
      time_taken_seconds: timeTaken,
      category_scores: catScores,
      certificate_id: certId
    };

    try {
      const existing = JSON.parse(localStorage.getItem('neuro_iq_leaderboard') || '[]');
      existing.push({
        name: state.user.name,
        age: state.user.age,
        iq_score: iqScore,
        percentile: percentile,
        classification: classification,
        time_taken_seconds: timeTaken
      });
      existing.sort((a, b) => b.iq_score - a.iq_score);
      localStorage.setItem('neuro_iq_leaderboard', JSON.stringify(existing.slice(0, 10)));
    } catch(e) {}

    return resObj;
  }

  // --------------------------------------------------------------------------
  // Results & Certificate Dashboard
  // --------------------------------------------------------------------------
  function renderResults(result) {
    const scoreVal = document.getElementById('res-iq-score');
    animateScoreCounter(scoreVal, 0, result.iq_score, 1200);

    document.getElementById('res-iq-badge').textContent = result.badge;
    document.getElementById('res-percentile-badge').innerHTML = `<span>🌟</span> Top ${Math.max(0.1, (100 - result.percentile)).toFixed(1)}% Global Population`;
    document.getElementById('res-classification-title').textContent = result.classification;
    document.getElementById('res-description-text').textContent = result.description;

    drawGaussianBellCurve(result.iq_score);

    const catContainer = document.getElementById('category-scores-container');
    catContainer.innerHTML = '';

    const domainLabels = {
      pattern: 'Pattern Recognition',
      numerical: 'Numerical Logic',
      spatial: 'Spatial Mechanics',
      logic: 'Deductive Reasoning',
      speed: 'Processing Velocity'
    };

    Object.keys(result.category_scores || {}).forEach(key => {
      const c = result.category_scores[key];
      const card = document.createElement('div');
      card.className = 'category-metric-card';
      card.innerHTML = `
        <div class="cat-metric-top">
          <span>${domainLabels[key] || key}</span>
          <span style="color: var(--accent-indigo); font-weight: 800;">${c.percentage}%</span>
        </div>
        <div class="cat-metric-bar-bg">
          <div class="cat-metric-bar-fill" style="width: 0%;"></div>
        </div>
        <div style="font-size: 11px; color: var(--text-muted); margin-top: 6px;">
          ${c.correct} of ${c.total} items correct
        </div>
      `;
      catContainer.appendChild(card);

      setTimeout(() => {
        card.querySelector('.cat-metric-bar-fill').style.width = `${c.percentage}%`;
      }, 150);
    });

    document.getElementById('cert-user-name').textContent = state.user.name;
    document.getElementById('cert-user-email').textContent = state.user.email;
    document.getElementById('cert-user-age').textContent = `Age ${state.user.age}`;
    document.getElementById('cert-iq-score').textContent = `${result.iq_score} IQ`;
    document.getElementById('cert-percentile').textContent = `${result.percentile}%`;
    document.getElementById('cert-id').textContent = result.certificate_id;

    const today = new Date().toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
    document.getElementById('cert-date').textContent = today;
  }

  function animateScoreCounter(el, start, end, duration) {
    let current = start;
    const stepTime = 25;
    const totalSteps = duration / stepTime;
    const increment = (end - start) / totalSteps;

    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        current = end;
        clearInterval(timer);
      }
      el.textContent = Math.round(current);
    }, stepTime);
  }

  function drawGaussianBellCurve(userIQ) {
    const canvas = document.getElementById('bell-curve-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const dpr = window.devicePixelRatio || 1;
    const displayW = 600;
    const displayH = 130;
    canvas.width = displayW * dpr;
    canvas.height = displayH * dpr;
    ctx.scale(dpr, dpr);

    const w = displayW;
    const h = displayH;
    ctx.clearRect(0, 0, w, h);

    const minIQ = 55;
    const maxIQ = 145;
    const mean = 100;
    const sd = 15;

    function normalPdf(x) {
      const exp = -0.5 * Math.pow((x - mean) / sd, 2);
      return (1 / (sd * Math.sqrt(2 * Math.PI))) * Math.exp(exp);
    }

    const baselineY = h - 25;
    const maxPdf = normalPdf(mean);

    const gradient = ctx.createLinearGradient(0, 0, 0, baselineY);
    gradient.addColorStop(0, 'rgba(79, 70, 229, 0.22)');
    gradient.addColorStop(1, 'rgba(79, 70, 229, 0.01)');

    ctx.beginPath();
    ctx.moveTo(30, baselineY);
    for (let xPx = 30; xPx <= w - 30; xPx++) {
      const iq = minIQ + ((xPx - 30) / (w - 60)) * (maxIQ - minIQ);
      const pdf = normalPdf(iq);
      const yPx = baselineY - (pdf / maxPdf) * (h - 48);
      ctx.lineTo(xPx, yPx);
    }
    ctx.lineTo(w - 30, baselineY);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    ctx.beginPath();
    for (let xPx = 30; xPx <= w - 30; xPx++) {
      const iq = minIQ + ((xPx - 30) / (w - 60)) * (maxIQ - minIQ);
      const pdf = normalPdf(iq);
      const yPx = baselineY - (pdf / maxPdf) * (h - 48);
      if (xPx === 30) ctx.moveTo(xPx, yPx);
      else ctx.lineTo(xPx, yPx);
    }
    ctx.strokeStyle = '#4f46e5';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(30, baselineY);
    ctx.lineTo(w - 30, baselineY);
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 1;
    ctx.stroke();

    [70, 85, 100, 115, 130].forEach(tickIQ => {
      const xPx = 30 + ((tickIQ - minIQ) / (maxIQ - minIQ)) * (w - 60);
      ctx.fillStyle = '#64748b';
      ctx.font = '10px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(tickIQ, xPx, baselineY + 16);
    });

    const boundedIQ = Math.max(minIQ, Math.min(maxIQ, userIQ));
    const userXPx = 30 + ((boundedIQ - minIQ) / (maxIQ - minIQ)) * (w - 60);
    const userPdf = normalPdf(boundedIQ);
    const userYPx = baselineY - (userPdf / maxPdf) * (h - 48);

    ctx.beginPath();
    ctx.moveTo(userXPx, baselineY);
    ctx.lineTo(userXPx, 14);
    ctx.strokeStyle = '#e11d48';
    ctx.lineWidth = 2;
    ctx.setLineDash([3, 3]);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.beginPath();
    ctx.arc(userXPx, userYPx, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#e11d48';
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = '#e11d48';
    ctx.font = 'bold 11px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`You: IQ ${userIQ}`, userXPx, 10);
  }

  // --------------------------------------------------------------------------
  // Modals & Storage
  // --------------------------------------------------------------------------
  function setupModals() {
    const openLeaderboardBtn = document.getElementById('open-leaderboard-btn');
    const modalLeaderboard = document.getElementById('modal-leaderboard');
    if (openLeaderboardBtn && modalLeaderboard) {
      openLeaderboardBtn.addEventListener('click', () => {
        window.soundEngine.playClick();
        loadLeaderboard();
        modalLeaderboard.classList.add('active');
      });
    }

    const openAdminBtn = document.getElementById('open-admin-btn');
    const modalAdmin = document.getElementById('modal-admin');
    const refreshAdminBtn = document.getElementById('refresh-admin-btn');

    if (openAdminBtn && modalAdmin) {
      openAdminBtn.addEventListener('click', () => {
        window.soundEngine.playClick();
        loadAdminRecords();
        modalAdmin.classList.add('active');
      });
    }

    if (refreshAdminBtn) {
      refreshAdminBtn.addEventListener('click', () => {
        window.soundEngine.playClick();
        loadAdminRecords();
      });
    }

    document.querySelectorAll('.modal-close-trigger').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-close');
        const modal = document.getElementById(targetId);
        if (modal) modal.classList.remove('active');
        window.soundEngine.playClick();
      });
    });

    document.querySelectorAll('.modal-backdrop').forEach(overlay => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          overlay.classList.remove('active');
        }
      });
    });

    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-backdrop.active').forEach(m => m.classList.remove('active'));
      }
    });
  }

  async function loadLeaderboard() {
    const tbody = document.getElementById('leaderboard-tbody');
    let leaders = [];

    try {
      const res = await fetch('/api/leaderboard');
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.leaderboard) {
          leaders = data.leaderboard;
        }
      }
    } catch (e) {}

    // Fallback to local storage for GitHub Pages
    if (leaders.length === 0) {
      try {
        leaders = JSON.parse(localStorage.getItem('neuro_iq_leaderboard') || '[]');
      } catch (e) {}
    }

    if (leaders.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 18px;">No tests recorded yet. Be the first!</td></tr>';
      return;
    }

    tbody.innerHTML = leaders.map((row, idx) => `
      <tr>
        <td style="font-weight: 800; color: ${idx === 0 ? '#d97706' : (idx === 1 ? '#64748b' : (idx === 2 ? '#b45309' : 'var(--text-secondary)'))};">
          #${idx + 1}
        </td>
        <td style="font-weight: 600;">${escapeHtml(row.name)}</td>
        <td>${row.age}</td>
        <td style="font-family: var(--font-mono); font-weight: 800; color: var(--accent-indigo);">${row.iq_score}</td>
        <td>${row.percentile}%</td>
        <td><span style="background: #dcfce7; color: #15803d; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">${escapeHtml(row.classification)}</span></td>
        <td>${row.time_taken_seconds}s</td>
      </tr>
    `).join('');
  }

  async function loadAdminRecords() {
    const usersTbody = document.getElementById('admin-users-tbody');
    const resultsTbody = document.getElementById('admin-results-tbody');
    let loaded = false;

    try {
      const res = await fetch('/api/admin/records');
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.data) {
          loaded = true;
          const users = data.data.users || [];
          const results = data.data.test_results || [];

          usersTbody.innerHTML = users.length === 0 ? '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No candidates recorded yet.</td></tr>' : users.map(u => `
            <tr>
              <td><strong>#${u.id}</strong></td>
              <td style="font-weight: 600;">${escapeHtml(u.name)}</td>
              <td>${u.age}</td>
              <td style="font-family: var(--font-mono); font-size: 12px;">${escapeHtml(u.email)}</td>
              <td><span style="background: #dcfce7; color: #15803d; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">✓ Active</span></td>
              <td style="font-size: 11px; color: var(--text-muted);">${formatDate(u.created_at)}</td>
            </tr>
          `).join('');

          resultsTbody.innerHTML = results.length === 0 ? '<tr><td colspan="10" style="text-align: center; color: var(--text-muted);">No results recorded yet.</td></tr>' : results.map(r => `
            <tr>
              <td><strong>#${r.id}</strong></td>
              <td style="font-weight: 600;">${escapeHtml(r.name)}</td>
              <td style="font-family: var(--font-mono); font-size: 12px;">${escapeHtml(r.email)}</td>
              <td>${r.age}</td>
              <td style="font-family: var(--font-mono); font-weight: 800; color: var(--accent-indigo);">${r.iq_score}</td>
              <td>${r.percentile}%</td>
              <td><span style="background: #dcfce7; color: #15803d; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">${escapeHtml(r.classification)}</span></td>
              <td style="font-family: var(--font-mono); font-size: 11px; color: var(--accent-indigo);">${r.certificate_id}</td>
              <td>${r.time_taken_seconds}s</td>
              <td style="font-size: 11px; color: var(--text-muted);">${formatDate(r.completed_at)}</td>
            </tr>
          `).join('');
        }
      }
    } catch (e) {}

    if (!loaded) {
      usersTbody.innerHTML = `<tr><td>#1</td><td style="font-weight:600;">${escapeHtml(state.user.name || 'Candidate')}</td><td>${state.user.age}</td><td>${escapeHtml(state.user.email || 'active')}</td><td><span style="background: #dcfce7; color: #15803d; padding: 2px 8px; border-radius: 12px; font-size: 11px;">✓ Local Active</span></td><td>Just now</td></tr>`;
      resultsTbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: var(--text-muted); padding: 12px;">Complete an assessment to view recorded results.</td></tr>';
    }
  }

  function setupResultActions() {
    const printBtn = document.getElementById('btn-print-cert');
    if (printBtn) {
      printBtn.addEventListener('click', () => {
        window.soundEngine.playClick();
        window.print();
      });
    }

    const viewLeaderboardBtn = document.getElementById('btn-view-leaderboard-res');
    if (viewLeaderboardBtn) {
      viewLeaderboardBtn.addEventListener('click', () => {
        window.soundEngine.playClick();
        loadLeaderboard();
        document.getElementById('modal-leaderboard').classList.add('active');
      });
    }

    const retestBtn = document.getElementById('btn-retest');
    if (retestBtn) {
      retestBtn.addEventListener('click', async () => {
        window.soundEngine.playClick();
        if (confirm('Retake assessment? A fresh set of questions will be fetched from the question server.')) {
          retestBtn.textContent = 'Querying Server...';
          retestBtn.disabled = true;

          try {
            const onlineQuestions = await fetchAllQuestionsFromServer(12);
            state.questions = (onlineQuestions && onlineQuestions.length >= 5) ? onlineQuestions : getStaticFallbackQuestions(12);
            startTest();
          } catch (e) {
            alert('Failed to refresh test: ' + e.message);
          } finally {
            retestBtn.textContent = '🔄 Retake (New Questions)';
            retestBtn.disabled = false;
          }
        }
      });
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, s => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[s]));
  }

  function formatDate(isoStr) {
    if (!isoStr) return '—';
    try {
      const d = new Date(isoStr);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' ' + d.toLocaleDateString([], { month: 'short', day: 'numeric' });
    } catch (e) {
      return isoStr;
    }
  }

})();
