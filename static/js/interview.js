const answerBox = document.getElementById("answerBox");
const feedbackBox = document.getElementById("feedbackBox");
const errorBox = document.getElementById("errorBox");
const micBtn = document.getElementById("micBtn");
const stopBtn = document.getElementById("stopBtn");
const submitBtn = document.getElementById("submitBtn");

/* ---------- CSRF FROM COOKIE (SAFE) ---------- */
function getCSRFToken() {
  let cookieValue = null;
  const cookies = document.cookie.split(';');
  for (let c of cookies) {
    c = c.trim();
    if (c.startsWith('csrftoken=')) {
      cookieValue = c.substring('csrftoken='.length);
      break;
    }
  }
  return cookieValue;
}

/* ---------- SUBMIT ANSWER ---------- */
submitBtn.onclick = () => {
  errorBox.innerText = "";

  const answer = answerBox.value.trim();
  if (!answer) {
    errorBox.innerText = "Please provide an answer.";
    return;
  }

  fetch("/interview/submit/", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-CSRFToken": getCSRFToken(),
    },
    body: `answer=${encodeURIComponent(answer)}`
  })
  .then(res => res.json())
  .then(data => {

    // 🔁 NEXT QUESTION CASE
    if (data.next_question) {
      document.getElementById("questionText").innerText = data.next_question;
      document.getElementById("questionCounter").innerText =
        `Question ${data.current} of ${data.total}`;

      answerBox.value = "";   // clear previous answer
      feedbackBox.style.display = "none";
      return;
    }
        submitBtn.disabled = true;

    setTimeout(() => {
      submitBtn.disabled = false;
    }, 500);


    // ✅ FINAL FEEDBACK CASE
    if (data.final_feedback) {
      document.getElementById("feedbackBox").innerText = data.final_feedback;
      document.getElementById("feedbackBox").style.display = "block";

      // lock interview UI
      answerBox.disabled = true;
      submitBtn.disabled = true;
      micBtn.disabled = true;
    }
  })
  .catch(err => {
    console.error(err);
    errorBox.innerText = "Something went wrong.";
  });
};

/* ---------- QUESTION TEXT TO SPEECH ---------- */
let questionSpoken = false;

function speakQuestion() {
  if (questionSpoken) return; // 🔒 speak only once

  const text = document.getElementById("questionText").innerText;
  if (!text) return;

  speechSynthesis.cancel(); // stop any previous speech

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 0.95;

  utterance.onend = () => {
    questionSpoken = true;
  };

  speechSynthesis.speak(utterance);
}
