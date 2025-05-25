import type { Config } from "drizzle-kit";
import dotenv from "dotenv";
dotenv.config();


export default {
  schema: "./schema/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    host: process.env.DB_HOST || "localhost",
    port: Number(process.env.DB_PORT) || 5432,
    user: process.env.DB_USER || "postgres",
    password: process.env.DB_PASSWORD || "password",
    database: process.env.DB_NAME || "mydb",
    ssl: process.env.DB_SSL === "true" ? { rejectUnauthorized: false } : false,
  },
} satisfies Config;
