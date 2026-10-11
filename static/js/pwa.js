/**
 * Khidamati PWA Client Management Script
 * خدماتي - إدارة تطبيق الويب التقدمي، التثبيت، والعمل دون إنترنت
 */

(function () {
    'use strict';

    let deferredPrompt = null;

    // 1. Register Service Worker with full origin scope
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function () {
            navigator.serviceWorker
                .register('/sw.js', { scope: '/' })
                .then(function (registration) {
                    console.log('[PWA] Service Worker registered with scope:', registration.scope);

                    // Check for SW updates
                    registration.addEventListener('updatefound', function () {
                        const newWorker = registration.installing;
                        if (newWorker) {
                            newWorker.addEventListener('statechange', function () {
                                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                    console.log('[PWA] New version available, will activate on next reload.');
                                }
                            });
                        }
                    });
                })
                .catch(function (error) {
                    console.error('[PWA] Service Worker registration failed:', error);
                });
        });
    }

    // 2. Check if already installed in Standalone Mode
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;

    // 3. Handle 'beforeinstallprompt' Event (Chromium, Android, Edge, Desktop)
    window.addEventListener('beforeinstallprompt', function (e) {
        // Prevent default browser install bar
        e.preventDefault();
        deferredPrompt = e;

        // Show install button in Navbar
        const navInstallBtn = document.getElementById('pwaInstallNavBtn');
        if (navInstallBtn && !isStandalone) {
            navInstallBtn.classList.remove('d-none');
            navInstallBtn.classList.add('d-inline-flex');
        }

        // Show floating install banner if not dismissed recently
        const dismissedAt = localStorage.getItem('pwa_banner_dismissed_at');
        const now = Date.now();
        const threeDays = 3 * 24 * 60 * 60 * 1000;

        if (!isStandalone && (!dismissedAt || (now - parseInt(dismissedAt, 10)) > threeDays)) {
            const installBanner = document.getElementById('pwaInstallBanner');
            if (installBanner) {
                setTimeout(function () {
                    installBanner.style.display = 'block';
                }, 3000);
            }
        }
    });

    // 4. Trigger Install Flow
    function triggerPwaInstall() {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then(function (choiceResult) {
                if (choiceResult.outcome === 'accepted') {
                    console.log('[PWA] User accepted the install prompt');
                } else {
                    console.log('[PWA] User dismissed the install prompt');
                }
                deferredPrompt = null;
                hideInstallBanner();
            });
        } else {
            // iOS or unsupported browser: check for iOS
            const isIos = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
            if (isIos && !isStandalone) {
                const iosModal = document.getElementById('pwaIosModal');
                if (iosModal && typeof bootstrap !== 'undefined') {
                    const modal = new bootstrap.Modal(iosModal);
                    modal.show();
                } else {
                    alert('لتثبيت تطبيق خدماتي على هاتفك:\nاضغط على أيقونة المشاركة (Share) في المتصفح ثم اختر "إضافة إلى الشاشة الرئيسية" (Add to Home Screen)');
                }
            } else {
                showToast('التطبيق مثبت بالفعل أو أن متصفحك لا يدعم التثبيت المباشر.', 'online');
            }
        }
    }

    function hideInstallBanner() {
        const installBanner = document.getElementById('pwaInstallBanner');
        if (installBanner) {
            installBanner.style.display = 'none';
        }
        localStorage.setItem('pwa_banner_dismissed_at', Date.now().toString());
    }

    // 5. Handle Successful Installation
    window.addEventListener('appinstalled', function () {
        console.log('[PWA] Khidamati App installed successfully!');
        deferredPrompt = null;
        hideInstallBanner();
        const navInstallBtn = document.getElementById('pwaInstallNavBtn');
        if (navInstallBtn) {
            navInstallBtn.classList.add('d-none');
            navInstallBtn.classList.remove('d-inline-flex');
        }
        showToast('تم تثبيت تطبيق خدماتي بنجاح على جهازك! 🎉', 'online');
    });

    // 6. Network Online / Offline Detection
    function showToast(message, type) {
        let toast = document.getElementById('pwaStatusToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'pwaStatusToast';
            toast.className = 'pwa-status-toast';
            document.body.appendChild(toast);
        }
        toast.className = 'pwa-status-toast ' + (type === 'offline' ? 'offline' : 'online');
        toast.innerHTML = (type === 'offline' ? '<i class="bi bi-wifi-off"></i> ' : '<i class="bi bi-wifi"></i> ') + message;
        toast.style.display = 'flex';

        if (type === 'online') {
            setTimeout(function () {
                toast.style.display = 'none';
            }, 3500);
        }
    }

    window.addEventListener('offline', function () {
        showToast('أنت تتصفح حالياً دون اتصال بالإنترنت (الوضع غير المتصل).', 'offline');
    });

    window.addEventListener('online', function () {
        showToast('تمت استعادة الاتصال بالإنترنت بنجاح!', 'online');
    });

    // 7. Wire Up UI Listeners
    document.addEventListener('DOMContentLoaded', function () {
        // Install buttons
        const navInstallBtn = document.getElementById('pwaInstallNavBtn');
        if (navInstallBtn) {
            navInstallBtn.addEventListener('click', triggerPwaInstall);
        }

        const bannerActionBtn = document.getElementById('pwaInstallActionBtn');
        if (bannerActionBtn) {
            bannerActionBtn.addEventListener('click', triggerPwaInstall);
        }

        const bannerCloseBtn = document.getElementById('pwaInstallCloseBtn');
        if (bannerCloseBtn) {
            bannerCloseBtn.addEventListener('click', hideInstallBanner);
        }

        // Check if iOS and show iOS install option if needed
        const isIos = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        if (isIos && !isStandalone && navInstallBtn) {
            navInstallBtn.classList.remove('d-none');
            navInstallBtn.classList.add('d-inline-flex');
        }
    });

    // Export trigger function globally
    window.triggerKhidamatiPwaInstall = triggerPwaInstall;
})();
