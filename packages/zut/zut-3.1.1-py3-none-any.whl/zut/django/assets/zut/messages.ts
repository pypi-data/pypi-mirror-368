const messagesDiv = document.getElementById('messages')!
const messagesContentDiv = document.getElementById('messages-content')!

/**
 * Add a message with the given level.
 */
export function addMessage(level: string, html: string) {
    let color = 'primary'
    if (level) {
        switch (level.toUpperCase()) {
            case 'DEBUG': color = 'secondary'; break
            case 'INFO': color = 'info'; break
            case 'SUCCESS': color = 'success'; break
            case 'WARNING': color = 'warning'; break
            case 'ERROR': color = 'danger'; break
        }
    }

    // Create message element
    /** @type {HTMLDivElement} */
    const messageDiv = document.createElement('div')
    messageDiv.className = `alert alert-${color} alert-dismissible fade show`
    messageDiv.role = 'alert'
    messageDiv.innerHTML = `${html}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`
    messagesContentDiv.appendChild(messageDiv)

    // Fix the messages container at the top of the screen if scrolling above 75 px
    if (window.scrollY > 75) {
        messagesDiv.classList.add('fixed-messages') // see layout.css
    }

    return messageDiv
}
