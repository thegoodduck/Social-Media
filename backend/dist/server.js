import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { registerUser, loginUser, getUserInfo } from './controller/user';
import rateLimit from 'express-rate-limit';
import { createPost, getPosts } from './controller/post';
dotenv.config();
const PORT = process.env.PORT || 3000;
const app = express();
app.use(cors({ origin: "*" }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.get('/', (req, res) => {
    res.send('Welcome to the backend server!');
});
app.post('/api/register', async (req, res) => {
    try {
        const { username, email, password } = req.body;
        const user = await registerUser({ username, email, password });
        res.status(201).json({ user });
    }
    catch (e) {
        console.error("Erreur complète registerUser:", e, typeof e, JSON.stringify(e));
        res.status(400).json({ error: e.message || e.toString() || "Erreur inconnue" });
    }
});
const loginRateLimiter = rateLimit({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 5, // Limit each IP to 5 login requests per `window` (1 minute)
    message: { error: "Too many login attempts. Please try again later." },
});
app.post('/api/login', loginRateLimiter, async (req, res) => {
    try {
        const { email, password } = req.body;
        const { token, user } = await loginUser({ email, password });
        res.json({ token, user });
    }
    catch (e) {
        res.status(400).json({ error: e.message });
    }
});
app.get('/api/user-info', (req, res) => {
    (async () => {
        try {
            const userId = req.query.userId;
            if (!userId)
                return res.status(400).json({ error: 'userId requis' });
            const user = await getUserInfo(userId);
            res.json({ user });
        }
        catch (e) {
            res.status(400).json({ error: e.message });
        }
    })();
});
app.get('/api/posts', getPosts);
app.post('/api/posts', createPost);
export default app;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
