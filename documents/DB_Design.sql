CREATE TABLE "userInfo" (
  "id" int PRIMARY KEY,
  "username" varchar,
  "email" varchar,
  "phone" varchar,
  "credit" int
);

CREATE TABLE "user" (
  "id" int,
  "base_info" link,
  "projects" list[]
);

CREATE TABLE "designer" (
  "id" int,
  "base_info" link,
  "profile_picture" link,
  "score" int,
  "avg_feedback" double,
  "rate" int,
  "projects" list[]
);

CREATE TABLE "design" (
  "id" int,
  "client" link,
  "worker" link,
  "on_portfolio" boolean,
  "design_type" selector,
  "description" varchar,
  "feedback" int,
  "price_spent" int,
  "time_posted" datetime,
  "target_deadline" datetime,
  "time_finished" datetime,
  "designer_requested" list[],
  "status" list[],
  "input_image" list[],
  "output_image" imageFile
);

CREATE TABLE "imageFile" (
  "int" id,
  "image" file,
  "thumbnail" file
);

ALTER TABLE "userInfo" ADD FOREIGN KEY ("id") REFERENCES "user" ("base_info");

ALTER TABLE "userInfo" ADD FOREIGN KEY ("id") REFERENCES "designer" ("base_info");

ALTER TABLE "user" ADD FOREIGN KEY ("id") REFERENCES "design" ("client");

ALTER TABLE "designer" ADD FOREIGN KEY ("id") REFERENCES "design" ("worker");

ALTER TABLE "imageFile" ADD FOREIGN KEY ("int") REFERENCES "designer" ("profile_picture");

ALTER TABLE "imageFile" ADD FOREIGN KEY ("int") REFERENCES "design" ("input_image");

ALTER TABLE "imageFile" ADD FOREIGN KEY ("int") REFERENCES "design" ("output_image");

ALTER TABLE "design" ADD FOREIGN KEY ("id") REFERENCES "designer" ("projects");

ALTER TABLE "design" ADD FOREIGN KEY ("id") REFERENCES "user" ("projects");
