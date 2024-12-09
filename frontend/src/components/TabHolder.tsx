import React, { useState } from 'react';
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
            default:
                return null;
        }
    };

    return (
        <div>
            <h1 className='title'> SCDF MyWellness Dashboard</h1>
            <div className='tabs'>
                <button className='tab' onClick={() => setActiveTab('Tab1')}>Registration</button>
                <button className='tab' onClick={() => setActiveTab('Tab2')}>EOC Report Data</button>
                <button className='tab' onClick={() => setActiveTab('Tab3')}>Text Blast</button>
            </div>
            <div>
                {renderContent()}
            </div>
        </div>
    );
}

export default TabHolder;
