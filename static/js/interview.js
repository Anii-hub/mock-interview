document.addEventListener("DOMContentLoaded", () => {

  const answerBox = document.getElementById("answerBox");
  const feedbackBox = document.getElementById("feedbackBox");
  const errorBox = document.getElementById("errorBox");
  const micBtn = document.getElementById("micBtn");
  const submitBtn = document.getElementById("submitBtn");
  const questionTextEl = document.getElementById("questionText");
  const questionCounterEl = document.getElementById("questionCounter");
  const readBtn = document.getElementById("readQuestionBtn");

  /* ---------- CSRF ---------- */
  function getCSRFToken() {
    let cookieValue = null;
    document.cookie.split(";").forEach(c => {
      c = c.trim();
      if (c.startsWith("csrftoken=")) {
        cookieValue = c.substring("csrftoken=".length);
      }
    });
    return cookieValue;
  }

  /* ---------- TEXT TO SPEECH ---------- */
  let hasSpokenQuestion = false;

  function speakQuestion() {
    if (hasSpokenQuestion) return;

    const text = questionTextEl.innerText.trim();
    if (!text) return;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";

    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);

    hasSpokenQuestion = true;
  }

  readBtn.addEventListener("click", speakQuestion);

  /* ---------- VOICE CONFIDENCE METRICS ---------- */
  let voiceMetrics = {
    words: 0,
    duration: 0
  };
  let speechStartTime = null;

  /* ---------- SPEECH TO TEXT ---------- */
  let recognition;
  let isRecording = false;

  if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      speechStartTime = Date.now();
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      answerBox.value += (answerBox.value ? " " : "") + transcript;
      voiceMetrics.words += transcript.trim().split(/\s+/).length;
    };

    recognition.onend = () => {
      if (speechStartTime) {
        voiceMetrics.duration += (Date.now() - speechStartTime) / 1000;
      }
      isRecording = false;
      micBtn.disabled = false;
    };
  }

  micBtn.addEventListener("click", () => {
    if (!recognition || isRecording) return;
    errorBox.innerText = "";
    isRecording = true;
    micBtn.disabled = true;
    recognition.start();
  });

  /* ---------- SUBMIT ANSWER ---------- */
  submitBtn.addEventListener("click", () => {
    errorBox.innerText = "";

    const answer = answerBox.value.trim();
    if (!answer) {
      errorBox.innerText = "Please provide an answer.";
      return;
    }

    submitBtn.disabled = true;

    fetch("/interview/submit/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCSRFToken()
      },
      body:
        `answer=${encodeURIComponent(answer)}` +
        `&voice_words=${voiceMetrics.words}` +
        `&voice_duration=${voiceMetrics.duration}`
    })
      .then(res => res.json())
      .then(data => {

        // NEXT QUESTION
        if (data.next_question) {
          questionTextEl.innerText = data.next_question;
          questionCounterEl.innerText =
            `Question ${data.current} of ${data.total}`;

          answerBox.value = "";
          hasSpokenQuestion = false;

          // reset voice metrics
          voiceMetrics.words = 0;
          voiceMetrics.duration = 0;

          submitBtn.disabled = false;
          return;
        }

        // FINAL FEEDBACK
        if (data.final_feedback) {
          feedbackBox.innerText = data.final_feedback;
          feedbackBox.style.display = "block";

          answerBox.disabled = true;
          submitBtn.disabled = true;
          micBtn.disabled = true;
        }
      })
      .catch(err => {
        console.error(err);
        errorBox.innerText = "Something went wrong.";
        submitBtn.disabled = false;
      });
  });

});
