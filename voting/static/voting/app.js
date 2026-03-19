// app.js — simple, no external libs
document.addEventListener("DOMContentLoaded", () => {
  const choices = document.querySelectorAll(".choice-card");
  const resultsSection = document.getElementById("resultsSection");
  const message = document.getElementById("message");
  const totalCountEl = document.getElementById("totalCount");

  function getCSRF() {
    // Django's CSRF token in cookie; fallback meta
    const meta = document.querySelector('meta[name="csrf-token"]');
    if(meta) return meta.content;
    const match = document.cookie.match(/csrftoken=([\w-]+)/);
    return match ? match[1] : "";
  }

  choices.forEach(btn => {
    btn.addEventListener("click", async () => {
      const choiceId = btn.dataset.choiceId;
      // get reg no if provided
      const regNoInput = document.getElementById("reg_no");
      const regNo = regNoInput ? regNoInput.value.trim() : "";
      // UI feedback: show selected state briefly
      btn.classList.add("selected");
      // send AJAX to vote endpoint
      try {
        const payload = new URLSearchParams();
        payload.append("choice_id", choiceId);
        if(regNo) payload.append("reg_no", regNo);

        const resp = await fetch(window.location.pathname + "vote/", {
          method: "POST",
          body: payload,
          headers: {
            "X-CSRFToken": getCSRF()
          }
        });

        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error || "Vote failed");

        showMessage("Vote recorded ✨ Thank you!", "show");
        updateResults(data.results, data.total);
        resultsSection.scrollIntoView({ behavior: "smooth" });

      } catch (err) {
        showMessage(err.message || "Error sending vote", "show");
        console.error(err);
      } finally {
        setTimeout(()=> btn.classList.remove("selected"), 700);
      }
    });
  });

  function showMessage(txt, cls) {
    message.textContent = txt;
    message.classList.add(cls);
    setTimeout(()=> message.classList.remove(cls), 3000);
  }

  function updateResults(results, total){
    // results: [{id, text, votes}, ...]
    totalCountEl.textContent = total || results.reduce((s,r)=>s+r.votes,0);
    results.forEach(r => {
      const row = document.querySelector(`.bar-row[data-choice-id="${r.id}"]`);
      if(!row) return;
      const fill = row.querySelector(".bar-fill");
      const count = row.querySelector(".bar-count");
      const percent = total ? Math.round((r.votes/total)*100) : 0;
      // animate width
      requestAnimationFrame(()=> {
        fill.style.width = percent + "%";
      });
      count.textContent = r.votes;
    });
  }

  // Optionally fetch initial results on load (in case poll already has votes)
  (async function fetchInit(){
    try{
      const resp = await fetch(window.location.pathname + "vote/"); // you can add GET handler if needed
      // If you don't have GET for results, you can embed initial data in the template instead.
    }catch(e){}
  })();
});
