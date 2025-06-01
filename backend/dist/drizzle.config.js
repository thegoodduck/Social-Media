export default {
    schema: "./schema/schema.ts",
    out: "./migrations",
    dialect: "postgresql",
    dbCredentials: {
        host: "localhost",
        port: 5432,
        user: "postgres",
        password: "sync",
        database: "social_db",
        ssl: false
    }
};
