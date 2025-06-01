import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import type { Request, Response } from 'express';
import { registerUser, loginUser, getUserInfo } from './controller/user.js';
import rateLimit from 'express-rate-limit';
import { createPost, getPosts, likePost, dislikePost } from './controller/post.js';
dotenv.config();



const PORT = process.env.PORT || 3000;
const app = express();

app.use(cors({origin: "*"})); 
app.use(express.json());
app.use(express.urlencoded({ extended: true }));



app.get('/', (req: Request, res: Response) => {
  res.send('Welcome to the backend server!');
});

app.post('/api/register', async (req: Request, res: Response) => {
  try {
    const { username, email, password } = req.body;
    const user = await registerUser({ username, email, password });
    res.status(201).json({ user });
  } catch (e: any) {
    console.error("Erreur complète registerUser:", e, typeof e, JSON.stringify(e));
    res.status(400).json({ error: e.message || e.toString() || "Erreur inconnue" });
  }
});

const loginRateLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 5, // Limit each IP to 5 login requests per `window` (1 minute)
  message: { error: "Too many login attempts. Please try again later." },
});

app.post('/api/login', loginRateLimiter, async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;
    const { token, user } = await loginUser({ email, password });
    res.json({ token, user });
  } catch (e: any) {
    res.status(400).json({ error: e.message });
  }
});

app.get('/api/user-info', (req, res) => {
  (async () => {
    try {
      const userId = req.query.userId as string;
      if (!userId) return res.status(400).json({ error: 'userId requis' });
      const user = await getUserInfo(userId);
      res.json({ user });
    } catch (e: any) {
      res.status(400).json({ error: e.message });
    }
  })();
});

app.get('/api/posts', getPosts as any);
app.post('/api/posts', createPost as any);
app.post('/api/posts/:postId/like', likePost as any);
app.post('/api/posts/:postId/dislike', dislikePost as any);

export default app;


app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
