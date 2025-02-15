function updateConversation(messages) {
    // Ensure this function correctly updates the conversation section
    const conversationSection = document.querySelector('.conversation-section');
    conversationSection.innerHTML = messages.map(message => `
        <div class="message" id="message-${message.id}">
            <span class="sender">${message.sender}</span>
            <span class="text">${message.text}</span>
        </div>
    `).join('');
} 