"use strict";

document.querySelectorAll("form[data-quiz]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const selected = form.querySelector("input:checked");
    const feedback = form.querySelector("[role='status']");
    feedback.textContent = selected
      ? selected.dataset.feedback
      : "先选择一个判断，再查看反馈。";
  });
});
