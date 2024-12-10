import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import {Pie} from 'react-chartjs-2';
ChartJS.register(ArcElement, Tooltip, Legend);

interface Props {
    data: any;
    options: any;
}
function EocChart(props: Props) {

  return (
    <div style={{ width: '500px', height: '500px' }}>
        <Pie  data={props.data} />
    </div>
  )
}

export default EocChart
