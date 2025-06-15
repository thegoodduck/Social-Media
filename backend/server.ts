import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import type { Request, Response } from 'express';
import { registerUser, loginUser, getUserInfo } from './controller/user.js';
import rateLimit from 'express-rate-limit';
import { createPost, getPosts, likePost, dislikePost } from './controller/post.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
dotenv.config();

// ESM-compatible __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = process.env.PORT || 3000;
const app = express();

// Load global config.json from project root
const configPath = path.resolve(__dirname, '../config.json');
let globalConfig: any = {};
try {
  if (fs.existsSync(configPath)) {
    globalConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  }
} catch (e) {
  console.error('Failed to load config.json:', e);
}

// Helper to get trusted servers from config
const getTrustedServers = (): string[] => {
  return Array.isArray(globalConfig.federationTrustedServers)
    ? globalConfig.federationTrustedServers
    : [];
};

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

// Helper to wrap async route handlers for Express/TypeScript
function wrapAsync(fn: any) {
  return function(req: Request, res: Response, next: any) {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

// --- Decentralized/Federation Endpoints ---
// Use the global fetch API available in Node.js v18+
// If you need to support older Node.js versions, install 'node-fetch' and import it at the top
// import fetch from 'node-fetch';

// Discover remote servers (static for now, could be dynamic in future)
app.get('/federation/servers', (req: Request, res: Response) => {
  res.json({
    servers: [
      // Example: { name: 'Pulse Demo', url: 'https://pulse-demo.example.com' }
    ]
  });
});

// Proxy remote posts from another Pulse server
app.get('/federation/posts', wrapAsync(async (req: Request, res: Response) => {
  const { remote } = req.query;
  const trustedServers = getTrustedServers();
  if (!remote || typeof remote !== 'string' || !trustedServers.includes(remote)) {
    return res.status(400).json({ error: 'Invalid or untrusted remote parameter' });
  }
  try {
    const fetchRes = await fetch(`${remote}/api/posts`);
    if (!fetchRes.ok) throw new Error('Remote fetch failed');
    const data = await fetchRes.json();
    res.json(data);
  } catch (e: any) {
    res.status(502).json({ error: 'Failed to fetch remote posts', message: 'An error occurred while processing the request.' });
  }
}));

// Proxy remote user info
app.get('/federation/user-info', wrapAsync(async (req: Request, res: Response) => {
  const { remote, userId } = req.query;
  const trustedServers = getTrustedServers();
  if (!remote || !userId || typeof remote !== 'string' || typeof userId !== 'string' || !trustedServers.includes(remote)) {
    return res.status(400).json({ error: 'Invalid or untrusted remote parameter' });
  }
  try {
    const fetchRes = await fetch(`${remote}/api/user-info?userId=${encodeURIComponent(userId)}`);
    if (!fetchRes.ok) throw new Error('Remote fetch failed');
    const data = await fetchRes.json();
    res.json(data);
  } catch (e: any) {
    res.status(502).json({ error: 'Failed to fetch remote user info', details: e.message });
  }
}));

// Proxy remote videos
app.get('/federation/videos', wrapAsync(async (req: Request, res: Response) => {
  const { remote } = req.query;
  const trustedServers = getTrustedServers();
  if (!remote || typeof remote !== 'string' || !trustedServers.includes(remote)) {
    return res.status(400).json({ error: 'Invalid or untrusted remote parameter' });
  }
  try {
    const fetchRes = await fetch(`${remote}/api/videos`);
    if (!fetchRes.ok) throw new Error('Remote fetch failed');
    const data = await fetchRes.json();
    res.json(data);
  } catch (e: any) {
    res.status(502).json({ error: 'Failed to fetch remote videos', details: e.message });
  }
}));

// API Discovery endpoint for federation (dynamic, based on current post API source)
app.get('/federation/discover', (req: Request, res: Response) => {
  // Try to detect the remote API used for posts (from env or config, fallback to local)
  // You can set this in an env var like FEDERATION_POSTS_API or similar
  const postsApi = process.env.FEDERATION_POSTS_API || 'http://localhost:3000/api/posts';
  const userInfoApi = process.env.FEDERATION_USERINFO_API || 'http://localhost:3000/api/user-info';
  const videosApi = process.env.FEDERATION_VIDEOS_API || 'http://localhost:3000/api/videos';

  // Federation endpoints (always local to this instance)
  const baseUrl = process.env.FEDERATION_BASE_URL || `http://localhost:${PORT}`;

  res.json({
    posts: postsApi,
    userInfo: userInfoApi,
    videos: videosApi,
    federationPosts: `${baseUrl}/federation/posts`,
    federationUserInfo: `${baseUrl}/federation/user-info`,
    federationVideos: `${baseUrl}/federation/videos`,
    federationInbox: `${baseUrl}/federation/inbox`,
    description: 'API discovery for Pulse federation. Endpoints reflect the current remote API configuration.'
  });
});

// Accept incoming federation requests (for future: e.g. push posts, follow, etc.)
app.post('/federation/inbox', (req: Request, res: Response) => {
  // For now, just log and accept
  console.log('Received federation inbox:', req.body);
  res.json({ status: 'ok' });
});

export default app;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
