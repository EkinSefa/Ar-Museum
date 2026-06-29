document.addEventListener("DOMContentLoaded", function() {
    var sidebar = document.querySelector("#jazzy-sidebar") || document.querySelector(".app-sidebar") || document.querySelector(".main-sidebar");
    if (sidebar) {
        // Ensure position relative for absolute positioning of children
        sidebar.style.position = "relative";

        // Check if button already exists to prevent duplicate injections
        if (document.getElementById("sidebar-return-button-container")) return;

        // Create the container div
        var container = document.createElement("div");
        container.id = "sidebar-return-button-container";
        container.className = "sidebar-custom-bottom p-3";
        container.style.position = "absolute";
        container.style.bottom = "0";
        container.style.left = "0";
        container.style.right = "0";
        container.style.borderTop = "1px solid rgba(255,255,255,0.15)";
        container.style.zIndex = "1040";
        container.style.backgroundColor = "inherit";
        
        // Create the anchor link
        var link = document.createElement("a");
        link.href = "/";
        link.className = "btn btn-warning btn-block font-weight-bold text-dark shadow-sm";
        link.style.borderRadius = "8px";
        link.style.backgroundColor = "#f59e0b";
        link.style.borderColor = "#f59e0b";
        link.style.color = "#000000";
        link.style.display = "flex";
        link.style.alignItems = "center";
        link.style.justifyContent = "center";
        link.style.padding = "8px 12px";
        link.style.textDecoration = "none";
        
        // Add icon and text
        link.innerHTML = '<i class="fas fa-arrow-left mr-2"></i><span class="btn-text">Siteye Dön</span>';
        
        container.appendChild(link);
        sidebar.appendChild(container);
        
        // Add padding to the sidebar wrapper / inner container to avoid overlap
        var sidebarInner = sidebar.querySelector(".sidebar-wrapper") || sidebar.querySelector(".sidebar");
        if (sidebarInner) {
            sidebarInner.style.paddingBottom = "75px";
        }

        // Monitor body class mutations to adjust button display if sidebar collapses/expands
        var observer = new MutationObserver(function() {
            if (sidebar.offsetWidth < 100) {
                // Collapsed state
                link.querySelector(".btn-text").style.display = "none";
                link.querySelector("i").style.marginRight = "0";
                link.style.padding = "8px 0";
                container.style.padding = "10px 5px";
            } else {
                // Expanded state
                link.querySelector(".btn-text").style.display = "inline";
                link.querySelector("i").style.marginRight = "8px";
                link.style.padding = "8px 12px";
                container.style.padding = "16px";
            }
        });

        observer.observe(document.body, { attributes: true, attributeFilter: ["class"] });
        observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
        
        // Initial check
        setTimeout(function() {
            if (sidebar.offsetWidth < 100) {
                link.querySelector(".btn-text").style.display = "none";
                link.querySelector("i").style.marginRight = "0";
                link.style.padding = "8px 0";
                container.style.padding = "10px 5px";
            }
        }, 100);
    }
});
