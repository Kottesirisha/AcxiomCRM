document.addEventListener('DOMContentLoaded', function() {
    const pipelineCtx = document.getElementById('pipelineChart');
    if (pipelineCtx) {
        const pipelineData = JSON.parse(pipelineCtx.getAttribute('data-chart') || '{}');
        new Chart(pipelineCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: pipelineData.labels || [],
                datasets: [{
                    label: 'Opportunities',
                    data: pipelineData.values || [],
                    backgroundColor: ['#3B82F6','#06B6D4','#F59E0B','#8B5CF6','#10B981','#EF4444'],
                    borderRadius: 8, borderSkipped: false
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend:{display:false}, title:{display:true, text:'Sales Pipeline', font:{size:16,weight:'600'}, color:'#1E293B'} },
                scales: { y:{beginAtZero:true, ticks:{stepSize:1,color:'#64748B'}, grid:{color:'#E2E8F0'}}, x:{ticks:{color:'#64748B'},grid:{display:false}} }
            }
        });
    }

    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        const statusData = JSON.parse(statusCtx.getAttribute('data-chart') || '{}');
        new Chart(statusCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: statusData.labels || [],
                datasets: [{ data: statusData.values || [], backgroundColor:['#3B82F6','#10B981','#EF4444'], borderWidth:0, hoverOffset:4 }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend:{position:'bottom',labels:{padding:20,font:{size:13},color:'#1E293B'}}, title:{display:true, text:'Opportunity Status', font:{size:16,weight:'600'}, color:'#1E293B'} },
                cutout: '65%'
            }
        });
    }
});
