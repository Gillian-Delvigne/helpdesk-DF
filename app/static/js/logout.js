const handleToggleAvatarDropdown = () => {
    const userAvatar = document.getElementById("user-avatar");
    if (!userAvatar) return;
    userAvatar.addEventListener("click", () => {
        const avatarDropdown = document.getElementById("avatar-dropdown");
        avatarDropdown.classList.toggle("hidden");
    });
};

const handleLogout = () => {
    const logoutBtns = document.querySelectorAll(".logout-btn");
    if (!logoutBtns.length) return;
    logoutBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            window.location.replace("/logout");
        });
    });
};

export {handleToggleAvatarDropdown, handleLogout}