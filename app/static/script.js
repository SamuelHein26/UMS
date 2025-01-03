setTimeout(() => {
    const flashMessages = document.getElementById('flash-messages');
    if (flashMessages) {
        flashMessages.classList.add('fade-out');
        setTimeout(() => flashMessages.remove(), 500);
    }
}, 3000);
