import DateSelecter from "./Eoc/DateSelecter";
import './TabHolder.css';
import { useState } from 'react';
import Modal from './Eoc/Modal';
import api from "../api";

function EocReport() {
    const [startDate, setStartDate] = useState<string>("");
    const [endDate, setEndDate] = useState<string>("");

    const [total_users, setTotalUsers] = useState<number>(0);
    const [total_users_reg, setTotalUsersReg] = useState<number>(0);
    const [total_qns, setTotalQns] = useState<number>(0);
    const [total_broadcasts, setTotalBroadcasts] = useState<number>(0);
    const [piedata, setPiedata] = useState<any[]>([]);

    // Modal state
    const [isModalOpen, setIsModalOpen] = useState(false);

    async function fetchEOCdData(startDate: string, endDate: string) {
      const response = await api.post('/generateEOC', { startDate, endDate }); 
      console.log(response); //use state fns here to set values

      setTotalUsers(response.data.total_users);
      setTotalUsersReg(response.data.total_users_reg);
      setTotalQns(response.data.total_qns);
      setTotalBroadcasts(response.data.total_broadcasts);
      setPiedata(response.data.piedata);
    }

    // Functions to open and close modal
    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);

    const handleSubmit = () => {
        console.log("Start Date:", startDate);
        console.log("End Date:", endDate);
        fetchEOCdData(startDate, endDate);
        openModal();
    };

    return (
        <div className="tab-content-area">
            <div>
          <h1>Generate EOC Report</h1>
          <p>Click on submit to generate the EOC report.</p>
            </div>
            <div className="dates-field">
          <DateSelecter text="Start Date:" selectedDate={startDate} setSelectedDate={setStartDate} />
          <DateSelecter text="End Date:" selectedDate={endDate} setSelectedDate={setEndDate} />
          <button className="submit-button" onClick={handleSubmit}>Submit</button>
            </div>
            <Modal 
              isOpen={isModalOpen} 
              onClose={closeModal} 
              startDate={startDate} 
              endDate={endDate} 
              total_users={total_users}
              total_users_reg={total_users_reg} 
              total_qns={total_qns} 
              total_broadcasts={total_broadcasts} 
              piedata={piedata}
            />
        </div>
    );
}

export default EocReport;
