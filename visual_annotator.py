class VisualAnnotator:
    def __init__(self):
        pass

    def get_annotation_script(self):
        """
        Returns a JavaScript snippet that finds all interactive elements
        on the page and draws a unique label next to each one.
        """
        return """
            (() => {
                const elements = document.querySelectorAll('a, button, input[type="submit"], input[type="button"], [role="button"]');
                const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
                let charIndex = 0;

                elements.forEach((el, i) => {
                    if (!el.offsetParent) return; // Skip hidden elements

                    const rect = el.getBoundingClientRect();
                    const label = document.createElement('div');

                    let labelText = '';
                    let currentIndex = charIndex++;
                    while (currentIndex >= 0) {
                        labelText = characters[currentIndex % 26] + labelText;
                        currentIndex = Math.floor(currentIndex / 26) - 1;
                    }

                    label.textContent = labelText;
                    label.style.position = 'absolute';
                    label.style.left = `${window.scrollX + rect.left - 20}px`;
                    label.style.top = `${window.scrollY + rect.top}px`;
                    label.style.backgroundColor = 'red';
                    label.style.color = 'white';
                    label.style.padding = '2px';
                    label.style.fontSize = '12px';
                    label.style.zIndex = '9999';
                    label.style.borderRadius = '3px';
                    label.setAttribute('data-bot-label', labelText);

                    document.body.appendChild(label);
                    el.setAttribute('data-bot-target', labelText);
                });
            })();
        """
