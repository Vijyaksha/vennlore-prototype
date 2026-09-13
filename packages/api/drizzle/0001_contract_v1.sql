CREATE TABLE "runs" (
	"run_id" text PRIMARY KEY NOT NULL,
	"engine_id" text NOT NULL,
	"kind" text NOT NULL,
	"engine_version" text NOT NULL,
	"models" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"corpus_hash" text DEFAULT '' NOT NULL,
	"anchor_ids" integer[] DEFAULT '{}'::integer[] NOT NULL,
	"started_at" timestamp with time zone NOT NULL,
	"finished_at" timestamp with time zone NOT NULL,
	"index_path" text,
	"contract_version" integer NOT NULL
);
--> statement-breakpoint
-- Intentional data reset: the 18 legacy rows predate the contract and are reseeded from app_seed.v2.json.
-- Required because engine_id/rank/run_id/contract_version are added NOT NULL with no default.
DELETE FROM "recommendations";--> statement-breakpoint
ALTER TABLE "recommendations" RENAME COLUMN "is_match" TO "match";--> statement-breakpoint
ALTER TABLE "recommendations" DROP CONSTRAINT "recommendations_for_talk_id_candidate_id_pk";--> statement-breakpoint
ALTER TABLE "recommendations" ALTER COLUMN "score" SET DATA TYPE real;--> statement-breakpoint
ALTER TABLE "recommendations" ADD COLUMN "engine_id" text NOT NULL;--> statement-breakpoint
ALTER TABLE "recommendations" ADD COLUMN "rank" integer NOT NULL;--> statement-breakpoint
ALTER TABLE "recommendations" ADD COLUMN "shared_methods" text[] DEFAULT '{}'::text[] NOT NULL;--> statement-breakpoint
ALTER TABLE "recommendations" ADD COLUMN "evidence" jsonb DEFAULT '{}'::jsonb NOT NULL;--> statement-breakpoint
ALTER TABLE "recommendations" ADD COLUMN "run_id" text NOT NULL;--> statement-breakpoint
ALTER TABLE "recommendations" ADD COLUMN "contract_version" integer NOT NULL;--> statement-breakpoint
ALTER TABLE "recommendations" ADD CONSTRAINT "recommendations_engine_id_for_talk_id_candidate_id_pk" PRIMARY KEY("engine_id","for_talk_id","candidate_id");--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "external_id" text;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "topics" text[] DEFAULT '{}'::text[] NOT NULL;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "type" text;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "is_invited" boolean DEFAULT false NOT NULL;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "is_withdrawn" boolean DEFAULT false NOT NULL;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "sort_order" integer;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "presentation_location" text;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "author_ids" integer[] DEFAULT '{}'::integer[] NOT NULL;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "presenter_ids" integer[] DEFAULT '{}'::integer[] NOT NULL;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "publication_reference" text;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "funding_acknowledgement" text;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "team_acknowledgement" text;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "session_id" integer;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "session_code" text;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "session_type" text;--> statement-breakpoint
ALTER TABLE "talks" ADD COLUMN "session_topics" text[] DEFAULT '{}'::text[] NOT NULL;--> statement-breakpoint
ALTER TABLE "recommendations" DROP COLUMN "same_method";--> statement-breakpoint
ALTER TABLE "recommendations" DROP COLUMN "specificity";--> statement-breakpoint
ALTER TABLE "recommendations" DROP COLUMN "usage_parallel";