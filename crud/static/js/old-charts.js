    // === Gráfico comparativo Corriente Disponible vs Consumo Total ===
    createChart('chart_comparativa_corriente_consumo', {
        type: 'line',
        data: {
            labels: {{ totales.fechas|tojson }},
            datasets: [
                {
                    label: 'Corriente Disponible',
                    data: {{ totales.corriente|tojson }},
                    borderColor: 'rgba(52,152,219,0.8)',
                    backgroundColor: 'rgba(52,152,219,0.1)',
                    fill: true,
                    borderWidth: 2
                },
                {
                    label: 'Consumo Total',
                    data: {{ totales.consumo_total|tojson }},
                    borderColor: 'rgba(231,76,60,0.8)',
                    backgroundColor: 'rgba(231,76,60,0.1)',
                    fill: true,
                    borderWidth: 2
                }
            ]
        },
        options:{
            ...chartConfig.defaultOptions,
            plugins: {
                ...chartConfig.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Disponibilidad vs Consumo',
                    padding: { top: 10, bottom: 20 }
                }
            },
            scales: {
            ...chartConfig.defaultOptions.scales,
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: 23,
                    grid: { color: 'rgba(0,0,0,0.05)' },
                    title: {
                        display: true,          // muestra el título
                        text: 'Corriente (A)',  // texto del eje
                        // color: '#2c3e50',       // color opcional
                        // font: {
                        //     size: 12,
                        //     weight: 'bold'
                        // },
                        padding: { top: 10, bottom: 0 }
                    }
                }
            }
        } 
    });






// VERSIÓN FUNCIONAL DEL GRAFICO CON TODOS LOS NODOS + CONSUMO TOTAL
   // === Gráfico con todos los nodos + Consumo Total ===
    const dataNodos = {{ data_por_nodo|tojson }};
    const allLabels = Object.values(dataNodos)[0].fechas;

    // datasets de cada nodo
    const datasetsNodos = Object.entries(dataNodos).map(([nodo, datos], idx) => ({
        label: `NC (${nodo}) - P:${datos.prioridad}`,
        data: datos.consumos,
        borderColor: chartConfig.colors.primary[idx % chartConfig.colors.primary.length],
        backgroundColor: chartConfig.colors.backgrounds[idx % chartConfig.colors.backgrounds.length],
        fill: false,
        borderWidth: 2,
        cubicInterpolationMode: 'monotone',
        tension: 0.7
    }));

    // dataset adicional con consumo total
    datasetsNodos.push({
        label: 'Total',
        data: {{ totales.consumo_total|tojson }},
        borderColor: 'rgba(231, 76, 60, 0.9)',         // color rojo fuerte
        backgroundColor: 'rgba(231, 76, 60, 0.15)',
        borderWidth: 3,
        fill: false,
        cubicInterpolationMode: 'monotone',
        tension: 0.6,
        borderDash: [5, 5]                             // línea punteada para diferenciarlo
    });

    // creación del gráfico
    createChart('chart_todos_nodos', {
        type: 'line',
        data: {
            labels: {{ totales.fechas|tojson }},       // usamos las fechas completas del total
            datasets: datasetsNodos
        },
        options: {
            ...chartConfig.defaultOptions,
            plugins: {
                ...chartConfig.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Consumo Individual por Nodo y Consumo Total',
                    padding: { top: 10, bottom: 20 }
                }
            },
            scales: {
                ...chartConfig.defaultOptions.scales,
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: 23,
                    grid: { color: 'rgba(0,0,0,0.05)' },
                    title: {
                        display: true,
                        text: 'Corriente (A)',
                        padding: { top: 10, bottom: 0 }
                    }
                }
            }
        }
    });


    document.querySelectorAll('.charts-visibility input').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const chartId = this.id.replace('show-', 'chart_');
            const card = document.querySelector(`#${chartId}`).closest('.card');
            card.style.display = this.checked ? 'flex' : 'none';
        });
    });

 // === Gráficos por nodo  anteriores==
    {% for nodo, datos in data_por_nodo.items() %}
    createChart('chart_{{ nodo }}', {
        type: 'line',
        data: {
            labels: {{ datos.fechas|tojson }},
            datasets: [{
                label: 'Consumo (A)',
                data: {{ datos.consumos|tojson }},
                borderColor: chartConfig.colors.primary[{{ loop.index0 }} % chartConfig.colors.primary.length],
                backgroundColor: chartConfig.colors.backgrounds[{{ loop.index0 }} % chartConfig.colors.backgrounds.length],
                fill: true,
                borderWidth: 2
            }]
        },
        options: {
            ...chartConfig.defaultOptions,
            plugins: {
                ...chartConfig.defaultOptions.plugins,
                title: { display: true, padding: { top: 10, bottom: 20 } }
            }
        }
    });
    {% endfor %}
