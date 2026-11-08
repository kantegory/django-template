(function () {
    "use strict";

    function positionDialog(dialog, triggerBtn) {
        if (!dialog || !triggerBtn) return;

        const rect = triggerBtn.getBoundingClientRect();
        const dialogWidth = dialog.offsetWidth || 300;
        const dialogHeight = dialog.offsetHeight || 320;

        // Calculate horizontal position (viewport-relative)
        let left = rect.left;
        if (left + dialogWidth > window.innerWidth - 15) {
            left = window.innerWidth - dialogWidth - 15;
        }
        if (left < 15) {
            left = 15;
        }

        // Calculate vertical position (below button, or above if no room)
        let top = rect.bottom + 6;
        if (top + dialogHeight > window.innerHeight - 15) {
            const aboveTop = rect.top - dialogHeight - 6;
            if (aboveTop > 10) {
                top = aboveTop;
            } else {
                top = Math.max(10, window.innerHeight - dialogHeight - 15);
            }
        }

        dialog.style.position = "fixed";
        dialog.style.left = Math.round(left) + "px";
        dialog.style.top = Math.round(top) + "px";
        dialog.style.margin = "0";
        dialog.style.transform = "none";
    }

    function initDialogFix() {
        if (!window.DateTimeShortcuts) return;

        // Hook openCalendar
        if (!window.DateTimeShortcuts._origOpenCalendar) {
            window.DateTimeShortcuts._origOpenCalendar = window.DateTimeShortcuts.openCalendar;
            window.DateTimeShortcuts.openCalendar = function (num) {
                window.DateTimeShortcuts._origOpenCalendar.call(this, num);
                const cal_box = document.getElementById(window.DateTimeShortcuts.calendarDivName1 + num);
                const cal_link = document.getElementById(window.DateTimeShortcuts.calendarLinkName + num);
                if (cal_box && cal_link) {
                    positionDialog(cal_box, cal_link);
                }
            };
        }

        // Hook openClock
        if (!window.DateTimeShortcuts._origOpenClock) {
            window.DateTimeShortcuts._origOpenClock = window.DateTimeShortcuts.openClock;
            window.DateTimeShortcuts.openClock = function (num) {
                window.DateTimeShortcuts._origOpenClock.call(this, num);
                const clock_box = document.getElementById(window.DateTimeShortcuts.clockDivName + num);
                const clock_link = document.getElementById(window.DateTimeShortcuts.clockLinkName + num);
                if (clock_box && clock_link) {
                    positionDialog(clock_box, clock_link);
                }
            };
        }

        // Close on clicking outside the dialog content
        document.querySelectorAll("dialog.calendarbox, dialog.clockbox").forEach(function (dialog) {
            if (!dialog._hasClickOutsideListener) {
                dialog._hasClickOutsideListener = true;
                dialog.addEventListener("click", function (e) {
                    const rect = dialog.getBoundingClientRect();
                    const isInDialog = (
                        rect.top <= e.clientY &&
                        e.clientY <= rect.top + rect.height &&
                        rect.left <= e.clientX &&
                        e.clientX <= rect.left + rect.width
                    );
                    if (!isInDialog) {
                        dialog.close();
                    }
                });
            }
        });
    }

    function initControlSidebar() {
        document.addEventListener("click", function (e) {
            const toggleBtn = e.target.closest('[data-widget="control-sidebar"]');
            if (toggleBtn) {
                e.preventDefault();
                const sidebar = document.querySelector(".control-sidebar");
                if (sidebar) {
                    sidebar.classList.toggle("control-sidebar-open");
                }
                return;
            }

            const openSidebar = document.querySelector(".control-sidebar.control-sidebar-open");
            if (openSidebar && !openSidebar.contains(e.target) && !e.target.closest('[data-widget="control-sidebar"]')) {
                if (!e.target.closest("#codeBox")) {
                    openSidebar.classList.remove("control-sidebar-open");
                }
            }
        });

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                const openSidebar = document.querySelector(".control-sidebar.control-sidebar-open");
                if (openSidebar) {
                    openSidebar.classList.remove("control-sidebar-open");
                }
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
            initDialogFix();
            initControlSidebar();
        });
    } else {
        initDialogFix();
        initControlSidebar();
    }
    window.addEventListener("load", function () {
        initDialogFix();
    });
})();
