import '../TabHolder.css';

interface DateSelecterProps {
    text: string;
    selectedDate: string;
    setSelectedDate: (date: string) => void;
}

const DateSelecter: React.FC<DateSelecterProps> = ({ text, selectedDate, setSelectedDate }) => {
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelectedDate(event.target.value);
    };

    const formatDate = (dateString: string) => {
        const options: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'long', year: 'numeric' };
        return new Date(dateString).toLocaleDateString('en-GB', options);
    };

    return (
        <div className="dateform">
            <label htmlFor="date">{text}</label>
            <input
                type="date"
                id="date"
                name="date"
                value={selectedDate}
                onChange={handleChange}
            />
            <p>Selected Date: {selectedDate ? formatDate(selectedDate) : ""}</p>
        </div>
    );
};

export default DateSelecter;

