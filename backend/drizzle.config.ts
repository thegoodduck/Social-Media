import type { Config } from "drizzle-kit";
export default {
  schema: "./schema/schema.ts",
  out: "./migrations",
  dialect: "postgresql",
  dbCredentials: {
    host: "localhost",
    port: 5432,
    user: "social_user",
    password: "social_pass",
    database: "social_db",
    ssl: false
  }
} satisfies Config;