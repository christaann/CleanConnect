// script.js - CleanConnect Main JavaScript
// ==========================================
// Handles: hamburger menu, auto-close flash messages,
// drag & drop uploads, and general UX enhancements.

document.addEventListener('DOMContentLoaded', function () {

    // =============================================
    // 1. MOBILE HAMBURGER MENU TOGGLE
    // =============================================
    const hamburger = document.getElementById('hamburger');
    const navLinks  = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function () {
            navLinks.classList.toggle('open');
            // Change icon appearance when open
            const spans = hamburger.querySelectorAll('span');
            hamburger.classList.toggle('active');
        });

        // Close menu when a nav link is clicked (mobile)
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('open');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', function (e) {
            if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('open');
            }
        });
    }

    // =============================================
    // 2. AUTO-DISMISS FLASH MESSAGES
    // Auto-close success messages after 5 seconds
    // =============================================
    const flashMsgs = document.querySelectorAll('.flash-msg');
    flashMsgs.forEach(function (msg) {
        setTimeout(function () {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(30px)';
            msg.style.transition = 'all 0.4s ease';
            setTimeout(() => msg.remove(), 400);
        }, 5000);  // 5 seconds
    });

    // =============================================
    // 3. DRAG & DROP FILE UPLOAD (on submit page)
    // =============================================
    const uploadArea = document.getElementById('fileUploadArea');
    if (uploadArea) {
        // Highlight drop zone on dragover
        uploadArea.addEventListener('dragover', function (e) {
            e.preventDefault();
            uploadArea.style.borderColor = '#16a34a';
            uploadArea.style.background  = '#dcfce7';
        });

        // Remove highlight on dragleave
        uploadArea.addEventListener('dragleave', function () {
            uploadArea.style.borderColor = '';
            uploadArea.style.background  = '';
        });

        // Handle drop event
        uploadArea.addEventListener('drop', function (e) {
            e.preventDefault();
            uploadArea.style.borderColor = '';
            uploadArea.style.background  = '';

            const file = e.dataTransfer.files[0];
            if (file) {
                // Assign the dropped file to the file input
                const input = document.getElementById('photo');
                const dt    = new DataTransfer();
                dt.items.add(file);
                input.files = dt.files;

                // Trigger the preview
                const event = new Event('change');
                input.dispatchEvent(event);
            }
        });
    }

    // =============================================
    // 4. ACTIVE NAV LINK HIGHLIGHTING
    // Marks the current page's nav link as active
    // =============================================
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // =============================================
    // 5. TABLE ROW CLICK (Admin - highlight selected)
    // =============================================
    const tableRows = document.querySelectorAll('.admin-table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function (e) {
            // Don't highlight if clicking on form/button
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'SELECT' || e.target.tagName === 'A') return;
            tableRows.forEach(r => r.style.background = '');
            this.style.background = '#f0fdf4';
        });
    });

    // NOTE: Fake hero stats removed — no count-up animation needed.

    // =============================================
    // 7. SCROLL ANIMATION - Fade in cards
    // =============================================
    const observerOptions = { threshold: 0.1 };
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity  = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Apply to cards and step cards
    document.querySelectorAll('.step-card, .type-card, .contact-card, .stat-card').forEach(el => {
        el.style.opacity   = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    console.log('✅ CleanConnect JS loaded successfully.');
});