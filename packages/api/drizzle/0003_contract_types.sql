ALTER TABLE "recommendations" ALTER COLUMN "score" SET DATA TYPE double precision;--> statement-breakpoint
ALTER TABLE "runs" ALTER COLUMN "anchor_ids" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "runs" ALTER COLUMN "anchor_ids" SET DATA TYPE bigint[] USING "anchor_ids"::bigint[];--> statement-breakpoint
ALTER TABLE "runs" ALTER COLUMN "anchor_ids" SET DEFAULT '{}'::bigint[];--> statement-breakpoint
ALTER TABLE "talks" ALTER COLUMN "author_ids" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "talks" ALTER COLUMN "author_ids" SET DATA TYPE bigint[] USING "author_ids"::bigint[];--> statement-breakpoint
ALTER TABLE "talks" ALTER COLUMN "author_ids" SET DEFAULT '{}'::bigint[];--> statement-breakpoint
ALTER TABLE "talks" ALTER COLUMN "presenter_ids" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "talks" ALTER COLUMN "presenter_ids" SET DATA TYPE bigint[] USING "presenter_ids"::bigint[];--> statement-breakpoint
ALTER TABLE "talks" ALTER COLUMN "presenter_ids" SET DEFAULT '{}'::bigint[];
