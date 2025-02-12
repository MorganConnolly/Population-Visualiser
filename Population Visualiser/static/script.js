// When page is loaded, execute the following code:
window.onload = () => {
    const content = document.getElementById("content");
    content.style.opacity = "1";
    
    showBreak();
}

// Fades out page content and transitions to the url in param.
function transitionTo(url) {
    const content = document.getElementById("content");
    content.style.opacity = "0";

    hideBreak()

    setTimeout(() => {             // Wait for fade out before switching page.
        window.location.href = url
    }, 1000);
}

function showBreak() {
    const linebreak = document.getElementById("linebreak");
    linebreak.style.width = "75%";
}

function hideBreak() {
    const linebreak = document.getElementById("linebreak");
    linebreak.style.width = "0%";
}