ALTER TABLE "posts" DROP CONSTRAINT "posts_author_id_users_id_fk";
--> statement-breakpoint
DROP INDEX "post_author_id_idx";--> statement-breakpoint
DROP INDEX "post_type_idx";--> statement-breakpoint
DROP INDEX "post_privacy_idx";--> statement-breakpoint
DROP INDEX "post_created_at_idx";--> statement-breakpoint
DROP INDEX "post_scheduled_for_idx";--> statement-breakpoint
ALTER TABLE "posts" ALTER COLUMN "content" SET NOT NULL;--> statement-breakpoint
ALTER TABLE "posts" ADD COLUMN "user_id" uuid NOT NULL;--> statement-breakpoint
ALTER TABLE "posts" ADD COLUMN "image_url" varchar(255);--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "author_id";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "type";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "media";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "privacy";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "location";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "tagged_users";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "hashtags";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "link_preview";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "poll_data";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "likes_count";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "comments_count";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "shares_count";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "views_count";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "is_edited";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "edited_at";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "scheduled_for";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "is_deleted";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "deleted_at";--> statement-breakpoint
ALTER TABLE "posts" DROP COLUMN "updated_at";