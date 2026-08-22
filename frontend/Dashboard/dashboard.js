const API_URL = "http://127.0.0.1:8000/dashboard/2";

async function loadDashboard() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok){
            throw new Error(
                `HTTP error: ${response.status}`
            );
        }
        const dashboard = await response.json();
        // console.log("analytics: ", dashboard.analytics);
        // console.log("charts", dashboard.charts);
        // console.log("number od charts", dashboard.charts?.length);
        renderKPIs(dashboard.analytics);
        renderCharts(dashboard.charts);
    } catch (error) {
        console.error(
            "Dashboard loading failed:",
            error
        );
    }
    
}

function renderKPIs(analytics) {
    const container = document.getElementById("kpiContainer");
    container.innerHTML = "";

    const numeric = analytics.numeric || {};

    for (const [column, stats] of Object.entries(numeric)) {
        const card = document.createElement("div");
        card.className = "kpi";
        card.innerHTML = `
            <div class="kpi-title">
                ${column}
            </div>

            <div class="kpi-value">
                ${formatNumber(stats.sum)}
            </div>
        `;

        container.appendChild(card)
    }
}

function formatNumber(value) {
    if (typeof value !== "number"){
        return value;
    }
    return value.toLocaleString();
}


function renderCharts(charts){

    const container = document.getElementById("chartContainer");
    container.innerHTML = "";

    if (!Array.isArray(charts)){
        console.warn("Charts data is not an array:", charts);
        return;
    }


    charts.forEach((chartConfig, index) => {

        console.log("CHART", index, chartConfig);
        if (!chartConfig){
            console.error("Chart config is undefined:", index);
            return
        }

        if (!chartConfig.type){
            console.error("Chart config has no type:", chartConfig);
            return
        }

        if (!Array.isArray(chartConfig.data)){
            console.warn("chartConfig has invalid data:", chartConfig);
            return;
        }
        
        const card = document.createElement("div");
        card.className = "chart-card";
        const title = document.createElement("h3");
        title.textContent = chartConfig.title || `Chart ${index + 1}`;

        // const wrapper = document.createElement("div");
        // wrapper.className = "chart-wrapper";

        const canvas = document.createElement("canvas");
        canvas.id = `chart-${index}`;

        // wrapper.appendChild(canvas);
        card.appendChild(title);
        card.appendChild(canvas)
        container.appendChild(card)

        const ctx = canvas.getContext("2d");

        if (
            chartConfig.type === "bar" || chartConfig.type === "line"
        ){
            const labels = chartConfig.data.map(row => row[chartConfig.xKey]);
            const datasets = chartConfig.series.map(series => ({
                label: series.label || series.dataKey,
                data: chartConfig.data.map(
                    row => row[series.dataKey]
                ),
                borderWidth: 2,
                // tension: chartConfig.type === "line"
                //     ? 0.3
                //     : 0
            }));

            new Chart(ctx, {
                type: chartConfig.type,
                data: {
                    labels: labels,
                    datasets: datasets
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: false,
                            ticks: {
                                autoSkip: true,
                                maxRotation: 45,
                                minRotation: 0
                            }
                        },
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        else if (chartConfig.type === "scatter") {
            const dataset = chartConfig.data.map(point => ({
                x: point.x,
                y: point.y
            }));

            new Chart(ctx, {
                type: "scatter",
                data: {
                    datasets: [
                        {
                            label: chartConfig.title,
                            data: dataset,
                            borderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: "linear",
                            position: "bottom"
                        },

                        y: {
                            beginAtZero: true
                        }
                    },

                    plugins: {
                        legend: {
                            display: true
                        }
                    }
                }
            });
        }

        else {
            console.warn(
                "Unsupported chart type:",
                chartConfig.type
            );
        }
    });
}


function createChart(canvas, chart){

    const labels = chart.data.map(
        row => row[chart.xKey]
    );

    const datasets = chart.series.map(series => {
        return {
            label: series.label,
            data: chart.data.map(
                row => row[series.dataKey]
            )
        };
    });

    new chart(canvas, {
        type: chart.type,

        data: {
            labels: labels,
            datasets: datasets
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

document.getElementById("refreshBtn").addEventListener(
    "click",
    loadDashboard
);

loadDashboard();