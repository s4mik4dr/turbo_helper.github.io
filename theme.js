document.addEventListener('DOMContentLoaded', function() {
    // Получаем кнопку переключения темы
    const themeToggle = document.getElementById('theme-toggle');
    const moonIcon = '<i class="fas fa-moon"></i>';
    const sunIcon = '<i class="fas fa-sun"></i>';
    
    // Проверяем, есть ли сохраненная тема
    const savedTheme = localStorage.getItem('theme');
    
    // Применяем сохраненную тему или используем светлую по умолчанию
    if (savedTheme === 'dark') {
        document.body.setAttribute('data-bs-theme', 'dark');
        themeToggle.innerHTML = sunIcon;
    } else {
        document.body.setAttribute('data-bs-theme', 'light');
        themeToggle.innerHTML = moonIcon;
    }
    
    // Добавляем обработчик события на кнопку
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.body.getAttribute('data-bs-theme');
        
        if (currentTheme === 'light') {
            document.body.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            themeToggle.innerHTML = sunIcon;
        } else {
            document.body.setAttribute('data-bs-theme', 'light');
            localStorage.setItem('theme', 'light');
            themeToggle.innerHTML = moonIcon;
        }
    });
}); 