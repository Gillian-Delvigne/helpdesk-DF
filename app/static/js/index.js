import * as Modal from "./modal.js";
import * as Logout from "./logout.js";
import * as Sidebar from "./sidebar.js"

const handleShowHidePassword = () => {
    const eyeIcons = document.querySelectorAll(".eye-icon");
    if (!eyeIcons.length) return;
    eyeIcons.forEach((icon) => {
        const field = icon.previousElementSibling;
        const slash = icon.querySelector(".eye-slash");
        icon.addEventListener("click", () => {
            field.type = field.type === "password" ? "text" : "password";
            slash.classList.toggle("hidden");
        });
    });
};

const handleDismissNotification = () => {
    window.onload = () => {
        const window = document.getElementById("main-container");
        if (!window) return;
        const notificationContainer = document.getElementById(
            "notification-container",
        );
        if (!notificationContainer) return;

        // Handle click outside the notification
        window.addEventListener("click", (event) => {
            if (event.target !== notificationContainer)
                notificationContainer.remove();
        });

        // Handle click on delete button
        notificationContainer.addEventListener("click", (event) => {
            const notifDismissBtn = event.target.closest(".dismiss-btn");
            if (!notifDismissBtn) return;
            const notif = notifDismissBtn.closest("div .notification");
            if (!notif) return;
            notif.remove();
        });
    };
};

const handleTableMasterCheckboxes = () => {
    const tables = document.querySelectorAll(".checkbox-table");
    if (!tables.length) return;
    // TODO: check all checkboxes when master is checked (and vice versa)
    console.log(tables);
};

// Init JS
// TODO: Wrap all this shit in a an init wrapper
handleShowHidePassword();
Logout.handleToggleAvatarDropdown();
Logout.handleLogout();
handleDismissNotification();
handleTableMasterCheckboxes();
Modal.handleOpenModal();
Modal.handleCloseModal();
Sidebar.handleSidebarCollapse();
