// main.js

// === Funciones ===
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
}

function toggleSidebar() {
    document.body.classList.toggle('sidebar-hidden');
    localStorage.setItem('sidebarHidden', document.body.classList.contains('sidebar-hidden') ? 'true' : 'false');
}

window.addEventListener('load', () => {
    // Obtener instancias de todos los gráficos activos
    const charts = Object.values(Chart.instances);

    const grid = document.getElementById('show-grid');
    const tooltips = document.getElementById('show-tooltips');
    const anim = document.getElementById('animate-charts');

    if (grid) grid.addEventListener('change', e => {
        charts.forEach(c => {
            c.options.scales.x.grid.display = e.target.checked;
            c.options.scales.y.grid.display = e.target.checked;
            c.update();
        });
    });

    if (tooltips) tooltips.addEventListener('change', e => {
        charts.forEach(c => {
            c.options.plugins.tooltip.enabled = e.target.checked;
            c.update();
        });
    });

    if (anim) anim.addEventListener('change', e => {
    charts.forEach(c => {
        const zoom = c.options.plugins.zoom;
        if (zoom) {
            zoom.zoom.wheel.enabled = e.target.checked;
            zoom.zoom.pinch.enabled = e.target.checked;
            zoom.pan.enabled = e.target.checked;
            c.update();
        }
		});
	});

    // Apply initial state for interaction based on checkbox
    if (anim && !anim.checked) {
        charts.forEach(c => {
            const zoom = c.options.plugins.zoom;
            if (zoom) {
                zoom.zoom.wheel.enabled = false;
                zoom.zoom.pinch.enabled = false;
                zoom.pan.enabled = false;
                c.update();
            }
        });
    }

    // Mostrar/ocultar gráficos desde los checkboxes 
    document.querySelectorAll('.charts-visibility input').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const chartId = this.id.replace('show-', 'chart_');
            const canvas = document.getElementById(chartId);
            if (!canvas) return console.warn(`No se encontró canvas con id: ${chartId}`);
            const card = canvas.closest('.card');
            if (card) card.style.display = this.checked ? 'flex' : 'none';
        });
    });

    // Botón de actualización
    document.querySelector('.btn-refresh')?.addEventListener('click', function() {
        location.reload();
    });

    // Cerrar sidebar en pantallas chicas
    window.addEventListener('resize', () => {
        if (window.innerWidth <= 768 && !document.body.classList.contains('sidebar-hidden')) {
            document.body.classList.add('sidebar-hidden');
            localStorage.setItem('sidebarHidden', 'true');
        }
    });

    document.querySelectorAll('.sidebar a').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                document.body.classList.add('sidebar-hidden');
                localStorage.setItem('sidebarHidden', 'true');
            }
        });
    });
});
