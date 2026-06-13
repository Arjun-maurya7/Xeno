// Global Xeno CRM JS Helpers

document.addEventListener('DOMContentLoaded', () => {
  // AI Message Generator binding
  const btnGenerateAi = document.getElementById('btn-generate-ai');
  const aiPromptInput = document.getElementById('ai_prompt');
  const messageTextarea = document.getElementById('message');

  if (btnGenerateAi && aiPromptInput && messageTextarea) {
    btnGenerateAi.addEventListener('click', async () => {
      const prompt = aiPromptInput.value;
      if (!prompt.trim()) {
        alert('Please enter a prompt first.');
        return;
      }

      const origText = btnGenerateAi.textContent;
      btnGenerateAi.textContent = 'Generating...';
      btnGenerateAi.disabled = true;

      try {
        const res = await fetch('/campaigns/generate-message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({ prompt })
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Failed to generate message.');
        }

        const data = await res.json();
        messageTextarea.value = data.message;
      } catch (e) {
        alert('Error: ' + e.message);
      } finally {
        btnGenerateAi.textContent = origText;
        btnGenerateAi.disabled = false;
      }
    });
  }
});
