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

    // Modal state
    const [isModalOpen, setIsModalOpen] = useState(false);

    async function fetchEOCdData() {
      const response = await api.post('/generateEOC', {startDate:{startDate}, endDate:{endDate}} ); 
      console.log(response)
    }

    // Functions to open and close modal
    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);

    const handleSubmit = () => {
        console.log("Start Date:", startDate);
        console.log("End Date:", endDate);
        fetchEOCdData();
        openModal();
    };

    return (
        <div className="tab-content-area">
            <div>
                <div>
                    <h1>Generate EOC Report</h1>
                    <p>Click on submit to generate the EOC report.</p>
                </div>
                <div className="dates-field">
                    <DateSelecter text="Start Date:" selectedDate={startDate} setSelectedDate={setStartDate} />
                    <DateSelecter text="End Date:" selectedDate={endDate} setSelectedDate={setEndDate} />
                    <button className="submit-button" onClick={handleSubmit}>Submit</button>
                </div>
            </div>

            {/* Modal Component */}
            <Modal isOpen={isModalOpen} onClose={closeModal} startDate={startDate} endDate={endDate} total_users={total_users}
            total_users_reg={total_users_reg} total_qns={total_qns} total_broadcasts={total_broadcasts} />
        </div>
    );
}

export default EocReport;
