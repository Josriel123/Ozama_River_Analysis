import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Activity, AlertTriangle, CheckCircle } from 'lucide-react';
import './index.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const COLORS = ['#ff2a5f', '#2a85ff', '#ffb02a', '#2aff85', '#a32aff', '#2ae2ff'];

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/mediciones')
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching data:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div style={{color:'white', padding:'4rem', textAlign:'center', fontSize: '1.5rem'}}>Launching Sentinel Analytics...</div>;

  // Filter out blanks or null parameters
  const parametrosList = [...new Set(data.map(d => d.parametro))].filter(p => p && p.trim() !== '');

  const renderParameterChart = (parametro, index) => {
     const specificData = data.filter(d => d.parametro === parametro && d.fecha).sort((a,b) => a.fecha.localeCompare(b.fecha));
     if (specificData.length === 0) return null;
     
     const rawValues = specificData.map(d => d.valor);
     const avgValue = rawValues.length > 0 ? rawValues.reduce((sum, val) => sum + val, 0) / rawValues.length : 0;
     const unitStr = specificData[0]?.unidad || '';
     
     let chartData = {
         labels: specificData.map(d => d.fecha.split(' ')[0]),
         datasets: [
             {
                 label: `Valor Actual`,
                 data: rawValues,
                 borderColor: COLORS[index % COLORS.length],
                 backgroundColor: `${COLORS[index % COLORS.length]}33`,
                 fill: true,
                 tension: 0.4
             },
             {
                 label: `Promedio Histórico (${avgValue.toFixed(1)})`,
                 data: rawValues.map(() => avgValue),
                 borderColor: '#ffb02a',
                 borderDash: [5, 5],
                 fill: false,
                 pointRadius: 0
             }
         ]
     };

     const rep = specificData[0];
     if (rep && (rep.limite_maximo || rep.limite_minimo)) {
         const limit = rep.limite_maximo || rep.limite_minimo;
         chartData.datasets.push({
            label: `Normativa (${limit})`,
            data: rawValues.map(() => limit),
            borderColor: '#ff2a5f',
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0
         });
     }

     const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { 
            legend: { labels: { color: '#E0E2E8', boxWidth: 12, font: {size: 11} } } 
        },
        scales: {
          x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9499A8', font: {size: 10} } },
          y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9499A8', font: {size: 10} } }
        }
     };

     return (
        <div key={parametro} className="glass-card mini-chart-container">
            <h3>{parametro} <span style={{fontSize: '0.8rem', color: '#9499A8'}}>({unitStr})</span></h3>
            <div style={{flex: 1, position: 'relative', minHeight: '220px'}}>
               <Line data={chartData} options={chartOptions} />
            </div>
        </div>
     );
  };

  const violaciones = data.filter(d => d.estado === 'VIOLACION').length;
  const seguros = data.filter(d => d.estado === 'SEGURO').length;

  return (
    <div className="dashboard">
      <header>
        <div>
          <h1>Rio Ozama Data Sentinel</h1>
          <p>Live ecological monitoring & legal compliance architecture</p>
        </div>
      </header>

      <div className="metrics-grid">
        <div className="glass-card metric-card">
          <div className="metric-icon blue"><Activity /></div>
          <div className="metric-details">
            <h3>Total Extractions</h3>
            <p>{data.length}</p>
          </div>
        </div>
        <div className="glass-card metric-card">
          <div className="metric-icon red"><AlertTriangle /></div>
          <div className="metric-details">
            <h3>Violations Found</h3>
            <p style={{color: 'var(--danger)'}}>{violaciones}</p>
          </div>
        </div>
        <div className="glass-card metric-card">
          <div className="metric-icon green"><CheckCircle /></div>
          <div className="metric-details">
            <h3>Safe Readings</h3>
            <p style={{color: 'var(--safe)'}}>{seguros}</p>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        {parametrosList.map((param, index) => renderParameterChart(param, index))}
      </div>

      <div className="glass-card table-container">
        <h2>Recent Data Extracts</h2>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Location</th>
              <th>Parameter</th>
              <th>Valor</th>
              <th>Normativa</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {data.slice().reverse().map((row, i) => (
              <tr key={i}>
                <td>{row.fecha ? row.fecha.split(' ')[0] : 'N/A'}</td>
                <td>{row.ubicacion}</td>
                <td>{row.parametro}</td>
                <td style={{fontFamily: 'Outfit', fontWeight: 600}}>
                  {row.operador && row.operador !== '=' ? `${row.operador} ` : ''}{row.valor} {row.unidad}
                </td>
                <td>
                  {row.limite_maximo ? `< ${row.limite_maximo}` : row.limite_minimo ? `> ${row.limite_minimo}` : 'Sin normativa'}
                </td>
                <td>
                  <span className={`status-badge ${row.estado && row.estado.toLowerCase()}`}>
                    {row.estado || 'UNKNOWN'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
