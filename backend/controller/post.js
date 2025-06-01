import { db } from '../schema/index.js';
import { posts, users } from '../schema/schema.js';
import { eq } from 'drizzle-orm';

export const createPost = async (req, res) => {
    const { username, message, photo } = req.body;
    if (!username || !message) {
        return res.status(400).json({ error: 'username and message are required' });
    }
    // Find user by username
    const user = await db.select().from(users).where(eq(users.username, username));
    if (!user.length) {
        return res.status(404).json({ error: 'User not found' });
    }
    const userId = user[0].id;
    // Insert post into DB
    const inserted = await db.insert(posts).values({
        userId,
        content: message,
        imageUrl: photo || null,
        createdAt: new Date(),
    }).returning();
    const newPost = inserted[0];
    res.status(201).json({
        _id: newPost.id,
        username,
        message: newPost.content,
        photo: newPost.imageUrl,
        timestamp: newPost.createdAt,
        likes: 0,
        dislikes: 0,
        views: 0,
        comments: [],
        showComments: false,
        commentInput: ''
    });
};

export const getPosts = async (req, res) => {
    // Join posts with users to get username
    const dbPosts = await db.select({
        id: posts.id,
        userId: posts.userId,
        content: posts.content,
        imageUrl: posts.imageUrl,
        createdAt: posts.createdAt,
        username: users.username
    }).from(posts).leftJoin(users, eq(posts.userId, users.id)).orderBy(posts.createdAt.desc());
    const postsOut = dbPosts.map(post => ({
        _id: post.id,
        username: post.username,
        message: post.content,
        photo: post.imageUrl,
        timestamp: post.createdAt,
        likes: 0,
        dislikes: 0,
        views: 0,
        comments: [],
        showComments: false,
        commentInput: ''
    }));
    res.json({ posts: postsOut });
};
