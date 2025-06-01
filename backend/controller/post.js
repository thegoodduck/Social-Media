// In-memory post storage (replace with DB in production)
let posts = [];
export const createPost = (req, res) => {
    const { username, message, photo, sessionId } = req.body;
    if (!username || !message) {
        return res.status(400).json({ error: 'username and message are required' });
    }
    const newPost = {
        _id: Date.now().toString(),
        username,
        message,
        photo: photo || null,
        sessionId: sessionId || null,
        timestamp: new Date().toISOString(),
        likes: 0,
        dislikes: 0,
        views: 0,
        comments: [],
        showComments: false,
        commentInput: ''
    };
    posts.unshift(newPost);
    res.status(201).json(newPost);
};
export const getPosts = (req, res) => {
    res.json({ posts });
};
