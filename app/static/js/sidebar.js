const toggleclasses = (element, classes) =>
    classes.map((className) => element.classList.toggle(className));

const handleSidebarCollapse = () => {
    const sidebar = document.getElementById("sidebar");
    if (!sidebar) return;
    const sidebarCollapseBtn = document.getElementById("sidebar-collapse-btn");
    const sidebarLabels = sidebar.querySelectorAll(".sidebar-label");
    if (!sidebarCollapseBtn || !sidebarLabels.length) return;

    sidebarCollapseBtn.addEventListener("click", (event) => {
        sidebar.classList.toggle("w-full");
		toggleclasses(sidebarCollapseBtn, ["bg-indigo-200", "rounded-md", "text-indigo-700", "text-indigo-900", "rotate-180"])
        sidebarLabels.forEach((label) => label.classList.toggle("hidden"));
    });
};

export { handleSidebarCollapse };
