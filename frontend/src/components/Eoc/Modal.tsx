import React, { useState } from "react";
import './Modal.css'; // Add some styles for the overlay and modal
import EocChart from "./EocChart";
import { Scale, scales } from "chart.js";

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    startDate: string;
    endDate: string;
    total_users: number;
    total_users_reg: number;
    total_qns: number;
    total_broadcasts: number;
    piedata: Array<number>;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, total_users, total_users_reg, total_qns, total_broadcasts, piedata  }) => {
  if (!isOpen) return null; // Render nothing if the modal is not open
    
    
    
    const data = {
        labels: [
            "Emotional Distress",
            "Salary Details",
            "ORD & POP [Operationally Ready Date and Passing Out Parade]",
            "Vocations",
            "Sign-on Related",
            "IPPT",
            "Training & Leaves",
            "Prohibited Items",
            "Miscellaneous/Other"
        ],
        datasets: [{
        label: 'SCDF Mywellness Categories',
        data: piedata,
        backgroundColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 205, 86)'
        ],
        hoverOffset: 4
        }]
    };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
  };


  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close-button" onClick={onClose}>
          Close
        </button>
        <div className="data-area" > 
            <h1>End Of Course Report</h1>
            <br></br>
            <p>Total Number Of Users: {total_users}</p>
            <p>Total Number Of Registered Users: {total_users_reg}</p>
            <p>Total Number of Questions asked: {total_qns}</p>
            <p>Total Number of Broadcasts: {total_broadcasts}</p>
        </div>
        <div className="pie-area">
            <EocChart options={options} data={data}/>
        </div>
      </div>

    </div>
    
  );
};

export default Modal;
