const overlay = document.getElementById("modalOverlay");

const handleOpenModal = () => {
    const openBtns = document.querySelectorAll(".team-delete-btn");
    if (!openBtns.length || !overlay) return;
    openBtns.forEach((openBtn) =>
        openBtn.addEventListener("click", (event) => {
			const confirmForm = document.getElementById("modalConfirmForm");
			if (!confirmForm) return;
            confirmForm.action = openBtn.dataset.confirmUrl;
            overlay.querySelector(".modal-title").textContent =
                openBtn.dataset.confirmTitle;
            overlay.classList.remove("hidden");
        }),
    );
};

const handleCloseModal = () => {
    if (!overlay) return;

    const closeBtn = overlay.querySelector(".modalCloseBtn");
    const cancelBtn = overlay.querySelector(".modalCancelBtn");

    if (!closeBtn || !cancelBtn) return;

    const closeModal = () => {
        overlay.classList.add("hidden");
    };

    closeBtn.onclick = cancelBtn.onclick = closeModal;

    overlay.onclick = (event) => {
        if (event.target === overlay) closeModal();
    };

    document.addEventListener("keydown", (event) => {
        if (overlay.classList.contains("hidden")) return;
        if (e.key === "Escape") closeModal();
    });
};


export { handleOpenModal, handleCloseModal };
