import { useState } from 'react';
import './TabHolder.css';
import RegisterRecruits from './RegisterRecruits';
import EocReport from './EocReport';
import TextBlast from './TextBlast';

function TabHolder() {
    const [activeTab, setActiveTab] = useState('Tab1');

    const renderContent = () => {
        switch (activeTab) {
            case 'Tab1':
                return <RegisterRecruits />;
            case 'Tab2':
                return <EocReport />;
            case 'Tab3':
                return <TextBlast />;
            case 'Tab4':
                return "Could automate more features like attedance, etc";
            default:
                return null;
        }
    };

    return (
        <div>
            <h1 className='title'> SCDF MyWellness Dashboard</h1>
            <div className='tabs'>
                <button 
                    className={`tab ${activeTab === 'Tab1' ? 'active' : ''}`} 
                    onClick={() => setActiveTab('Tab1')}
                >
                    Registration
                </button>
                <button 
                    className={`tab ${activeTab === 'Tab2' ? 'active' : ''}`} 
                    onClick={() => setActiveTab('Tab2')}
                >
                    EOC Report Data
                </button>
                <button 
                    className={`tab ${activeTab === 'Tab3' ? 'active' : ''}`} 
                    onClick={() => setActiveTab('Tab3')}
                >
                    Text Blast
                </button>
                <button 
                    className={`tab ${activeTab === 'Tab4' ? 'active' : ''}`} 
                    onClick={() => setActiveTab('Tab4')}
                >
                    Attendance
                </button>
            </div>
            <div>
                {renderContent()}
            </div>
        </div>
    );
}

export default TabHolder;
