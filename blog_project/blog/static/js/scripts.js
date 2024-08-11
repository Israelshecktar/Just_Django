// scripts.js
document.addEventListener('DOMContentLoaded', function() {
    const theme = localStorage.getItem('theme') || 'light';
    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        document.getElementById('light-theme').disabled = true;
        document.getElementById('dark-theme').disabled = false;
        document.getElementById('theme-switch').checked = true;
    } else {
        document.documentElement.classList.remove('dark');
        document.getElementById('light-theme').disabled = false;
        document.getElementById('dark-theme').disabled = true;
        document.getElementById('theme-switch').checked = false;
    }
});

function toggleTheme() {
    const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.classList.toggle('dark');
    document.getElementById('light-theme').disabled = newTheme === 'dark';
    document.getElementById('dark-theme').disabled = newTheme === 'light';
    localStorage.setItem('theme', newTheme);
}
