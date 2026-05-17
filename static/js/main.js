document.addEventListener('DOMContentLoaded', function () {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.site-nav .nav-link').forEach(function (link) {
        const href = link.getAttribute('href');
        if (!href || href === '#') {
            return;
        }

        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });
});
