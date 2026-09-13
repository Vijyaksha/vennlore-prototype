CREATE TABLE "locations" (
	"id" bigint PRIMARY KEY NOT NULL,
	"building" text NOT NULL,
	"room" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "recommendations" (
	"for_talk_id" integer NOT NULL,
	"candidate_id" integer NOT NULL,
	"same_method" integer NOT NULL,
	"specificity" integer NOT NULL,
	"usage_parallel" integer NOT NULL,
	"score" integer NOT NULL,
	"is_match" boolean NOT NULL,
	"cross_domain" boolean NOT NULL,
	"why" text DEFAULT '' NOT NULL,
	"strongest_parallel" text DEFAULT '' NOT NULL,
	CONSTRAINT "recommendations_for_talk_id_candidate_id_pk" PRIMARY KEY("for_talk_id","candidate_id")
);
--> statement-breakpoint
CREATE TABLE "talks" (
	"id" integer PRIMARY KEY NOT NULL,
	"title" text NOT NULL,
	"session_title" text,
	"units" text[] DEFAULT '{}'::text[] NOT NULL,
	"start" timestamp with time zone,
	"end" timestamp with time zone,
	"building" text,
	"room" text,
	"abstract" text DEFAULT '' NOT NULL
);
