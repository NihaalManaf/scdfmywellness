import axios from 'axios';

const api = axios.create({
    baseURL: 'https://scdf-mywellness-cf1617a48e34.herokuapp.com/',

});

export default api;