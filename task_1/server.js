import express from 'express';
import morgan from 'morgan';
import axios from 'axios';

const app = express();
const port = 3000;

const WEATHER_API_KEY = '94c4034781da81dbae0f55c3cea2bf4e';

app.use(morgan('dev'));

app.get('/', async (req, res) => {
    res.json({ message: "Hello World"})
});

app.get('/api/hello', async (req, res) => {
    let visitorName = req.query.visitor_name;

    if (visitorName.startsWith('"') && visitorName.endsWith('"')) {
        visitorName = visitorName.slice(1, -1);
    }

    const ipList = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    const ip = Array.isArray(ipList) ? ipList[0] : ipList.split(',')[0].trim();

    try {
        const locationResponse = await axios.get(`http://ip-api.com/json/${ip}`);
        const locationData = locationResponse.data;

        const city = locationData.city || 'Unknown';

        const weatherResponse = await axios.get(`https://api.openweathermap.org/data/2.5/weather?q=${city}&units=metric&appid=${WEATHER_API_KEY}`);
        const weatherData = weatherResponse.data;
        const temperature = weatherData.main.temp;

        res.status(200).json({
            "client_ip": ip,
            "location": city,
            "greeting": `Hello, ${visitorName}!, the temperature is ${temperature} degrees Celcius in ${city}`
        })
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Failed to retrieve location or weather data' });
    }
});

app.use((req, res, next) => {
    res.status(404).send('404 - Page Not Found');
});

app.listen(port, () => {
    console.log(`Succesfully Connected on port ${port}`);
});