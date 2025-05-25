import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
dotenv.config();



const PORT = process.env.PORT || 3000;
const app = express();

app.use(cors({origin: "*"})); 
app.use(express.json());
app.use(express.urlencoded({ extended: true }));



app.get('/', (req, res) => {
  res.send('Welcome to the backend server!');
});



app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
