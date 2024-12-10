import React from "react";
import './Modal.css'; // Add some styles for the overlay and modal

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    startDate: string;
    endDate: string;
    total_users: number;
    total_users_reg: number;
    total_qns: number;
    total_broadcasts: number;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, total_users, total_users_reg, total_qns, total_broadcasts  }) => {
  if (!isOpen) return null; // Render nothing if the modal is not open

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="modal-close-button" onClick={onClose}>
          Close
        </button>

        <h1>End Of Course Report</h1>
        <br></br>
        <p>Total Number Of Users: {total_users}</p>
        <p>Total Number Of Registered Users: {total_users_reg}</p>
        <p>Total Number of Questions asked: {total_qns}</p>
        <p>Total Number of Broadcasts: {total_broadcasts}</p>

      </div>
    </div>
    
  );
};

export default Modal;
